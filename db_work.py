from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import datetime
import traceback

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    admin = db.Column(db.Integer, unique=False, nullable=True)
    sex = db.Column(db.String(10), unique=False, nullable=False)
    timer = db.Column(db.Integer, unique=False, nullable=True)
    delegated_tasks = db.Column(db.String(60), unique=False, nullable=True)

    def __repr__(self):
        return '<User {} {} {}>'.format(
            self.user_id, self.name, self.admin)


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    maker_id = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String(60), unique=False, nullable=False)
    description = db.Column(db.String(400), unique=False, nullable=False)
    responsible = db.Column(db.String(400), unique=False, nullable=False)
    priority = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.Integer, unique=False, nullable=True)
    limit = db.Column(db.String(100), unique=False, nullable=False)
    tags = db.Column(db.String(100), unique=False, nullable=False)
    category = db.Column(db.String(60), unique=False, nullable=False)

    def __repr__(self):
        return '<Task {} {} {} {} {}>'.format(
            self.task_id, self.maker_id, self.name, self.status, self.limit)


def user_exist(name):
    user = User.query.filter_by(name=name).first()
    return user


monthes = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]


def get_expired():
    tasks = Task.query.all()
    res = []
    for i in tasks:
        if i.status == 0:
            deadline = i.limit.split('-')
            deadline = (int(deadline[0]) - 2017) * 365 + monthes[int(deadline[1]) - 1] * 30 + int(deadline[2])
            today = str(datetime.datetime.now().date()).split('-')
            today = (int(today[0]) - 2017) * 365 + monthes[int(today[1]) - 1] * 30 + int(today[2])
            print(today, deadline)
            if today > deadline:
                res.append(i)
    return res


def insert_user(name, password, sex):
    new_user = User(name=name,
                    password=password,
                    admin=0,
                    sex=sex,
                    timer=0,
                    delegated_tasks='')
    db.session.add(new_user)
    db.session.commit()
    return


def get_all_users():
    return User.query.all()


def get_user_with_id(user_id):
    return User.query.filter_by(user_id=user_id).first()


def get_users_made_tasks(user_id):
    return Task.query.filter_by(maker_id=user_id).all()


def edit_task(task_id, maker_id, name, description, responsible, priority, status, limit, tags, category):
    task = Task.query.filter_by(task_id=task_id).first()
    db.session.delete(task)
    add_task(maker_id, name, description, responsible, priority, status, limit, tags, category)


def edit_status(task_id, status):
    task = Task.query.filter_by(task_id=task_id).first()
    db.session.delete(task)
    add_task(task.maker_id, task.name, task.description, task.responsible, task.priority, status, task.limit, task.tags,
             task.category)


def add_task(maker_id, name, description, responsible, priority, status, limit, tags, category):
    new_task = Task(maker_id=maker_id,
                    name=name,
                    description=description,
                    responsible=responsible,
                    priority=priority,
                    limit=limit,
                    status=status,
                    tags='|'.join(tags),
                    category=category)
    db.session.add(new_task)
    db.session.commit()


def get_categories():
    return Categories.query.all()


def delete_task(task_id):
    task = Task.query.filter_by(task_id=task_id).first()
    edit_task(task_id, task.maker_id, task.name, task.description, task.responsible, task.priority, -1, task.limit,
              task.tags, task.category)


def get_delegated_tasks(user_id):
    try:
        user = User.query.filter_by(user_id=user_id).first()
        tasks = Task.query.all()
        tasks2 = []
        for t in tasks:
            if t.status == 0:
                resp = t.responsible.split('|')
                if str(user.user_id) in resp:
                    tasks2.append(t)
        return tasks2

    except:
        traceback.print_exc()


class TelegramId(db.Model):
    primary_key = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, unique=True, nullable=False)
    telegram_id = db.Column(db.Integer, unique=True, nullable=False)


class Code(db.Model):
    primary_key = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, unique=False, nullable=True)


class Categories(db.Model):
    primary_key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=False, nullable=False)


def connect_system_telegram(system_id, telegram_id):
    same1 = TelegramId.query.filter_by(system_id=system_id).first()
    if same1:
        db.session.delete(same1)
    same2 = TelegramId.query.filter_by(telegram_id=telegram_id).first()
    if same2:
        db.session.delete(same2)
    db.session.commit()
    new = TelegramId(system_id=system_id,
                     telegram_id=telegram_id)
    db.session.add(new)
    db.session.commit()


db.create_all()
