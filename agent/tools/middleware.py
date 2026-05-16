from langchain.agents.middleware import wrap_tool_call, dynamic_prompt, before_model
from big_ai.common.logger_handler import logger
from langchain.agents import create_agent, AgentState
from langgraph.runtime import Runtime
from big_ai.common.prompt_loader import load_report_prompts,load_system_prompts
#工具执行的监控
@wrap_tool_call
def monitor_tool(
        #request为请求的数据封装（入参）
        request
        #执行函数的本身
        ,handler):
        #打印日志
        logger.info(f"[tool monitor]执行工具：{request.tool_call['name']}")
        logger.info(f"[tool monitor]传入参数：{request.tool_call['args']}")
        try:
            #调用函数
            result=handler(request)
            #打印成功的日志
            logger.info(f"[tool monitor] 工具{request.tool_call['name']}调用成功")
            if request.tool_call['name']=='fill_context_for_report':
                request.runtime.context['report']=True
            #返回成功的数据
            return result
        except Exception as e:
            logger.error(f'工具{request.tool_call['name']}调用失败，原因{str(e)}')
            raise e

@before_model()
#在模型执行前输出日志
def log_before_model(
        #整个Agent智能体中的状态记录
        state:AgentState,
        #记录了整个执行过程中的上下文信息
        runtime:Runtime) -> None:
        logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")
        #获取数据后.strip()去除前后空格
        logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__}，{state['messages'][-1].content.strip()}。")
        return None


#每次生成提示词前，都会调用此函数
@dynamic_prompt
#动态切换提示词

def report_prompt_switch(request):
   is_report= request.runtime.context.get('report', False)
   if is_report: #是报告生成场景，返回报告生成提示词内容
       return load_report_prompts()
   #否则返回系统提示词
   return load_system_prompts()