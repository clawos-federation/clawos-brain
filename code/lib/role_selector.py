#!/usr/bin/env python3
"""
ClawOS PM 选角算法
根据任务需求从 capabilities.json 选择最合适的 Worker 角色组合
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class RoleCandidate:
    role_id: str
    function: str
    domain: str
    capabilities: List[str]
    match_score: float
    performance_score: float
    final_score: float

# ============================================================================
# 选角算法
# ============================================================================

class RoleSelector:
    """PM 选角算法"""
    
    def __init__(self, capabilities_path: str = "~/openclaw-system/clawos/registry/capabilities.json"):
        self.capabilities_path = Path(capabilities_path).expanduser()
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """加载角色注册表"""
        with open(self.capabilities_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def select_team(self, 
                    task_description: str,
                    required_capabilities: List[str],
                    pm_type: str = "coding-pm",
                    team_size: int = 3) -> List[Dict]:
        """
        为任务选择最佳角色组合
        
        Args:
            task_description: 任务描述
            required_capabilities: 需要的能力列表
            pm_type: PM 类型（决定可召唤的角色范围）
            team_size: 团队大小
        
        Returns:
            推荐的角色组合
        """
        # 1. 获取 PM 可召唤的角色
        available_roles = self._get_available_roles(pm_type)
        
        # 2. 计算每个角色的匹配度
        candidates = []
        for role in available_roles:
            candidate = self._evaluate_role(role, required_capabilities)
            if candidate:
                candidates.append(candidate)
        
        # 3. 按分数排序
        candidates.sort(key=lambda x: x.final_score, reverse=True)
        
        # 4. 选择组合（确保职能多样性）
        selected = self._ensure_diversity(candidates, team_size)
        
        # 5. 生成选角决策
        return self._generate_decision(selected, task_description)
    
    def _get_available_roles(self, pm_type: str) -> List[Dict]:
        """获取 PM 可召唤的角色"""
        pm_info = self.registry.get("pmLayer", {}).get(pm_type, {})
        can_summon = pm_info.get("canSummon", [])
        
        all_roles = self.registry.get("workerMatrix", {}).get("roles", [])
        return [r for r in all_roles if r["id"] in can_summon]
    
    def _evaluate_role(self, role: Dict, required_caps: List[str]) -> RoleCandidate:
        """评估角色匹配度"""
        role_caps = set(role.get("capabilities", []))
        required = set(required_caps)
        
        # 计算能力匹配度
        if not required:
            match_score = 0.5
        else:
            matched = len(role_caps & required)
            match_score = matched / len(required)
        
        # 如果完全不匹配，跳过
        if match_score == 0:
            return None
        
        # 获取历史表现
        perf = role.get("performance", {})
        perf_score = perf.get("avgScore", 7.5) / 10.0  # 归一化到 0-1
        
        # 任务数量加权（经验越多越可靠）
        tasks = perf.get("tasksCompleted", 0)
        exp_weight = min(tasks / 50, 0.2)  # 最多 0.2 加成
        
        # 综合分数
        final_score = match_score * 0.6 + perf_score * 0.3 + exp_weight * 0.1
        
        return RoleCandidate(
            role_id=role["id"],
            function=role.get("function", ""),
            domain=role.get("domain", ""),
            capabilities=list(role_caps),
            match_score=match_score,
            performance_score=perf_score,
            final_score=final_score
        )
    
    def _ensure_diversity(self, candidates: List[RoleCandidate], size: int) -> List[RoleCandidate]:
        """确保职能多样性"""
        if len(candidates) <= size:
            return candidates
        
        selected = []
        functions_used = set()
        
        # 第一轮：每个职能选最好的
        for c in candidates:
            if c.function not in functions_used:
                selected.append(c)
                functions_used.add(c.function)
                
                if len(selected) >= size:
                    break
        
        # 第二轮：如果不够，按分数补充
        if len(selected) < size:
            for c in candidates:
                if c not in selected:
                    selected.append(c)
                    if len(selected) >= size:
                        break
        
        return selected
    
    def _generate_decision(self, selected: List[RoleCandidate], task: str) -> List[Dict]:
        """生成选角决策"""
        return [
            {
                "role": c.role_id,
                "function": c.function,
                "domain": c.domain,
                "reason": f"能力匹配度 {c.match_score:.0%}，历史评分 {c.performance_score*10:.1f}",
                "priority": i + 1,
                "capabilities": c.capabilities
            }
            for i, c in enumerate(selected)
        ]
    
    def infer_capabilities(self, task_description: str) -> List[str]:
        """从任务描述推断需要的能力"""
        # 关键词映射
        keyword_map = {
            # 分析类
            "分析": ["代码分析", "架构评估", "问题诊断"],
            "评估": ["架构评估", "技术选型"],
            "设计": ["架构设计", "方案设计"],
            
            # 创造类
            "编写": ["代码编写", "功能实现"],
            "实现": ["功能实现", "代码编写"],
            "开发": ["代码编写", "功能实现"],
            "创建": ["代码编写", "功能实现"],
            
            # 评审类
            "审查": ["代码审查", "安全分析"],
            "检查": ["代码审查", "质量检查"],
            "优化": ["性能优化", "代码优化"],
            
            # 执行类
            "执行": ["代码执行", "脚本运行"],
            "测试": ["测试执行", "覆盖率统计"],
            "部署": ["构建部署", "系统操作"],
            
            # 写作类
            "写作": ["长文写作", "结构设计"],
            "撰写": ["长文写作", "内容创作"],
            "文档": ["技术文档", "文档编写"],
            
            # 研究类
            "研究": ["信息检索", "数据分析"],
            "调研": ["信息检索", "文献综述"],
            "分析": ["数据分析", "批判性阅读"]
        }
        
        capabilities = set()
        desc_lower = task_description.lower()
        
        for keyword, caps in keyword_map.items():
            if keyword in desc_lower:
                capabilities.update(caps)
        
        return list(capabilities) if capabilities else ["代码编写"]  # 默认


# ============================================================================
# 便捷函数
# ============================================================================

def select_team_for_task(task_description: str, pm_type: str = "coding-pm") -> List[Dict]:
    """为任务选择团队"""
    selector = RoleSelector()
    
    # 推断能力需求
    required_caps = selector.infer_capabilities(task_description)
    
    # 选择团队
    return selector.select_team(task_description, required_caps, pm_type)


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ClawOS PM 选角")
    parser.add_argument("--task", help="任务描述")
    parser.add_argument("--pm", default="coding-pm", help="PM类型")
    parser.add_argument("--size", type=int, default=3, help="团队大小")
    
    args = parser.parse_args()
    
    if args.task:
        team = select_team_for_task(args.task, args.pm)
        print(json.dumps(team, indent=2, ensure_ascii=False))
    else:
        parser.print_help()
