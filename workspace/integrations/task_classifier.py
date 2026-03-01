#!/usr/bin/env python3
"""
多维度任务分类系统 - Advanced Task Classifier
基于复杂度、风险、重要性、多领域4个维度智能分类任务
"""

from datetime import datetime
from typing import Dict, List, Tuple
import json


class AdvancedTaskClassifier:
    """增强型任务分类器"""
    
    def __init__(self):
        # 维度权重
        self.weights = {
            "complexity": 0.35,
            "risk": 0.30,
            "importance": 0.35
        }
        
        # 阈值配置
        self.thresholds = {
            "gm_agent": 7.5,
            "assisted": 5.0,
            "henry": 0.0
        }
        
        # 关键词数据库
        self.keywords = {
            "risk": self._init_risk_keywords(),
            "importance": self._init_importance_keywords(),
            "domains": self._init_domain_keywords(),
            "complexity": self._init_complexity_keywords()
        }
    
    def classify(self, task: str, context: Dict = None) -> Dict:
        """
        多维度任务分类
        
        Args:
            task: 任务描述
            context: 上下文信息（可选）
        
        Returns:
            分类结果字典
        """
        if context is None:
            context = {}
        
        # 维度1：复杂度 (0-10)
        complexity_score = self._assess_complexity(task, context)
        
        # 维度2：风险 (0-10)
        risk_score = self._assess_risk(task, context)
        
        # 维度3：重要性 (0-10)
        importance_score = self._assess_importance(task, context)
        
        # 维度4：多领域 (bool)
        is_multi_domain = self._check_multi_domain(task, context)
        
        # 综合评分
        total_score = self._calculate_total_score(
            complexity_score, risk_score, importance_score
        )
        
        # 决策
        decision = self._make_decision(
            total_score, is_multi_domain, task, context
        )
        
        return {
            "task": task,
            "scores": {
                "complexity": complexity_score,
                "risk": risk_score,
                "importance": importance_score,
                "total": round(total_score, 1)
            },
            "is_multi_domain": is_multi_domain,
            "decision": decision,
            "classified_at": datetime.now().isoformat()
        }
    
    def _assess_complexity(self, task: str, context: Dict) -> float:
        """评估复杂度 (0-10)"""
        score = 0.0
        
        task_lower = task.lower()
        
        # 1. 步骤数分析
        steps = self._count_steps(task)
        score += min(steps * 1.5, 4.0)  # 最多4分
        
        # 2. 技术难度关键词
        tech_keywords = self.keywords["complexity"]["technical"]
        for keyword, points in tech_keywords.items():
            if keyword in task_lower:
                score += points
                break  # 只取最高的
        
        # 3. 依赖复杂度
        deps = self._count_dependencies(task)
        score += min(deps * 0.5, 2.0)  # 最多2分
        
        # 4. 数据处理复杂度
        if "database" in task_lower or "sql" in task_lower:
            score += 1.0
        if "api" in task_lower or "integration" in task_lower:
            score += 0.5
        
        # 限制范围 [0, 10]
        return min(score, 10.0)
    
    def _assess_risk(self, task: str, context: Dict) -> float:
        """评估风险 (0-10)"""
        score = 0.0
        
        task_lower = task.lower()
        
        # 1. 风险关键词
        for keyword, points in self.keywords["risk"].items():
            if keyword in task_lower:
                score += points
        
        # 2. 数据敏感度
        if "user data" in task_lower or "personal information" in task_lower:
            score += 2.0
        if "payment" in task_lower or "credit card" in task_lower:
            score += 2.5
        if "password" in task_lower or "authentication" in task_lower:
            score += 1.5
        
        # 3. 生产环境风险
        if "production" in task_lower or "live" in task_lower:
            score += 2.0
        if "deploy" in task_lower:
            score += 1.0
        
        # 4. 上下文风险评估
        if context.get("risk_level"):
            context_risk = {
                "critical": 3.0,
                "high": 2.0,
                "medium": 1.0,
                "low": 0.0
            }
            score += context_risk.get(context["risk_level"], 0.0)
        
        # 限制范围 [0, 10]
        return min(score, 10.0)
    
    def _assess_importance(self, task: str, context: Dict) -> float:
        """评估重要性 (0-10)"""
        score = 0.0
        
        task_lower = task.lower()
        
        # 1. 优先级关键词
        for keyword, points in self.keywords["importance"].items():
            if keyword in task_lower:
                score += points
        
        # 2. 战略关键词
        if "core" in task_lower or "strategic" in task_lower:
            score += 2.0
        if "key" in task_lower or "critical" in task_lower:
            score += 1.5
        
        # 3. 上下文重要性
        if context.get("priority"):
            priority = context["priority"].lower()
            if priority == "critical":
                score += 3.0
            elif priority == "high":
                score += 2.0
            elif priority == "medium":
                score += 1.0
        
        # 4. 用户影响
        if "blocking" in task_lower or "blocked by" in task_lower:
            score += 1.5
        
        # 限制范围 [0, 10]
        return min(score, 10.0)
    
    def _check_multi_domain(self, task: str, context: Dict) -> bool:
        """检查是否多领域"""
        domains = []
        task_lower = task.lower()
        
        # 检查各领域关键词
        for domain, keywords in self.keywords["domains"].items():
            for keyword in keywords:
                if keyword in task_lower:
                    domains.append(domain)
                    break
        
        # 检查上下文中的领域
        if context.get("domains"):
            for domain in context["domains"]:
                if domain not in domains:
                    domains.append(domain)
        
        return len(domains) > 1
    
    def _calculate_total_score(self, complexity: float, risk: float, importance: float) -> float:
        """计算综合评分"""
        total = (
            complexity * self.weights["complexity"] +
            risk * self.weights["risk"] +
            importance * self.weights["importance"]
        )
        return total
    
    def _make_decision(self, score: float, multi: bool, task: str, context: Dict) -> Dict:
        """智能决策"""
        
        # 决策规则
        if multi or score > self.thresholds["gm_agent"]:
            return {
                "handler": "GM Agent",
                "mode": "managed",
                "confidence": "high",
                "reason": self._generate_gm_reason(score, multi, task),
                "estimated_time": "10-20 分钟",
                "oversight": True,
                "requires_human_review": score > 9.0
            }
        elif score > self.thresholds["assisted"]:
            return {
                "handler": "Henry",
                "mode": "assisted",
                "confidence": "medium",
                "reason": self._generate_assisted_reason(score, task),
                "estimated_time": "3-5 分钟",
                "oversight": True,
                "requires_gm_review": True
            }
        else:
            return {
                "handler": "Henry",
                "mode": "solo",
                "confidence": "high",
                "reason": self._generate_henry_reason(score, task),
                "estimated_time": "< 2 分钟",
                "oversight": False,
                "requires_gm_review": False
            }
    
    def _generate_gm_reason(self, score: float, multi: bool, task: str) -> str:
        """生成 GM Agent 决策原因"""
        reasons = []
        
        if multi:
            reasons.append("涉及多个领域，需要跨领域协调")
        if score > 8.0:
            reasons.append("综合评分极高，需要深度处理")
        elif score > 7.5:
            reasons.append("综合评分较高，需要专业把控")
        
        return "; ".join(reasons) if reasons else "符合 GM Agent 处理标准"
    
    def _generate_assisted_reason(self, score: float, task: str) -> str:
        """生成辅助决策原因"""
        reasons = []
        
        if 5.0 < score <= 6.0:
            reasons.append("中等复杂度")
        elif 6.0 < score <= 7.5:
            reasons.append("较高复杂度，建议 GM Agent 审查")
        
        return "; ".join(reasons) if reasons else "需要辅助处理"
    
    def _generate_henry_reason(self, score: float, task: str) -> str:
        """生成 Henry 决策原因"""
        reasons = []
        
        if score < 3.0:
            reasons.append("简单任务，快速处理")
        elif 3.0 <= score < 5.0:
            reasons.append("低复杂度，可以快速完成")
        
        return "; ".join(reasons) if reasons else "简单快速处理"
    
    # 辅助方法
    def _count_steps(self, task: str) -> int:
        """估算步骤数"""
        steps = 1
        
        # 计数连接词
        connectors = ["and", "then", "after", "also", "plus"]
        task_lower = task.lower()
        for connector in connectors:
            steps += task_lower.count(f" {connector} ")
        
        return min(steps, 10)  # 最多10步
    
    def _count_dependencies(self, task: str) -> int:
        """估算依赖数"""
        deps = 0
        
        if "database" in task.lower():
            deps += 1
        if "api" in task.lower():
            deps += 1
        if "integration" in task.lower():
            deps += 1
        if "external" in task.lower():
            deps += 1
        
        return deps
    
    # 关键词初始化
    def _init_risk_keywords(self) -> Dict[str, float]:
        """初始化风险关键词"""
        return {
            "security": 2.0,
            "privacy": 2.0,
            "legal": 1.5,
            "compliance": 1.5,
            "money": 2.0,
            "payment": 2.5,
            "financial": 2.0,
            "data loss": 2.5,
            "downtime": 1.5
        }
    
    def _init_importance_keywords(self) -> Dict[str, float]:
        """初始化重要性关键词"""
        return {
            "urgent": 2.0,
            "critical": 2.5,
            "important": 1.5,
            "asap": 2.0,
            "priority": 1.5,
            "immediately": 2.0,
            "as soon as possible": 2.0
        }
    
    def _init_domain_keywords(self) -> Dict[str, List[str]]:
        """初始化领域关键词"""
        return {
            "dev": ["code", "develop", "programming", "software", "app"],
            "design": ["design", "ui", "ux", "interface", "visual"],
            "marketing": ["market", "content", "campaign", "brand", "promotion"],
            "legal": ["legal", "contract", "compliance", "policy"],
            "ops": ["deploy", "monitor", "infrastructure", "ops"]
        }
    
    def _init_complexity_keywords(self) -> Dict[str, Dict[str, float]]:
        """初始化复杂度关键词"""
        return {
            "technical": {
                "machine learning": 3.0,
                "ai model": 2.5,
                "distributed system": 2.5,
                "microservices": 2.0,
                "database": 1.5,
                "api": 1.0,
                "authentication": 1.5,
                "encryption": 1.0
            }
        }


