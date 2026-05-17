# import sys
# 解决线上 chromadb / protobuf 错误
import os
os.environ["CHROMA_TELEMETRY"] = "0"
os.environ["OTEL_SDK_DISABLED"] = "1"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import time

import streamlit as st
from common.env_bootstrap import ensure_dashscope_api_key_in_env

ensure_dashscope_api_key_in_env()

# 然后用相对导入
from agent.react_agent import ReactAgent
from model.factory import get_chat_model
# 标题
st.title("智扫通机器人智能客服")
st.divider()

# 在页面启动时检测模型是否可用；如果不可用则提示用户设置 DASHSCOPE_API_KEY 或安装 dashscope
_chat_available = get_chat_model() is not None
if not _chat_available:
    st.warning(
        "当前处于降级模式：未检测到 dashscope 包或环境变量 DASHSCOPE_API_KEY 未设置。\n"
        "若要启用真实模型响应，请在部署环境（例如 Streamlit Cloud 的 Settings -> Advanced -> Environment variables）中添加 `DASHSCOPE_API_KEY`，"
        "并确保 `requirements.txt` 中包含 `dashscope`。\n"
        "当前将使用本地降级/模拟响应以保持应用可用。"
    )

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = [{'role':'assistant','content':'请输入您想咨询关于扫地机器人内容'}]

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 用户输入提示词
prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []
    with st.spinner("智能客服思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator, cache_list):

            for chunk in generator:
                cache_list.append(chunk)

                for char in chunk:
                    time.sleep(0.01)
                    yield char

        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]})
        st.rerun()


