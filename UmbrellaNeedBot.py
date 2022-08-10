import telebot
from telebot import types
from pyowm.commons.exceptions import NotFoundError
import requests

token = "5386079328:AAEUFk3RECKKWPw7aeFitBBwEiu-zdsREc4"
bot = telebot.TeleBot(token)

markupDefault = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton('Узнать погоду сейчас')
btn2 = types.KeyboardButton('Добавить постоянный запрос погоды')
markupDefault.add(btn1, btn2)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я показываю погоду. Выберите действие:", reply_markup=markupDefault)


@bot.message_handler(content_types=['text'])
def echo_all(message):
    if message.text == "Узнать погоду сейчас":
        msg = bot.send_message(message.chat.id, "Напишите Ваш город")
        bot.register_next_step_handler(msg, send_weather)
    elif message.text == "Добавить постоянный запрос погоды":
        bot.send_message(message.chat.id, "2")
    else:
        bot.send_message(message.chat.id, "Не понял Вас")


def send_weather(message):
    try:
        city = message.text
        body = {'q': city, 'limit': 1, 'appid': "d491912f4c590c59b48e8f977324a8e2"}
        r = requests.get("http://api.openweathermap.org/geo/1.0/direct", params=body)
        r_dict = r.json()[0]
        lat = r_dict['lat']
        lon = r_dict['lon']
        rez_city = r_dict['local_names']['ru']

        body2 = {'lat': lat, 'lon': lon}
        head = {'X-Yandex-API-Key': "dfc4c800-e690-42c6-be72-9113abcdbeca"}
        r2 = requests.get("https://api.weather.yandex.ru/v2/informers", params=body2, headers=head)
        answer = rez_city + " " + str(r2.json()['fact']['temp'])
        bot.send_message(message.chat.id, answer)
    except NotFoundError:
        answer = bot.send_message(message.chat.id, f'Не могу найти такой город. Попробуйте еще раз:')
        bot.register_next_step_handler(answer, send_weather, reply_markup=markupDefault)


bot.infinity_polling(none_stop=True)


# получить город
# найти координаты
# запросить погоду
# сделать клавиатуру
# разовая или каждый день(время, город)
