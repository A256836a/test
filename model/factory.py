from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel, ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from common.config_handler import rag_conf
import os
from typing import Any


# Lazy-loaded singletons
_CHAT_MODEL: Optional[BaseChatModel] = None
_EMBED_MODEL: Optional[Embeddings] = None


def get_chat_model() -> Optional[BaseChatModel]:
    """Return a cached Chat model instance, creating it on first call.

    This avoids instantiating heavy models at import time (which fails in
    deployment when optional dependencies or env vars are missing).
    """
    global _CHAT_MODEL
    if _CHAT_MODEL is not None:
        return _CHAT_MODEL

    try:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        _CHAT_MODEL = ChatTongyi(model=rag_conf.get("chat_model_name"), api_key=api_key)
        return _CHAT_MODEL
    except Exception as e:
        # Fail gracefully: log to stderr to make deployment logs clearer.
        import logging

        logging.getLogger("model.factory").exception("Failed to initialize chat model: %s", str(e))
        _CHAT_MODEL = None
        return None


def get_embed_model() -> Optional[Embeddings]:
    global _EMBED_MODEL
    if _EMBED_MODEL is not None:
        return _EMBED_MODEL

    try:
        _EMBED_MODEL = DashScopeEmbeddings(model=rag_conf.get("embedding_model_name"))
        return _EMBED_MODEL
    except Exception as e:
        import logging

        logging.getLogger("model.factory").exception("Failed to initialize embedding model: %s", str(e))
        _EMBED_MODEL = None
        return None

