"""
React 智能体主类
功能：集成工具、中间件、模型，实现流式对话 + 报告生成双场景
核心流程：用户提问 → 智能体规划 → 调用工具 → 动态提示词 → 流式输出
"""
from typing import Generator
from model.factory import ModelSingleton
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (
    rag_summarize, get_weather, get_user_location,
    get_user_id, get_current_month, fetch_external_data,
    fill_context_for_report
)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from langchain.agents import create_agent
from utils.logger_handler import logger


class ReactAgent:
    def __init__(self):
        """初始化智能体：加载模型、注册工具、绑定中间件"""
        logger.info("[ReactAgent] 开始初始化智能体...")

        # 1. 获取单例大模型（避免重复加载）
        self.llm = ModelSingleton.get_chat_model()

        # 2. 创建 LangGraph React 智能体
        self.agent = create_agent(
            model=self.llm,
            system_prompt=load_system_prompts(),
            # 注册所有工具（包含报告触发工具）
            tools=[
                rag_summarize,
                get_weather,
                get_user_location,
                get_user_id,
                get_current_month,
                fetch_external_data,
                fill_context_for_report
            ],
            # 绑定三大中间件：监控、日志、动态提示词
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )
        logger.info("[ReactAgent] 智能体初始化完成！")

    def execute_stream(self, query: str, report_mode: bool = False) -> Generator[str, None, None]:
        """
        流式执行智能体（支持前端/控制台逐字输出）
        :param query: 用户输入的问题
        :param report_mode: 报告生成模式开关，自动切换专用提示词
        :return: 流式生成的回答文本
        """
        # 构造智能体输入格式
        input_data = {
            "messages": [{"role": "user", "content": query}]
        }

        try:
            # 流式调用智能体（传递上下文，控制提示词切换）
            for chunk in self.agent.stream(
                input=input_data,
                stream_mode="values",
                context={"report": report_mode}
            ):
                messages = chunk.get("messages", [])
                if not messages:
                    continue

                # 获取最新一条消息，过滤无效内容
                latest_msg = messages[-1]
                content = latest_msg.content.strip()
                if content:
                    yield content + "\n"

        except Exception as e:
            logger.error(f"[智能体执行异常] {str(e)}", exc_info=True)
            yield "智能体服务异常，请稍后重试\n"


# ===================== 测试入口 =====================
if __name__ == '__main__':
    # 初始化智能体
    agent = ReactAgent()

    # ========== 测试场景1：生成扫地机器人使用报告 ==========
    print("=" * 50)
    print("开始生成用户使用报告...\n")
    for content in agent.execute_stream(
        query="生成我的扫地机器人使用报告",
        report_mode=True  # 开启报告模式
    ):
        print(content, end="", flush=True)

    # ========== 测试场景2：普通知识库问答 ==========
    # print("\n" + "=" * 50)
    # print("普通问答测试：\n")
    # for content in agent.execute_stream(
    #     query="小户型适合哪种扫地机器人",
    #     report_mode=False
    # ):
    #     print(content, end="", flush=True)