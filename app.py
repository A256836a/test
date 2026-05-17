# import sys
# 解决线上 chromadb / protobuf 错误
import os
import streamlit as st
# 隐藏所有 Streamlit 自带的 UI 元素
st.set_page_config(
    page_title="智扫通机器人智能客服",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# 自定义 CSS 隐藏右上角按钮和右下角管理按钮
hide_streamlit_style = """
<style>
/* 隐藏右上角工具栏所有按钮 */
#MainMenu {visibility: hidden;}
.stDeployButton {display:none;}
header[data-testid="stHeader"] {display: none;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}

/* 隐藏右下角 Manage app 按钮 */
[data-testid="manage-app-button"] {display: none;}
.stAppDeployButton {display: none;}

/* 隐藏底部水印 */
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
os.environ["CHROMA_TELEMETRY"] = "0"
os.environ["OTEL_SDK_DISABLED"] = "1"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import time

from common.env_bootstrap import ensure_dashscope_api_key_in_env

ensure_dashscope_api_key_in_env()

# 然后用相对导入
from agent.react_agent import ReactAgent
from model.factory import get_chat_model
# 标题
# st.title("智扫通机器人智能客服")
# st.divider()

# 在页面启动时检测模型是否可用；如果不可用则提示用户设置 DASHSCOPE_API_KEY 或安装 dashscope
_chat_available = get_chat_model() is not None
if not _chat_available:
    st.warning(
        "当前处于降级模式：未检测到可用的 DashScope API Key。\n\n"
        "请在以下任一位置配置密钥后重新部署：\n"
        "1. **Streamlit Cloud → Settings → Secrets**，添加：\n"
        "   ```toml\n"
        "   DASHSCOPE_API_KEY = \"sk-你的密钥\"\n"
        "   ```\n"
        "2. **Settings → Advanced → Environment variables**，名称 `DASHSCOPE_API_KEY`\n"
        "3. **本地开发**：在项目根目录创建 `.env`，内容为 `DASHSCOPE_API_KEY=sk-...`\n\n"
        "并确认 `requirements.txt` 中已包含 `dashscope`。"
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