def main():
    """测试任务分类器"""
    classifier = AdvancedTaskClassifier()
    
    # 测试案例
    test_tasks = [
        "Write a README file",
        "Create a user authentication system with OAuth",
        "Build a payment processing system for production",
        "Design a landing page and implement the backend API",
        "Fix a critical bug in the production database",
        "Search the web for latest AI news",
        "Deploy the application with database migration"
    ]
    
    print("=" * 80)
    print("多维度任务分类系统测试")
    print("=" * 80)
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n任务 {i}: {task}")
        print("-" * 80)
        
        result = classifier.classify(task)
        
        print(f"复杂度: {result['scores']['complexity']:.1f}/10")
        print(f"风险: {result['scores']['risk']:.1f}/10")
        print(f"重要性: {result['scores']['importance']:.1f}/10")
        print(f"综合评分: {result['scores']['total']}/10")
        print(f"多领域: {'是' if result['is_multi_domain'] else '否'}")
        print()
        print(f"🎯 处理者: {result['decision']['handler']}")
        print(f"   模式: {result['decision']['mode']}")
        print(f"   置信度: {result['decision']['confidence']}")
        print(f"   原因: {result['decision']['reason']}")
        print(f"   预计时间: {result['decision']['estimated_time']}")


if __name__ == "__main__":
    main()
