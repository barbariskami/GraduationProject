import db_work
import traceback
import datetime
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler


def main():
    # Основная функция бота
    try:
        token = '683346269:AAE66lBZvg--IDGUbUh-mPK2SWRrAv_Tvhw'
        updater = Updater(token)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler('auth', auth, pass_user_data=True, pass_args=True))
        dp.add_handler(CommandHandler('start', start, pass_user_data=True, pass_job_queue=True, pass_chat_data=True))
        dp.add_handler(CommandHandler('task', task, pass_user_data=True))
        dp.add_handler(CommandHandler('expired_task', expired_task, pass_user_data=True))
        dp.add_handler(CommandHandler('delegate_task', delegate_task, pass_args=True))
        dp.add_handler(CommandHandler("set_timer", set_timer,
                                      pass_job_queue=True, pass_chat_data=True))
        add_module_handler = ConversationHandler(
            entry_points=[CommandHandler('add_task', add_task)],

            states={
                'name': [MessageHandler(Filters.text, description_response, pass_user_data=True)],
                'description': [MessageHandler(Filters.text, category_response, pass_user_data=True)],
                'category': [MessageHandler(Filters.text, limit_response, pass_user_data=True)],
                'limit': [MessageHandler(Filters.text, save_task, pass_user_data=True)],
            },

            fallbacks=[CommandHandler('stop', stop_adding)]
        )
        dp.add_handler(add_module_handler)

        updater.start_polling()

        updater.idle()
    except:
        traceback.print_exc()


def start(bot, update, user_data, job_queue, chat_data):
    try:
        user_id = update.effective_user.id
        if db_work.TelegramId.query.filter_by(telegram_id=user_id).first():
            system_id = db_work.TelegramId.query.filter_by(telegram_id=user_id).first().system_id
            user_data['user'] = db_work.User.query.filter_by(user_id=system_id).first()
            update.message.reply_text('Здравствуйте. Вы уже авторизованы')
        else:
            update.message.reply_text('Здравствуйте. Авторизуйтесь с помощью команды /auth')
            user_data['user'] = None
        set_timer(bot, update, job_queue, chat_data)
    except:
        traceback.print_exc()


def auth(bot, update, user_data, args):
    # Войти в аккаунт
    try:
        if len(args) != 2:
            update.message.reply_text('Вы ввели не то количество аргументов')
            return
        name = args[0]
        password = args[1]
        user = db_work.user_exist(name)
        print(user)
        if user_data['user']:
            update.message.reply_text('Вы уже авторизованы')
            return
        if user:
            if user.password == password:
                user_data['user'] = user
                db_work.connect_system_telegram(user.user_id, update.effective_user.id)
                update.message.reply_text('Вы успешно вошли в аккаунт')
            else:
                update.message.reply_text('Неверный пароль')
        else:
            update.message.reply_text('Пользователя с таким логином не существует')
            return
    except:
        traceback.print_exc()


monthes = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]  # Для удобной проверки просроченности
month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # для валидации ввода даты


def task(bot, update, user_data):
    # Список задач
    try:
        tasks = db_work.get_delegated_tasks(user_data['user'])
        text = []
        for t in tasks:
            if not t.status:
                string = '{}  {}  {}'.format(str(t.task_id), t.name, t.limit)
                deadline = t.limit.split('-')
                deadline = (int(deadline[0]) - 2017) * 365 + monthes[int(deadline[1]) - 1] * 30 + int(deadline[2])
                today = str(datetime.datetime.now().date()).split('-')
                today = (int(today[0]) - 2017) * 365 + monthes[int(today[1]) - 1] * 30 + int(today[2])
                print(today, deadline)
                if today > deadline:
                    string = '❗️' + string  # Воскл знак, если просроченная
                text.append(string)
        if text:
            update.message.reply_text('\n'.join(text))
        else:
            update.message.reply_text('У вас нет ни одной задачи. Можете отдыхать!')
    except:
        traceback.print_exc()


