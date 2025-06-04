from app import app, db
from datetime import datetime
from flask import render_template, url_for, request, redirect, flash, jsonify, copy_current_request_context, abort
from flask_login import login_required, login_user, logout_user, current_user
from app.forms import UserForm, LoginForm, ConfiguracoesForm
from app.models import User, Notificacao, Mensagem
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
import threading
import time
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

### INDEX
@app.route('/')
def index():
    return render_template('index.html')

### HOME
from flask import flash

@app.route('/home/<int:id>/', endpoint='home')
@login_required
def home(id):
    obj = User.query.get_or_404(id)

    pesquisa = request.args.get('pesquisa', '').strip()

    if pesquisa:
        dados = User.query.filter(
            or_(
                User.nome.ilike(f'%{pesquisa}%'),
                User.sobreNome.ilike(f'%{pesquisa}%')
            )
        ).order_by(User.nome).all()
    else:
        dados = User.query.order_by(User.nome).all()

    pessoas = User.query.all()
    quantidade = len(pessoas)

    context = {
        'busca': bool(pesquisa),
        'dados': dados
    }

    # Buscar notificações não lidas para o usuário atual (obj)
    notificacoes_nao_lidas = Notificacao.query.filter_by(
        destinatario_id=obj.id,
        lida=False
    ).all()

    # Marcar notificações como lidas e salvar no banco
    if notificacoes_nao_lidas:
        for notificacao in notificacoes_nao_lidas:
            notificacao.lida = True
        db.session.commit()

    # Carregar todas notificações do usuário (podem estar todas lidas após atualização)
    notificacoes = Notificacao.query.options(
        joinedload(Notificacao.remetente)
    ).filter(
        Notificacao.destinatario_id == obj.id
    ).all()

    # Verificar se existem notificações não lidas (deve ser falso após marcar todas)
    tem_notificacao = any(notificacao.lida == False for notificacao in notificacoes)

    # Definir cor de fundo padrão caso não exista
    fundo = obj.cor_fundo if obj.cor_fundo and obj.cor_fundo.strip() else "linear-gradient(to right, #fff, #a6e3ed)"

    return render_template(
        'home.html',
        obj=obj,
        usuario=obj,
        fundo=fundo,
        context=context,
        pessoas=pessoas,
        quantidade=quantidade,
        user_id=id,
        notificacoes=notificacoes,
        tem_notificacao=tem_notificacao,
    )


### CADASTRO
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = UserForm()

    obj = {
        'cor_fundo': "linear-gradient(to right, #fff, #a6e3ed)"  # Cor original
    }

    if form.validate_on_submit():
        arquivo_imagem = form.imagem.data
        nome = form.nome.data
        sobreNome = form.sobreNome.data
        email = form.email.data
        senha = generate_password_hash(form.senha.data)
        status = form.status.data
        cpf_cnpj = form.cpf_cnpj.data

        if arquivo_imagem and arquivo_imagem.filename != '':
            extensao = os.path.splitext(arquivo_imagem.filename)[1]
            nome_arquivo = f"{uuid.uuid4().hex}{extensao}"  # Nome único para evitar conflito
            caminho = os.path.join(app.root_path, 'static/imagens', nome_arquivo)
            arquivo_imagem.save(caminho)
        else:
            nome_arquivo = 'default.png'

        novo_usuario = User(
            imagem=nome_arquivo,
            nome=nome,
            sobreNome=sobreNome,
            email=email,
            senha=senha,
            status=status,
            cpf_cnpj = cpf_cnpj
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html', form=form, obj=obj)

### LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home', id=current_user.id))

    form = LoginForm()

    obj = {
        'cor_fundo': "linear-gradient(to right, #fff, #a6e3ed)"  # Cor original
    }

    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('home', id=user.id))
        else:
            flash('E-mail ou senha inválidos.', 'danger')

    return render_template('login.html', form=form, obj=obj)

