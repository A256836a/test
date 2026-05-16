import os

from langchain_core.tools import tool
from big_ai.rag.rag_service import RagSummarizeService
import random
from big_ai.common.config_handler import agent_conf
from big_ai.common.path_tool import get_abs_path
from big_ai.common.logger_handler import logger
rag=RagSummarizeService()
user_id=['1001','1002','1003','1004','1005','1006','1007','1008','1009','1010','1011','1012','1013']
choice_month=['1','2','3','4','5','6','7','8','9','10','11','12']

external_data={}
@tool(description='从向量库中检索参考资料')
def rag_summarize(query:str)->str:
    return rag.rag_summarize(query)

@tool(description='获取指定城市的天气，以消息字符串的形式返回')
def get_warther(query:str)->str:
    return f'城市{query}是一个好天气，气温为26摄氏度，空气湿度为50%，南风1级，AQI21，最近6小时降雨概率极低'

@tool(description='获取用户所在的城市定位，以字符串的形式返回')
def get_user_location(query:str)->str:
    return random.choice(['深圳','广州','汕头','北京'])

@tool(description='获取用户的id，以字符串形式返回')
def get_user_id(query:str)->str:
    return random.choice(user_id)

@tool(description='获取月份，以字符串形式返回')
def get_current_month(query:str)->str:
    return random.choice(choice_month)

def generate_exernal_data():
    """"
    {
    'user_id':{
            'month':{'特征1'：xxxx},
            'month':{'特征2'：xxx}
        }，
    'user_id':{
        'month':{'特征1'：xxxx},
        'month':{'特征2'：xxx}
    }
    }
    """
    if not external_data:
        external_data_path= get_abs_path(agent_conf['external_data_path'])
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f'外部数据文件{external_data_path}不存在')
    with open(external_data_path,'r',encoding='utf-8') as f:
        for line in f.readlines()[1:]:
            arr = line.strip().split(',')
            user_id: str=arr[0].replace('"','')
            feature: str=arr[1].replace('"','')
            efficiency: str=arr[2].replace('"','')
            consumables: str=arr[3].replace('"','')
            comparison: str=arr[4].replace('"','')
            time: str=arr[5].replace('"','')
            if user_id not in external_data:
                external_data[user_id]={}
            external_data[user_id][time]={
                '特征':feature,
                '效率':efficiency,
                '耗材':consumables,
                '对比':comparison
            }
@tool(description='根据外部资料，来获取指定用户的指定月份的使用记录，以字符串的形式返回，如未检索到则返回空字符串')
def fetch_external_data(user_id:str,month:str)->str:
    generate_exernal_data()
    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f'【generate_exernal_data】未能检索到{user_id}在{month}的使用记录')
        return ''

@tool(description='无入参，无返回值')
def fill_context_for_report():
    return '[fill_context_for_report]已被调用'

if __name__ == '__main__':
    res=fetch_external_data('1001','2025-01')
    print(res)