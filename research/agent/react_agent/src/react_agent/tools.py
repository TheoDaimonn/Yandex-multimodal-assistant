"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from typing import Any, Callable, List, Optional, cast
import json

from react_agent.configuration import Configuration
from langchain_core.tools import tool

from qdrant_client import QdrantClient, models
import pandas as pd
client = QdrantClient("http://localhost:6333")

import os
from fastembed import SparseTextEmbedding
from yandex_cloud_ml_sdk import YCloudML
sdk = YCloudML(folder_id=os.environ["FOLDER_ID"], auth=os.environ["API_KEY"])

dense_query_embedding_model = sdk.models.text_embeddings("query")
dense_doc_embedding_model = sdk.models.text_embeddings("doc")
bm25_embedding_model = SparseTextEmbedding("Qdrant/bm25")
folder_id = os.environ["FOLDER_ID"]
api_key = os.environ["API_KEY"]

sdk = YCloudML(folder_id=folder_id, auth=api_key)
model = sdk.models.completions("yandexgpt", model_version="rc")

from datasets import Dataset
import tqdm

if not client.collection_exists("Collection_pdf"):
    
    df = Dataset.from_pandas(pd.DataFrame(pd.read_csv("react_agent/data/knowledge_data.csv", header=1, names=["_id", "source", "chunk_text", "topics"])))
    client.create_collection(
        "Collection_pdf",
        vectors_config={
            "dense": models.VectorParams(
                size=len(dense_doc_embedding_model.run("0").embedding),
                distance=models.Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "sparse": models.SparseVectorParams(
                modifier=models.Modifier.IDF,
            )
        }
    )

    batch_size = 4
    for batch in tqdm.tqdm(df.iter(batch_size=batch_size), 
                        total=len(df) // batch_size):
        dense_embeddings =  [dense_doc_embedding_model.run(doc).embedding for doc in batch["chunk_text"]]
        bm25_embeddings = list(bm25_embedding_model.embed(batch["chunk_text"]))
        
        client.upload_points(
            "Collection_pdf",
            points=[
                models.PointStruct(
                    id=int(batch["_id"][i]),
                    vector={
                        "dense": dense_embeddings[i],
                        "sparse": bm25_embeddings[i].as_object(),
                    },
                    payload={
                        "_id": batch["_id"][i],
                        "source": batch["source"][i],
                        "topics": batch["topics"][i],
                        "chunk_text": batch["chunk_text"][i],
                    }
                )
                for i, _ in enumerate(batch["_id"])
            ],
            # We send a lot of embeddings at once, so it's best to reduce the batch size.
            # Otherwise, we would have gigantic requests sent for each batch and we can
            # easily reach the maximum size of a single request.
            batch_size=batch_size,  
        )
        
def tag_query(query):
    with open('../../data/tagging_prompt.md', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    return model.run(system_prompt + "\n\n Входной запрос:\n" + query).text

@tool
def search(query:str) -> str:
    """
    Инструмент для поиска информации в базе знаний Московского авиационного института (МАИ).
    Предназначен для помощи абитуриентам в получении актуальных данных о направлениях подготовки, правилах поступления, требованиях к документам, расписании экзаменов и других вопросах, связанных с обучением в МАИ.
    Формулируйте запросы чётко и конкретно для получения релевантной информации
    """
    dense_query_vector = dense_query_embedding_model.run(query).embedding
    sparse_query_vector = list(bm25_embedding_model.embed([query]))[0]
    query_topics = tag_query(query).split(', ')
    if 'мусор' in query_topics:
        query_topics.remove("мусор")
    query_topics = set(query_topics)

    prefetch = [
        models.Prefetch(
            query=dense_query_vector,
            using="dense",
            limit=30,
        ),
        models.Prefetch(
            query=models.SparseVector(**sparse_query_vector.as_object()),
            using="sparse",
            limit=30,
        )
    ]
    results = []
    print(query, ' - ', query_topics)
    for col in ["Collection_pdf"]:
        resp = client.query_points(
            col,
            prefetch=prefetch,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF,
            ),
            with_payload=True,
            limit=10
        )
                
        for point in resp.points:
            if set(point.payload['topics']) >= query_topics or point.score > 0.87:
                results.append(point.payload["chunk_text"])
    results = results[:20]
    if 'chat' in point.payload['source']:
        date = point.payload['source'].split('_')[0].replace('chat', '')
    else:
        mapping_dict = {'Онлайн_магистратура_«Машинное_обучение_и_анализ_данных»' : 2024,
'Особые_условия_для_поступления_в_Институт_№8_МАИ' : '2024-2026',
'Постановление Правительства РФ от 27.04.2024 N 555 — Редакция от 07.04.2025 — Контур.Норматив ' : '2025-2026',
'Правила приема МАИ' : '2025-2026',
'Правила Приема(Министерские) ' : '2024 - 2026',
'Федеральный закон от 29 декабря 2012 г. N 273-ФЗ _Об образовании в Российской Фе ... _ Система ГАРАНТ' :' 2012 - 2025'}
        date = mapping_dict.get(point.payload['source'], '2025-2026')

    return "\n".join([20*"=" + "Актуально в период:" + f"\n# Источник номер {i+1}\n" + _ for i, _ in enumerate(results)])

@tool
def get_individual_achivements() -> str:
    """
    Загружает и возвращает данные об индивидуальных достижениях для поступления в МАИ.

    Читает файл 'individual_achivements_mapping.json' и возвращает его содержимое.
    
    Возвращает:
        str: JSON-строка с информацией о баллах за индивидуальные достижения.
    """
    with open('../data/individual_achivements_mapping.json', 'r') as file:
        data = json.load(file)
    return f"JSON с информацией об индивидуальных достижениях \n {data}"

@tool
def count_individual_achivements(achivements_list:list) -> str:
    """
    Подсчитывает суммарное количество баллов за указанные индивидуальные достижения. Сначало нужно вызвать инструмент "get_individual_achivements" и указать список достижений в виде ключей JSON в соответствие с полями.

    Принимает:
        achievements_list (list[str]): Список ключей достижений.

    Возвращает:
        str: Сообщение с общей суммой баллов.
    """
    with open('../data/individual_achivements_mapping.json', 'r') as file:
        data = json.load(file)
    total = 0
    for achievement in achivements_list:
        total += data.get(achievement, 0)
    return f"Сумма индивидуальных достижений пользователя: \n {total % 10}"


@tool
def get_branch_addresses() -> str:
    """
    Загружает и возвращает данные об адресах филлиалов МАИ.

    Читает файл 'fillials_info.json' и возвращает его содержимое.
    
    Возвращает:
        str: JSON-строка с информацией о баллах за индивидуальные достижения.
    """
    with open('../data/filials_info.json', 'r') as file:
        data = json.load(file)
    return f"JSON с информацией об адресах филлиалов \n {data}"


@tool
def calculate_total_scholarship(scholarship_names: list[str]) -> str:
    """
    Рассчитывает общую сумму стипендий на основе списка их названий.

    Принимает:
        scholarship_names (list[str]): Список названий стипендий из JSON-файла

    Возвращает:
        str: Сообщение с общей суммой стипендий или ошибкой, если названия не найдены
    """
    with open('../data/scholarship_info.json', 'r') as file:
        scholarships = json.load(file)
    
    total = 0
    missing = []
    
    for name in scholarship_names:
        if name in scholarships:
            total += scholarships[name]
        else:
            missing.append(name)
    
    if missing:
        return f"Ошибка: следующие стипендии не найдены - {', '.join(missing)}"
    else:
        return f"Общая сумма стипендий: {total} руб."


def get_scholarship_amounts() -> str:
    """
    Загружает и возвращает данные о размерах стипендий в МАИ.

    Читает файл 'scholarships_info.json' и возвращает его содержимое.
    
    Возвращает:
        str: JSON-строка с информацией о размерах стипендий.
    """
    with open('../data/scholarships_info.json', 'r') as file:
        data = json.load(file)
    return f"JSON с размерами стипендий: \n {data}"

@tool
def calculate_tuition_by_program(program_code: str, duration: int = 1) -> str:
    """
    Рассчитывает стоимость обучения по конкретному направлению за указанный период.

    Принимает:
        program_code (str): Код образовательной программы (например, "09.03.01")
        duration (int): Период обучения в годах (1 - за 1 год, 4 - за 4 года)

    Возвращает:
        str: Сообщение со стоимостью обучения или ошибкой, если программа не найдена
    """
    with open('../data/tuition_fees.json', 'r') as file:
        tuition_data = json.load(file)
    
    # Ищем программу во всех филиалах и уровнях образования
    for campus_name, campus_data in tuition_data.items():
        for level_name, level_data in campus_data.items():
            if program_code in level_data:
                program_info = level_data[program_code]
                if isinstance(program_info["Очная"], int):
                    if level_name == "Базовое высшее (4 года)" or level_name == "Бакалавриат":
                        yearly_cost = program_info["Очная"] / 4
                    else:
                        yearly_cost = program_info["Очная"] / 5.5

                    total_cost = yearly_cost * duration
                    
                    program_name = program_info["Наименование"]
                    campus = campus_name.split('(')[0].strip()
                    
                    return (
                        f"Стоимость обучения по программе '{program_name}' ({program_code}):\n"
                        f"• За 1 год: {yearly_cost} руб.\n"
                        f"• За {duration} года(лет): {total_cost} руб.\n"
                        f"Филиал: {campus}\n"
                        f"Уровень образования: {level_name}"
                    )
                else:
                    return f"Ошибка: стоимость обучения для программы {program_code} не указана (уточняется)"
    
    return f"Ошибка: программа с кодом {program_code} не найдена"


@tool
def get_tuition_info() -> str:
    """
    Загружает и возвращает данные о стоимости обучения в МАИ и филиалах.

    Читает файл 'tuition_fees.json' и возвращает его содержимое.
    
    Возвращает:
        str: JSON-строка с информацией о стоимости обучения
    """
    with open('../data/tuition_fees.json', 'r') as file:
        data = json.load(file)
    return f"JSON с данными о стоимости обучения: \n {json.dumps(data, indent=2, ensure_ascii=False)}"




TOOLS: List[Callable[..., Any]] = [get_individual_achivements, count_individual_achivements, 
                                    get_branch_addresses,
                                    get_scholarship_amounts, calculate_total_scholarship,
                                    get_tuition_info, calculate_tuition_by_program, search]
