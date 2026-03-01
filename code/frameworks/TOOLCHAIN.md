# TOOL-CHAIN.md - ClawOS 工具链式调用框架

**版本**: 1.0.0
**更新时间**: 2026-02-25
**状态**: ✅ 已定义

---

## 概念

### 单工具调用 vs 链式调用

**单工具调用** (当前):
```
Task → Tool A → Result
```

**链式调用** (目标):
```
Task → Tool A → Tool B → Tool C → Final Result
         ↓         ↓         ↓
      Result A  Result B  Result C
```

### 为什么需要链式调用？

| 场景 | 单工具 | 链式调用 |
|------|--------|----------|
| 复杂任务 | 需要多次交互 | 一次完成 |
| 数据转换 | 手动转换 | 自动传递 |
| 错误处理 | 分散处理 | 统一处理 |
| 可追溯性 | 难以追踪 | 完整链路 |

---

## 链式调用定义

### 基础结构

```yaml
name: tool-chain-name
description: 链式调用描述
version: 1.0.0

steps:
  - id: step-1
    tool: tool-name-a
    params:
      param1: "${input.value1}"
      param2: "static-value"
    output:
      as: result_a
      select: "$.data.items"

  - id: step-2
    tool: tool-name-b
    params:
      input: "${steps.step-1.output}"
      options:
        mode: "enhanced"
    output:
      as: result_b
    condition: "${steps.step-1.output.count > 0}"

  - id: step-3
    tool: tool-name-c
    params:
      data: "${steps.step-2.output}"
    output:
      as: final_result

error_handling:
  strategy: "fallback|retry|abort"
  fallback:
    - tool: backup-tool
      params: {}

metadata:
  author: "clawos"
  tags: ["automation", "productivity"]
```

### 参数传递

**变量引用语法**:
| 语法 | 说明 | 示例 |
|------|------|------|
| `${input.x}` | 输入参数 | `${input.query}` |
| `${steps.a.output}` | 步骤输出 | `${steps.search.output}` |
| `${steps.a.output.x}` | 步骤输出字段 | `${steps.search.output.items}` |
| `${env.VAR}` | 环境变量 | `${env.HOME}` |
| `${context.x}` | 上下文变量 | `${context.user_id}` |

**JSONPath 选择**:
```yaml
output:
  select: "$.data.items[*].name"  # 提取所有名称
```

---

## 示例：研究 + 总结 + 存储

```yaml
name: research-summarize-store
description: 研究主题，总结结果，存储到记忆

input:
  topic: string        # 研究主题
  depth: number=3      # 研究深度
  store_location: string="memory"

steps:
  - id: search
    tool: web_search
    params:
      query: "${input.topic}"
      count: 10
    output:
      as: search_results
      select: "$.results[*]"

  - id: fetch
    tool: web_fetch
    params:
      url: "${steps.search.output[0].url}"
    output:
      as: page_content
    condition: "${steps.search.output.size > 0}"

  - id: summarize
    tool: llm_summarize
    params:
      content: "${steps.fetch.output}"
      style: "bullet-points"
      max_length: 500
    output:
      as: summary

  - id: store
    tool: memory_store
    params:
      content: "${steps.summarize.output}"
      metadata:
        topic: "${input.topic}"
        sources: "${steps.search.output[*].url}"
        type: "research"
    output:
      as: memory_id

output:
  summary: "${steps.summarize.output}"
  memory_id: "${steps.store.output}"
  sources_count: "${steps.search.output.size}"

error_handling:
  strategy: "fallback"
  fallback:
    - condition: "${steps.search.error}"
      tool: memory_recall
      params:
        query: "${input.topic}"
```

---

## 执行引擎

### 执行流程

```
1. 解析链定义
   ↓
2. 验证参数和依赖
   ↓
3. 构建执行图 (DAG)
   ↓
4. 拓扑排序
   ↓
5. 并行/串行执行
   ↓
6. 收集结果
   ↓
7. 处理错误
   ↓
8. 返回最终结果
```

