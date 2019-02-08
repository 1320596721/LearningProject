# -*- encoding = UTF-8 -*-


from nowStagram import app, db
from flask_script import Manager
from nowStagram.models import User, Image, Comment, Like
import random
import unittest
from sqlalchemy import or_, and_


manager = Manager(app)


def get_image_url():
    return 'https://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'


@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 20):
        db.session.add(User('User' + str(i+1), 'a'+str(i+1)))
        for j in range(0, 5):
            db.session.add(Image(get_image_url(), i+1))
            for k in range(0, 3):
                db.session.add(Comment('This is a comment ' + str(k), 1+3*i+j, i+1))
            for l in range(0, 3):
                db.session.add((Like(random.randint(1, i+1), Image.query.filter_by(user_id=i+1).first().id)))
    db.session.add(User('lgx', 'lgx', 'admin', ''))
    db.session.commit()


@manager.command
def run_test():
    db.drop_all()
    db.create_all()
    tests = unittest.TestLoader().discover('./')
    unittest.TextTestRunner().run(tests)
    pass


@manager.command
def database_query():
    print(1, User.query.get(3))
    print(2, User.query.filter(User.username.endswith('0')).limit(3).all())
    print(3, User.query.filter_by(id=5).first())
    print(4, User.query.order_by(User.id.desc()).offset(1).limit(2).all())
    print(5, User.query.paginate(page=1, per_page=10).items)

    user = User.query.get(1)
    print(6, user.images)

    image = Image.query.get(1)
    print(7, image.user)


@manager.command
def update():
    for i in range(50, 100, 2):
        user = User.query.get(i)
        user.username = '[New]' + user.username
    User.query.filter_by(id=51).update({'username': '[New2]'})
    db.session.commit()

    for i in range(51, 100, 2):
        comment = Comment.query.get(i+1)
        db.session.delete(comment)


if __name__ == "__main__":
    manager.run()
