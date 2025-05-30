from app import db
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
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(150))
    imagem = db.Column(db.String(150), default='default.png')

    # Usuários que este usuário segue
    seguindo = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('seguidores', lazy='dynamic'),
        lazy='dynamic'
    )

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
