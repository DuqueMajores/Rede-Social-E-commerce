from app import db
from datetime import datetime, timedelta
from flask_login import UserMixin

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    sobreNome = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(150), nullable=True)
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    imagem = db.Column(db.String(150), default='default.png')
    cor_fundo = db.Column(db.String(255), default='background-image: linear-gradient(to right, #fff, #a6e3ed);')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    notificacoes = db.relationship(
        'Notificacao',
        backref='destinatario',
        lazy='dynamic',
        foreign_keys='Notificacao.destinatario_id'
    )

    notificacoes_enviadas = db.relationship(
        'Notificacao',
        backref='remetente',
        lazy='dynamic',
        foreign_keys='Notificacao.remetente_id'
    )

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def total_seguidores(self):
        return self.followers.count()

    def total_seguindo(self):
        return self.followed.count()

    def is_online(self):
        if self.last_seen:
            return datetime.utcnow() - self.last_seen < timedelta(minutes=0.10)
        return False

class Notificacao(db.Model):
    __tablename__ = 'notificacao'

    id = db.Column(db.Integer, primary_key=True)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    remetente_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mensagem = db.Column(db.String(255))
    lida = db.Column(db.Boolean, default=False)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(50))

    

class Mensagem(db.Model):
    __tablename__ = 'mensagem'

    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    corpo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    editada = db.Column(db.Boolean, default=False)
    lida = db.Column(db.Boolean, default=False)

    remetente = db.relationship('User', foreign_keys=[remetente_id], backref='mensagens_enviadas')
    destinatario = db.relationship('User', foreign_keys=[destinatario_id], backref='mensagens_recebidas')

