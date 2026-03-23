from typing import Callable, Optional
from utils.prompt_loader import load_system_prompts, load_report_prompts
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger


@wrap_tool_call
def monitor_tool(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    """
    工具调用监控中间件
    功能：日志记录工具执行信息、触发报告生成模式上下文
    """
    # 工具执行日志
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call["args"]
    logger.info(f"[工具监控] 执行工具：{tool_name}")
    logger.info(f"[工具监控] 传入参数：{tool_args}")

    try:
        # 执行原始工具逻辑
        result = handler(request)
        logger.info(f"[工具监控] 工具 {tool_name} 调用成功")

        # 触发报告生成：设置上下文标记，动态切换提示词
        if tool_name == "fill_context_for_report":
            request.runtime.context["report"] = True
            logger.info("[工具监控] 已激活报告生成模式上下文")

        return result

    except Exception as e:
        logger.error(f"[工具监控] 工具 {tool_name} 调用失败：{str(e)}", exc_info=True)
        raise e


@before_model
def log_before_model(
        state: AgentState,
        runtime: Runtime,
) -> Optional[None]:
    """
    模型调用前置中间件
    功能：打印模型调用前的状态日志，便于调试
    """
    msg_count = len(state["messages"])
    logger.info(f"[模型前置] 即将调用大模型，当前消息总数：{msg_count}")

    # 安全获取最后一条消息，避免空列表报错
    if msg_count > 0:
        last_msg = state["messages"][-1]
        msg_type = last_msg.__class__.__name__
        msg_content = last_msg.content.strip()
        logger.debug(f"[模型前置] 最后消息 | {msg_type} | {msg_content}")

    return None


@dynamic_prompt
def report_prompt_switch(request: ModelRequest) -> str:
    """
    动态提示词切换中间件
    逻辑：根据 runtime 上下文，自动切换 常规对话 / 报告生成 提示词
    """
    # 安全获取上下文标记，默认关闭报告模式
    is_report_mode = request.runtime.context.get("report", False)

    if is_report_mode:
        logger.info("[动态提示词] 切换为 → 报告生成专用提示词")
        return load_report_prompts()

    logger.info("[动态提示词] 切换为 → 常规对话系统提示词")
    return load_system_prompts()