from app import db
from datetime import datetime, timedelta
from flask_login import UserMixin

# Tabela de associação (auto-relacionamento N:N)
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150))
    sobreNome = db.Column(db.String(150))
    status = db.Column(db.String(150))
    cpf_cnpj = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(150))
    imagem = db.Column(db.String(150), default='default.png')
    cor_fundo = db.Column(db.String(255), default='background-image: linear-gradient(to right, #fff, #a6e3ed);')
    notificacoes = db.relationship('Notificacao', backref='usuario', lazy='dynamic')

    # Usuários que este usuário segue
    seguindo = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('seguidores', lazy='dynamic'),
        lazy='dynamic'
    )

    # Relacionamento com notificações
    notificacoes = db.relationship('Notificacao', backref='dono', lazy='dynamic')

    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def seguir(self, usuario):
        if not self.esta_seguindo(usuario):
            self.seguindo.append(usuario)

    def deixar_de_seguir(self, usuario):
        if self.esta_seguindo(usuario):
            self.seguindo.remove(usuario)

    def esta_seguindo(self, usuario):
        return self.seguindo.filter(followers.c.followed_id == usuario.id).count() > 0

    def total_seguidores(self):
        return self.seguidores.count()

    def total_seguindo(self):
        return self.seguindo.count()
    
    def is_following(self, usuario):
        return self.esta_seguindo(usuario)

    def follow(self, usuario):
        self.seguir(usuario)

    def unfollow(self, usuario):
        self.deixar_de_seguir(usuario)

    def is_online(self):
        if self.last_seen is None:
            return False
        return datetime.utcnow() - self.last_seen < timedelta(minutes=0.10)


class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)



