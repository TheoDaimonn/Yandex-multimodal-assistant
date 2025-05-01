
import os
import asyncio
from typing import Dict, Any

from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv(override=True)

AGENT_HOST = os.getenv("AGENT_HOST", "http://localhost")
AGENT_PORT = int(os.getenv("AGENT_PORT", 2024))
AGENT_API_KEY = os.getenv("AGENT_API_KEY")
AGENT_NAME = os.getenv("AGENT_NAME", "agent")

from langgraph_sdk import get_client 

client = get_client(url=AGENT_HOST+":"+str(AGENT_PORT), api_key=AGENT_API_KEY)

async def answer_to_user_func(context: str) -> str:
        
    assistants = await client.assistants.search()
    assistants = await client.assistants.search(graph_id=AGENT_NAME)
    
    agent = assistants[0]
    thread = await client.threads.create()
    
    user_text = context
    if not user_text:
        return "❗️ Пустой запрос"
    print('boba', user_text)
    human = HumanMessage(content=user_text)
    payload = {"messages": [human]}

    try:
        async for response_obj in client.runs.stream(thread['thread_id'], agent['assistant_id'], input=payload, config={"recursion_limit": 100}):
            print(response_obj)
        
        msgs = response_obj.data['messages'][-1]["content"]
            
        if not msgs:
            return "Ошибка при ответе, праститеееее исправимся, дайте деняк по больше токенов и сооооон"
        
        return msgs
    except Exception as e:
        return f"⚠️ Ошибка при обращении к агенту: {e}"
