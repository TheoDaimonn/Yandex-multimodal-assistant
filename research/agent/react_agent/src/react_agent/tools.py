"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from typing import Any, Callable, List, Optional, cast

from langchain_tavily import TavilySearch  # type: ignore[import-not-found]

from react_agent.configuration import Configuration
from langchain_core.tools import tool

import json


# async def search(query: str) -> Optional[dict[str, Any]]:
#     """Search for general web results.

#     This function performs a search using the Tavily search engine, which is designed
#     to provide comprehensive, accurate, and trusted results. It's particularly useful
#     for answering questions about current events.
#     """
#     configuration = Configuration.from_context()
#     wrapped = TavilySearch(max_results=configuration.max_search_results)
#     return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))
@tool
def search(query:str) -> str:
    """Ищет информацию нужную пользователю"""
    return f"Крутая  информация про {query}"

@tool
def get_individual_achivements() -> str:
    """Получает JSON с информацией об индивидуальных достижениях"""
    with open('research/agent/react_agent/src/achievements.json', 'r') as file:
        data = json.load(file)
    return f"JSON с информацией об индивидуальных достижениях \n {data}"

@tool
def count_individual_achivements(achivements_list:list) -> str:
    """Подсчитывает сумму баллов за индивидуальные достижения"""
    with open('research/agent/react_agent/src/achievements.json', 'r') as file:
        data = json.load(file)
    total = 0
    for achievement in achivements_list:
        total += data.get(achievement, 0)
    return f"Сумма индивидуальных достижений пользователя: \n {total % 10}"






TOOLS: List[Callable[..., Any]] = [search]
