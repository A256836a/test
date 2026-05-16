# ========== 必须放在文件第一行 ==========
import sys
import os
import time

# 关键：添加项目根目录（AI大模型）到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ======================================

# 然后用相对导入
from agent.react_agent import ReactAgent
import streamlit as st

st.title('智扫通机器人')
st.divider()
prompt=st.chat_input()
if 'agent' not in st.session_state:
    st.session_state['agent']=ReactAgent()

if 'message' not in st.session_state:
    st.session_state['message']=[{'role':'assistant','content':'请输入内容'}]
for msg in st.session_state['message']:
    st.chat_message(msg['role']).write(msg['content'])

if prompt:
    st.session_state['message'].append({'role':'user','content':prompt})
    st.chat_message('user').write(prompt)
    app_list=[]
    with st.spinner('数据正在加载中。。。'):
       res= st.session_state['agent'].execute_stream(prompt)
       def captrue(data,list):
           for chunk in data:
               list.append(chunk)
               for char in chunk:
                    time.sleep(0.01)
                    yield char

       st.chat_message('assistant').write(captrue(res,app_list))
       st.session_state['message'].append({'role':'assistant','content':app_list[-1]})
       st.rerun()



