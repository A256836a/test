import sys
import os
import hashlib
from big_ai.common.file_handler import pdf_loader,txt_loader,listdir_with_allowed_type,get_file_md5_hex
from big_ai.common.path_tool import get_abs_path
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from big_ai.common.config_handler import chroma_conf
from big_ai.model.factory import embed_model
from big_ai.common.logger_handler import logger
class VectorStoreService:
    def __init__(self):
        self.chroma = Chroma(
            collection_name=chroma_conf['collection_name'],
            embedding_function=embed_model,  # 嵌入模型
            persist_directory=chroma_conf['persist_directory']
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf['chunk_size'],  # 分割后的文本段最大长度
            chunk_overlap=chroma_conf['chunk_overlap'],  # 连续文本段之间的字符重叠数量
            # separator=config.separator, #自然段落划分的符号
            length_function=len,  # 使用python自带的len函数做长度统计的依据
        )
    def get_retroever(self):
        return self.chroma.as_retriever(search_kwargs={'k':chroma_conf['k']})
    def load_document(self):
        """"
        从数据文件夹内读取数据文件，转为向量存入向量库，
        要计算文件的MD5做去重
        """
        #检查是否存在md5数据
        def check_document(md5):
            if not os.path.exists(get_abs_path(chroma_conf['md5_hex_store'])):
                open(get_abs_path(chroma_conf['md5_hex_store']),'w',encoding='utf-8').close()
                return False
            else:
               with open(get_abs_path(chroma_conf['md5_hex_store']),'r',encoding='utf-8') as f:
                   for line in f.readlines():
                    line = line.strip()
                    if line==md5:
                        return True
            return False
        #保存md5数据
        def save_document(md5):
            with open(get_abs_path(chroma_conf['md5_hex_store']),'a',encoding='utf-8') as f:
                f.write(md5+'\n')
       #读取文件是pdf文件还是txt文件
        def get_file_document(read_path :str):
            if read_path.endswith('pdf'):
                return pdf_loader(read_path)
            if read_path.endswith('txt'):
                return txt_loader(read_path)
            return []
        #获取文件夹数据（传入data路径和data类型）
        allow_file_path=listdir_with_allowed_type(
            get_abs_path(chroma_conf['data_path']),
            tuple(chroma_conf['allow_knowledge_file_type'])
        )
        #遍历文件夹数据
        for path in allow_file_path:
            #变成md5的数据
            md5_hex=get_file_md5_hex(path)
            #检查md5数据是否存在
            if check_document(md5_hex):
                logger.debug(f'加载知识库{path}已经存在，跳过')
                continue
            try:
                # 读取文件是pdf文件还是txt文件，否则返回[]
                document=get_file_document(path)
                #如果不存在，那么没有效内容跳过
                if not document:
                    logger.warning(f'加载知识库{path}内没有有效文本内容，跳过')
                    continue
                    #切成分片
                split_document=self.spliter.split_documents(document)
                #判断分片存不存在，不存在跳过
                if not split_document:
                    logger.warning(f'加载知识库{path}分片后没有有效文本内容，跳过')
                    continue

                #将内容存入向量库中
                self.chroma.add_documents(split_document)

                #记录已经处理好文件的md5，防止重复加载
                save_document(md5_hex)
                logger.info(f'加载知识库{path}成功')
            except Exception as e:
                # exc_info为True会记录详细的报错，如果为False仅记录报错信息本身
                logger.error(f'加载知识库{path}加载失败：{str(e)}',exc_info=True)
                continue
if __name__ == '__main__':
    vs=VectorStoreService()
    vs.load_document()
    res=vs.get_retroever()
    res1=res.invoke('机器人能干嘛')
    for r in res1:
        print(r)