### LOGOUT
@app.route("/sair/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

### SEGUIR
@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)

    if user == current_user:
        flash('Você não pode seguir a si mesmo.')
        return redirect(url_for('home', id=user_id))

    if not current_user.is_following(user):
        current_user.follow(user)

        mensagem = f"{current_user.nome} {current_user.sobreNome} começou a te seguir."

        nova_notificacao = Notificacao(
            mensagem=mensagem,
            destinatario_id=user.id,
            remetente_id=current_user.id,
            tipo='novo_seguidor',
            criada_em=datetime.utcnow()
        )

        db.session.add(nova_notificacao)
        db.session.commit()

        flash(f'Você está seguindo {user.nome}.')
    else:
        flash(f'Você já está seguindo {user.nome}.')

    return redirect(url_for('home', id=user_id))


@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user_to_unfollow = User.query.get_or_404(user_id)
    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    return jsonify(success=True, user_id=user_id)

### SEGUIDORES
@app.route('/seguidores/<int:user_id>/', endpoint='seguidores')
@login_required
def seguidores(user_id):
    usuario = User.query.get_or_404(user_id)

    seguidores = usuario.followers.all()  # Obter seguidores como lista

    ids_que_eu_sigo = [u.id for u in current_user.followed.all()]

    obj = {
        'cor_fundo': None
    }

    return render_template('seguidores.html', usuario=usuario, seguidores=seguidores, ids_que_eu_sigo=ids_que_eu_sigo, obj=obj)


### USUÁRIOS QUE ESTOU SEGUINDO
@app.route('/seguindo/<int:id>/', endpoint='seguindo')
@login_required
def seguindo(id):
    obj = User.query.get_or_404(id)
    pesquisa = request.args.get('pesquisa', '').strip()

    seguindo_query = obj.followed.all()

    if pesquisa:
        seguindo_filtrado = [user for user in seguindo_query if pesquisa.lower() in user.nome.lower()]
    else:
        seguindo_filtrado = seguindo_query

    context = {
        'dados': seguindo_filtrado,
        'usuario_atual_seguindo_ids': {u.id for u in current_user.followed.all()}
    }

    return render_template('seguindo.html', obj=obj, context=context)


### SEGUIR E DEIXAR DE SEGUIR (via AJAX)
@app.route('/seguir/<int:id>', methods=['POST'])
@login_required
def seguir_usuario(id):
    usuario = User.query.get_or_404(id)
    if not current_user.is_following(usuario):
        current_user.follow(usuario)
        db.session.commit()

        nova_notificacao = Notificacao(
            user_id=usuario.id,
            tipo='novo_seguidor',
            mensagem=f'{current_user.nome} começou a te seguir.',
            lida=False,
            criado_em=datetime.utcnow()
        )
        db.session.add(nova_notificacao)
        db.session.commit()
    return jsonify({'status': 'seguido'})

@app.route('/deixar_de_seguir/<int:id>', methods=['POST'])
@login_required
def deixar_de_seguir_usuario(id):
    usuario = User.query.get_or_404(id)
    if current_user.is_following(usuario):
        current_user.unfollow(usuario)
        db.session.commit()
    return jsonify({'status': 'removido'})


### NOTIFICACAO

@app.route('/notificacao/delete/<int:notificacao_id>', methods=['DELETE'])
@login_required
def deletar_notificacao(notificacao_id):
    notificacao = Notificacao.query.get_or_404(notificacao_id)

    # Segurança: só pode deletar notificações do próprio usuário
    if notificacao.destinatario_id != current_user.id:
        return jsonify({"erro": "Acesso negado"}), 403

    db.session.delete(notificacao)
    db.session.commit()
    return jsonify({"status": "sucesso"})

@app.route('/notificacoes_lidas', methods=['POST'])
@login_required
def notificacoes_lidas():
    notificacoes = Notificacao.query.filter_by(destinatario_id=current_user.id, lida=False).all()
    for n in notificacoes:
        n.lida = True
    db.session.commit()
    return jsonify({"status": "notificações marcadas como lidas"})

@app.route('/verificar_novas_notificacoes')
@login_required
def verificar_novas_notificacoes():
    count = Notificacao.query.filter_by(destinatario_id=current_user.id, lida=False).count()
    return jsonify(temNovas=count > 0)

