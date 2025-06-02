from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional

import os
from flask import current_app
from werkzeug.utils import secure_filename

from app import db, bcrypt, app
from app.models import User

class UserForm(FlaskForm):
    imagem = FileField('Foto de Perfil', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens são permitidas')])
    nome = StringField('Nome', validators=[DataRequired()])
    sobreNome = StringField('Sobrenome', validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired()])
    cpf_cnpj = StringField('CPF/CNPJ', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirme_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])
    btnSubmit = SubmitField('Cadastrar')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Usuário já cadastrado com esse e-mail!')

    def save(self):
        senha_hash = bcrypt.generate_password_hash(self.senha.data).decode('utf-8')
        user = User(
            nome=self.nome.data,
            sobreNome=self.sobreNome.data,
            status=self.status.data,  # Adicionado
            cpf_cnpj=self.cpf_cnpj.data,  # Adicionado
            email=self.email.data,
            senha=senha_hash
        )
        db.session.add(user)
        db.session.commit()
        return user

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Entrar')

    def login(self):
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            raise ValidationError("Usuário não encontrado.")
        if not bcrypt.check_password_hash(user.senha, self.senha.data.encode('utf-8')):
            raise ValidationError("Senha incorreta.")
        return user


class ConfiguracoesForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobreNome = StringField('Sobrenome', validators=[DataRequired()])
    status = StringField('Status')
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    imagem = FileField('Foto de Perfil', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    cor_fundo = StringField('Cor de Fundo (hex)', validators=[Optional()])
    submit = SubmitField('Salvar Alterações')

    def validate_email(self, email):
        from flask_login import current_user
        if email.data != current_user.email:
            usuario = User.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('E-mail já está em uso.')

    def salvar_imagem(foto, nome_arquivo_antigo=None):
        if foto and foto.filename != '':
            nome_arquivo = secure_filename(foto.filename)
            caminho_novo = os.path.join(current_app.root_path, 'static/imagens', nome_arquivo)

            # Remove antiga
            if nome_arquivo_antigo:
                caminho_antigo = os.path.join(current_app.root_path, 'static/imagens', nome_arquivo_antigo)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)

            # Salva nova
            foto.save(caminho_novo)
            return nome_arquivo
        return nome_arquivo_antigo

    