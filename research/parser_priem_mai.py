import random

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import queue
import time
from datetime import datetime

import json

# Настройки
BASE_URL = "https://priem.mai.ru"  # Замените на URL вашего сайта
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
COOKIES_ACCEPT_BUTTON_SELECTOR = ".cookies-accept-button"  # CSS-селектор кнопки "Принять куки"

# Инициализация
visited_urls = set()
url_queue = queue.Queue()
url_queue.put(BASE_URL)


def accept_cookies(session, url):
    """Принимает куки на сайте, если это необходимо."""
    try:
        response = session.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        accept_button = soup.select_one(COOKIES_ACCEPT_BUTTON_SELECTOR)
        if accept_button:
            button_url = accept_button.get('onclick') or accept_button.get('href')
            if button_url:
                session.post(urljoin(url, button_url), headers=HEADERS)
                print(f"Cookies accepted for {url}")
    except Exception as e:
        print(f"Error accepting cookies: {e}")


def extract_text_from_page(html):
    """Извлекает текстовый контент со страницы."""
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    # Извлекаем текст из параграфов
    text = "\n".join([p.get_text(strip=True) for p in paragraphs])

    # Заменяем &NBSP; на обычные пробелы
    text = text.replace('&NBSP;', ' ')

    # Удаляем лишние пробелы и переносы строк
    text = ' '.join(text.split())
    return text


def is_pdf_link(href):
    """Проверяет, является ли ссылка PDF-файлом."""
    return href.lower().endswith('.pdf')


def generate_output_filename():
    """Генерирует имя файла на основе текущего времени."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{timestamp}_parsed.txt"


def crawl_site():
    """Основная функция для парсинга сайта."""
    session = requests.Session()
    output_filename = generate_output_filename()

    while not url_queue.empty():
        current_url = url_queue.get()
        if current_url in visited_urls:
            continue

        print(f"Processing: {current_url}")
        visited_urls.add(current_url)

        try:
            # Пропускаем PDF-файлы
            if is_pdf_link(current_url):
                print(f"Skipping PDF link: {current_url}")
                continue

            # Принимаем куки, если это необходимо
            accept_cookies(session, current_url)

            # Получаем HTML-код страницы
            response = session.get(current_url, headers=HEADERS)
            if response.status_code != 200:
                print(f"Failed to fetch {current_url}: {response.status_code}")
                continue

            # Извлекаем текст
            text = extract_text_from_page(response.text)
            with open(output_filename, "a", encoding="utf-8") as f:
                f.write(f"\n--- Page: {current_url} ---\n{text}\n")

            # Извлекаем ссылки
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(BASE_URL, href)
                parsed_url = urlparse(full_url)

                # Проверяем, что ссылка относится к текущему домену и еще не посещена
                if parsed_url.netloc == urlparse(BASE_URL).netloc and full_url not in visited_urls:
                    if not is_pdf_link(full_url):  # Пропускаем PDF-файлы
                        url_queue.put(full_url)

        except Exception as e:
            print(f"Error processing {current_url}: {e}")

        # Пауза между запросами, чтобы не перегружать сервер
        sleep = random.randint(200, 300)
        time.sleep(sleep * 0.001)


if __name__ == "__main__":
    crawl_site()