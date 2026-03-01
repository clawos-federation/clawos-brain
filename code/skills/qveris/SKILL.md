# QVeris 金融数据 Skill

---
name: qveris
description: QVeris 金融数据接入 Skill，提供实时市场数据、行情分析、风险评估能力，支持 10,000+ 工具统一调用
license: MIT
compatibility: opencode
metadata:
  category: finance
  version: 1.0.0
  provider: qveris-ai
  features:
    - market-data
    - real-time-quotes
    - historical-data
    - risk-analysis
    - portfolio-analysis
  data_coverage:
    - US-stocks
    - A-shares (待验证)
    - HK-stocks (待验证)
    - Crypto
---

## 功能概述

QVeris 是一个 AI Agent 工具操作系统，提供 10,000+ 工具的统一调用接口。本 Skill 封装其金融数据能力，用于：

- 实时市场数据查询
- 历史行情分析
- 风险评估报告
- 投资组合分析

## 配置

### 环境变量

```bash
# API 密钥配置
export QVERIS_API_KEY="your-api-key-here"
export QVERIS_ENDPOINT="https://qveris.ai/api/v1"
```

### MCP 配置（推荐）

```json
{
  "mcpServers": {
    "qveris": {
      "command": "npx",
      "args": ["@qverisai/mcp"],
      "env": {
        "QVERIS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Python SDK 安装

```bash
pip install qveris
```

## 命令模板

### 1. 搜索金融工具

```bash
# 搜索股票价格相关工具
curl -X POST "https://qveris.ai/api/v1/search" \
  -H "Authorization: Bearer $QVERIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "stock price API A股 中国股票",
    "limit": 10
  }'
```

### 2. 执行工具调用

```bash
# 执行股票查询工具
curl -X POST "https://qveris.ai/api/v1/tools/execute?tool_id={tool_id}" \
  -H "Authorization: Bearer $QVERIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "search_id": "{search_id}",
    "parameters": {
      "symbol": "000001.SZ",
      "market": "cn"
    }
  }'
```

### 3. Python SDK 调用

```python
import asyncio
from qveris import Agent, Message

async def get_stock_data(symbol: str):
    """获取股票数据"""
    agent = Agent()
    messages = [
        Message(
            role="user", 
            content=f"Search for a stock price tool and get the current price of {symbol}"
        )
    ]
    
    result = []
    async for event in agent.run(messages):
        if event.type == "content" and event.content:
            result.append(event.content)
    
    return "".join(result)

# 使用示例
asyncio.run(get_stock_data("000001.SZ"))
```

## Alpha 集成场景

### alpha-hunter 数据采集

```bash
# 采集 A 股实时行情
curl -X POST "$QVERIS_ENDPOINT/search" \
  -H "Authorization: Bearer $QVERIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "A股实时行情 涨跌幅 成交量", "limit": 5}'
```

### alpha-strategist 策略分析

```bash
# 获取板块热度数据
curl -X POST "$QVERIS_ENDPOINT/search" \
  -H "Authorization: Bearer $QVERIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "sector analysis industry heat map", "limit": 5}'
```

### risk-controller 风控评估

```bash
# 市场风险评估
curl -X POST "$QVERIS_ENDPOINT/search" \
  -H "Authorization: Bearer $QVERIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "market risk volatility VIX", "limit": 5}'
```

## 输出格式

### 标准响应

```json
{
  "success": true,
  "timestamp": "2026-02-27T10:00:00Z",
  "source": "qveris",
  "search_id": "search_xxx",
  "tools": [
    {
      "tool_id": "tool_xxx",
      "name": "Stock Price API",
      "description": "Get real-time stock prices",
      "parameters": {
        "symbol": {"type": "string", "required": true},
        "market": {"type": "string", "default": "us"}
      }
    }
  ]
}
```

### 执行结果

```json
{
  "success": true,
  "tool_id": "tool_xxx",
  "execution_time_ms": 250,
  "result": {
    "symbol": "000001.SZ",
    "name": "平安银行",
    "price": 12.50,
    "change": 0.25,
    "change_percent": 2.04,
    "volume": 125000000,
    "turnover_rate": 1.5,
    "timestamp": "2026-02-27T10:00:00Z"
  }
}
```

## 错误处理

| 错误代码 | 说明 | 处理方式 |
|---------|------|---------|
| 401 | API Key 无效 | 检查 QVERIS_API_KEY 配置 |
| 429 | 请求频率超限 | 等待 60 秒后重试，或升级 Pro |
| 404 | 工具不存在 | 重新搜索工具 |
| 500 | 服务端错误 | 重试 3 次，间隔 5 秒 |

### 错误重试策略

```python
import time
from functools import wraps

def retry_on_error(max_retries=3, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator
```

## 与其他 Skills 的关系

| Skill | 关系 | 协作方式 |
|-------|------|---------|
| **alpha-bridge** | 协同 | 将 QVeris 数据转发到 Alpha 系统 |
| **blackboard** | 下游 | 将分析结果写入共享黑板 |
| **error-escalation** | 异常 | 上报 QVeris API 错误 |

## 权限需求

| 权限 | 命令 | 风险等级 | 说明 |
|------|------|---------|------|
| 网络访问 | curl | 中 | 访问 qveris.ai API |
| 环境变量 | export | 低 | 存储 API Key |
| 进程执行 | npx | 中 | 运行 MCP Server |

## 定价参考

| 计划 | 价格 | 额度 | 限制 |
|------|------|------|------|
| Free | $0 | 1,000 Credits | 10 req/min |
| Pro | $19/月 | 10,000 Credits | 100 req/min |
| Scale | 按需 | 充值 | $1 起充 |

## 相关链接

| 资源 | URL |
|------|-----|
| 官网 | https://qveris.ai |
| 文档 | https://qveris.ai/docs |
| GitHub | https://github.com/QVerisAI/QVerisAI |
| Python SDK | https://github.com/QVerisAI/sdk-python |
| 定价 | https://qveris.ai/pricing |
| Discord | https://discord.gg/Rehbf3Wz |

## 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-02-27 | 1.0.0 | 初始创建，支持基础金融数据查询 |
