import requests
import sqlite3  # import всего нужного
from flask import Flask, render_template, redirect, session, request, jsonify, make_response, send_from_directory
from wtforms import PasswordField, BooleanField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_restful import reqparse, abort, Api, Resource
import random


app = Flask(__name__)  # создание приложения
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)
parser2 = reqparse.RequestParser()
parser2.add_argument('user_name', required=True)
parser2.add_argument('password_hash', required=True)

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
    task_id = db.Column(db.Integer, unique=True, nullable=False)
    maker_id = db.Column(db.Integer, primary_key=True)
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


db.create_all()


def user_exist(name):
    user = User.query.filter_by(name=name).first()
    return user


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
                return redirect("/index")
            else:
                return render_template('login.html', place='Неправильный пароль')
        else:
            return render_template('login.html', place='Данного пользователя не существует')
    return render_template('login.html', place='Введите логин')


if __name__ == '__main__':
    app.run(port=8800, host='127.0.0.1')

