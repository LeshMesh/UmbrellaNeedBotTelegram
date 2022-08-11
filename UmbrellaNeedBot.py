import time

import requests
import telebot
from pyowm.commons.exceptions import NotFoundError
from telebot import types

import maya
import schedule

token = "5386079328:AAEUFk3RECKKWPw7aeFitBBwEiu-zdsREc4"
bot = telebot.TeleBot(token)

user_dict = {}

markupDefault = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton('Узнать погоду сейчас')
btn2 = types.KeyboardButton('Создать ежедневный запрос погоды')
btnHelp = types.InlineKeyboardButton(text='Помощь', callback_data='/help')  # почтитать
markupDefault.add(btn1, btn2)
markupDefault.add(btnHelp)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я показываю погоду. \nВыберите действие:", reply_markup=markupDefault)


@bot.message_handler(content_types=['text'])
def get_task(message):
    if message.text == "Узнать погоду сейчас":
        msg = bot.send_message(message.chat.id, "Напишите Ваш город")
        bot.register_next_step_handler(msg, send_weather)
    elif message.text == "Создать ежедневный запрос погоды":
        msg = bot.send_message(message.chat.id, "Напишите Ваш город")
        bot.register_next_step_handler(msg, save_city)
    elif message.text == "Помощь":
        send_welcome(message)  # сделать отдельную функцию help
    else:
        bot.send_message(message.chat.id, "Не понял Вас")


def get_geo(message):
    try:
        #        city = message.text
        body = {'q': message, 'limit': 1, 'appid': "d491912f4c590c59b48e8f977324a8e2"}
        r = requests.get("http://api.openweathermap.org/geo/1.0/direct", params=body)
        r_dict = r.json()[0]
        lat = r_dict['lat']
        lon = r_dict['lon']
        rez_city = r_dict['local_names']['ru']
        return lat, lon, rez_city
    except NotFoundError:  # написать другое исключение
        answer = bot.send_message(message.chat.id, f'Не могу найти такой город. Попробуйте еще раз:')
        bot.register_next_step_handler(answer, get_geo, reply_markup=markupDefault)


def get_weather(lat, lon):
    body = {'lat': lat, 'lon': lon}
    header = {'X-Yandex-API-Key': "dfc4c800-e690-42c6-be72-9113abcdbeca"}
    r = requests.get("https://api.weather.yandex.ru/v2/informers", params=body, headers=header)
    now_temp = str(r.json()['fact']['temp'])
    return now_temp


def send_weather(message):
    city = message.text
    lat, lon, rez_city = get_geo(city)
    now_temp = get_weather(lat, lon)
    answer = "По данным Яндекс.Погоды, в городе " + rez_city + " сейчас " + now_temp
    bot.send_message(message.chat.id, answer, reply_markup=markupDefault)


@bot.message_handler(content_types=['text'])
def save_city(message):
    lat, lon, rez_city = get_geo(message.text)
    user_dict["city"] = rez_city
    user_dict["lat"] = lat
    user_dict["lon"] = lon
    user_dict["chat_id"] = message.chat.id
    msg = bot.send_message(message.chat.id, "Напишите время уведомления по МСК")
    bot.register_next_step_handler(msg, save_time)


@bot.message_handler(content_types=['text'])
def save_time(message):
    time = message.text
    dt = maya.parse(time).datetime()
    user_dict["time"] = str(dt.time())
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('Да')
    btn2 = types.KeyboardButton('Нет, изменить')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Создать уведомление:", reply_markup=markup)
    msg = bot.send_message(message.chat.id, user_dict["city"] + " в " + user_dict["time"] + "?")
    bot.register_next_step_handler(msg, save_notification)


@bot.message_handler(content_types=['text'])
def save_notification(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Ок", reply_markup=markupDefault)
        send_notification()
    elif message.text == "Нет, изменить":
        msg = bot.send_message(message.chat.id, "Напишите Ваш город")
        bot.register_next_step_handler(msg, save_city)
    else:
        bot.send_message(message.chat.id, "Не понял Вас")


def send_notification():
    city = user_dict["city"]
    time_nf = user_dict["time"]
    lat, lon, rez_city = get_geo(city)
    now_temp = get_weather(lat, lon)
    answer = "По данным Яндекс.Погоды, в городе " + city + " сейчас " + now_temp + " " + time_nf
    bot.send_message(user_dict["chat_id"], answer, reply_markup=markupDefault)


# schedule.every(2).minutes.do(send_notification)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

bot.infinity_polling(none_stop=True)

