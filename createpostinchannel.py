# Импорт TELEBOT
import telebot
# Импорт TELEGRAPH
from telegraph import Telegraph

def post(header_title, autor, first_photo, massive_text, massive_photos):

    # Создаём аккаунт
    telegraph = Telegraph()
    telegraph.create_account(short_name = autor)

    # Начинаем формировать контент нашей страницы
    # Загружаем главное фото
    content = "<img src = {}/>".format(first_photo)
    # Формируем первые 2 текста
    content += "<p>{}</p>".format(str(massive_text[0]))
    content += "<p>{}</p>".format(str(massive_text[1]))
    # Удаляем данные из списка
    massive_text.pop(0)
    massive_text.pop(0)
    # Формируем первые 1 картинку
    content += "<img src = {}/>".format(massive_photos[0])
    # Удаляем данные из списка
    massive_photos.pop(0)
    # Дописываем всё в фаил
    for element in massive_text:
            content += "<p>{}</p>".format(str(element))
    # Если есть ещё картинки то дописываем в фаил
    for element in massive_photos:
            content += "<img src = {}/>".format(element)
    # Создаём страницу
    response = telegraph.create_page(header_title, html_content = content)
    return response['url']

def createpost(header_title, autor, first_photo, massive_text, massive_photos):

    # Уникальный идентификатор бота
    botkey = '5173334150:AAEnQVapLgLix4xfgOoA24sCAColdGQBcak'
    # Номер диалога для отправки сообщений в канал WildWorldOfComics
    channel_id = '-1001659164973'

    # Токен для связи с ботом
    bot = telebot.TeleBot(botkey)

    # Отправляем сообщение в канал
    url = post(header_title, autor, first_photo, massive_text, massive_photos)
    message = header_title + "\n\n" + url
    bot.send_message(channel_id, message)