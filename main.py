import math
import os
import shutil
import time
import datetime
import locale
import requests
import telebot

from bs4 import BeautifulSoup as BS
from telegraph import Telegraph
from dates import *

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

# Функция формирования списка URLs
def importnews():

    # Получаем сегодняшнее число
    today = datetime.datetime.today()
    day = today.strftime("%d")
    intday = int(day)
    month = today.strftime("%m")
    months = ["января", "февраля", "марта", "апреля", "майя", "июня", "июля", "августа", "сентября", "октября",
              "ноября", "декабря"]
    year = today.strftime("%Y")
    today = str(intday) + " " + months[int(month)-1] + " " + year
    print(today)

    # Формируем headers, чтобы нам отвечал сервер корректно
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    # Url cтраницы с коротой будем парсить данные
    urlpage = "https://gamebomb.ru/news"
    page = requests.get(urlpage, headers=headers)

    # Разбираем страницу с помощью BeautifulSoup
    html = BS(page.content, 'html.parser')
    postdates = html.select(".gbnews-listShort > td > a")

    # Формируем список ссылок на новости
    pathlist = []
    i = 0
    for element in postdates:
        if i%2 == 0:
            pathlist.append(element["href"])
        i = i + 1
    dates = html.select(".sub")
    print(dates)

    result = []
    i = 0
    for element in dates:
        # Ограничение на максимальное количество новостей на странице
        if i == 20:
            break
        # Обрезаем дату поста новости, для сравнения с текущей датой
        date_post = str(element.text)[:-8]
        # Если дата поста совпадает с сегодняшней датой, то
        if date_post == today:
            # Формируем итоговый массив с ссылками
            result.append(str(pathlist[i]))
        i = i + 1
    print(result)
    return result

# Функция планирования отложенного постинга
def planingpost(urls):
    starttimeposting = datetime.time(9,00).strftime("%H")
    endtimeposting = datetime.time(23,00).strftime("%H")
    delta = int(endtimeposting) - int(starttimeposting)
    nextstep = math.floor(delta / len(urls))
    mass = []
    timetopost = int(starttimeposting)
    for element in urls:
        mass.append([timetopost, element])
        timetopost += nextstep
    return mass

# Функция публикации отложенного постинга
def postinchannel(url):
    # Токен для связи с ботом
    bot = telebot.TeleBot(botkey)
    print(url)
    # Публикуем данную ссылку с заголовком статьи в канал
    #message = self.header_title + "\n\n" + url
    bot.send_message(channel_id, url)

