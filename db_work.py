from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    admin = db.Column(db.Integer, unique=False, nullable=True)
    sex = db.Column(db.String(1), unique=False, nullable=False)
    timer = db.Column(db.Integer, primary_key=True)
    delegated_tasks = db.Column(db.String(60), unique=True, nullable=False)

    def __repr__(self):
        return '<User {} {} {}>'.format(
            self.user_id, self.name, self.admin)


class Task(db.Model):
    task_id = db.Column(db.Integer, unique=True, nullable=False)
    maker_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=False, nullable=False)
    description = db.Column(db.String(400), unique=False, nullable=False)
    responsible = db.Column(db.String(400), unique=False, nullable=False)
    priority = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.Integer, unique=False, nullable=True)
    limit = db.Column(db.String(100), unique=False, nullable=False)

    def __repr__(self):
        return '<Task {} {} {} {} {}>'.format(
            self.task_id, self.maker_id, self.name, self.status, self.limit)


def user_exist(name):
    user = User.query.filter_by(name=name).first()
    return user


def insert_user(name, password, sex):
    new_user = User(name=name,
                    password=password,
                    admin=0,
                    sex=sex,
                    timer=0)
    db.session.add(new_user)
    db.session.commit()
    return


def get_all_users():
    return User.query.all()


def get_user_with_id(user_id):
    return User.query.filter_by(user_id=user_id).first()


def add_task(maker_id, name, description, responsible, priority, limit):
    new_task = Task(maker_id=maker_id,
                    name=name,
                    description=description,
                    responsible=responsible,
                    priority=priority,
                    limit=limit)
    db.session.add(new_task)
    db.session.commit()


def get_delegated_tasks(user):
    tasks = []
    tasks_ids = user.delegated_tasks.split('|')
    for i in tasks_ids:
        tasks.append(Task.query.filter_by(task_id=i).first())
    return tasks