def excluir_notificacao_com_delay(notificacao_id, delay=0.10):
    @copy_current_request_context
    def tarefa():
        time.sleep(delay)
        notificacao = Notificacao.query.get(notificacao_id)
        if notificacao and notificacao.lida:
            db.session.delete(notificacao)
            db.session.commit()
    threading.Thread(target=tarefa).start()

@app.route('/notificacao/<int:notificacao_id>/ler', methods=['POST'])
@login_required
def marcar_notificacao_como_lida(notificacao_id):
    notificacao = Notificacao.query.get_or_404(notificacao_id)

    # Segurança: só permitir leitura da própria notificação
    if notificacao.destinatario_id != current_user.id:
        return jsonify({'erro': 'Acesso negado'}), 403

    if not notificacao.lida:
        notificacao.lida = True
        db.session.commit()
        excluir_notificacao_com_delay(notificacao_id)

    return jsonify({'status': 'notificação marcada como lida'})

###STATUS ONLINE/OFLINE
@app.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

###LOJA
@app.route("/loja/")
def loja():
    obj = {
        'cor_fundo': "linear-gradient(to right, #fff, #a6e3ed)"  # Cor original
    }
    return render_template('loja.html', obj=obj)

###CONFIGURAÇÕES
@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    form = ConfiguracoesForm(obj=current_user)

    obj = current_user

    if form.validate_on_submit():
        current_user.nome = form.nome.data
        current_user.sobreNome = form.sobreNome.data
        current_user.status = form.status.data
        current_user.email = form.email.data
        current_user.cor_fundo = form.cor_fundo.data

        # Tratamento da nova imagem
        if form.imagem.data:
            imagem = form.imagem.data
            extensao = os.path.splitext(imagem.filename)[1]
            nome_arquivo = f"{uuid.uuid4().hex}{extensao}"
            caminho_novo = os.path.join(app.root_path, 'static/imagens', nome_arquivo)
            imagem.save(caminho_novo)

            # Exclui a imagem anterior se não for a padrão
            imagem_antiga = current_user.imagem
            if imagem_antiga and imagem_antiga != 'default.png':
                caminho_antigo = os.path.join(app.root_path, 'static/imagens', imagem_antiga)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)

            # Atualiza no banco o novo nome da imagem
            current_user.imagem = nome_arquivo

        db.session.commit()
        flash('Configurações atualizadas com sucesso.', 'success')
        return redirect(url_for('configuracoes'))

    return render_template('configuracoes.html', form=form, obj=obj)

###EXCLUIR CONTA
@app.route('/excluir_conta/<int:id>/', methods=['POST'])
@login_required
def excluir_conta(id):
    usuario = User.query.get_or_404(id)

    # Caminho da imagem
    imagem_usuario = usuario.imagem
    if imagem_usuario and imagem_usuario != 'default.png':
        caminho_imagem = os.path.join(app.root_path, 'static/imagens', imagem_usuario)
        if os.path.exists(caminho_imagem):
            os.remove(caminho_imagem)

    logout_user()  # Desloga o usuário antes de excluir
    db.session.delete(usuario)
    db.session.commit()

    flash("Sua conta foi excluída com sucesso.", "success")
    return redirect(url_for('index'))

