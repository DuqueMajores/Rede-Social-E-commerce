from app import app, db
from datetime import datetime
from flask import render_template, url_for, request, redirect, flash, jsonify, copy_current_request_context
from flask_login import login_required, login_user, logout_user, current_user
from app.forms import UserForm, LoginForm, ConfiguracoesForm
from app.models import User, Notificacao
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
import threading
import time
from sqlalchemy import or_

### INDEX
@app.route("/")
def index():

    """db.session.query(Notificacao).delete()
    db.session.commit()"""

    """# Busca o usuário pelo e-mail
    user = User.query.filter_by(email="duque.majores@gmail.com").first()

    if user:
        user.status = "CEO & CTO da Social E-Commerce"
        user.cpf_cnpj = "17324412785"
        db.session.commit()
        print("Usuário atualizado com sucesso.")
        db.session.add(user)
        db.session.commit()
    else:
        print("Usuário não encontrado.")"""

    obj = {
        'cor_fundo': "linear-gradient(to right, #fff, #a6e3ed)"  # Cor original
    }

    return render_template('index.html', obj=obj)

### HOME
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
        ).order_by(User.nome)
    else:
        dados = User.query.order_by(User.nome)

    pessoas = User.query.all()
    quantidade = len(pessoas)

    context = {
        'busca': bool(pesquisa),
        'dados': dados.all()
    }

    notificacoes = Notificacao.query.filter_by(user_id=obj.id, lida=False).all()
    tem_notificacao = bool(notificacoes)

    return render_template(
        'home.html',
        obj=obj,
        context=context,
        pessoas=pessoas,
        quantidade=quantidade,
        user_id=id,
        notificacoes=notificacoes,
        tem_notificacao=tem_notificacao
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
        cfp_cnpj = form.cpf_cnpj.data

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
            cfp_cnpj = cfp_cnpj
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

    if not current_user.esta_seguindo(user):
        current_user.seguir(user)

        mensagem = f"{current_user.nome} {current_user.sobreNome} começou a te seguir."

        nova_notificacao = Notificacao(
            mensagem=mensagem,
            user_id=user.id  # corrigido para o nome correto do atributo da FK
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
    user = User.query.get_or_404(user_id)
    current_user.unfollow(user)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})  # resposta para AJAX
    else:
        return redirect(request.referrer or url_for('seguindo', id=current_user.id))


### SEGUIDORES
@app.route('/seguidores/<int:user_id>/', endpoint='seguidores')
@login_required
def seguidores(user_id):
    usuario = User.query.get_or_404(user_id)
    seguidores = usuario.seguidores  # lista de objetos de usuários
    ids_que_eu_sigo = [u.id for u in current_user.seguindo]  # lista de IDs

    obj = {
        'cor_fundo': None
    }

    return render_template('seguidores.html', usuario=usuario,seguidores=seguidores, ids_que_eu_sigo=ids_que_eu_sigo, obj=obj)


### USUÁRIOS QUE ESTOU SEGUINDO
@app.route('/seguindo/<int:id>/', endpoint='seguindo')
@login_required
def seguindo(id):
    obj = User.query.get_or_404(id)

    pesquisa = request.args.get('pesquisa', '').strip()

    seguindo_query = obj.seguindo

    if pesquisa:
        seguindo_filtrado = [user for user in seguindo_query if pesquisa.lower() in user.nome.lower()]
    else:
        seguindo_filtrado = seguindo_query

    context = {
        'dados': seguindo_filtrado,
        'usuario_atual_seguindo_ids': {u.id for u in current_user.seguindo}
    }

    return render_template('seguindo.html', obj=obj, context=context)


### SEGUIR E DEIXAR DE SEGUIR (via AJAX)
@app.route('/seguir/<int:id>', methods=['POST'])
@login_required
def seguir_usuario(id):
    usuario = User.query.get_or_404(id)
    if usuario not in current_user.seguindo:
        current_user.seguindo.append(usuario)
        db.session.commit()
    return jsonify({'status': 'seguido'})


@app.route('/deixar_de_seguir/<int:id>', methods=['POST'])
@login_required
def deixar_de_seguir_usuario(id):
    usuario = User.query.get_or_404(id)
    if usuario in current_user.seguindo:
        current_user.seguindo.remove(usuario)
        db.session.commit()
    return jsonify({'status': 'removido'})


@app.route('/seguidores/<int:id_usuario>')
@login_required
def listar_seguidores(id_usuario):
    usuario = User.query.get_or_404(id_usuario)
    seguidores = usuario.seguidores

    ids_que_eu_sigo = [u.id for u in current_user.seguindo]

    return render_template('seguidores.html', usuario=usuario, seguidores=seguidores, ids_que_eu_sigo=ids_que_eu_sigo)


### ATUALIZACAO DO STATUS DE NOTIFICACAO
@app.route('/notificacoes_lidas', methods=['POST'])
@login_required
def notificacoes_lidas():
    notificacoes = Notificacao.query.filter_by(user_id=current_user.id, lida=False).all()
    for n in notificacoes:
        n.lida = True
    db.session.commit()
    return '', 204


@app.route('/verificar_novas_notificacoes')
@login_required
def verificar_novas_notificacoes():
    count = Notificacao.query.filter_by(user_id=current_user.id, lida=False).count()
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

    if notificacao.user_id != current_user.id:
        return jsonify({'erro': 'Acesso negado'}), 403

    notificacao.lida = True
    db.session.commit()

    # Simula o delay antes de excluir
    time.sleep(0.1)

    db.session.delete(notificacao)
    db.session.commit()

    return jsonify({'status': 'Notificação marcada como lida e excluída com sucesso.'})

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
