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
from yandex_chain import YandexEmbeddings

from langchain_openai import OpenAIEmbeddings
import pandas as pd
client = QdrantClient(url="http://localhost:6333")

import os
from fastembed import TextEmbedding, SparseTextEmbedding

dense_embedding_model = YandexEmbeddings(folder_id=os.environ["folder_id"], api_key=os.environ["api_key"])
bm25_embedding_model = SparseTextEmbedding("Qdrant/bm25")

if not client.collection_exists("Collection_pdf"):
    client.create_collection(
        "Collection_pdf",
        vectors_config={
            "dense": models.VectorParams(
                size=len(dense_embedding_model.embed_document("0")),
                distance=models.Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "bm25": models.SparseVectorParams(
                modifier=models.Modifier.IDF,
            )
        }
    )
    df = pd.DataFrame(pd.read_csv("react_agent/data/final_data_with_topics_nd_preprocess.csv"))
    
    client.upload_collection(
        "Collection_pdf",
        vectors = {
            "dense": dense_embedding_model.embed_documents(df["chunk_text"].tolist()),
            "bm25": bm25_embedding_model.embed(df["chunk_text"].tolist()),
        },
        payload=df.to_dict(),
    )


@tool
def search(query:str) -> str:
    """
    Выполняет поиск по базам данных, историям переписки, сайту и документам приёмной комиссии
    Московского авиационного института (МАИ), чтобы предоставить абитуриентам 
    актуальную информацию о поступлении.

    Параметры:
        query (str): Чётко сформулированный поисковый запрос (с программой, формой,
                     годом и т. д.).

    Возвращает:
        str: Текстовую сводку с результатами и ссылками на релевантные документы.
    """
    dense_query_vector = dense_embedding_model.embed_query(query)
    sparse_query_vector = list(bm25_embedding_model.embed([query]))[0]
    prefetch = [
        models.Prefetch(
            query=dense_query_vector,
            using="dense",
            limit=20,
        ),
        models.Prefetch(
            query=models.SparseVector(**sparse_query_vector.as_object()),
            using="bm25",
            limit=20,
        )
    ]
    results = []
    for i in ["Collection_pdf"]: #, "Collection_threads", "Collection_ocr"]:
        results.append(client.query_points(
            i,
            prefetch=prefetch,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF,
            ),
            with_payload=True,
            limit=10,
        ))
    return results

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
    Подсчитывает суммарное количество баллов за указанные индивидуальные достижения.

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
