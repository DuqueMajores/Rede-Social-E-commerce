from app import app, db
from flask import render_template, url_for, request, redirect
from flask_login import login_required
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Contato, Post
from app.forms import ContatoForm, UserForm, LoginForm, PostForm, PostComentarioForm

### Pagina Cadastro
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/cadastro/", methods=['GET', 'POST'])
def cadastro():
    form = UserForm()
    context = {}
    if form.validate_on_submit():
        user = form.save()
        login_user(user, remember=True)
        return redirect(url_for('home'))
    return render_template('cadastro.html',context=context, form=form)
