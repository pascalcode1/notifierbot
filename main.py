import requests
import telebot
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import json
from os import environ as env

BOT_ID = env.get('BOT_ID')

bot = telebot.TeleBot(BOT_ID)
# интервал обновления данных в секундах
update_interval = 360

logging.basicConfig(filename='log.log', level=logging.INFO)


@bot.message_handler(commands=['start'])
def start_message(message):
    log(message)  # TODO хуйнуть локализацию
    bot.send_message(message.chat.id,
                     '''Отправь мне ссылку на taplink профиль для того, чтоб подписаться на изменения этого профиля''')


@bot.message_handler(content_types=['text'])
def send_text(message):
    log(message)
    # TODO нужна норм проверка на валидность ссылки
    if 'taplink.cc/' in message.text.lower():
        subscribe(message)
    else:
        bot.send_message(message.chat.id, 'пошел ты нахер, козел!')


# TODO идея в том, чтоб подписки хранить в бд
def subscribe(message):
    # bot.send_message(message.chat.id, 'Сейчас я вам тут всё попарсю.... ')
    send_all_content(message)


def send_all_content(message):
    response = message.text + '\n\n'
    raw_web_page = requests.get(message.text)
    soup = BeautifulSoup(raw_web_page.text, 'lxml')
    dict_data = json.loads(get_json_from_script(soup))
    items = dict_data['fields'][0]['items']
    for item in items:
        if len(item['options']) != 0:
            if 'title' in item['options']:
                response = response + item['options']['title'] + '\n'
            if 'subtitle' in item['options']:
                response = response + item['options']['subtitle'] + '\n'
            if 'value' in item['options']:
                response = response + item['options']['value'] + '\n'
        response = response + '\n'
    bot.send_message(message.chat.id, response)


def get_json_from_script(soup):
    s = soup.find('script').text
    return s[s.index('window.data') + 14: len(s) - 2]


def log(message):
    username = message.from_user.username
    userid = message.from_user.id
    dt = datetime.fromtimestamp(message.date)
    msg = '{} User {} (id {}) send "{}"'.format(dt, username, userid, message.text.lower())
    print(msg)
    logging.info(msg)


bot.polling()
