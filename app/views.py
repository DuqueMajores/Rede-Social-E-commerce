from flask import render_template, url_for, request, redirect
from flask_login import login_user, logout_user, login_required, current_user

from app.forms import UserForm
from app.models import User
from app import db
from app import create_app

app = create_app()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/home")
@login_required
def home():
    return render_template('home.html')

@app.route("/cadastro/", methods=['GET', 'POST'])
def cadastro():
    form = UserForm()
    if form.validate_on_submit():
        user = form.save()
        login_user(user, remember=True)
        return redirect(url_for('home'))
    return render_template('cadastro.html', form=form)
