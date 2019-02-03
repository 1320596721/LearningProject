# -*- encoding = UTF-8 -*-


from nowStagram import app, db
from flask import render_template, redirect, request, flash, get_flashed_messages
from .models import Image, User
import random
import hashlib
import json
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
def index():
    images = Image.query.order_by('id desc').paginate(page=1, per_page=5, error_out=False)
    return render_template('index.html', images=images.items, has_next=images.has_next)


@app.route('/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    paginate = Image.query.order_by('id desc').paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.user_id, 'url': image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


@app.route('/image/<int:image_id>/')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/')
    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3, error_out=False)
    return render_template('profile.html', user=user, images=paginate.items, has_next=paginate.has_next)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


@app.route('/reglogin/')
def reglogin():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['reglogin']):
        msg = msg + m
    return render_template('login.html', msg=msg, next=request.values.get('next'))


@app.route('/register/', methods={'post', 'get'})
def register():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    if username == '' or password == '':
        return redirect_with_msg('/reglogin/', u'用户名或密码不能为空', 'reglogin')
    user = User.query.filter_by(username=username).first()
    if user != None:
        return redirect_with_msg('/reglogin/', u'用户名已存在', 'reglogin')
    salt = '.'.join(random.sample('0123456789afcdgxvzAWFCHXZNKIL', 10))
    m = hashlib.md5()
    m.update((password + salt).encode('utf8'))
    password = m.hexdigest()
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')


@app.route('/login/', methods={'post', 'get'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    if username == '' or password == '':
        return redirect_with_msg('/reglogin/', u'用户名或密码不能为空', 'reglogin')
    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect_with_msg('/reglogin/', u'用户名不存在', 'reglogin')
    m = hashlib.md5()
    m.update((password + user.salt).encode('utf8'))
    if m.hexdigest() != user.password:
        return redirect_with_msg('/reglogin/', u'密码错误', 'reglogin')

    login_user(user)

    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')


def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg, category=category)
        return redirect(target)

