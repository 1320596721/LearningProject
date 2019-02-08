# -*- encoding=UTF-8 -*-


from nowStagram import db, login_manager
import random
from datetime import datetime
import hashlib


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=0)  # 0 正常 1 被删除
    user = db.relationship('User')

    def __init__(self, content, image_id, user_id):
        self.content = content
        self.image_id = image_id
        self.user_id = user_id

    def __repr__(self):
        return '<Comment %d %s>' % (self.id, self.content)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    url = db.Column(db.String(512))
    created_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')
    who_thumbs_up = db.relationship('Like')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.created_date = datetime.now()

    def __repr__(self):
        return '<Image %d %s>' % (self.id, self.url)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))

    def __init__(self, user_id, image_id):
        self.user_id = user_id
        self.image_id = image_id

    def __repr__(self):
        return '<Like %d %d>' % (self.user_id, self.image_id)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    power = db.Column(db.String(10), default='normal')
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(32))
    salt = db.Column(db.String(32))
    head_url = db.Column(db.String(256))
    images = db.relationship('Image', backref='user', lazy='dynamic')

    def __init__(self, username, password, power='normal', salt=''):
        self.username = username
        self.salt = salt
        m = hashlib.md5()
        m.update((password + self.salt).encode('utf8'))
        self.password = m.hexdigest()
        self.power = power
        self.head_url = 'https://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'

    def __repr__(self):
        return '<User %d %s>' % (self.id, self.username)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