def expired_task(bot, update, user_data):
    # Только просроченные задачи
    try:
        tasks = db_work.get_delegated_tasks(user_data['user'])
        text = []
        for t in tasks:
            if not t.status:
                string = '{}  {}  {}'.format(str(t.task_id), t.name, t.limit)
                deadline = t.limit.split('-')
                deadline = (int(deadline[0]) - 2017) * 365 + monthes[int(deadline[1]) - 1] * 30 + int(deadline[2])
                today = str(datetime.datetime.now().date()).split('-')
                today = (int(today[0]) - 2017) * 365 + monthes[int(today[1]) - 1] * 30 + int(today[2])
                print(today, deadline)
                if today > deadline:
                    string = '❗️' + string
                    text.append(string)
        if text:
            update.message.reply_text('\n'.join(text))
        else:
            update.message.reply_text('У вас нет ни одной просроченной задачи. Но не расслабляйтесь!!')
    except:
        traceback.print_exc()


def add_task(bot, update):
    # Начало диалога
    try:
        update.message.reply_text('Введите название будущей задачи')
        return 'name'
    except:
        traceback.print_exc()


def description_response(bot, update, user_data):
    user_data['name'] = update.message.text
    update.message.reply_text('Теперь введите описание задачи')
    return 'description'


def category_response(bot, update, user_data):
    user_data['description'] = update.message.text
    update.message.reply_text('Теперь введите категорию задачи')
    return 'category'


def limit_response(bot, update, user_data):
    user_data['category'] = update.message.text
    categories = [i.name for i in db_work.get_categories()]
    if user_data['category'] in categories:
        update.message.reply_text('Теперь введите дату сдачи задачи (в формате гггг-мм-дд)')
        return 'limit'
    else:
        update.message.reply_text('Такой категории не существует. Попробуйте снова')
        return 'category'


def save_task(bot, update, user_data):
    try:
        user_data['limit'] = update.message.text
        if len(user_data['limit'].split('-')) == 3 and len(user_data['limit'].split('-')[0]) == 4 and len(
                user_data['limit'].split('-')[1]) == len(user_data['limit'].split('-')[2]) == 2 and 1 <= int(
            user_data['limit'].split('-')[1]) <= 12 and 1 <= int(user_data['limit'].split('-')[2]) <= month[
            user_data['limit'].split('-')[2] - 1]:  # Проверка правильности ввода даты
            db_work.add_task(user_data['user'].user_id,
                             user_data['name'], user_data['description'],
                             '', 0, user_data['limit'], 0, '',
                             user_data['category'])
            update.message.reply_text('Задача сохранена')
            return ConversationHandler.END
        else:
            update.message.reply_text('Дата сдачи не соответствует формату. '
                                      'Попробуйте еще раз (в формате гггг-мм-дд)')
            return 'limit'
    except:
        traceback.print_exc()


def stop_adding(bot, update):
    # Экстренное завершение режима добавления
    update.message.reply_text('Вы завершили режим добавления без сохранения')
    return ConversationHandler.END


def delegate_task(bot, update, args):
    if len(args) != 2:
        update.message.reply_text('Вы ввели неверное число аргументов')
        return
    task_id = int(args[0])
    user_id = int(args[1])
    user = db_work.User.query.filter_by(user_id=user_id).first()
    task = db_work.Task.query.filter_by(task_id=task_id).first()
    if user and task:
        # Изменение Ответственного у задачи
        db_work.edit_task(task_id, task.maker_id, task.name, task.description, user_id, task.priority,
                          task.status, task.limit, task.tags, task.category)
        update.message.reply_text('Задача успешно делегирована')
    elif not (user):
        update.message.reply_text('Такого пользователя нет. попробуйте снова')
    elif not (task):
        update.message.reply_text('Такой задачи нет. попробуйте снова')


def set_timer(bot, update, job_queue, chat_data):  # Установка таймера для проверки необходимости отправки кода
    delay = 10
    job = job_queue.run_once(_task, delay, context=[update.message.chat_id, update, job_queue, chat_data])

    chat_data['job'] = job


def _task(bot, job):  # Задача для таймера
    code = db_work.Code.query.filter_by(primary_key=1).first()
    if code and code.code:
        bot.send_message(job.context[0], text=code.code)
    code.code = 0
    db_work.db.session.commit()
    set_timer(bot, job.context[1], job.context[2], job.context[3])


if __name__ == '__main__':
    main()
