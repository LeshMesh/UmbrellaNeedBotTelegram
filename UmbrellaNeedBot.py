import telebot
from telebot import types
from pyowm.commons.exceptions import NotFoundError
import requests

token = "5386079328:AAEUFk3RECKKWPw7aeFitBBwEiu-zdsREc4"
bot = telebot.TeleBot(token)

markupDefault = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton('Узнать погоду сейчас')
btn2 = types.KeyboardButton('Создать ежедневный запрос погоды')
btnHelp = types.KeyboardButton('Помощь')
markupDefault.add(btn1, btn2)
markupDefault.add(btnHelp)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я показываю погоду. \nВыберите действие:", reply_markup=markupDefault)


@bot.message_handler(content_types=['text'])
def echo_all(message):      # переименовать
    if message.text == "Узнать погоду сейчас":
        msg = bot.send_message(message.chat.id, "Напишите Ваш город")
        bot.register_next_step_handler(msg, get_geo)
    elif message.text == "Создать ежедневный запрос погоды":
        bot.send_message(message.chat.id, "2")
    elif message.text == "Помощь":
        send_welcome(message)       # сделать отдельную функцию help
    else:
        bot.send_message(message.chat.id, "Не понял Вас")


def get_geo(message):
    try:
        city = message.text
        body = {'q': city, 'limit': 1, 'appid': "d491912f4c590c59b48e8f977324a8e2"}
        r = requests.get("http://api.openweathermap.org/geo/1.0/direct", params=body)
        r_dict = r.json()[0]
        lat = r_dict['lat']
        lon = r_dict['lon']
        rez_city = r_dict['local_names']['ru']
        get_weather(lat, lon, rez_city, message)
    except NotFoundError:
        answer = bot.send_message(message.chat.id, f'Не могу найти такой город. Попробуйте еще раз:')
        bot.register_next_step_handler(answer, get_geo, reply_markup=markupDefault)


def get_weather(lat, lon, rez_city, message):
    body = {'lat': lat, 'lon': lon}
    header = {'X-Yandex-API-Key': "dfc4c800-e690-42c6-be72-9113abcdbeca"}
    r = requests.get("https://api.weather.yandex.ru/v2/informers", params=body, headers=header)
    now_temp = str(r.json()['fact']['temp'])
    answer = "По данным Яндекс.Погоды, в городе " + rez_city + " сейчас " + now_temp
    bot.send_message(message.chat.id, answer, reply_markup=markupDefault)


bot.infinity_polling(none_stop=True)