### 执行器实现

```python
class ToolChainExecutor:
    def __init__(self, tools_registry):
        self.tools = tools_registry
        self.context = {}

    def execute(self, chain_definition, input_params):
        """执行工具链"""
        # 1. 解析和验证
        chain = self._parse_chain(chain_definition)
        self._validate(chain, input_params)

        # 2. 构建执行图
        dag = self._build_dag(chain.steps)

        # 3. 执行步骤
        results = {}
        for step in self._topological_sort(dag):
            try:
                # 检查条件
                if not self._check_condition(step, results):
                    results[step.id] = {"skipped": True}
                    continue

                # 准备参数
                params = self._resolve_params(step.params, input_params, results)

                # 执行工具
                tool = self.tools.get(step.tool)
                result = tool.execute(**params)

                # 提取输出
                if step.output and step.output.select:
                    result = self._jsonpath_select(result, step.output.select)

                results[step.id] = {"output": result, "success": True}

            except Exception as e:
                # 错误处理
                results[step.id] = {"error": str(e), "success": False}

                if not self._handle_error(step, e, results):
                    raise

        # 4. 构建最终输出
        return self._build_output(chain.output, results)

    def _resolve_params(self, params_template, input_params, step_results):
        """解析参数模板"""
        resolved = {}
        for key, value in params_template.items():
            if isinstance(value, str) and value.startswith("${"):
                # 变量引用
                resolved[key] = self._resolve_variable(value, input_params, step_results)
            elif isinstance(value, dict):
                # 递归解析
                resolved[key] = self._resolve_params(value, input_params, step_results)
            else:
                resolved[key] = value
        return resolved

    def _resolve_variable(self, expr, input_params, step_results):
        """解析变量表达式"""
        # ${input.x} → input_params.x
        # ${steps.a.output} → step_results.a.output
        # ${env.X} → os.environ.X

        inner = expr[2:-1]  # 去掉 ${ }

        if inner.startswith("input."):
            path = inner[6:]
            return self._get_nested(input_params, path)

        elif inner.startswith("steps."):
            parts = inner[6:].split(".")
            step_id = parts[0]
            path = ".".join(parts[1:])
            return self._get_nested(step_results[step_id], path)

        elif inner.startswith("env."):
            return os.environ.get(inner[4:])

        elif inner.startswith("context."):
            return self._get_nested(self.context, inner[8:])

        return expr

    def _check_condition(self, step, results):
        """检查条件"""
        if not step.condition:
            return True

        # 简单条件评估
        condition = step.condition
        condition = self._resolve_variables_in_string(condition, results)

        # 使用安全评估器
        return self._safe_eval(condition)

    def _handle_error(self, step, error, results):
        """处理错误"""
        if not step.error_handling:
            return False

        strategy = step.error_handling.strategy

        if strategy == "retry":
            return self._retry_step(step, results)

        elif strategy == "fallback":
            return self._execute_fallback(step, results)

        elif strategy == "abort":
            return False

        return False
```

---

## 并行执行

### 并行条件

```
Step A → Step B  (A 必须在 B 前完成)
Step A | Step B  (A 和 B 可以并行)
```

### 并行检测

```python
def detect_parallelizable(dag):
    """检测可并行执行的步骤"""
    levels = {}
    for node in dag.nodes:
        # 计算依赖深度
        levels[node] = max(
            [levels[dep] + 1 for dep in dag.predecessors(node)] or [0]
        )

    # 按层级分组
    parallel_groups = {}
    for node, level in levels.items():
        if level not in parallel_groups:
            parallel_groups[level] = []
        parallel_groups[level].append(node)

    return parallel_groups
```

### 并行执行器

