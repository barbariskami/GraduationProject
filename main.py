import requests
import sqlite3  # import всего нужного
from flask import Flask, render_template, redirect, session, request, jsonify, make_response, send_from_directory
from wtforms import PasswordField, BooleanField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_restful import reqparse, abort, Api, Resource
import traceback
import datetime
import random


app = Flask(__name__)  # создание приложения
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Задаём конфиги
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)
parser2 = reqparse.RequestParser()
parser2.add_argument('user_name', required=True)
parser2.add_argument('password_hash', required=True)

db = SQLAlchemy(app)  # Создание sqlalchemy

monthes = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]


class User(db.Model):  # Класс юзеров
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


class Task(db.Model):  # Класс задач
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


class Code(db.Model):
    primary_key = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, unique=False, nullable=True)
    user_id = db.Column(db.Integer, unique=False, nullable=True)



def user_exist(name):  # Проверка существования
    user = User.query.filter_by(name=name).first()
    return user


def insert_user(name, password, sex):  # Вставка юзера
    new_user = User(name=name,
                    password=password,
                    admin=0,
                    sex=sex,
                    timer=0,
                    delegated_tasks='')
    db.session.add(new_user)
    db.session.commit()
    return


def get_all_users():  # Получение всех юзеров
    return User.query.all()


def get_user_with_id(user_id):
    return User.query.filter_by(user_id=user_id).first()


def get_users_made_tasks(user_id):
    return Task.query.filter_by(maker_id=user_id).all()


def edit_task(task_id, maker_id, name, description, responsible, priority, status, limit, tags, category):
    # Редактировка задачи
    task = Task.query.filter_by(task_id=task_id).first()
    db.session.delete(task)
    add_task(maker_id, name, description, responsible, priority, status, limit, tags, category)


def get_expired():  # Просрочки
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


def edit_status(task_id, status):  # Изменение статуса
    task = Task.query.filter_by(task_id=task_id).first()
    db.session.delete(task)
    add_task(task.maker_id, task.name, task.description, task.responsible, task.priority, status, task.limit, task.tags,
             task.category)


def add_task(maker_id, name, description, responsible, priority, status, limit, tags, category):  # добавление таска
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


def get_categories():  # все категоии
    return Categories.query.all()


def delete_task(task_id):  # удаление таска
    task = Task.query.filter_by(task_id=task_id).first()
    edit_task(task_id, task.maker_id, task.name, task.description, task.responsible, task.priority, -1, task.limit,
              task.tags, task.category)


def get_delegated_tasks(user_id):  # всё шо надо сделать
    try:
        user = User.query.filter_by(user_id=user_id).first()
        tasks = Task.query.all()
        tasks2 = []
        for t in tasks:
            if t.status == 0:
                resp = t.responsible.split('|')
                if str(user_id) in resp:
                    tasks2.append(t)
        return tasks2
    except:
        traceback.print_exc()


class TelegramId(db.Model):  # забаненный в РФ контент
    primary_key = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, unique=True, nullable=False)
    telegram_id = db.Column(db.Integer, unique=True, nullable=False)


class Categories(db.Model):  # категории
    primary_key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=False, nullable=False)


def bySlovo(slovo):  # сортировка уровней
    return slovo[1]


class AddNewsForm(FlaskForm):  # form добавления новости
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):  # form входа
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegForm(FlaskForm):  # form регистрации
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегестрироваться')


@app.errorhandler(404)  # страница ошибки 404
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])  # основная страница
def index():
    return render_template('index.html')


@app.route('/registr/<int:news_id>', methods=['GET', 'POST'])  # страница регистрации
def reg(news_id):
    errorchik = news_id
    if request.method == 'POST':
        user_name = request.form['email']
        password = request.form['pass']
        password2 = request.form['pass2']
        if password != password2:
            return redirect('/registr/3')
        sex = request.form['sex']
        double_exist = user_exist(user_name)
        if double_exist:
            return redirect('/registr/2')
        insert_user(user_name, password, sex)
        exists = user_exist(user_name)
        print(exists)
        if exists:
            session['username'] = user_name
            session['user_id'] = exists.user_id
        return redirect("/lucky_man")
    if errorchik == 1:
        return render_template('registr.html', place='Неправильный логин или пароль')
    elif errorchik == 2:
        return render_template('registr.html', place='Пользователь уже есть')
    elif errorchik == 3:
        return render_template('registr.html', place='Пароли не совпадают')
    else:
        return render_template('registr.html', place='Введите логин')


@app.route('/logout')  # страница выхода
def logout():
    session.pop('username',0)
    session.pop('user_id',0)
    return redirect('/index')


@app.route('/lucky_man', methods=['GET', 'POST'])  # страница входа
def lucky_man():
    if request.method == 'POST':
        return redirect('/login')
    return render_template('lucky_man.html')


