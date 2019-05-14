import requests
import sqlite3  # import всего нужного
from flask import Flask, render_template, redirect, session, request, jsonify, make_response, send_from_directory
from wtforms import PasswordField, BooleanField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_restful import reqparse, abort, Api, Resource
import random

app = Flask(__name__)  # создание приложения
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)
parser2 = reqparse.RequestParser()
parser2.add_argument('user_name', required=True)
parser2.add_argument('password_hash', required=True)


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


if __name__ == '__main__':
    app.run(port=8800, host='127.0.0.1')
