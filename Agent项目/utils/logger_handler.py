import datetime
import logging
import os

from utils.Path_tool import get_abs_path

# 日志保存的根目录
LOG_ROOT = get_abs_path("logs")
# 确保日志文件夹存在（不存在则创建）
os.makedirs(LOG_ROOT, exist_ok=True)

# 日志的格式配置（修复拼写错误：asctime）
DEFAULT_LOG_FORMAT = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
)

def get_logger(
        name : str = "agent",
        console_level : int = logging.INFO,
        file_level : int = logging.DEBUG,
        log_file = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加处理器（核心优化，防止日志重复打印）
    if logger.handlers:
        return logger

    # 控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)

    # 文件Handler（修复datetime调用错误）
    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)

    return logger

# 快捷获取日志器（全局单例，避免重复创建）
logger = get_logger()

if __name__ == '__main__':
    logger.debug('这是debug级别的日志')
    logger.info('这是info级别的日志')