###ROTA MENSAGEM
@app.route('/mensagens/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def mensagens(usuario_id):
    destinatario = User.query.get_or_404(usuario_id)

    # Marcar notificações como lidas ao abrir a página de mensagens
    notificacoes_nao_lidas = Notificacao.query.filter_by(
        destinatario_id=current_user.id, lida=False
    ).all()

    for n in notificacoes_nao_lidas:
        n.lida = True
    db.session.commit()

    # Verifica se o usuário segue o destinatario
    usuarios_seguidos = current_user.followed.all()

    if request.method == 'POST':
        corpo = request.form.get('mensagem', '').strip()
        if corpo:
            nova_mensagem = Mensagem(
                remetente_id=current_user.id,
                destinatario_id=destinatario.id,
                corpo=corpo
            )
            db.session.add(nova_mensagem)

            # Criar notificação para destinatário
            notificacao = Notificacao(
                destinatario_id=destinatario.id,
                remetente_id=current_user.id,
                mensagem=f'Nova mensagem de {current_user.nome}',
                tipo='nova_mensagem'
            )
            db.session.add(notificacao)
            db.session.commit()

            flash('Mensagem enviada com sucesso.', 'success')
            return redirect(url_for('mensagens', usuario_id=usuario_id))
        else:
            flash('Mensagem não pode estar vazia.', 'warning')
            return redirect(url_for('mensagens', usuario_id=usuario_id)), 400

    mensagens = Mensagem.query.filter(
        ((Mensagem.remetente_id == current_user.id) & (Mensagem.destinatario_id == destinatario.id)) |
        ((Mensagem.remetente_id == destinatario.id) & (Mensagem.destinatario_id == current_user.id))
    ).order_by(Mensagem.data_envio.asc()).all()

    usuarios = User.query.all()

    return render_template(
        'mensagens.html',
        destinatario=destinatario,
        usuarios_seguidos=usuarios_seguidos,
        mensagens=mensagens,
        usuarios=usuarios,
        obj=current_user,
    )

@app.route('/enviar_mensagem', methods=['POST'])
@login_required
def enviar_mensagem():
    destinatario_id = request.form.get('destinatario_id')
    corpo = request.form.get('corpo')

    try:
        destinatario_id = int(destinatario_id)
    except (ValueError, TypeError):
        return jsonify({'status': 'destinatário inválido'}), 400

    if not corpo or corpo.strip() == '':
        return jsonify({'status': 'corpo da mensagem vazio'}), 400

    msg = Mensagem(
        remetente_id=current_user.id,
        destinatario_id=destinatario_id,
        corpo=corpo.strip(),
        lida=False,
        data_envio=datetime.utcnow()
    )
    db.session.add(msg)

    nova_notificacao = Notificacao(
        destinatario_id=destinatario_id,
        remetente_id=current_user.id,
        tipo='nova_mensagem',
        mensagem=f'Você recebeu uma nova mensagem de {current_user.nome}.',
        lida=False,
        criada_em=datetime.utcnow()
    )
    db.session.add(nova_notificacao)

    db.session.commit()
    return jsonify({'status': 'mensagem enviada'})

@app.route('/reexibir_usuario/<int:user_id>', methods=['POST'])
@login_required
def reexibir_usuario(user_id):
    # lógica para reexibir o usuário
    return redirect(url_for('home', id=current_user.id))

@app.route('/mensagens/editar/<int:mensagem_id>', methods=['POST'])
@login_required
def editar_mensagem(mensagem_id):
    mensagem = Mensagem.query.get_or_404(mensagem_id)

    if mensagem.remetente_id != current_user.id:
        abort(403)

    novo_texto = request.form.get('novo_texto')
    if novo_texto and novo_texto.strip():
        mensagem.corpo = novo_texto.strip()
        mensagem.editada = True
        db.session.commit()
        flash('Mensagem editada com sucesso.', 'success')

    return redirect(url_for('mensagens', usuario_id=mensagem.destinatario_id))

@app.route('/mensagens/excluir/<int:mensagem_id>', methods=['POST'])
@login_required
def excluir_mensagem(mensagem_id):
    mensagem = Mensagem.query.get_or_404(mensagem_id)

    if mensagem.remetente_id != current_user.id:
        abort(403)

    destinatario_id = mensagem.destinatario_id
    db.session.delete(mensagem)
    db.session.commit()
    flash('Mensagem excluída com sucesso.', 'success')

    return redirect(url_for('mensagens', usuario_id=destinatario_id))

@app.route('/mensagens/excluir_todas/<int:usuario_id>', methods=['POST'])
@login_required
def excluir_mensagens_usuario(usuario_id):
    usuario = User.query.get_or_404(usuario_id)

    mensagens_para_apagar = Mensagem.query.filter(
        ((Mensagem.remetente_id == current_user.id) & (Mensagem.destinatario_id == usuario.id)) |
        ((Mensagem.remetente_id == usuario.id) & (Mensagem.destinatario_id == current_user.id))
    ).all()

    for msg in mensagens_para_apagar:
        db.session.delete(msg)
    db.session.commit()

    flash(f'Todas as mensagens do chat com {usuario.nome} foram apagadas.', 'success')
    return redirect(url_for('mensagens', usuario_id=usuario.id))


