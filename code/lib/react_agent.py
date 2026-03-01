#!/usr/bin/env python3
"""
ClawOS 增强版 ReAct 执行器
实现 Think → Act → Observe → Reflect → Adapt 五阶段循环
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# 阶段定义
# ============================================================================

class Phase(Enum):
    THINK = "think"
    ACT = "act"
    OBSERVE = "observe"
    REFLECT = "reflect"
    ADAPT = "adapt"

class Decision(Enum):
    CONTINUE = "continue"
    PIVOT = "pivot"
    ABORT = "abort"
    COMPLETE = "complete"

@dataclass
class PhaseResult:
    phase: Phase
    success: bool
    output: Dict[str, Any]
    duration_ms: float
    error: Optional[str] = None

@dataclass
class CycleResult:
    iteration: int
    phases: List[PhaseResult]
    decision: Decision
    final_output: Optional[Dict] = None

@dataclass
class Experience:
    id: str
    task_type: str
    task_description: str
    outcome: Dict[str, Any]
    lessons: List[str]
    patterns: List[Dict]
    timestamp: str

# ============================================================================
# ReAct Agent
# ============================================================================

class EnhancedReActAgent:
    """增强版 ReAct Agent"""
    
    def __init__(self, 
                 agent_id: str,
                 tools: Dict[str, Callable],
                 llm_func: Callable,
                 max_iterations: int = 10,
                 experience_store: Optional[Callable] = None):
        """
        Args:
            agent_id: Agent ID
            tools: 可用工具映射
            llm_func: LLM 调用函数
            max_iterations: 最大迭代次数
            experience_store: 经验存储函数
        """
        self.agent_id = agent_id
        self.tools = tools
        self.llm = llm_func
        self.max_iterations = max_iterations
        self.experience_store = experience_store
        
        self.iteration = 0
        self.context: Dict[str, Any] = {}
        self.history: List[CycleResult] = []
        self.experiences: List[Experience] = []
    
    def execute(self, task: str, context: Dict = None) -> Dict:
        """
        执行任务
        
        Args:
            task: 任务描述
            context: 初始上下文
        
        Returns:
            执行结果
        """
        self.iteration = 0
        self.context = context or {}
        self.history = []
        
        # 获取相关经验
        relevant_experiences = self._get_relevant_experiences(task)
        
        while self.iteration < self.max_iterations:
            cycle_result = self._execute_cycle(task, relevant_experiences)
            self.history.append(cycle_result)
            
            if cycle_result.decision == Decision.COMPLETE:
                return {
                    "success": True,
                    "result": cycle_result.final_output,
                    "iterations": self.iteration + 1,
                    "history": [self._cycle_to_dict(c) for c in self.history]
                }
            
            elif cycle_result.decision == Decision.ABORT:
                return {
                    "success": False,
                    "reason": cycle_result.final_output.get("reason", "Aborted"),
                    "iterations": self.iteration + 1,
                    "history": [self._cycle_to_dict(c) for c in self.history]
                }
            
            self.iteration += 1
        
        return {
            "success": False,
            "reason": "Max iterations exceeded",
            "iterations": self.max_iterations,
            "history": [self._cycle_to_dict(c) for c in self.history]
        }
    
    def _execute_cycle(self, task: str, experiences: List[Experience]) -> CycleResult:
        """执行一个完整循环"""
        phases = []
        
        # 1. Think
        think_result = self._think(task, experiences)
        phases.append(think_result)
        
        if not think_result.success:
            return CycleResult(
                iteration=self.iteration,
                phases=phases,
                decision=Decision.ABORT,
                final_output={"reason": "Think phase failed"}
            )
        
        # 2. Act
        act_result = self._act(think_result.output)
        phases.append(act_result)
        
        if not act_result.success:
            return CycleResult(
                iteration=self.iteration,
                phases=phases,
                decision=Decision.PIVOT,
                final_output={"reason": "Act phase failed", "error": act_result.error}
            )
        
        # 3. Observe
        observe_result = self._observe(act_result.output)
        phases.append(observe_result)
        
        # 4. Reflect
        reflect_result = self._reflect(
            task, 
            think_result.output,
            act_result.output,
            observe_result.output
        )
        phases.append(reflect_result)
        
        # 5. Adapt
        adapt_result = self._adapt(reflect_result.output)
        phases.append(adapt_result)
        
        # 记录经验
        if reflect_result.output.get("lessons"):
            self._record_experience(task, reflect_result.output)
        
        return CycleResult(
            iteration=self.iteration,
            phases=phases,
            decision=Decision(adapt_result.output.get("decision", "continue")),
            final_output=observe_result.output if adapt_result.output.get("decision") == "complete" else None
        )
    
    # ========================================================================
    # 五阶段实现
    # ========================================================================
    
    def _think(self, task: str, experiences: List[Experience]) -> PhaseResult:
        """思考阶段"""
        start = datetime.now()
        
        prompt = f"""
You are analyzing a task. Think through it carefully.

Task: {task}

Relevant Past Experiences:
{self._format_experiences(experiences)}