@app.route('/login', methods=['GET', 'POST'])  # страница входа
def login():
    if request.method == 'POST':
        user_name = request.form['email']
        password = request.form['pass']
        exists = user_exist(user_name)
        if exists:
            if exists.password == password:
                session['username'] = user_name
                session['user_id'] = exists.user_id
                return redirect("/2code")
            else:
                return render_template('login.html', place='Неправильный пароль')
        else:
            return render_template('login.html', place='Данного пользователя не существует')
    return render_template('login.html', place='Введите логин')


@app.route('/add-task/<int:id>', methods=['GET', 'POST'])  # страница добавления таска
def add_tas(id):
    idd = id
    if request.method == 'POST':
        if idd == 0:
            name = request.form['map']
            descr = request.form['about']
            prior = request.form['class']
            prior = int(prior[-2])
            users = get_all_users()
            for_rows = {}
            cheliks = []
            for i in users:
                for_rows[i.name] = i.user_id
            key = for_rows.keys()
            for i in key:
                try:
                    per = request.form[i]
                except Exception:
                    per = 'off'
                if per == 'on':
                    cheliks.append(str(for_rows[i]))
            if cheliks != []:
                cheliks = '|'.join(cheliks)
            date = request.form['date']
            tags = request.form['mapppp']
            tags = tags.split(',')
            cat = request.form['cat']
            add_task(session['user_id'], name, descr, cheliks, prior, 0, date, tags, cat)
            return redirect('/index')
        else:
            name = request.form['map']
            descr = request.form['about']
            prior = request.form['class']
            prior = int(prior[-2])
            users = get_all_users()
            for_rows = {}
            cheliks = []
            for i in users:
                for_rows[i.name] = i.user_id
            key = for_rows.keys()
            for i in key:
                try:
                    per = request.form[i]
                except Exception:
                    per = 'off'
                if per == 'on':
                    cheliks.append(str(for_rows[i]))
            if cheliks != []:
                cheliks = '|'.join(cheliks)
            date = request.form['date']
            tags = request.form['mapppp']
            tags = tags.split(',')
            cat = request.form['cat']
            edit_task(id, session['user_id'], name, descr, cheliks, prior, 0, date, tags, cat)
            return redirect('/index')
    users = get_all_users()
    for_rows = []
    ccc = get_categories()
    cccc = []
    for i in ccc:
        cccc.append(i.name)
    for i in users:
        for_rows.append(i.name)
    return render_template('add_post.html', news=for_rows, cats=cccc)


@app.route('/delegs/<int:id>', methods=['GET', 'POST'])  # страница делегирования
def delegs(id):
    idd = id
    tasks = get_delegated_tasks(session['user_id'])
    news = []
    print(tasks)
    if tasks:
        for i in tasks:
            if i.status == 0:
                news.append([i.task_id, i.name, i.description])
    return render_template('levels.html', news=news)


@app.route('/tasks/<int:id>')  # помечает сделанным таск
def task_done(id):
    edit_status(id, 1)
    return redirect('/index')


@app.route('/mytasks/<int:id>')  # мои таски
def mytasks(id):
    idd = id
    news = get_users_made_tasks(session['user_id'])
    new = []
    if news:
        for i in news:
            if i.status == 0:
                new.append([i.task_id, i.name, i.description])
    return render_template('my_tasks.html', news=new)


@app.route('/task/<int:id>')  # удаляет таск
def task_delete(id):
    edit_status(id, -1)
    return redirect('/index')


@app.route('/youllgonnadie')  # просроченные
def prospano():
    news = get_expired()
    new = []
    if news:
        for i in news:
            if i.status == 0:
                new.append([i.task_id, i.name, i.description])
    return render_template('prospano.html', news=new)


@app.route('/all-tasks')  # все таски
def all():
    tasks = Task.query.all()
    norm = []
    zdano = []
    prosr = []
    for i in tasks:
        if i.status == 0:
            norm.append([i.task_id, i.name, i.description])
        elif i.status == 1:
            zdano.append([i.task_id, i.name, i.description])
        elif i.status == -1:
            prosr.append([i.task_id, i.name, i.description])
    return render_template('all.html', news=prosr, news2=zdano, news3=norm)


@app.route('/2code')  # двухфакторка
def code2():
    global codik, arffff
    if request.method == 'POST':
        password = request.form['pass']
        if password == codik:
            session['username'] = arffff[0]
            session['user_id'] = arffff[1]
            return redirect('/index')
        else:
            return redirect('/2code')

    fir = session['username']
    sec = session['user_id']
    arffff = [fir, sec]
    telegram_id = TelegramId.query.filter_by(system_id=sec)
    session.pop('username', 0)
    session.pop('user_id', 0)
    code = random.randrange(100000, 900000)
    codik = code
    new_el = Code(code=code, user_id=telegram_id)
    db.session.add(new_el)
    db.session.commit()


if __name__ == '__main__':
    codik = 0
    arffff = []
    app.run(port=8800, host='127.0.0.1')

