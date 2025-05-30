from app import app, db
from flask import render_template, url_for, request, redirect, flash, jsonify
from flask_login import login_required
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import UserForm, LoginForm
from app.models import User
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

### INDEX
@app.route("/")
def index():

    """usuario = User.query.get(1)  # Substitua 1 pelo ID desejado

    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        print("Usuário excluído com sucesso.")
    else:
        print("Usuário não encontrado.")"""

    return render_template('index.html')

### HOME
@app.route('/home/<int:id>/', endpoint='home')
@login_required
def home(id):
    obj = User.query.get_or_404(id)

    pesquisa = request.args.get('pesquisa', '')

    if pesquisa:
        dados = User.query.filter(User.nome.ilike(f'%{pesquisa}%')).order_by(User.nome)
    else:
        dados = User.query.order_by(User.nome)

    pessoas = User.query.all()
    quantidade = len(pessoas)

    context = {'dados': dados.all()}

    return render_template('home.html', obj=obj, context=context, pessoas=pessoas, quantidade=quantidade, user_id=id)

### CADASTRO
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = UserForm()

    if form.validate_on_submit():
        arquivo_imagem = form.imagem.data
        nome = form.nome.data
        sobreNome = form.sobreNome.data
        email = form.email.data
        senha = generate_password_hash(form.senha.data)

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
            senha=senha
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html', form=form)



### LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home', id=current_user.id))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('home', id=user.id))
        else:
            flash('E-mail ou senha inválidos.', 'danger')

    return render_template('login.html', form=form)

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
    current_user.follow(user)
    db.session.commit()
    flash(f'Você está seguindo {user.nome}.')
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

    return render_template('seguidores.html', 
                           usuario=usuario, 
                           seguidores=seguidores,
                           ids_que_eu_sigo=ids_que_eu_sigo)

### USUÁRIOS QUE ESTOU SEGUINDO
@app.route('/seguindo/<int:id>/', endpoint='seguindo')
@login_required
def seguindo(id):
    obj = User.query.get_or_404(id)

    pesquisa = request.args.get('pesquisa', '')

    # Pegando apenas os usuários que o obj está seguindo
    seguindo_query = obj.seguindo
    dados = [usuario for usuario in obj.seguindo if pesquisa.lower() in usuario.nome.lower()]

    if pesquisa:
        seguindo_filtrado = [user for user in seguindo_query if pesquisa.lower() in user.nome.lower()]
    else:
        seguindo_filtrado = seguindo_query

    context = {
        'dados': dados,
        'usuario_atual_seguindo_ids': {u.id for u in current_user.seguindo}
    }

    return render_template('seguindo.html', obj=obj, context=context)

###SEGUIR E DEIXAR DE SEGUIR
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

    # Coleta os IDs dos usuários que o usuário logado segue
    ids_que_eu_sigo = [u.id for u in current_user.seguindo]

    return render_template('seguidores.html', usuario=usuario, seguidores=seguidores, ids_que_eu_sigo=ids_que_eu_sigo)
