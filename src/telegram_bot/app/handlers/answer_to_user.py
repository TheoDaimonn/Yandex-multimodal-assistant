import os
import asyncio
from typing import Dict, Any

from langgraph.client import GraphClient
from langchain_core.messages import HumanMessage

AGENT_HOST = os.getenv("AGENT_HOST", "localhost")
AGENT_PORT = int(os.getenv("AGENT_PORT", 8000))
AGENT_API_KEY = os.getenv("AGENT_API_KEY")
AGENT_NAME = os.getenv("AGENT_NAME", "react-agent")

client = GraphClient(
    host=AGENT_HOST,
    port=AGENT_PORT,
    api_key=AGENT_API_KEY,
    agent_name=AGENT_NAME,
    timeout=30  
)

async def answer_to_user_func(context: Dict[str, Any]) -> str:

    user_text = context.get("text", "")
    if not user_text:
        return "❗ Пустой запрос"

    human = HumanMessage(content=user_text)
    payload = {"messages": [human]}

    try:
        response_obj = await client.invoke(payload)
        msgs = response_obj.get("messages", [])
        if not msgs:
            return "Ошибка при ответе, праститеееее исправимся, дайте деняк по больше токенов и сооооон"
        
        ai_msg = msgs[-1]
        return getattr(ai_msg, "content", str(ai_msg))
    except Exception as e:
        return f"⚠️ Ошибка при обращении к агенту: {e}"
