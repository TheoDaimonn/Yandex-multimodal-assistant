import requests
from typing import List, Dict

# Базовый URL для MAI NIU на Postupi.Online
BASE_URL = "https://msk.postupi.online/vuz/api-mai-niu/spec/"

def fetch_spec(year: int, fcost: int = 2) -> List[Dict]:
    """
    Делает запрос к эндпоинту /spec/ и возвращает JSON-список всех программ:
      - year  — год приёмной кампании
      - fcost — форма обучения (2 = бюджет)
    """
    params = {"year": year, "fcost": fcost}
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_cutoffs(speciality_code: str, years: List[int], fcost: int = 2) -> Dict[int, Dict]:
    """
    Собирает проходные баллы конкретной специальности за указанные годы.
    
    :param speciality_code: код специальности (например, "01.03.02")
    :param years: список годов, например [2019, 2020, 2021, 2022]
    :param fcost: форма обучения (2 = бюджет)
    :return: словарь {год: данные_о_баллах}
    """
    results = {}
    for year in years:
        try:
            data = fetch_spec(year, fcost)
            # находим запись по коду специальности
            entry = next((item for item in data if item.get("specialnost") == speciality_code), None)
            if entry:
                results[year] = entry
                print(f"✅ {year}: минимум {entry.get('minScore')} баллов")
            else:
                print(f"❌ {year}: специальность {speciality_code} не найдена")
        except requests.HTTPError as e:
            print(f"❌ {year}: HTTP {e.response.status_code}")
        except Exception as e:
            print(f"❌ {year}: ошибка {e}")
    return results

if __name__ == "__main__":
    # Пример использования
    SPECIALITY_CODE = "01.03.02"            # код специальности в URL
    YEARS = [2019, 2020, 2021, 2022, 2023]  # интересующие годы

    cutoffs = get_cutoffs(SPECIALITY_CODE, YEARS)
    # Выводим итоговую структуру
    for y, info in cutoffs.items():
        print(f"\n=== {y} ===")
        # Поля могут отличаться в реальном JSON — проверьте ключи
        print(info)