Current Context:
{json.dumps(self.context, indent=2)}

Think through:
1. What is the core problem?
2. What are the constraints?
3. What options do we have?
4. Which option is best and why?

Output JSON:
{{
  "analysis": {{
    "problem": "core problem description",
    "constraints": ["constraint1", "constraint2"],
    "unknowns": ["unknown1"]
  }},
  "options": [
    {{
      "id": "option-1",
      "description": "option description",
      "pros": ["pro1"],
      "cons": ["con1"],
      "risk": "low|medium|high"
    }}
  ],
  "selectedOption": "option-1",
  "reasoning": "why this option"
}}
"""
        
        try:
            response = self.llm(prompt)
            output = self._parse_json(response)
            
            return PhaseResult(
                phase=Phase.THINK,
                success=True,
                output=output,
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )
        except Exception as e:
            return PhaseResult(
                phase=Phase.THINK,
                success=False,
                output={},
                duration_ms=(datetime.now() - start).total_seconds() * 1000,
                error=str(e)
            )
    
    def _act(self, think_output: Dict) -> PhaseResult:
        """行动阶段"""
        start = datetime.now()
        
        selected = think_output.get("selectedOption", "option-1")
        options = think_output.get("options", [])
        
        # 找到选中的选项
        option = next((o for o in options if o["id"] == selected), None)
        if not option:
            return PhaseResult(
                phase=Phase.ACT,
                success=False,
                output={},
                duration_ms=(datetime.now() - start).total_seconds() * 1000,
                error="No option selected"
            )
        
        # 根据选项选择工具
        tool_name, params = self._select_tool(option)
        
        if tool_name not in self.tools:
            return PhaseResult(
                phase=Phase.ACT,
                success=False,
                output={},
                duration_ms=(datetime.now() - start).total_seconds() * 1000,
                error=f"Tool not found: {tool_name}"
            )
        
        try:
            result = self.tools[tool_name](**params)
            
            return PhaseResult(
                phase=Phase.ACT,
                success=True,
                output={
                    "tool": tool_name,
                    "params": params,
                    "result": result
                },
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )
        except Exception as e:
            return PhaseResult(
                phase=Phase.ACT,
                success=False,
                output={},
                duration_ms=(datetime.now() - start).total_seconds() * 1000,
                error=str(e)
            )
    
    def _observe(self, act_output: Dict) -> PhaseResult:
        """观察阶段"""
        start = datetime.now()
        
        result = act_output.get("result", {})
        
        prompt = f"""
Analyze the execution result:

Result:
{json.dumps(result, indent=2, ensure_ascii=False)}

Extract:
1. Key findings
2. Unexpected findings
3. Questions that need follow-up

Output JSON:
{{
  "keyFindings": ["finding1", "finding2"],
  "unexpectedFindings": ["unexpected1"],
  "questions": ["question1"]
}}
"""
        
        try:
            response = self.llm(prompt)
            output = self._parse_json(response)
            output["raw_result"] = result
            
            return PhaseResult(
                phase=Phase.OBSERVE,
                success=True,
                output=output,
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )
        except Exception as e:
            return PhaseResult(
                phase=Phase.OBSERVE,
                success=True,  # 观察失败不影响流程
                output={"raw_result": result, "error": str(e)},
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )
    
    def _reflect(self, task: str, think: Dict, act: Dict, observe: Dict) -> PhaseResult:
        """反思阶段"""
        start = datetime.now()
        
        prompt = f"""
Reflect on the execution:

Task: {task}

Think Phase:
{json.dumps(think, indent=2, ensure_ascii=False)}

Act Phase:
{json.dumps(act, indent=2, ensure_ascii=False)}

Observe Phase:
{json.dumps(observe, indent=2, ensure_ascii=False)}

Evaluate:
1. Did we achieve the goal?
2. What went well?
3. What could be improved?
4. What did we learn?

