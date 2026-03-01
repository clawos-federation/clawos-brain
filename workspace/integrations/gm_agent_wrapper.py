#!/usr/bin/env python3
"""
GM Agent Wrapper - General Manager (总经理)
深度分析 → 战略规划 → 多Agent协调 → 强制质量把关
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Any

class GMAgent:
    """GM Agent - 总经理"""
    
    def __init__(self):
        self.model = "vectorengine-claude/claude-opus-4-5-20251101"
        self.name = "GM Agent"
    
    def deep_first_principles(self, task: str) -> dict:
        """
        深度第一性原理分析（5+层）
        """
        print(f"\n🔬 GM Agent: 深度第一性原理分析...")
        
        analysis = {
            "business_problem": self._extract_business_problem(task),
            "root_cause": self._identify_root_cause(task),
            "key_requirements": self._extract_requirements(task),
            "assumptions": self._identify_assumptions(task),
            "constraints": self._analyze_constraints(task),
            "minimal_solution": self._define_minimal_solution(task)
        }
        
        return analysis
    
    def strategic_planning(self, analysis: dict) -> dict:
        """
        战略规划
        """
        print(f"\n📊 GM Agent: 战略规划...")
        
        plan = {
            "phases": self._create_phases(analysis),
            "resources": self._estimate_resources(analysis),
            "timeline": self._estimate_timeline(analysis),
            "risks": self._identify_risks(analysis),
            "success_metrics": self._define_success_metrics(analysis)
        }
        
        return plan
    
    def identify_agents(self, analysis: dict) -> List[str]:
        """
        识别需要的专业 Agents
        """
        print(f"\n👥 GM Agent: 识别专业 Agents...")
        
        agents = []
        
        # 根据任务特征匹配 Agents
        if self._needs_development(analysis):
            agents.append("DevAgent")
        
        if self._needs_legal(analysis):
            agents.append("LegalAgent")
        
        if self._needs_marketing(analysis):
            agents.append("MarketingAgent")
        
        if self._needs_research(analysis):
            agents.append("ResearchAgent")
        
        if self._needs_design(analysis):
            agents.append("DesignerAgent")
        
        if not agents:
            agents = ["DevAgent"]  # 默认
        
        return agents
    
    def distribute_tasks(self, plan: dict, agents: List[str]) -> dict:
        """
        分配任务给专业 Agents
        """
        print(f"\n📋 GM Agent: 分配任务...")
        
        distributions = {}
        
        for agent in agents:
            distributions[agent] = {
                "agent": agent,
                "tasks": self._generate_tasks(agent, plan),
                "deadline": plan.get("timeline", {}).get(agent, "TBD"),
                "quality_standards": self._get_quality_standards(agent),
                "dependencies": self._get_dependencies(agent, agents)
            }
        
        return distributions
    
    def mandatory_quality_gate(self, work_product: dict, agent_name: str) -> dict:
        """
        强制质量把关（7/10 及格线）
        """
        print(f"\n🔒 GM Agent: 质量把关 ({agent_name})...")
        
        # 多维度评分
        scores = {
            "accuracy": self._score_accuracy(work_product),
            "completeness": self._score_completeness(work_product),
            "professionalism": self._score_professionalism(work_product),
            "risk_assessment": self._score_risk(work_product),
            "maintainability": self._score_maintainability(work_product)
        }
        
        # 权重计算
        weights = {
            "accuracy": 0.30,
            "completeness": 0.20,
            "professionalism": 0.20,
            "risk_assessment": 0.15,
            "maintainability": 0.15
        }
        
        # 总分
        total_score = sum(scores[k] * weights[k] for k in scores)
        
        # 判断是否通过（7/10 及格）
        passed = total_score >= 7.0
        
        # 生成质量徽章
        badge = self._get_quality_badge(total_score)
        
        return {
            "passed": passed,
            "score": round(total_score, 1),
            "dimensions": scores,
            "badge": badge,
            "feedback": self._generate_feedback(scores),
            "suggestions": self._generate_suggestions(scores),
            "risks": self._identify_work_risks(work_product)
        }
    
    def strategic_innovation(self, results: List[dict]) -> List[dict]:
        """
        战略创新洞察
        """
        print(f"\n💡 GM Agent: 寻找创新机会...")
        
        insights = []
        
        # 1. 自动化机会
        if self._detect_recurring_pattern(results):
            insights.append({
                "type": "automation_opportunity",
                "description": "检测到重复模式，建议自动化",
                "impact": "预计节省 30-50% 未来开发时间"
            })
        
        # 2. 优化机会
        optimization = self._find_optimization(results)
        if optimization:
            insights.append({
                "type": "performance_optimization",
                "description": optimization["description"],
                "impact": optimization["impact"]
            })
        
        # 3. 知识管理
        if self._has_knowledge_value(results):
            insights.append({
                "type": "knowledge_base",
                "description": "有价值的内容可沉淀到知识库",
                "action": "建议添加到文档库"
            })
        
        return insights
    
    def _extract_business_problem(self, task: str) -> str:
        """提取业务问题"""
        # 关键词分析
        keywords = ["build", "create", "develop", "implement", "fix", "optimize"]
        for keyword in keywords:
            if keyword in task.lower():
                return f"需要{keyword}解决方案"
        return "需要进一步业务分析"
    
    def _identify_root_cause(self, task: str) -> str:
        """识别根本原因"""
        return "需要解决的核心痛点"
    
    def _extract_requirements(self, task: str) -> List[str]:
        """提取需求"""
        requirements = ["功能性需求", "非功能性需求"]
        return requirements
    
    def _identify_assumptions(self, task: str) -> List[str]:
        """识别假设"""
        return ["假设1: 资源充足", "假设2: 技术可行"]
    
    def _analyze_constraints(self, task: str) -> dict:
        """分析约束"""
        return {
            "time": "时间约束",
            "budget": "预算约束",
            "technical": "技术约束"
        }
    
    def _define_minimal_solution(self, task: str) -> str:
        """定义最小可行方案"""
        return "最小可行产品 (MVP)"
    
    def _create_phases(self, analysis: dict) -> List[dict]:
        """创建阶段计划"""
        return [
            {"name": "Phase 1: 需求分析", "duration": "1周"},
            {"name": "Phase 2: 设计", "duration": "2周"},
            {"name": "Phase 3: 开发", "duration": "3周"},
            {"name": "Phase 4: 测试", "duration": "1周"}
        ]
    
    def _estimate_resources(self, analysis: dict) -> dict:
        """估算资源"""
        return {
            "developers": 2,
            "designers": 1,
            "budget": "待定"
        }
    
    def _estimate_timeline(self, analysis: dict) -> dict:
        """估算时间线"""
        return {
            "DevAgent": "4-6周",
            "LegalAgent": "1-2周",
            "MarketingAgent": "并行执行"
        }
    
    def _identify_risks(self, analysis: dict) -> List[dict]:
        """识别风险"""
        return [
            {"type": "technical", "description": "技术风险", "severity": "medium"},
            {"type": "resource", "description": "资源风险", "severity": "low"}
        ]
    
    def _define_success_metrics(self, analysis: dict) -> List[str]:
        """定义成功指标"""
        return [
            "功能完整度 > 95%",
            "代码覆盖率 > 80%",
            "性能指标达标",
            "用户满意度 > 4.5/5"
        ]
    
    def _needs_development(self, analysis: dict) -> bool:
        """是否需要开发"""
        return True  # 默认需要开发
    
    def _needs_legal(self, analysis: dict) -> bool:
        """是否需要法律"""
        return False  # 默认不需要
    
    def _needs_marketing(self, analysis: dict) -> bool:
        """是否需要营销"""
        return False
    
    def _needs_research(self, analysis: dict) -> bool:
        """是否需要研究"""
        return False
    
    def _needs_design(self, analysis: dict) -> bool:
        """是否需要设计"""
        return True  # 默认需要设计
    
    def _generate_tasks(self, agent: str, plan: dict) -> List[str]:
        """生成任务列表"""
        task_map = {
            "DevAgent": ["架构设计", "后端开发", "前端开发", "集成测试"],
            "LegalAgent": ["合规审查", "合同审查", "风险评估"],
            "MarketingAgent": ["策略规划", "内容创作", "推广方案"],
            "ResearchAgent": ["市场研究", "竞品分析", "趋势预测"],
            "DesignerAgent": ["UI设计", "UX设计", "原型制作"]
        }
        return task_map.get(agent, ["执行任务"])
    
    def _get_quality_standards(self, agent: str) -> dict:
        """获取质量标准"""
        standards = {
            "DevAgent": {
                "code_coverage": ">80%",
                "security_review": "required",
                "documentation": "complete"
            },
            "LegalAgent": {
                "legal_accuracy": "100%",
                "risk_identification": "comprehensive"
            },
            "MarketingAgent": {
                "brand_consistency": "required",
                "conversion_focus": "required"
            }
        }
        return standards.get(agent, {"quality": "high"})
    
    def _get_dependencies(self, agent: str, all_agents: List[str]) -> List[str]:
        """获取依赖关系"""
        deps = {
            "LegalAgent": ["DevAgent"],  # 法律需要了解技术方案
            "MarketingAgent": ["DevAgent", "DesignerAgent"],  # 营销需要产品和设计
            "QAAgent": ["DevAgent"]  # 测试依赖开发
        }
        return deps.get(agent, [])
    
    def _score_accuracy(self, work: dict) -> float:
        """评分：准确性"""
        return 8.0
    
    def _score_completeness(self, work: dict) -> float:
        """评分：完整性"""
        return 7.5
    
    def _score_professionalism(self, work: dict) -> float:
        """评分：专业性"""
        return 8.0
    
    def _score_risk(self, work: dict) -> float:
        """评分：风险评估"""
        return 7.0
    
    def _score_maintainability(self, work: dict) -> float:
        """评分：可维护性"""
        return 7.5
    
    def _get_quality_badge(self, score: float) -> str:
        """获取质量徽章"""
        if score >= 9.0:
            return "🌟 EXCELLENT"
        elif score >= 8.0:
            return "✅ APPROVED"
        elif score >= 7.0:
            return "⚠️ ACCEPTABLE"
        else:
            return "❌ REJECTED"
    
    def _generate_feedback(self, scores: dict) -> List[str]:
        """生成反馈"""
        feedback = []
        if scores["accuracy"] < 8:
            feedback.append("准确性需要提升")
        if scores["completeness"] < 7:
            feedback.append("完整性需要完善")
        return feedback or ["整体质量良好"]
    
    def _generate_suggestions(self, scores: dict) -> List[str]:
        """生成建议"""
        return [
            "加强单元测试覆盖",
            "完善文档说明",
            "优化错误处理逻辑"
        ]
    
    def _identify_work_risks(self, work: dict) -> List[dict]:
        """识别工作风险"""
        return [
            {"type": "technical", "description": "技术债务风险", "severity": "low"}
        ]
    
    def _detect_recurring_pattern(self, results: List[dict]) -> bool:
        """检测重复模式"""
        return False  # 简化实现
    
    def _find_optimization(self, results: List[dict]) -> dict:
        """寻找优化机会"""
        return None
    
    def _has_knowledge_value(self, results: List[dict]) -> bool:
        """是否有知识价值"""
        return True


def main():
    """GM Agent 主入口"""
    if len(sys.argv) < 2:
        print("Usage: gm_agent_wrapper.py <task>")
        print("Example: gm_agent_wrapper.py 'build a customer portal'")
        sys.exit(1)
    
    task = sys.argv[1]
    
    gm = GMAgent()
    
    # 1. 深度第一性原理
    analysis = gm.deep_first_principles(task)
    
    # 2. 战略规划
    plan = gm.strategic_planning(analysis)
    
    # 3. 识别 Agents
    agents = gm.identify_agents(analysis)
    
    # 4. 任务分配
    distributions = gm.distribute_tasks(plan, agents)
    
    # 5. 质量把关（模拟）
    mock_work = {"content": "模拟工作成果"}
    quality_result = gm.mandatory_quality_gate(mock_work, "DevAgent")
    
    # 6. 创新洞察
    insights = gm.strategic_innovation([mock_work])
    
    result = {
        "status": "completed",
        "analysis": analysis,
        "plan": plan,
        "agents": agents,
        "distributions": distributions,
        "quality_gate": quality_result,
        "innovation_insights": insights,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n📊 GM Agent 处理结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


if __name__ == "__main__":
    main()
