import os
import shutil
from pprint import pprint

import requests
from bs4 import BeautifulSoup as BS

import createpostinchannel


def importdates(urlpage):
    # Формируем headers, чтобы нам отвечал сервер корректно
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    page = requests.get(urlpage, headers=headers)
    # Разбираем страницу с помощью BeautifulSoup
    html = BS(page.content, 'html.parser')
    # Достаём название статьи
    header_title = html.select(".container-header > h1")[0].text
    # Достаём автора статьи
    autor = html.select(".gbusers-login > span")[0].text
    # Достаём адрес главной картинки
    first_photo = "https://gamebomb.ru/" + html.select(".img > a")[0]['href']
    # Достаём текстовую информацию и формируем из неё массив
    maintext = html.select(".content > div > p")
    massive_text = []
    for element in maintext:
        if element.text == "":
            continue
        else:
            massive_text.append(element.text)
    # Достаём URL картинкок и формируем из неё массив
    massive_photos = []
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
                massive_photos.append("https://gamebomb.ru" + element['href'])
        else:
            continue

    # Скачиваем главную картинку
    page = requests.get(first_photo)
    url = "main_photo.jpg"
    outputpage = open(url, "wb")
    outputpage.write(page.content)
    outputpage.close()
    # Закачиваем на сервер главную картинку
    with open(url, 'rb') as f:
        path = requests.post(
            'https://telegra.ph/upload',
            files={'file': ('file', f, 'image/jpg')}
            # image/gif, image/jpeg, image/jpg, image/png, video/mp4
            ).json()[0]['src']
        first_photo = path
        # Подчищаем главную картинку
        # os.remove(url)
    # Скачиваем в папку TEMP картинки
    os.mkdir("TEMP")
    i = 0
    # Скачиваем картинки из massive_photos
    for element in massive_photos:
        page = requests.get(element)
        url = "TEMP/" + str(i) + ".jpg"
        outputpage = open(url, "wb")
        outputpage.write(page.content)
        outputpage.close()
        i = i + 1

    # Формируем ссылки для картинок, которые загружаем
    # Путь до папки с комиксами
    pathtemp = './TEMP/'
    # Получаем список подпапок
    directory_list = os.listdir(pathtemp)
    # Обнуляем massive_photos
    massive_photos = []
    for element in directory_list:
        waytoimage = "./TEMP/" + element
        print("WAY: ", waytoimage)
        with open(waytoimage, 'rb') as f:
            path = requests.post(
                'https://telegra.ph/upload',
                files={'file': ('file', f, 'image/jpg')}
                # image/gif, image/jpeg, image/jpg, image/png, video/mp4
            ).json()[0]['src']
            print(path)
        massive_photos.append(path)
    # Подчищаем папку
    shutil.rmtree(str(pathtemp)[2:-1])
    print("Удалил папку TEMP")

    # Запускаем функцию формирования постов для telegram канала
    createpostinchannel.createpost(header_title, autor, first_photo, massive_text, massive_photos)
