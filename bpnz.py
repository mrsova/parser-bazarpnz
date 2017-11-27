import sqlite3
import requests
from io import StringIO
from lxml import html

def parser(message, bot, url_index):
    """
        Функция парсит сайт по ссылке page, избегая агенства.
    """
    connection = sqlite3.connect('bazar.sqlite')
    cursor = connection.cursor()
    page = requests.get(url_index)
    page.encoding = "WINDOWS-1251"

    root = html.parse(StringIO(page.text)).getroot()
    elements = root.xpath('//table[@class="list"]//tr[@class="norm"]')

    results = []

    for element in elements:
        if element[0].get('colspan') != '12':
            name = element[3][0][0].text_content()
            url = element[3][0][0].get('href')
            price = element[1][0].text_content()
            id = url.split('/')[2]
            date = element[5].text_content()

            page = requests.get("http://bazarpnz.ru/" + url)
            page.encoding = 'WINDOWS-1251'
            root = html.parse(StringIO(page.text)).getroot()
            user_info = root.xpath('//p[@class="adv_text"]') 
            
            try:
                description = user_info[0].text_content()
            except:
                description = "Нет описания"
            item = {
                "id": id,
                "price": price,
                "name": name,
                "url": "http://bazarpnz.ru" + url,
                "description": description,
                "date": date.strip()
            }
            results.append(item)

    for el in results:
        cursor.execute("SELECT * FROM Bazar WHERE id_bazar=:id",{"id": el["id"]})
        results = cursor.fetchall()
        if len(results) == 0:
            try:                
                cursor.execute("insert into Bazar (name, description, url, id_bazar, data, price) values (:name, :description, :url, :id_bazar, :data,:price)",
                    {
                        "name": el["name"],
                        "description": el["description"],
                        "url": el["url"],
                        "id_bazar":el["id"],
                        "data": el["date"],
                        "price": el["price"]
                    })
                result = cursor.fetchall()

                mess = "{0} \n Ссылка: {1}\n Цена: {2}\n Дата: {3}\n\n{4}".format(el["name"], el["url"], el["price"], el["date"], el["description"])

                bot.send_message(str(message.from_user.id), str(mess))
            except sqlite3.DatabaseError as err:       
                print("Error: ", err)
            else:
                connection.commit()
        else:
            print("Есть в базе данных")

    connection.close()
