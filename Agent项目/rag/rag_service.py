"""
RAG总结服务：
核心流程：用户提问 → 向量库检索参考资料 → 拼接上下文 → 大模型生成专业回答
"""
from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from model.factory import ModelSingleton
from utils.logger_handler import logger


class RagSummarizeService:
    """RAG 问答总结服务（单例模式）"""
    _instance = None

    def __new__(cls):
        # 单例：全局仅一个RAG服务实例，避免重复加载
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_rag_service()
        return cls._instance

    def _init_rag_service(self):
        """私有化初始化（单例专用）"""
        # 1. 初始化向量库检索器
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()

        # 2. 初始化提示词模板
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)

        # 3. 初始化大模型 + 输出解析器
        self.model = ModelSingleton.get_chat_model()
        self.output_parser = StrOutputParser()

        # 4. 构建 LCEL 链式调用
        self.rag_chain = self._build_chain()
        logger.info("[RAG总结服务] 初始化完成，就绪！")

    def _build_chain(self):
        """构建RAG链式调用"""
        return self.prompt_template | self.model | self.output_parser

    def retrieve_documents(self, query: str) -> List[Document]:
        """
        从向量库检索相关文档
        :param query: 用户问题
        :return: 匹配的文档列表
        """
        try:
            docs = self.retriever.invoke(query)
            logger.info(f"[RAG检索] 问题：{query}，检索到 {len(docs)} 条参考资料")
            return docs
        except Exception as e:
            logger.error(f"[RAG检索] 失败：{str(e)}", exc_info=True)
            return []

    def _build_context(self, docs: List[Document]) -> str:
        """极简拼接上下文（优化冗余代码）"""
        if not docs:
            return "未找到相关参考资料"

        context_list = []
        # 简化计数器：使用enumerate替代手动count
        for i, doc in enumerate(docs, 1):
            context_list.append(f"[参考资料{i}]\n内容：{doc.page_content}\n")
        return "\n".join(context_list)

    def generate_answer(self, query: str) -> str:
        """
        对外核心接口：RAG生成回答
        :param query: 用户问题
        :return: 大模型基于知识库生成的答案
        """
        # 1. 检索文档
        context_docs = self.retrieve_documents(query)
        # 2. 拼接上下文
        context = self._build_context(context_docs)
        # 3. 调用大模型生成
        try:
            answer = self.rag_chain.invoke({
                "input": query,
                "context": context
            })
            logger.info("[RAG生成] 回答完成")
            return answer
        except Exception as e:
            logger.error(f"[RAG生成] 失败：{str(e)}", exc_info=True)
            return "生成回答失败，请稍后重试"


# 测试入口
if __name__ == "__main__":
    rag_service = RagSummarizeService()
    user_query = "小户型适合哪种扫地机器人"
    result = rag_service.generate_answer(user_query)

    print("\n" + "="*50)
    print("用户问题：", user_query)
    print("="*50)
    print("AI回答：\n", result)