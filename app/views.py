from app import app, db
from flask import render_template, url_for, request, redirect, flash
from flask_login import login_required
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import UserForm, LoginForm
from app.models import User
from werkzeug.security import check_password_hash, generate_password_hash

### INDEX
@app.route("/")
def index():
    """
    APAGA O BANCO DE DADOS
    usuario = User.query.get(1)  # Substitua 1 pelo ID desejado

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
    return render_template('home.html', obj=obj)

### CADASTRO
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = UserForm()

    if form.validate_on_submit():
        nome = form.nome.data
        sobreNome = form.sobreNome.data
        email = form.email.data
        senha = generate_password_hash(form.senha.data)  # <-- Aqui você faz o hash
        novo_usuario = User(nome=nome, sobreNome=sobreNome, email=email, senha=senha)

        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html', form=form)

### LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)  # Requer Flask-Login
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
