from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask import current_app as app

from app.extensions import db, bcrypt
from app.models import User

class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobreNome = StringField('Sobrenome', validators=[DataRequired()])
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
            email=self.email.data,
            senha=senha_hash
        )
        db.session.add(user)
        db.session.commit()
        return user
