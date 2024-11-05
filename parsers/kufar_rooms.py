import requests
from bs4 import BeautifulSoup

# URL для первой страницы
BASE_URL = "https://re.kufar.by/l/minsk/snyat/komnatu-dolgosrochno?cur=USD&prc=r%3A0%2C140"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Переменная для хранения адреса последнего обработанного объявления
last_ad_address = None


def get_latest_ad_data(url):
    """Функция получает данные последнего объявления на странице"""
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    latest_ad = soup.find('a', class_='styles_wrapper__Q06m9')

    if latest_ad:
        link = latest_ad['href']
        price = latest_ad.find('span', class_='styles_price__usd__HpXMa').get_text(strip=True)
        address = latest_ad.find('span', class_='styles_address__l6Qe_').get_text(strip=True)

        return {
            'link': link,
            'price': price,
            'address': address
        }
    return None


def parse_kufar_rooms():
    """Функция для получения новых объявлений, возвращает только новое объявление, если оно есть"""
    global last_ad_address
    latest_ad = get_latest_ad_data(BASE_URL)

    # Проверяем, если адрес последнего объявления отличается от предыдущего
    if latest_ad and latest_ad['address'] != last_ad_address:
        last_ad_address = latest_ad['address']  # Обновляем последний адрес
        return [latest_ad]  # Возвращаем новое объявление в списке для совместимости с ботом
    return []  # Возвращаем пустой список, если новых объявлений нет