Output JSON:
{{
  "evaluation": {{
    "success": true,
    "score": 0.85,
    "criteria": {{
      "correctness": 0.9,
      "completeness": 0.8,
      "efficiency": 0.85
    }}
  }},
  "issues": [
    {{
      "type": "error|inefficiency|gap",
      "description": "issue description",
      "severity": "low|medium|high",
      "cause": "root cause"
    }}
  ],
  "lessons": [
    "lesson1",
    "lesson2"
  ],
  "improvements": [
    "improvement1"
  ]
}}
"""
        
        try:
            response = self.llm(prompt)
            output = self._parse_json(response)
            
            return PhaseResult(
                phase=Phase.REFLECT,
                success=True,
                output=output,
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )
        except Exception as e:
            return PhaseResult(
                phase=Phase.REFLECT,
                success=True,
                output={"evaluation": {"success": False}, "lessons": []},
                duration_ms=(datetime.now() - start).total_seconds() * 1000,
                error=str(e)
            )
    
    def _adapt(self, reflect_output: Dict) -> PhaseResult:
        """适应阶段"""
        start = datetime.now()
        
        evaluation = reflect_output.get("evaluation", {})
        issues = reflect_output.get("issues", [])
        
        # 决定下一步
        if evaluation.get("success") and evaluation.get("score", 0) >= 0.8:
            decision = "complete"
        elif len(issues) > 3 or any(i.get("severity") == "high" for i in issues):
            decision = "pivot"
        elif self.iteration >= self.max_iterations - 1:
            decision = "abort"
        else:
            decision = "continue"
        
        output = {
            "decision": decision,
            "reason": f"Score: {evaluation.get('score', 0)}, Issues: {len(issues)}",
            "nextAction": {
                "type": "continue" if decision == "continue" else "done"
            }
        }
        
        return PhaseResult(
            phase=Phase.ADAPT,
            success=True,
            output=output,
            duration_ms=(datetime.now() - start).total_seconds() * 1000
        )
    
    # ========================================================================
    # 辅助方法
    # ========================================================================
    
    def _select_tool(self, option: Dict) -> Tuple[str, Dict]:
        """根据选项选择工具"""
        # 简化实现：根据描述匹配工具
        desc = option.get("description", "").lower()
        
        if "search" in desc or "find" in desc:
            return "web_search", {"query": desc}
        elif "fetch" in desc or "read" in desc:
            return "web_fetch", {"url": ""}
        elif "summarize" in desc:
            return "summarize", {"content": ""}
        else:
            return "default", {}
    
    def _parse_json(self, text: str) -> Dict:
        """解析 JSON"""
        import re
        # 尝试直接解析
        try:
            return json.loads(text)
        except:
            pass
        
        # 尝试提取 JSON 块
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        # 尝试找到 { } 块
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        
        return {}
    
    def _format_experiences(self, experiences: List[Experience]) -> str:
        """格式化经验"""
        if not experiences:
            return "No relevant experiences found."
        
        lines = []
        for exp in experiences[:3]:  # 最多显示 3 条
            lines.append(f"- {exp.task_description}")
            for lesson in exp.lessons[:2]:
                lines.append(f"  • {lesson}")
        
        return "\n".join(lines)
    
    def _get_relevant_experiences(self, task: str) -> List[Experience]:
        """获取相关经验"""
        # 简化实现：返回所有经验
        return self.experiences[:5]
    
    def _record_experience(self, task: str, reflect_output: Dict):
        """记录经验"""
        experience = Experience(
            id=f"exp-{uuid.uuid4().hex[:8]}",
            task_type="general",
            task_description=task,
            outcome={"evaluation": reflect_output.get("evaluation", {})},
            lessons=reflect_output.get("lessons", []),
            patterns=[],
            timestamp=datetime.now().isoformat()
        )
        
        self.experiences.append(experience)
        
        if self.experience_store:
            self.experience_store(experience)
    
    def _cycle_to_dict(self, cycle: CycleResult) -> Dict:
        """转换循环结果为字典"""
        return {
            "iteration": cycle.iteration,
            "phases": [
                {
                    "phase": p.phase.value,
                    "success": p.success,
                    "duration_ms": p.duration_ms,
                    "error": p.error
                }
                for p in cycle.phases
            ],
            "decision": cycle.decision.value
        }

# ============================================================================
# 模拟 LLM
# ============================================================================

def mock_llm(prompt: str) -> str:
    """模拟 LLM 响应"""
    if "Think through" in prompt:
        return json.dumps({
            "analysis": {
                "problem": "Need to search for information",
                "constraints": ["Must be accurate", "Time limit"],
                "unknowns": ["Best source"]
            },
            "options": [
                {
                    "id": "option-1",
                    "description": "Search the web for information",
                    "pros": ["Quick", "Comprehensive"],
                    "cons": ["May have noise"],
                    "risk": "low"
                }
            ],
            "selectedOption": "option-1",
            "reasoning": "Web search is fastest"
        })
    elif "Analyze the execution" in prompt:
        return json.dumps({
            "keyFindings": ["Found relevant information"],
            "unexpectedFindings": [],
            "questions": []
        })
    elif "Reflect on" in prompt:
        return json.dumps({
            "evaluation": {
                "success": True,
                "score": 0.9,
                "criteria": {
                    "correctness": 0.9,
                    "completeness": 0.9,
                    "efficiency": 0.9
                }
            },
            "issues": [],
            "lessons": ["Web search is effective for quick lookups"],
            "improvements": []
        })
    else:
        return "{}"

# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ClawOS Enhanced ReAct Agent")
    parser.add_argument("--task", help="Task to execute")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--max-iter", type=int, default=5, help="Max iterations")
    
    args = parser.parse_args()
    
    # 示例工具
    tools = {
        "web_search": lambda query: {"results": [f"Result for: {query}"]},
        "summarize": lambda content: f"Summary of: {content[:50]}..."
    }
    
    agent = EnhancedReActAgent(
        agent_id="demo-agent",
        tools=tools,
        llm_func=mock_llm,
        max_iterations=args.max_iter
    )
    
    if args.demo or args.task:
        task = args.task or "Find information about ClawOS"
        result = agent.execute(task)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        parser.print_help()
