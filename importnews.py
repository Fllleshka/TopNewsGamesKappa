from datetime import date
import locale
import  requests
from bs4 import BeautifulSoup as BS

import importdatesfrompages

def importnews():
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    # Получаем сегодняшнее число
    today = date.today()
    day = today.strftime("%d")
    month = today.strftime("%m")
    months = ["января", "февраля", "марта", "апреля", "майя", "июня", "июля", "августа", "сентября", "октября",
              "ноября", "декабря"]
    year = today.strftime("%Y")
    today = day + " " + months[int(month)-1] + " " + year
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

    i = 0
    for element in dates:
        # Ограничение на максимальное количество новостей на странице
        if i == 20:
            break

        # Обрезаем дату поста новости, для сравнения с текущей датой
        date_post = str(element.text)[:-8]

        # Если дата поста совпадает с сегодняшней датой, то
        if date_post == today:
            # Запускаем функцию парсинга данных
            pageforparce = str(pathlist[i])
            importdatesfrompages.importdates(pageforparce)
        i = i + 1