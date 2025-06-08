"""Utility & helper functions."""

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os

def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'model/tag'.
    """
    if os.environ["LLM_PROVIDER"] == "GigaChat":
        from langchain_gigachat import GigaChat
        llm = GigaChat(
            model=fully_specified_name,
            temperature=0.6,
            top_p=0.95
        )
    elif os.environ["LLM_PROVIDER"] == "Yandex":
        llm = ChatOpenAI(
            model="gpt://" + os.environ["FOLDER_ID"] + fully_specified_name,
            api_key=os.environ["API_KEY"],
            base_url="https://llm.api.cloud.yandex.net/v1",
            temperature=0.6,
            top_p=0.95
        )
    else:
        llm = ChatOpenAI(
            model=fully_specified_name,
            temperature=0.6,
            top_p=0.95
        )
    
    
    return llm

def load_query_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'model/tag'.
    """
    if os.environ["LLM_PROVIDER"] == "GigaChat":
        from langchain_gigachat import GigaChatEmbeddings
        llm = GigaChatEmbeddings(
            model=fully_specified_name
        )
    elif os.environ["LLM_PROVIDER"] == "GigaChat":
        llm = OpenAIEmbeddings(
            model="gpt://" + os.environ["FOLDER_ID"] + fully_specified_name,
            api_key=os.environ["API_KEY"],
            base_url="https://llm.api.cloud.yandex.net/v1"
        )
    else:
        from langchain_openai import OpenAIEmbeddings
        llm = OpenAIEmbeddings(
            model=fully_specified_name
        )
    
    
    return llm

def load_doc_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'model/tag'.
    """
    if os.environ["LLM_PROVIDER"] == "GigaChat":
        from langchain_gigachat import GigaChatEmbeddings
        llm = GigaChatEmbeddings(
            model=fully_specified_name
        )
    elif os.environ["LLM_PROVIDER"] == "GigaChat":
        llm = OpenAIEmbeddings(
            model="gpt://" + os.environ["FOLDER_ID"] + fully_specified_name,
            api_key=os.environ["API_KEY"],
            base_url="https://llm.api.cloud.yandex.net/v1"
        )
    else:
        llm = OpenAIEmbeddings(
            model=fully_specified_name
        )
    
    
    return llm


