import requests
from bs4 import BeautifulSoup
import time
import random
from sqlalchemy import create_engine
from db_create import Apartmets, Base
from sqlalchemy.orm import sessionmaker

#"Конструктор урла"
city = 'moskva'

page = ''   #номер страницы
if page:
    page = f'&p={page}'

district = '' #номер района
if district:
    district = f'&district={district}'

#тип квартиры
type = {'vse': '-ASgBAgICAUSSA8YQ?cd=1',
        'studii': '/studii-ASgBAQICAUSSA8YQAUDKCBT~WA?cd=1',
        'svobodnaya_planirovka': '/svobodnaya_planirovka-ASgBAQICAUSSA8YQAUDKCBT8zzI?cd=1',
        '1-komnatnye': '/1-komnatnye-ASgBAQICAUSSA8YQAUDKCBSAWQ?cd=1',
        '2-komnatnye': '/2-komnatnye-ASgBAQICAUSSA8YQAUDKCBSCWQ?cd=1',
        '3-komnatnye': '/3-komnatnye-ASgBAQICAUSSA8YQAUDKCBSEWQ?cd=1',
        '4-komnatnye': '/4-komnatnye-ASgBAQICAUSSA8YQAUDKCBSGWQ?cd=1',
        '5': f'-ASgBAgICAUSSA8YQ?cd=1{district}&f=ASgBAQICAUSSA8YQAUDKCGSKWZqsAZisAZasAZSsAYhZ'}

HOST = 'https://www.avito.ru'
#URL = 'https://www.avito.ru/moskva/kvartiry/prodam-ASgBAgICAUSSA8YQ?cd=1'
URL = f'https://www.avito.ru/{city}/kvartiry/prodam' + type['1-komnatnye'] + district + page

headers = {
    'authority': 'www.avito.ru',
    'sec-ch-ua': '^\\^Chromium^\\^;v=^\\^91^\\^, ^\\^',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://www.avito.ru/',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': '<сюда надо кукисы положить>'
}


def get_html(url, params=None):
    r = requests.get(url, headers=headers, params=params)
    return r

#кол=во страниц
def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='pagination-item-1WyVp')
    num_of_pages = 1
    for item in pagination:
        try:
            if int(item.get_text()) > num_of_pages:
                num_of_pages = int(item.get_text())
        except:
            pass
    return num_of_pages

#разбор хтмл
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    apartments = []
    items = soup.find_all('div', class_='iva-item-body-NPl6W')
    for item in items:
        try:
            title = item.find('a', class_='link-link-39EVK link-design-default-2sPEv title-root-395AQ iva-item-title-1Rmmj title-listRedesign-3RaU2 title-root_maxHeight-3obWc').get('title')
        except:
            title = ''
        try:
            price = item.find(itemprop='price').get('content')
        except:
            price = ''
        try:
            link = HOST+item.find('a', class_='link-link-39EVK link-design-default-2sPEv title-root-395AQ iva-item-title-1Rmmj title-listRedesign-3RaU2 title-root_maxHeight-3obWc').get('href')
        except:
            link = ''
        apartments.append({
            'title': title,
            'price': price,
            'link': link,
        })
    return apartments


def parse():
    #Парсинг и запись в бд
    #Предварительно нужно создать базу через db_create.py с названием apartmentsDB.db
    engine = create_engine('sqlite:///apartmentsDB.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    html = get_html(URL)
    if html.status_code == 200:
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count+1):
            print(f'парсинг {page} из {pages_count}')
            html = get_html(URL, params={'p': page})
            apartments = get_content(html.text)
            print(apartments)
            for apartment in apartments:
                title = apartment['title']
                price = apartment['price']
                link = apartment['link']
                new_apartment = Apartmets(title=title, price=price, link=link)
                session.add(new_apartment)
                session.commit()
            time.sleep(random.random()*5 + random.random()*2 + 2)


parse()
