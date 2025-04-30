import datetime
import logging
import os
import json
from yandex_cloud_ml_sdk import YCloudML

folder_id = os.environ["FOLDER_ID"]
api_key = os.environ["API_KEY"]
sdk = YCloudML(folder_id=folder_id, auth=api_key)
model = sdk.models.completions("yandexgpt", model_version="rc")

with open('data/prompts/profile.md', 'r', encoding="utf-8") as f:
    sys_prompt = f.read().strip()

async def profile_query(dialog: str) -> str:
    prompt = f"{sys_prompt}\n\nДиалог для суммаризации:\n{dialog.strip()}"
    
    run_result = await model.run(prompt)
    response = run_result.text.strip()
    
    try:
        profile = json.loads(response)
    except json.JSONDecodeError:
        profile = {"raw": response.replace('\n', ' ')}
    
    return json.dumps(profile, ensure_ascii=False)
