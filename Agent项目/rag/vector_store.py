import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
from typing import List
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from utils.config_handler import chroma_config, get_abs_path
from utils.file_handler import txt_loader, pdf_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger
from model.factory import ModelSingleton


class VectorStoreService:
    # 单例模式：全局只创建一个向量库实例
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_service()
        return cls._instance

    def _init_service(self):
        """私有化初始化（单例专用）"""
        # 自动创建所有必需文件夹
        self._auto_create_dirs()

        # 1. 初始化模型（单例，不重复创建）
        self.embedding_model = ModelSingleton.get_embedding_model()

        # 2. 初始化向量库
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"],
            embedding_function=self.embedding_model,
            persist_directory=get_abs_path(chroma_config["persist_directory"]),
        )

        # 3. 初始化文本分割器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separator"],
            length_function=len,
        )

        # 4. 初始化配置参数
        self.data_path = get_abs_path(chroma_config["data_path"])
        self.md5_path = get_abs_path(chroma_config["md5_hex_store"])
        self.allow_types = tuple(f".{t}" for t in chroma_config["allow_knowledge_file_type"])

        logger.info("[向量库服务] 初始化完成，就绪！")

    def _auto_create_dirs(self):
        """自动创建data/chroma_db文件夹，避免手动创建"""
        dirs = [
            get_abs_path(chroma_config["data_path"]),
            get_abs_path(chroma_config["persist_directory"])
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def get_retriever(self):
        """获取RAG检索器"""
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})

    def _check_md5_exists(self, md5_value: str) -> bool:
        """MD5去重：检查文件是否已入库"""
        if not os.path.exists(self.md5_path):
            with open(self.md5_path, "w", encoding="utf-8"):
                pass
            return False

        with open(self.md5_path, "r", encoding="utf-8") as f:
            return md5_value.strip() in f.read().splitlines()

    def _save_md5(self, md5_value: str):
        """保存已入库文件MD5"""
        with open(self.md5_path, "a", encoding="utf-8") as f:
            f.write(f"{md5_value}\n")

    def _load_file_documents(self, file_path: str) -> List[Document]:
        """根据文件类型自动加载文档"""
        try:
            if file_path.endswith(".txt"):
                return txt_loader(file_path)
            if file_path.endswith(".pdf"):
                return pdf_loader(file_path)
        except Exception as e:
            logger.error(f"[文件加载] 失败: {file_path}, 错误: {str(e)}")
        return []

    def load_knowledge_base(self):
        """批量加载知识库文件"""
        logger.info("【加载知识库】开始初始化本地知识库...")

        allowed_files = listdir_with_allowed_type(self.data_path, self.allow_types)
        if not allowed_files:
            logger.warning("【加载知识库】未找到任何可加载的文件")
            return

        for file_path in allowed_files:
            file_md5 = get_file_md5_hex(file_path)
            if not file_md5 or self._check_md5_exists(file_md5):
                logger.info(f"【加载知识库】已存在，跳过: {file_path}")
                continue

            try:
                documents = self._load_file_documents(file_path)
                if not documents:
                    logger.warning(f"【加载知识库】无内容，跳过: {file_path}")
                    continue

                split_docs = self.splitter.split_documents(documents)
                self.vector_store.add_documents(split_docs)
                self._save_md5(file_md5)

                logger.info(f"【加载知识库】加载成功: {file_path}")

            except Exception as e:
                logger.error(f"【加载知识库】加载失败: {file_path}", exc_info=True)


# ===================== 测试入口 =====================
if __name__ == "__main__":
    # 单例模式，多次调用也只初始化一次
    vs = VectorStoreService()
    vs.load_knowledge_base()

    # 检索测试
    retriever = vs.get_retriever()
    print("\n" + "=" * 50)
    print("【检索测试结果】")
    print("=" * 50)

    results = retriever.invoke("迷路")
    for res in results:
        print(res.page_content)
        print("-" * 20)