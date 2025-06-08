import datetime
import logging
import os
import json
import asyncio

from react_agent.utils import load_chat_model

model=load_chat_model(os.environ["LLM_PROFILE_MODEL"])

with open('data/prompts/profile.md', 'r', encoding="utf-8") as f:
    SYS_PROMPT = f.read().strip()

async def profile_query(dialog: str) -> str:
    prompt = f"{SYS_PROMPT}\n\nДиалог для суммаризации:\n{dialog.strip()}"

    # выполняем model.run в фоновом потоке
    run_result = await asyncio.to_thread(model.invoke, prompt)
    response = run_result.content

    try:
        profile = json.loads(response)
    except json.JSONDecodeError:
        profile = {"raw": response.replace('\n', ' ')}

    return json.dumps(profile, ensure_ascii=False)
