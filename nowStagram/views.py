# -*- encoding = UTF-8 -*-


from nowStagram import app, db
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
from .models import Image, User, Comment, Like
import random
import hashlib
import json
from flask_login import login_user, logout_user, current_user, login_required
import uuid
import os


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
        comments = []
        for i in range(0, min(2, len(image.comments))):
            comment = image.comments[i]
            comments.append({'username': comment.user.username, 'user_id': comment.user_id,
                             'content': comment.content})
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments),
                 'user_id': image.user_id, 'head_url': image.user.head_url,
                 'created_date': str(image.created_date), 'comments': comments}
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
    paginate = Image.query.filter_by(user_id=user_id).order_by('id desc').paginate(page=1, per_page=3, error_out=False)
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
        print(user.salt)
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


def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name


@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


@app.route('/update/', methods={"post"})
def update():
    file = request.files['file']
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        filename = str(uuid.uuid1()).replace('-', '')+'.'+file_ext
        url = save_to_local(file, filename)
        if url != None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()
    return redirect('/profile/%d' % current_user.id)


@app.route('/addcomment/', methods={'post'})
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content'].strip()
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({'code': 0, 'id': comment.id, 'content': content,
                       'username': comment.user.username,
                       'user_id': comment.user.id})


# 新增加的功能
@app.route('/thumbs_up/', methods={'post'})  # 点赞
@login_required
def thumbs_up():
    image_id = int(request.values['image_id'])
    like = Like(current_user.id, image_id)
    db.session.add(like)
    db.session.commit()
    return json.dumps({'code': 0, 'username': current_user.username,
                       'image_id': like.image_id})


@app.route('/set_admin/')
@login_required
def set_admin():
    if current_user.power == 'admin':
        user_id = request.values['user_id']
        user = User.query.get(user_id)
        user.power = 'admin'
        db.session.commit()
        return json.dumps({'code': 0, 'admin': current_user.id, 'new_admin': user.id})
    return json.dumps({'code': 1})


@app.route('/admin_image_delete/', methods={'post'})
@login_required
def admin_image_delete():
    image_id = request.values['image_id']
    if current_user.power == 'admin':
        image = Image.query.filter_by(id=image_id).first()
        db.session.delete(image)
        db.session.commit()
        return json.dumps({'code': 0, 'admin': current_user.id})
    return json.dumps({'code': 1})