class News:

    # Метод-конструктор с переменными экземпляра класса
    def __init__(self, url):
        self.url = url
        self.header_title = ""
        self.autor = ""
        self.first_photo = ""
        self.massive_text = []
        self.massive_photos = []
        self.importdates(url)

    def printimportdates(self):
        print("========================")
        print("URL:")
        print("\t" + self.url)
        print("\t" + self.header_title)
        print("\t" + self.autor)
        print("\t" + self.first_photo)
        for element in self.massive_text:
            print("\t" + element)
        for element in self.massive_photos:
            print("\t" + element)
        print("========================")

    def importdates(self, urlpage):

        print("Запускаем импорт данных с: ", urlpage)

        # Headers, чтобы нам отвечал сервер корректно
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

        # Получаем страницу
        page = requests.get(urlpage, headers=headers)

        # Разбираем страницу с помощью BeautifulSoup
        html = BS(page.content, 'html.parser')

        # Достаём название статьи
        self.header_title = html.select(".container-header > h1")[0].text

        # Достаём автора статьи
        self.autor = html.select(".gbusers-login > span")[0].text

        # Достаём адрес главной картинки
        self.first_photo = "https://gamebomb.ru/" + html.select(".img > a")[0]['href']

        # Достаём текстовую информацию и формируем из неё массив
        maintext = html.select(".content > div > p")
        for element in maintext:
            if element.text == "":
                continue
            else:
                self.massive_text.append(element.text)

        # Достаём URL картинкок
        mainphotos = html.select(".content > div > p > a")

        # Пробегаемся по массиву и исключаем из него данные которые не подходят
        for element in mainphotos:
            substring = str(str(element)[10:])[:5]
            if substring != "files":
                mainphotos.remove(element)

        # Проверка полученных ссылок на картинки
        for element in mainphotos:
            substring = str(str(element)[9:])[:5]
            if substring == "/file":
                if ("https:" in element['href']) == True:
                    continue
                else:
                    self.massive_photos.append("https://gamebomb.ru" + element['href'])
            else:
                continue

        # Печатаем данные
        #self.printimportdates()
        # Выполняем выгрузку данных
        self.downloadfiles()

    def downloadfiles(self):
        # Скачиваем главную картинку
        page = requests.get(self.first_photo)
        url = "main_photo.jpg"
        outputpage = open(url, "wb")
        outputpage.write(page.content)
        outputpage.close()

        # Создаём временную папку TEMP
        urltemp = "TEMP"
        os.mkdir(urltemp)

        # Скачиваем картинки из massive_photos
        i = 0
        for element in self.massive_photos:
            page = requests.get(element)
            urlphotos = "TEMP/" + str(i) + ".jpg"
            outputpage = open(urlphotos, "wb")
            outputpage.write(page.content)
            outputpage.close()
            i = i + 1

        # Выполняем загрузку фаилов в Telegram
        self.uploadfiles(url)

    def uploadfiles(self,urlmainphoto):

        # Закачиваем на сервер главную картинку
        with open(urlmainphoto, 'rb') as f:
            path = requests.post(
                'https://telegra.ph/upload',
                files={'file': ('file', f, 'image/jpg')}
                # image/gif, image/jpeg, image/jpg, image/png, video/mp4
            ).json()[0]['src']
            self.first_photo = path
            #print("============================================>", self.first_photo)
        # Подчищаем главную картинку
        os.remove(urlmainphoto)

        # Путь до папки с TEMP
        pathtemp = './TEMP/'

        # Получаем список фаилов папки TEMP
        directory_list = os.listdir(pathtemp)

        # Обнуляем massive_photos
        self.massive_photos = []

        # Загружаем картинки в Telegram и переопределяем массив со ссылками
        for element in directory_list:
            waytoimage = "./TEMP/" + element
            #print("WAY: ", waytoimage)
            with open(waytoimage, 'rb') as f:
                path = requests.post(
                    'https://telegra.ph/upload',
                    files={'file': ('file', f, 'image/jpg')}
                    # image/gif, image/jpeg, image/jpg, image/png, video/mp4
                ).json()[0]['src']
                #print(path)
            self.massive_photos.append(path)

        # Подчищаем папку
        shutil.rmtree(str(pathtemp)[2:-1])

        # Создаём пост
        self.createpost()

    def createpost(self):

        #self.printimportdates()

        # Создаём ссылку ссылку на пост
        url = self.post()
        exporturls.append(url)

    def post(self):
        # Создаём аккаунт
        telegraph = Telegraph()
        telegraph.create_account(short_name = self.autor)

        # Начинаем формировать контент нашей страницы
        # Загружаем главное фото
        content = "<img src = {}/>".format(self.first_photo)
        # Формируем первые 2 текста
        content += "<p>{}</p>".format(str(self.massive_text[0]))
        content += "<p>{}</p>".format(str(self.massive_text[1]))
        # Удаляем данные из списка
        self.massive_text.pop(0)
        self.massive_text.pop(0)
        # Формируем первые 1 картинку
        content += "<img src = {}/>".format(self.massive_photos[0])
        # Удаляем данные из списка
        self.massive_photos.pop(0)
        # Дописываем всё в фаил
        for element in self.massive_text:
            content += "<p>{}</p>".format(str(element))
        # Если есть ещё картинки то дописываем в фаил
        for element in self.massive_photos:
            content += "<img src = {}/>".format(element)
        #pprint(content)
        # Создаём страницу
        response = telegraph.create_page(self.header_title, html_content = content)
        return response['url']

importtime = datetime.time(23, 55).strftime("%H:%M")
planpostingdates = datetime.time(23, 58).strftime("%H:%M")
timetopost = datetime.time(9, 00).strftime("%H:%M")
nulltime = datetime.time(23, 0).strftime("%H:%M")
# Список экспортированных url
exporturls = []
while True:
    # Время сейчас
    today = datetime.datetime.today()
    todaytime = today.strftime("%H:%M")
    # Обнуление переменных в конце дня
    if todaytime == nulltime:
        # Список импортированных url
        importurls = []
        # Список экспортированных url
        exporturls = []
    elif todaytime == importtime:
        print("ImportTime: ", importtime)
        # Заполняем данные импортированных новостей
        importurls = importnews()
        print("Импортированные новости: ", importurls)
        # Цикл создания новостей
        for element in importurls:
            # Создаём экземпляр новости и работаем с ней
            News(element)
        print("Экспортированные новости: ", exporturls)
    elif todaytime == planpostingdates:
        if len(exporturls) == 0:
            print("Массив экспортированных новостей пуст")
        else:
            print("Массив экспортированных новостей не пуст")
            # Отчистка списка запланированных постов с временем
            timewithposts = []
            print("PlanPostingDates: ", planpostingdates)
            timewithposts = planingpost(exporturls)
            print("План постинга выглядит так:\n", timewithposts)
    elif todaytime == timetopost:
        print("TimeToPost: ", timetopost)
        print("До удаления элемента =============> ", timewithposts)
        print("Размер TimeWithPosts: ", len(timewithposts))
        if len(timewithposts) == 1:
            postinchannel(timewithposts[0][1])
            timetopost = datetime.time(9, 00).strftime("%H:%M")
        else:
            postinchannel(timewithposts[0][1])
            timetopost = datetime.time(timewithposts[1][0], 00).strftime("%H:%M")
            print("Следующее вермя поста: ", timetopost)
            timewithposts.pop(0)
        print("После удаления элемента =============> ", timewithposts)
    else:
        print(todaytime)
    time.sleep(60)