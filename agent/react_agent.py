from langgraph.prebuilt import create_react_agent
from big_ai.model.factory import chat_model
from big_ai.agent.tools.middleware import monitor_tool,log_before_model,report_prompt_switch
from big_ai.common.prompt_loader import load_report_prompts,load_system_prompts
from big_ai.agent.tools.agent_tools import (rag_summarize,get_warther,get_user_location,get_user_id,get_current_month,generate_exernal_data,fetch_external_data)
class ReactAgent:
    def __init__(self):
        self.agent = create_react_agent(
            model=chat_model,
            tools=[rag_summarize,get_warther,get_user_location,get_user_id,get_current_month,generate_exernal_data,fetch_external_data],
            middleware=[monitor_tool,log_before_model,report_prompt_switch],
            system_prompt=load_system_prompts()
        )
    def execute_stream(self,query:str)->str:
        #第三个参数context就是上下文runtime中的信息，就是我们做提示词切换的标记
        result=self.agent.stream({
            'messages':[
                {'role':'user','content':query}
            ]
        },stream_mode='values',context={'report':False})
        for chunk in result:
            last_content=chunk['messages'][-1]
            if last_content.content:
                yield last_content.content.strip() +'\n'
            # try:
            #     if last_content.tool_calls:
            #         print(f'工具调用了{[item['name'] for item in last_content.tool_calls]}')
            # except AttributeError as e:
            #     print(str(e))
            #     raise e

if __name__ == '__main__':
    agent = ReactAgent()
    for chunk in agent.execute_stream('生成我的使用报告'):
        print(chunk,end='',flush=True)