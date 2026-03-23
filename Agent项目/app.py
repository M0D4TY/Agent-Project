import streamlit as st
from agent.react_agent import ReactAgent

# 页面配置（必须放在最顶部）
st.set_page_config(
    page_title="智扫通机器人智能客服",
    layout="wide"
)

# 标题
st.title("🤖 智扫通机器人智能客服")
st.divider()

# 初始化会话状态（单例智能体，避免重复初始化）
if "agent" not in st.session_state:
    with st.spinner("智能体初始化中..."):
        st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

# 渲染历史消息
for message in st.session_state["message"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 用户输入
prompt = st.chat_input("请输入你想咨询的问题...")

if prompt:
    # 1. 展示用户消息
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    # 2. 自动识别报告模式（输入包含"报告"自动开启）
    report_mode = "报告" in prompt

    # 3. 流式响应
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            # 调用智能体流式输出
            res_stream = st.session_state["agent"].execute_stream(
                query=prompt,
                report_mode=report_mode  # 自动传递报告模式
            )
            # 流式输出（原生流畅，无卡顿）
            response = st.write_stream(res_stream)

    # 4. 保存助手消息
    st.session_state["message"].append({"role": "assistant", "content": response})
    st.rerun()