from abc import ABC, abstractmethod
from typing import Optional
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from utils.config_handler import rag_config
from utils.logger_handler import logger

# 抽象基类：模型工厂
class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self) -> BaseChatModel:
        logger.info("[模型工厂] 初始化本地对话模型: %s", rag_config["chat_model_name"])
        return ChatOllama(
            base_url=rag_config.get("base_url", "http://localhost:11434"),
            model=rag_config["chat_model_name"],
            temperature=0.1
        )

# 嵌入模型工厂（向量化）
class EmbeddingModelFactory(BaseModelFactory):
    def generator(self) -> Embeddings:
        logger.info("[模型工厂] 初始化本地嵌入模型: %s", rag_config["embedding_model_name"])
        return OllamaEmbeddings(
            base_url=rag_config.get("base_url", "http://localhost:11434"),
            model=rag_config["embedding_model_name"]
        )

# ===================== 单例模式（全局唯一，避免重复初始化） =====================
class ModelSingleton:
    _chat_instance = None
    _embedding_instance = None

    @classmethod
    def get_chat_model(cls):
        if cls._chat_instance is None:
            cls._chat_instance = ChatModelFactory().generator()
        return cls._chat_instance

    @classmethod
    def get_embedding_model(cls):
        if cls._embedding_instance is None:
            cls._embedding_instance = EmbeddingModelFactory().generator()
        return cls._embedding_instance