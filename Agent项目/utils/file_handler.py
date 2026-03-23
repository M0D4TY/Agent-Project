import os
import hashlib

from typing import List, Tuple
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from utils.logger_handler import logger

def get_file_md5_hex(filepath: str) -> str | None:
    """
    计算文件的MD5十六进制字符串（用于文件去重/校验）
    :param filepath: 文件绝对路径
    :return: MD5字符串 / None（失败）
    """
    if not os.path.exists(filepath):
        logger.error(f"[MD5计算] 文件不存在：{filepath}")
        return

    if not os.path.isfile(filepath):
        logger.error(f"[MD5计算] 不是有效文件：{filepath}")
        return

    md5_obj = hashlib.md5()
    chunk_size = 4096
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        md5_hex = md5_obj.hexdigest()
        logger.info(f"[MD5计算] 成功：{filepath} | {md5_hex}")
        return md5_hex
    except Exception as e:
        logger.error(f"[MD5计算] 失败：{filepath} | 错误：{str(e)}")
        return None

def listdir_with_allowed_type(path: str, allowed_type: Tuple[str]) -> Tuple[str]:
    """
    获取文件夹中指定后缀的文件（返回完整绝对路径，避免路径错误）
    :param path: 文件夹路径
    :param allowed_type: 允许的文件后缀，如 ('.pdf', '.txt')
    :return: 符合条件的文件完整路径元组
    """
    files_full_path = []

    if not os.path.isdir(path):
        logger.error(f"[文件筛选] 不是有效文件夹：{path}")
        return tuple(files_full_path)

    for filename in os.listdir(path):
        # 拼接完整路径
        full_path = os.path.join(path, filename)
        # 只筛选文件，排除文件夹
        if os.path.isfile(full_path) and filename.endswith(allowed_type):
            files_full_path.append(full_path)

    logger.info(f"[文件筛选] 路径：{path} | 符合条件文件数：{len(files_full_path)}")
    return tuple(files_full_path)

def pdf_loader(filepath: str, password: str = None) -> List[Document]:
    """
    加载PDF文件，转换为Document列表（带异常处理+密码支持）
    :param filepath: PDF文件路径
    :param password: PDF密码（可选）
    :return: Document列表
    """
    try:
        loader = PyPDFLoader(filepath)
        # 修复：正确传入密码参数
        if password:
            docs = loader.load(password=password)
        else:
            docs = loader.load()
        logger.info(f"[PDF加载] 成功：{filepath} | 页数：{len(docs)}")
        return docs
    except Exception as e:
        logger.error(f"[PDF加载] 失败：{filepath} | 错误：{str(e)}")
        return []

def txt_loader(filepath: str, encoding: str = "utf-8") -> List[Document]:
    """
    加载TXT文件，转换为Document列表（指定编码，解决中文乱码）
    :param filepath: TXT文件路径
    :param encoding: 文件编码
    :return: Document列表
    """
    try:
        # 修复：指定编码，兼容中文
        loader = TextLoader(filepath, encoding=encoding)
        docs = loader.load()
        logger.info(f"[TXT加载] 成功：{filepath}")
        return docs
    except Exception as e:
        logger.error(f"[TXT加载] 失败：{filepath} | 错误：{str(e)}")
        return []