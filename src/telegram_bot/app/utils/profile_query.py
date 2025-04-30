import datetime
import logging
import os
import json
from ycloud import YCloudML  
from yandex_cloud_ml_sdk import YCloudML

folder_id = os.environ["FOLDER_ID"]
api_key   = os.environ["API_KEY"]
sdk       = YCloudML(folder_id=folder_id, auth=api_key)
model     = sdk.models.completions("yandexgpt", model_version="rc")

def profile_query(dialog: str) -> dict:
    with open('../../data/prompts/profile.md', 'r', encoding="utf-8") as f:
        sys_prompt = f.read().strip()

    prompt = (
        sys_prompt
        + "\n\nДиалог для суммаризации:\n"
        + dialog.strip()
    )   
    response = model.run(prompt).text.strip()

    try:
        profile = json.loads(response)
    except json.JSONDecodeError:
        profile = {"raw": response}

    return profile
