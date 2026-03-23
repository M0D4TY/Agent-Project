import yaml
from typing import Dict, Any
from utils.Path_tool import get_abs_path

def load_config(config_name: str) -> Dict[str, Any]:
    """
    通用配置加载函数（重构冗余代码）
    :param config_name: 配置文件名（不含.yml）
    :return: 配置字典
    """
    config_path = get_abs_path(f"config/{config_name}.yml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        raise Exception(f"配置文件不存在：{config_path}")
    except yaml.YAMLError:
        raise Exception(f"YAML 格式错误：{config_path}")

# 统一加载所有配置
rag_config = load_config("rag")
chroma_config = load_config("chroma")
prompts_config = load_config("prompts")
agent_config = load_config("agent")

if __name__ == '__main__':
    print("当前对话模型：", rag_config["chat_model_name"])
    print("当前嵌入模型：", rag_config["embedding_model_name"])