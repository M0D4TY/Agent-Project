# Agent-Project 智能问答代理系统

基于 Python 和 LangChain 构建的智能问答代理系统，专注于扫地机器人领域的知识问答服务。

## ✨ 功能特点

- 🤖 **智能对话**: 基于本地 LLM 的智能问答助手
- 📊 **报告生成**: 自动生成个性化使用报告
- 🔍 **RAG 检索**: 使用向量数据库实现知识检索
- 🛠 **多工具集成**: 支持天气查询、外部数据抓取等多种工具
- 📚 **领域知识库**: 内置扫地机器人专业知识数据
- 🌐 **流式输出**: 实时流式响应，提供流畅交互体验

## 🛠 技术栈

- **AI 框架**: LangChain + LangGraph
- **大语言模型**: 支持多种 LLM（需本地部署）
- **向量数据库**: ChromaDB
- **嵌入模型**: sentence-transformers
- **后端**: Python
- **配置管理**: YAML

## 📋 环境要求

- Python 3.10+
- 4GB+ RAM
- 本地 LLM 服务（如 Ollama）

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/M0D4TY/Agent-Project.git
cd Agent-Project
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 LLM

确保已安装并运行本地 LLM 服务（如 Ollama）

### 4. 运行项目

```bash
cd Agent项目
python main.py
```

## 📁 项目结构

```
Agent-Project/
├── Agent项目/
│   ├── agent/                 # Agent 核心代码
│   │   ├── react_agent.py    # React Agent 实现
│   │   └── tools/            # 工具集
│   ├── rag/                  # RAG 服务
│   │   ├── rag_service.py   # RAG 服务实现
│   │   └── vector_store.py  # 向量存储
│   ├── config/               # 配置文件
│   │   ├── agent.yml        # Agent 配置
│   │   ├── chroma.yml       # ChromaDB 配置
│   │   ├── prompts.yml     # 提示词配置
│   │   └── rag.yml         # RAG 配置
│   ├── data/                 # 知识数据
│   │   ├── external/        # 外部数据
│   │   ├── 扫地机器人100问.txt
│   │   ├── 选购指南.txt
│   │   ├── 故障排除.txt
│   │   └── 维护保养.txt
│   ├── prompts/             # 提示词模板
│   ├── utils/               # 工具类
│   └── main.py              # 程序入口
├── tests/                   # 测试文件
├── requirements.txt
└── README.md
```

## 💬 使用示例

### 普通问答

```
用户: 小户型适合哪种扫地机器人？
Agent: 根据您的小户型情况，建议选择...
```

### 报告生成

```
用户: 生成我的扫地机器人使用报告
Agent: (生成个性化报告...)
```

## ⚙️ 配置说明

主要配置文件位于 `Agent项目/config/` 目录：

- `agent.yml` - Agent 基础配置
- `chroma.yml` - 向量数据库配置
- `prompts.yml` - 提示词配置
- `rag.yml` - RAG 系统配置

## 🔧 中间件功能

项目实现了三个中间件：
1. **工具调用监控** - 记录工具执行日志
2. **模型调用日志** - 追踪 LLM 调用
3. **提示词动态切换** - 根据场景自动切换提示词策略

## 📄 许可证

MIT License
启动：
cd D:\Pycharm\Agent项目
streamlit run app.py
## 📧 联系方式

如有问题，请提交 Issue
# Agent-Project

