import telebot
from telebot import types
import pandas as pd
import time
import csv
import plotly.express as px
from collections import defaultdict
import logging
import config

logging.basicConfig(filename="info/bot_info.log", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')


# users = pd.read_csv('2021_lake_results_for_bot.csv', delimiter =';', quotechar =',', quoting=csv.QUOTE_MINIMAL)
users = pd.read_csv('2021_lake_results_for_bot.csv')
bot = telebot.TeleBot(config.TOKEN)

# -------------------------------------------------------------------------------------------------------------------- #
# Шаги на которых может находиться пользователь в боте
# START - Запустил бота
# FIND - Добрался до ввода ФИО
# ERROR - В БД нет указанного ФИО
# FINISH - Заканчиваем принимать информацию от пользователя
START, FIND, ERROR, FINISH = range(4)
# Словарь, в котором у каждого нового пользователя базовое значение START
USER_STATE = defaultdict(lambda: START)

# Функция для получения текущего этапа пользователя
def get_state(message):
    return USER_STATE[message.chat.id]
# Функция для обновления этапа пользователя
def update_state(message, state):
    USER_STATE[message.chat.id] = state

# Функция для сбора данных о пользователе в csv
def write_csv(data):
    with open('info/bot_analytics.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow((data['datetime'], data['user_id'], data['first_name'], data['last_name'], data['username'], data['text'], data['event']))


# Функция для сбор данных по пользователю: время, количество участников в группе, график.png
def user_data(target_user, df):
    # Достаем данные по пользователю
    user_time = df[df['name'] == target_user]['time'].values[0]
    user_group_count = len(df[df['time'] == user_time])

    # Добавляем разбивку групп на два типа с target_user и без него
    df['group'] = ''

    def find_user_group(row):
        time = row['time']
        if time == user_time:
            return 'target'
        else:
            return 'other'

    df['group'] = df.apply(find_user_group, axis=1)

    # Рисуем график
    fig = px.scatter(df, x="x", y="y", color="group",
                     template='plotly_white')
    fig.update_xaxes(autorange="reversed",
                     ticks="inside",
                     nticks=len(df['time'].unique()) + 5)
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_layout(title='Средняя скорость на 1000 метров',
                      xaxis_title='Минут', showlegend=False,
                      font=dict(family="Courier New, monospace", size=24))
    fig.write_image('images/' + target_user + '.png', width=1920, height=1080)

    return user_time, user_group_count, target_user


# START -------------------------------------------------------------------------------------------------------------- #
@bot.message_handler(func=lambda message: get_state(message) == START)
def handle_message(message):
    bot.send_message(message.chat.id,
                     text='{0.first_name}, мы начнем с общих вводных.'
                     .format(message.from_user),
                     parse_mode='html')

    time.sleep(1)
    bot.send_message(message.chat.id,
                     text='Сейчас я знаю результаты только по сезону <b>Open Water 2021 (май-сентябрь)</b>.'
                     .format(message.from_user),
                     parse_mode='html')

    time.sleep(1)
    bot.send_message(message.chat.id,
                     text='В мое поле зрения попал <b>21 заплыв без течения</b>, а именно:'
                          '\n-<b>Auroraswim</b> (Санкт-Петербург)'
                          '\n-<b>Впитереплыть</b> (Санкт-Петербург)'
                          '\n-<b>Vyborgswim</b> (Выборг)'
                          '\n-<b>Oceanman</b>: Moscow, St.Petersburg'
                          '\n-<b>Swimcup Open Water</b>: Мещерский, Сrimea swim festival, Истра, Белое Озеро, Онего, Кондуки, Руза, Крылатское, Дербент.'
                          '\n-<b>X-Waters</b>: Moscow Strogino, Seliger, Ural, Baikal, Plateau Putorana, Moscow Istra'
                     .format(message.from_user),
                     parse_mode='html')

    time.sleep(2)
    bot.send_message(message.chat.id,
                     text='После применения сложнейших математических алгоритмов, я готов поделиться с тобой тайным знанием — распределением <b>3 726</b> участников по скорости.'
                     .format(message.from_user),
                     parse_mode='html')

    time.sleep(2)
    bot.send_message(message.chat.id,
                     text='Лови моего электронного ската!'
                     .format(message.from_user),
                     parse_mode='html')
    time.sleep(1)
    image = open('images/00.png', 'rb')
    bot.send_photo(message.chat.id, photo=image)

    time.sleep(3)
    bot.send_message(message.chat.id,
                     text='Круто, Да!? И пусть я пока не могу показать тебе итоги вообще всех заплывов в России (потерпи чуть-чуть, скоро все будет), но, если хочешь, могу показать тебя, {0.first_name}, на моем электронном скате.'
                     .format(message.from_user),
                     parse_mode='html')

    time.sleep(2)
    bot.send_message(message.chat.id,
                     text='Просто напиши свою <b>Фамилию</b> и <b>Имя</b> (как при регистрации на заплыв), например «Иванов Иван»)'
                     .format(message.from_user),
                     parse_mode='html')

    write_csv({'datetime':message.date,
               'user_id':message.chat.id,
               'first_name':message.from_user.first_name,
               'last_name':message.from_user.last_name,
               'username':message.from_user.username,
               'text':message.text,
               'event':'start'})
    update_state(message, FIND)


# FIND & ERROR ------------------------------------------------------------------------------------------------------- #
# Функция для проверки ФИО в базе
def check_user(message):
    for user in users['name']:
        # Поменял условие user in users['name'] на ==, чтобы бот избегал ошибок, когда один str будет в другом str
        # Пример возникаемой до этого ошибки:
        # "сороков виталий" in "сороков виталийаовав" возвращает True и переходит к этапу then
        # Это устраняет ошибку №2
        if user == message.text.lower():
            return True
    return False

@bot.message_handler(func=lambda message: get_state(message) == FIND)
def handle_title(message):
    # Так как check_user починен, убрал try, except из-за отсутсвия необходимости
    if check_user(message):
        user_time, user_group_count, target_user = user_data(message.text.lower(), users)
        time.sleep(1)
        bot.send_message(message.chat.id,
                         text='Так! Если мои разработчики ничего не перепутали, то'
                         '\n-твой лучший темп на 1000 метров находится в диапазоне от <b>{}</b> до <b>{}</b> минут;'
                         '\n-в этом диапазоне плывет еще <b>{}</b> человек;'
                         '\nОтметил вас всех красным цветом на графике. Красиво?!'
                         .format((user_time-1),user_time, user_group_count), parse_mode='html')
        image = open('images/' + target_user + '.png', 'rb')
        bot.send_photo(message.chat.id, photo=image)

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton('Найти пейсмейкера', callback_data='pacemaker')
        markup.add(button)

        time.sleep(3)
        bot.send_message(message.chat.id,
                         text='Теперь минутка скучной теории.'
                         '\nУ бегунов есть такое понятие, как пейсмейкер. Это человек, который задает и держит определенный темп всю дистанцию. Обычно он как-то выделяется в общей массе участников, его легко заметить, пристроиться в группу и пробежать дистанцию с желаемым результатом' 
                         '\n\nУ нас, как ты понимаешь, все сильно сложнее. Мы не бегаем, а плаваем. И чтобы найти нужного себе пейсмейкера в стартовом створе, необходимо проявлять чудеса изобретательности и коммуникации. Но теперь, когда у тебя есть я все будет сильно проще. ',
                         parse_mode='html')

        time.sleep(2)
        bot.send_message(message.chat.id,
                         text='Если хочешь, то я помогу тебе подобрать персонального пейсмейкера и встретиться на твоем следующем старте! Этот человек будет плыть чуть-чуть быстрее тебя. Ты сможешь попробовать продержаться за ним всю дистанцию. Справишься – улучшишь свой результат!',
                         reply_markup=markup)
        write_csv({'datetime': message.date,
                   'user_id': message.chat.id,
                   'first_name': message.from_user.first_name,
                   'last_name': message.from_user.last_name,
                   'username': message.from_user.username,
                   'text': message.text,
                   'event': 'find'})
        update_state(message, FINISH)
    else:
        markup_2 = types.InlineKeyboardMarkup()
        button_2 = types.InlineKeyboardButton('Разрешаю написать', callback_data='subscribe')
        markup_2.add(button_2)


        time.sleep(2)
        bot.send_message(message.chat.id,
                         text='Упс ... Или я еще ничего не знаю о твоих подвигах, или ты пишешь с ошибками. \nПопробуй еще раз или разреши написать тебе, когда в моих данных появятся твои результаты.',
                         reply_markup=markup_2)
        write_csv({'datetime': message.date,
                   'user_id': message.chat.id,
                   'first_name': message.from_user.first_name,
                   'last_name': message.from_user.last_name,
                   'username': message.from_user.username,
                   'text': message.text,
                   'event': 'error'})
        update_state(message, FIND)



# FINISH ------------------------------------------------------------------------------------------------------------- #
@bot.message_handler(func=lambda message: get_state(message) == FINISH)
def handle_title(message):
    bot.send_message(message.chat.id,
                     text='Прости, но я должен отвечать и другим пользователям. Вас много, а я один. \nНе обижайся и наберись терпения. Скоро все будет!')


# Button ------------------------------------------------------------------------------------------------------------- #
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Убрал if call.message, так как функция сработает и без нее
    if call.data == 'pacemaker':
        bot.send_message(call.message.chat.id,
                         text='Отлично! Я обязательно напишу тебе, как только получу данные по твоим результатам. Наберись терпения, жди и тренируйся!')
        write_csv({'datetime': call.message.date,
                   'user_id': call.message.chat.id,
                   'first_name': call.from_user.first_name,
                   'last_name': call.from_user.last_name,
                   'username': call.from_user.username,
                   'text': ' ',
                   'event': 'pacemaker'})

        # Удаление кнопки после использования
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Найти пейсмейкера",
                              reply_markup=None)

    elif call.data == 'subscribe':
        bot.send_message(call.message.chat.id,
                         text='Отлично! Я обязательно напишу тебе, как только получу данные по твоим результатам. '
                              'Наберись терпения, жди и тренируйся!')
        update_state(call.message, FINISH)
        write_csv({'datetime': call.message.date,
                   'user_id': call.message.chat.id,
                   'first_name': call.from_user.first_name,
                   'last_name': call.from_user.last_name,
                   'username': call.from_user.username,
                   'text': ' ',
                   'event': 'subscribe'})

        # Удаление кнопки после использования
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Разрешаю написать",
                              reply_markup=None)

# Ошибка №1 возникает на фоне того, что вы изменяли, удаляли или отправляли сообщение человеку, который никогда не пользовался ботом
# Дабы ищбежать в дальнейшем такой ошибки, поменял запись данных 'user_id' в csv с message.from_user.id на message.chat.id
# В случае дальнейшего возникновения такой ошибки, рекомендую проверить, какие данные о chat_id сохраняются в файл и затем отправляются пользователю
# Возможно, вы где-то вместо chat_id отправляли сообщения по message_id или любому другому параметру

# Убрал глобальный try except и поменял запуск бота на цикл while True с блоком try, except запускающий бесконечную запись ошибочных логов, но не ложащий бота
# Также добавил параметр none_stop к работе бота, чтобы любая вызванная ошибка точно его не ложила.

# Ошибку №3 может вызывать нестабильное соединение с сетью, а также то, что ваш TOKEN мог быть взят с открытого репазитория github
# У самого так пару раз было. Для лечения можете просто поменять токен в BotFather
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(e, exc_info=True)
            print(f'Error ocurred: {e}')