```python
class ParallelToolChainExecutor(ToolChainExecutor):
    def execute(self, chain_definition, input_params):
        chain = self._parse_chain(chain_definition)
        dag = self._build_dag(chain.steps)

        # 检测并行组
        parallel_groups = detect_parallelizable(dag)

        results = {}
        for level in sorted(parallel_groups.keys()):
            steps = parallel_groups[level]

            # 并行执行同层级步骤
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(
                        self._execute_step, step, input_params, results
                    ): step for step in steps
                }

                for future in as_completed(futures):
                    step = futures[future]
                    try:
                        results[step.id] = future.result()
                    except Exception as e:
                        results[step.id] = {"error": str(e), "success": False}

        return self._build_output(chain.output, results)
```

---

## 预定义工具链

### 1. 研究链 (research-chain)

```yaml
name: research-chain
description: 搜索 → 抓取 → 总结 → 存储

steps:
  - id: search
    tool: web_search
    params:
      query: "${input.query}"
      count: 5

  - id: fetch_all
    tool: parallel_fetch
    params:
      urls: "${steps.search.output[*].url}"

  - id: summarize
    tool: llm_summarize
    params:
      content: "${steps.fetch_all.output}"
      style: "structured"

  - id: store
    tool: memory_store
    params:
      content: "${steps.summarize.output}"
      type: "research"
```

### 2. 开发链 (dev-chain)

```yaml
name: dev-chain
description: 设计 → 编码 → 测试 → 审查

steps:
  - id: design
    tool: llm_design
    params:
      requirements: "${input.requirements}"

  - id: code
    tool: code_generator
    params:
      design: "${steps.design.output}"
      language: "${input.language}"

  - id: test
    tool: test_runner
    params:
      code: "${steps.code.output}"
      coverage: true

  - id: review
    tool: code_reviewer
    params:
      code: "${steps.code.output}"
      test_results: "${steps.test.output}"

  - id: fix
    tool: code_fixer
    params:
      code: "${steps.code.output}"
      review: "${steps.review.output}"
    condition: "${steps.review.output.issues.size > 0}"
```

### 3. 写作链 (write-chain)

```yaml
name: write-chain
description: 大纲 → 研究 → 写作 → 审核 → 修订

steps:
  - id: outline
    tool: outline_generator
    params:
      topic: "${input.topic}"
      style: "${input.style}"

  - id: research
    tool: research-chain
    params:
      query: "${input.topic}"

  - id: write
    tool: content_writer
    params:
      outline: "${steps.outline.output}"
      research: "${steps.research.output}"

  - id: review
    tool: content_reviewer
    params:
      content: "${steps.write.output}"

  - id: revise
    tool: content_reviser
    params:
      content: "${steps.write.output}"
      feedback: "${steps.review.output}"
    condition: "${steps.review.output.score < 8}"
```

---

## 监控与调试

### 执行日志

```json
{
  "chain_id": "chain-uuid",
  "name": "research-chain",
  "started_at": "2026-02-25T18:50:00+08:00",
  "completed_at": "2026-02-25T18:50:15+08:00",
  "duration_ms": 15000,
  "steps": [
    {
      "id": "search",
      "tool": "web_search",
      "duration_ms": 2000,
      "status": "success",
      "input": {"query": "ClawOS"},
      "output": {"results": [...]}
    },
    {
      "id": "fetch_all",
      "tool": "parallel_fetch",
      "duration_ms": 8000,
      "status": "success",
      "parallel_count": 5
    },
    {
      "id": "summarize",
      "tool": "llm_summarize",
      "duration_ms": 4000,
      "status": "success",
      "tokens_used": 500
    },
    {
      "id": "store",
      "tool": "memory_store",
      "duration_ms": 1000,
      "status": "success",
      "memory_id": "mem-uuid"
    }
  ],
  "total_tokens": 500,
  "success": true
}
```

### 性能指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| 执行时间 | 链总执行时间 | < 30s |
| 并行效率 | 并行加速比 | > 2x |
| 错误恢复率 | 自动恢复比例 | > 80% |
| 资源利用率 | CPU/内存利用率 | > 60% |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-02-25 | 初始版本，定义链式调用框架 |

---

**ClawOS 2026.3 - Tool Chain Framework**
