"""Load API keys from .env, process env, and Streamlit secrets."""
import os
from pathlib import Path


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        root = Path(__file__).resolve().parent.parent
        load_dotenv(root / ".env")
    except Exception:
        pass


_load_dotenv()


def _read_streamlit_secret() -> str | None:
    try:
        import streamlit as st

        if "DASHSCOPE_API_KEY" in st.secrets:
            return str(st.secrets["DASHSCOPE_API_KEY"]).strip()

        dashscope = st.secrets.get("dashscope")
        if isinstance(dashscope, dict):
            key = dashscope.get("api_key") or dashscope.get("DASHSCOPE_API_KEY")
            if key:
                return str(key).strip()
    except Exception:
        pass
    return None


def get_dashscope_api_key() -> str | None:
    key = os.getenv("DASHSCOPE_API_KEY")
    if key and key.strip():
        return key.strip()
    return _read_streamlit_secret()


def ensure_dashscope_api_key_in_env() -> bool:
    """Expose the resolved key via os.environ for SDKs that only read env vars."""
    key = get_dashscope_api_key()
    if not key:
        return False
    os.environ["DASHSCOPE_API_KEY"] = key
    return True
