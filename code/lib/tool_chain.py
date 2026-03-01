#!/usr/bin/env python3
"""
ClawOS 工具链执行器
实现工具的链式调用和并行执行
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml

# ============================================================================
# 链定义
# ============================================================================

@dataclass
class ChainStep:
    id: str
    tool: str
    params: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    condition: Optional[str] = None
    error_handling: Optional[Dict[str, Any]] = None

@dataclass
class ToolChain:
    name: str
    description: str
    version: str
    input_schema: Dict[str, Any]
    steps: List[ChainStep]
    output: Dict[str, Any]
    error_handling: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# 参数解析器
# ============================================================================

class ParamResolver:
    """参数模板解析器"""
    
    def __init__(self, input_params: Dict, step_results: Dict, context: Dict = None):
        self.input = input_params
        self.steps = step_results
        self.context = context or {}
    
    def resolve(self, value: Any) -> Any:
        """递归解析值"""
        if isinstance(value, str):
            return self._resolve_string(value)
        elif isinstance(value, dict):
            return {k: self.resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.resolve(item) for item in value]
        else:
            return value
    
    def _resolve_string(self, s: str) -> Any:
        """解析字符串中的变量引用"""
        # ${input.x}
        if s.startswith("${input."):
            path = s[8:-1]  # 去掉 ${input. 和 }
            return self._get_nested(self.input, path)
        
        # ${steps.a.output}
        if s.startswith("${steps."):
            inner = s[8:-1]  # steps.a.output
            parts = inner.split(".")
            step_id = parts[0]
            path = ".".join(parts[1:])
            
            if step_id not in self.steps:
                raise ValueError(f"Step not found: {step_id}")
            
            return self._get_nested(self.steps[step_id], path)
        
        # ${env.X}
        if s.startswith("${env."):
            import os
            return os.environ.get(s[6:-1], "")
        
        # ${context.x}
        if s.startswith("${context."):
            path = s[10:-1]
            return self._get_nested(self.context, path)
        
        return s
    
    def _get_nested(self, obj: Any, path: str) -> Any:
        """获取嵌套属性"""
        if not path:
            return obj
        
        parts = path.split(".")
        current = obj
        
        for part in parts:
            if current is None:
                return None
            
            # JSONPath 数组索引: items[0]
            match = re.match(r"(\w+)\[(\d+)\]", part)
            if match:
                key, idx = match.groups()
                current = current.get(key, [])
                if isinstance(current, list) and len(current) > int(idx):
                    current = current[int(idx)]
                else:
                    return None
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        
        return current

# ============================================================================
# 条件评估器
# ============================================================================

class ConditionEvaluator:
    """安全条件评估器"""
    
    def __init__(self, context: Dict):
        self.context = context
    
    def evaluate(self, condition: str) -> bool:
        """评估条件表达式"""
        if not condition:
            return True
        
        # 解析变量
        resolver = ParamResolver(
            self.context.get("input", {}),
            self.context.get("steps", {}),
            self.context
        )
        
        resolved = resolver.resolve(f"${{{condition}}}")
        
        # 处理比较表达式
        if isinstance(resolved, str):
            # size > 0
            if " > " in resolved:
                left, right = resolved.split(" > ", 1)
                return self._to_number(left) > self._to_number(right)
            if " < " in resolved:
                left, right = resolved.split(" < ", 1)
                return self._to_number(left) < self._to_number(right)
            if " == " in resolved:
                left, right = resolved.split(" == ", 1)
                return str(left).strip() == str(right).strip()
            
            # 布尔值
            return resolved.lower() in ("true", "1", "yes")
        
        return bool(resolved)
    
    def _to_number(self, value: Any) -> float:
        """转换为数字"""
        if isinstance(value, (int, float)):
            return value
        try:
            return float(str(value).strip())
        except:
            return 0

# ============================================================================
# 工具链执行器
# ============================================================================

class ToolChainExecutor:
    """工具链执行器"""
    
    def __init__(self, tools: Dict[str, Callable]):
        """
        Args:
            tools: 工具名称到函数的映射
        """
        self.tools = tools
        self.execution_log: List[Dict] = []
    
    def execute(self, chain: ToolChain, input_params: Dict) -> Dict:
        """
        执行工具链
        
        Args:
            chain: 工具链定义
            input_params: 输入参数
        
        Returns:
            执行结果
        """
        self.execution_log = []
        start_time = datetime.now()
        
        # 初始化上下文
        context = {
            "input": input_params,
            "steps": {},
            "chain": chain.metadata
        }
        
        resolver = ParamResolver(input_params, context["steps"])
        evaluator = ConditionEvaluator(context)
        
        # 按顺序执行步骤
        for step in chain.steps:
            step_start = datetime.now()
            step_result = {
                "id": step.id,
                "tool": step.tool,
                "status": "pending"
            }
            
            try:
                # 检查条件
                if step.condition:
                    if not evaluator.evaluate(step.condition):
                        step_result["status"] = "skipped"
                        step_result["reason"] = "Condition not met"
                        context["steps"][step.id] = {"skipped": True}
                        self.execution_log.append(step_result)
                        continue
                
                # 解析参数
                params = resolver.resolve(step.params)
                step_result["input"] = params
                
                # 获取工具
                if step.tool not in self.tools:
                    raise ValueError(f"Tool not found: {step.tool}")
                
                tool = self.tools[step.tool]
                
                # 执行工具
                output = tool(**params)
                step_result["output"] = output
                step_result["status"] = "success"
                
                # 存储结果
                context["steps"][step.id] = {"output": output, "success": True}
                
            except Exception as e:
                step_result["status"] = "error"
                step_result["error"] = str(e)
                context["steps"][step.id] = {"error": str(e), "success": False}
                
                # 错误处理
                if not self._handle_error(step, e, context, resolver):
                    # 无法恢复，终止执行
                    self.execution_log.append(step_result)
                    return {
                        "success": False,
                        "error": str(e),
                        "step": step.id,
                        "log": self.execution_log
                    }
            
            finally:
                step_result["duration_ms"] = (datetime.now() - step_start).total_seconds() * 1000
                self.execution_log.append(step_result)
        
        # 构建最终输出
        output = resolver.resolve(chain.output)
        
        return {
            "success": True,
            "output": output,
            "log": self.execution_log,
            "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
        }
    
    def _handle_error(self, step: ChainStep, error: Exception, 
                      context: Dict, resolver: ParamResolver) -> bool:
        """处理错误"""
        if not step.error_handling:
            return False
        
        strategy = step.error_handling.get("strategy", "abort")
        
        if strategy == "retry":
            retries = step.error_handling.get("retries", 1)
            # 简单重试实现
            for _ in range(retries):
                try:
                    params = resolver.resolve(step.params)
                    output = self.tools[step.tool](**params)
                    context["steps"][step.id] = {"output": output, "success": True}
                    return True
                except:
                    pass
            return False
        
        elif strategy == "fallback":
            fallback = step.error_handling.get("fallback")
            if fallback:
                try:
                    params = resolver.resolve(fallback.get("params", {}))
                    output = self.tools[fallback["tool"]](**params)
                    context["steps"][step.id] = {"output": output, "success": True, "fallback": True}
                    return True
                except:
                    pass
            return False
        
        elif strategy == "ignore":
            context["steps"][step.id] = {"error": str(error), "success": False, "ignored": True}
            return True
        
        return False  # abort

# ============================================================================
# 并行执行器
# ============================================================================

class ParallelToolChainExecutor(ToolChainExecutor):
    """支持并行执行的工具链执行器"""
    
    def __init__(self, tools: Dict[str, Callable], max_workers: int = 5):
        super().__init__(tools)
        self.max_workers = max_workers
    
    def execute_parallel(self, chain: ToolChain, input_params: Dict) -> Dict:
        """并行执行工具链"""
        # 构建依赖图
        dag = self._build_dag(chain.steps)
        levels = self._topological_levels(dag)
        
        context = {
            "input": input_params,
            "steps": {}
        }
        
        resolver = ParamResolver(input_params, context["steps"])
        
        # 按层级执行
        for level in sorted(levels.keys()):
            steps_at_level = levels[level]
            
            # 并行执行同层步骤
            if len(steps_at_level) == 1:
                # 单步骤，直接执行
                self._execute_step(steps_at_level[0], context, resolver)
            else:
                # 多步骤，并行执行
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {
                        executor.submit(
                            self._execute_step, step, context.copy(), resolver
                        ): step for step in steps_at_level
                    }
                    
                    for future in as_completed(futures):
                        step = futures[future]
                        try:
                            future.result()
                        except Exception as e:
                            # 处理错误
                            context["steps"][step.id] = {"error": str(e), "success": False}
        
        # 构建输出
        output = resolver.resolve(chain.output)
        
        return {
            "success": True,
            "output": output,
            "log": self.execution_log
        }
    
    def _build_dag(self, steps: List[ChainStep]) -> Dict[str, List[str]]:
        """构建依赖图"""
        dag = {step.id: [] for step in steps}
        
        for step in steps:
            # 解析参数中的依赖
            deps = self._extract_dependencies(step.params)
            for dep in deps:
                if dep in dag:
                    dag[step.id].append(dep)
        
        return dag
    
    def _extract_dependencies(self, params: Dict) -> List[str]:
        """提取参数中的步骤依赖"""
        deps = []
        params_str = json.dumps(params)
        
        # 查找 ${steps.xxx. 引用
        import re
        matches = re.findall(r"\$\{steps\.(\w+)\.", params_str)
        deps.extend(matches)
        
        return list(set(deps))
    
    def _topological_levels(self, dag: Dict[str, List[str]]) -> Dict[int, List[ChainStep]]:
        """计算拓扑层级"""
        levels = {}
        calculated = {}
        
        def get_level(node):
            if node in calculated:
                return calculated[node]
            
            deps = dag.get(node, [])
            if not deps:
                calculated[node] = 0
                return 0
            
            max_dep_level = max(get_level(dep) for dep in deps)
            calculated[node] = max_dep_level + 1
            return calculated[node]
        
        for node in dag:
            level = get_level(node)
            if level not in levels:
                levels[level] = []
            # 这里需要从 steps 列表中找到对应的 ChainStep
            # 简化处理，返回 ID
            levels[level].append(node)
        
        return levels

# ============================================================================
# 链定义解析器
# ============================================================================

def parse_chain_from_yaml(yaml_content: str) -> ToolChain:
    """从 YAML 解析工具链"""
    data = yaml.safe_load(yaml_content)
    
    steps = []
    for step_data in data.get("steps", []):
        steps.append(ChainStep(
            id=step_data["id"],
            tool=step_data["tool"],
            params=step_data.get("params", {}),
            output=step_data.get("output"),
            condition=step_data.get("condition"),
            error_handling=step_data.get("error_handling")
        ))
    
    return ToolChain(
        name=data["name"],
        description=data.get("description", ""),
        version=data.get("version", "1.0.0"),
        input_schema=data.get("input", {}),
        steps=steps,
        output=data.get("output", {}),
        error_handling=data.get("error_handling", {}),
        metadata=data.get("metadata", {})
    )

def parse_chain_from_file(file_path: str) -> ToolChain:
    """从文件解析工具链"""
    path = Path(file_path)
    content = path.read_text(encoding='utf-8')
    
    if path.suffix in (".yaml", ".yml"):
        return parse_chain_from_yaml(content)
    elif path.suffix == ".json":
        data = json.loads(content)
        # 类似 YAML 解析
        steps = [ChainStep(**s) for s in data.get("steps", [])]
        return ToolChain(
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            input_schema=data.get("input", {}),
            steps=steps,
            output=data.get("output", {}),
            error_handling=data.get("error_handling", {}),
            metadata=data.get("metadata", {})
        )
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")

# ============================================================================
# 预定义工具链
# ============================================================================

# 研究 + 总结 + 存储
RESEARCH_CHAIN = """
name: research-chain
description: 搜索 → 抓取 → 总结 → 存储
version: 1.0.0

