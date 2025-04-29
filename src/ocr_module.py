import os
import base64
import requests
import time
from PIL import Image
from pdf2image import convert_from_path
from io import BytesIO
from dotenv import load_dotenv
import json
import shutil  # Импортируем shutil для очистки папки

# Загрузка переменных окружения
load_dotenv()

API_KEY = os.getenv('API_KEY')
RECOGNIZE_URL = 'https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText'
MAX_RETRIES = 10
RETRY_DELAY = 15
TEMP_IMAGES_DIR = "temp_images"

# Создаем временную директорию, если она не существует
os.makedirs(TEMP_IMAGES_DIR, exist_ok=True)

def pdf_to_images(pdf_path: str):
    """Конвертация PDF в изображения и их сохранение в временной папке."""
    try:
        images = convert_from_path(pdf_path)
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(TEMP_IMAGES_DIR, f"page_{i + 1}.jpg")
            image.save(image_path, "JPEG")
            image_paths.append(image_path)
            print(f"Сохранено: {image_path}")
        return image_paths
    except Exception as e:
        print(f"Не удалось конвертировать PDF: {str(e)}")
        return []

def call_api(url, data):
    """Вызов API."""
    headers = {
        "Authorization": f"Api-Key {API_KEY}"
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def ocr(image: Image.Image):
    """Распознавание текста на изображении с помощью OCR API."""
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    myimage = buffer.getvalue()

    j = {
        "mimeType": "JPEG",
        "languageCodes": ["ru"],
        "model": "handwritten",
        "content": base64.b64encode(myimage).decode('utf-8')
    }
    res = call_api(RECOGNIZE_URL, j)
    return res

def save_json_response(response, output_path):
    """Сохранение JSON-ответа в файл."""
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(response, json_file, ensure_ascii=False, indent=4)
        print(f"JSON ответ сохранён в: {output_path}")

def clear_temp_folder(folder_path):
    """Очистка временной папки."""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Удаляем всю папку и её содержимое
        os.makedirs(folder_path)  # Снова создаем папку
        print(f"Временная папка очищена: {folder_path}")

def extract_text_from_response(response):
    """Извлечение текста из JSON-ответа от API."""
    extracted_text = []
    if 'result' in response and 'textAnnotation' in response['result']:
        text_annotation = response['result']['textAnnotation']
        blocks = text_annotation.get('blocks', [])
        
        for block in blocks:
            for line in block.get('lines', []):
                extracted_text.append(line.get('text', ''))
    return "\n".join(extracted_text)

def process_pdf(pdf_path: str):
    """Основная функция для обработки PDF документа."""
    image_paths = pdf_to_images(pdf_path)

    all_text = []
    json_responses = []  # Список для хранения JSON ответов

    for image_path in image_paths:
        with Image.open(image_path).convert("RGB") as img:

            for attempt in range(MAX_RETRIES):
                result = ocr(img)
                
                # Проверяем структуру ответа
                json_responses.append(result)  # Сохраняем ответ JSON для текущего изображения
                
                # Извлекаем текст и добавляем его в общий список
                extracted_text = extract_text_from_response(result)
                if extracted_text:
                    all_text.append(extracted_text)
                    print(extracted_text)
                    print(f"Текст распознан на {image_path}")
                    break
                print(f"🔄 Попытка {attempt + 1}/{MAX_RETRIES} для {image_path}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ Не удалось распознать текст на {image_path}. Ответ: {result}")

    # Сохраняем распознанный текст в файл
    if all_text:
        output_path = os.path.join("data/ocred_pdf", os.path.basename(pdf_path).replace(".pdf", ".txt"))
        os.makedirs("data/ocred_pdf", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_text))
        print(f"✅ Многостраничный текст сохранен в: {output_path}")

    # Сохраняем все JSON ответы в отдельный файл
    json_output_path = os.path.join("data/ocred_pdf", os.path.basename(pdf_path).replace(".pdf", "_responses.json"))
    save_json_response(json_responses, json_output_path)

    # Очищаем временную папку
    clear_temp_folder(TEMP_IMAGES_DIR)

if __name__ == "__main__":
    print(os.listdir('data/pdf'))
    for i in os.listdir('data/pdf'):
        process_pdf('data/pdf/'+i)
