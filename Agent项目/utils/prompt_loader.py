from utils.config_handler import prompts_config
from utils.Path_tool import get_abs_path
from utils.logger_handler import logger

def load_prompt(prompt_key: str, prompt_desc: str) -> str:
    """
    通用提示词加载函数（修复所有bug，精简代码）
    :param prompt_key: 配置文件中的key（main_prompt_path等）
    :param prompt_desc: 提示词描述（日志用）
    :return: 提示词文本内容
    """
    # 1. 读取配置路径
    try:
        prompt_path = get_abs_path(prompts_config[prompt_key])
    except KeyError as e:
        logger.error(f"[加载提示词] 配置文件缺少配置项：{prompt_key}")
        raise e

    # 2. 读取文件内容（自动关闭文件，返回文本）
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        logger.info(f"[加载提示词] 成功加载 {prompt_desc}：{prompt_path}")
        return content
    except Exception as e:
        logger.error(f"[加载提示词] 加载 {prompt_desc} 失败：{str(e)}")
        raise e

# 对外提供三个专用函数（保持原有调用方式不变）
def load_system_prompts() -> str:
    """加载主系统提示词"""
    return load_prompt("main_prompt_path", "主系统提示词")

def load_rag_prompts() -> str:
    """加载RAG总结提示词"""
    return load_prompt("rag_summarize_prompt_path", "RAG总结提示词")

def load_report_prompts() -> str:
    """加载报告生成提示词"""
    return load_prompt("report_prompt_path", "报告生成提示词")

if __name__ == "__main__":
    # 测试：直接打印提示词文本内容
    print("="*50)
    print("系统提示词内容：")
    print(load_system_prompts())
    print("="*50)