""""
RAG总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复
"""
from big_ai.rag.vector_store import VectorStoreService
from langchain_core.prompts import PromptTemplate
from big_ai.common.config_handler import rag_conf
from big_ai.common.prompt_loader import  load_rag_prompts
from big_ai.model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser

def chat_info(data):
    print(data.to_string())
    return data
class RagSummarizeService:
    def __init__(self):
        self.vector_sotre=VectorStoreService()
        #检索器
        self.retriever= self.vector_sotre.get_retroever()
        #提示词模版
        self.prompt_text=load_rag_prompts()
        self.prompt_template=PromptTemplate.from_template(self.prompt_text)

        #调用的模型
        self.model=chat_model
        #chain链
        self.chain=self._init_chain()
    def _init_chain(self):
        chain=self.prompt_template|chat_info|self.model|StrOutputParser()
        return chain
    def retrieve_docs(self,query:str)-> list:
        return self.retriever.invoke(query)
    def rag_summarize(self,query:str) -> str:
        context_docs=self.retrieve_docs(query)
        counter=0
        context=''
        for doc in context_docs:
            counter+=1
            context+=f'【参考资料{counter}】:参考资料{doc.page_content}|参考元数据：{doc.metadata}\n'
        return self.chain.invoke({
            'input':query,
            'context':context
        })
    def _load_prompt_text(self):
        pass

if __name__ == '__main__':
    services=RagSummarizeService()
    res=services.rag_summarize('小户型适合哪些扫地机器人？')
    print(res)