input:
  query: string
  count: number=5

steps:
  - id: search
    tool: web_search
    params:
      query: "${input.query}"
      count: "${input.count}"
    output:
      as: search_results

  - id: summarize
    tool: llm_summarize
    params:
      content: "${steps.search.output}"
      max_length: 500
    output:
      as: summary

  - id: store
    tool: memory_store
    params:
      content: "${steps.summarize.output}"
      type: research
      topic: "${input.query}"
    output:
      as: memory_id

output:
  summary: "${steps.summarize.output}"
  memory_id: "${steps.store.output}"
"""

# ============================================================================
# 示例工具
# ============================================================================

def mock_web_search(query: str, count: int = 5) -> Dict:
    """模拟网页搜索"""
    return {
        "results": [
            {"title": f"Result {i+1}", "url": f"https://example.com/{i+1}", "snippet": f"About {query}"}
            for i in range(count)
        ]
    }

def mock_llm_summarize(content: Any, max_length: int = 500) -> str:
    """模拟 LLM 总结"""
    if isinstance(content, dict):
        content = json.dumps(content)
    return f"Summary: {str(content)[:max_length]}..."

def mock_memory_store(content: str, type: str = "general", **metadata) -> str:
    """模拟记忆存储"""
    return f"mem-{uuid.uuid4().hex[:8]}"

# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ClawOS Tool Chain Executor")
    parser.add_argument("--chain", help="Chain definition file (YAML/JSON)")
    parser.add_argument("--demo", action="store_true", help="Run demo chain")
    parser.add_argument("--input", help="Input parameters as JSON")
    
    args = parser.parse_args()
    
    # 注册示例工具
    tools = {
        "web_search": mock_web_search,
        "llm_summarize": mock_llm_summarize,
        "memory_store": mock_memory_store
    }
    
    executor = ToolChainExecutor(tools)
    
    if args.demo:
        chain = parse_chain_from_yaml(RESEARCH_CHAIN)
        input_params = {"query": "ClawOS", "count": 3}
        result = executor.execute(chain, input_params)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.chain:
        chain = parse_chain_from_file(args.chain)
        input_params = json.loads(args.input) if args.input else {}
        result = executor.execute(chain, input_params)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()
