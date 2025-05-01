
import os
import asyncio
from typing import Dict, Any

from react_agent import graph
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv(override=True)

AGENT_HOST = os.getenv("AGENT_HOST", "localhost")
AGENT_PORT = int(os.getenv("AGENT_PORT", 8000))
AGENT_API_KEY = os.getenv("AGENT_API_KEY")
AGENT_NAME = os.getenv("AGENT_NAME", "react-agent")

client = graph

async def answer_to_user_func(context: str) -> str:

    user_text = context
    if not user_text:
        return "❗️ Пустой запрос"
    print('boba', user_text)
    human = HumanMessage(content=user_text)
    payload = {"messages": [human]}

    try:
        response_obj = await graph.ainvoke(payload)
        msgs = response_obj['messages'][-1].content
        if not msgs:
            return "Ошибка при ответе, праститеееее исправимся, дайте деняк по больше токенов и сооооон"
        
        return msgs
    except Exception as e:
        return f"⚠️ Ошибка при обращении к агенту: {e}"
