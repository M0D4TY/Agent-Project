import os
import random
from typing import Dict, Any

from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService
from utils.config_handler import agent_config, get_abs_path
from utils.logger_handler import logger

# ===================== 全局初始化 =====================
# RAG总结服务单例
rag_service = RagSummarizeService()
# 模拟用户ID/月份数据
USER_IDS = [f"100{i:02d}" for i in range(1, 11)]
MONTH_ARR = [f"2025-{i:02d}" for i in range(1, 13)]
# 外部数据存储（全局单例，仅加载一次）
external_data: Dict[str, Dict[str, Dict[str, str]]] = {}


# ===================== RAG 核心检索工具 =====================
@tool(description="从扫地机器人知识库检索资料并生成总结回答")
def rag_summarize(query: str) -> str:
    """RAG问答工具：基于本地知识库回答用户问题"""
    return rag_service.generate_answer(query)


# ===================== 模拟数据工具 =====================
@tool(description="获取指定城市的实时天气信息")
def get_weather(city: str) -> str:
    return f"城市{city}天气为晴天，气温26℃，湿度50%，南风1级，AQI21，6小时内无降雨"


@tool(description="获取用户当前所在的城市")
def get_user_location() -> str:
    return random.choice(["深圳", "合肥", "杭州"])


@tool(description="随机获取一个用户ID")
def get_user_id() -> str:
    return random.choice(USER_IDS)


@tool(description="随机获取2025年的月份数据")
def get_current_month() -> str:
    return random.choice(MONTH_ARR)


# ===================== 外部CSV数据加载工具 =====================
def generate_external_data() -> None:
    """加载外部CSV用户使用数据到内存（全局仅执行一次）"""
    global external_data
    if external_data:
        return

    try:
        external_data_path = get_abs_path(agent_config["external_data_path"])
        logger.info(f"[外部数据] 加载路径：{external_data_path}")

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件不存在：{external_data_path}")

        # 解析CSV文件
        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                line = line.strip()
                if not line:
                    continue
                arr = line.split(",")
                # 清洗数据
                user_id = arr[0].replace('"', "").strip()
                feature = arr[1].replace('"', "").strip()
                efficiency = arr[2].replace('"', "").strip()
                consumables = arr[3].replace('"', "").strip()
                comparison = arr[4].replace('"', "").strip()
                time = arr[5].replace('"', "").strip()

                # 构建内存字典
                if user_id not in external_data:
                    external_data[user_id] = {}
                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison
                }
        logger.info(f"[外部数据] 加载完成，共 {len(external_data)} 个用户数据")

    except Exception as e:
        logger.error(f"[外部数据] 加载失败：{str(e)}", exc_info=True)
        external_data = {}


@tool(description="查询用户指定月份的扫地机器人使用记录，返回字符串格式")
def fetch_external_data(user_id: str, month: str) -> str:
    """查询用户月度使用数据，无数据返回空字符串"""
    generate_external_data()

    try:
        data = external_data[user_id][month]
        return (
            f"用户{user_id}{month}使用记录：\n"
            f"设备特征：{data['特征']}\n"
            f"清洁效率：{data['效率']}\n"
            f"耗材状态：{data['耗材']}\n"
            f"对比数据：{data['对比']}"
        )
    except KeyError:
        logger.warning(f"[外部数据] 未找到用户：{user_id} 在 {month} 的记录")
        return ""


# ===================== 报告模式触发工具=====================
@tool(description="触发报告生成模式，无入参无实际返回值")
def fill_context_for_report() -> str:
    """专门用于中间件触发report上下文标记的工具"""
    return "已激活报告生成模式"


# ===================== 测试入口 =====================
if __name__ == "__main__":
    # 测试RAG工具
    print("=" * 50)
    print("RAG工具测试：")
    print(rag_summarize.invoke("小户型适合哪种扫地机器人"))

    # 测试天气工具
    print("\n天气工具测试：")
    print(get_weather.invoke("深圳"))

    # 测试用户数据工具
    print("\n外部数据工具测试：")
    print(fetch_external_data.invoke("1001", "2025-01"))

    # 测试报告触发工具
    print("\n报告模式工具测试：")
    print(fill_context_for_report.invoke({}))