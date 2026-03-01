#!/usr/bin/env python3
"""
Henry 自我质量检查系统 - Henry Self Quality Check
Henry 执行前的快速质量检查，确保输出符合基本标准
"""

from datetime import datetime
from typing import Dict, List, Any
import json


class HenrySelfChecker:
    """Henry 自我质量检查器"""
    
    def __init__(self):
        self.check_levels = {
            "basic": {
                "name": "基础验证",
                "required": True,
                "checklist": [
                    "execution_success",      # 执行成功
                    "result_exists",         # 结果存在
                    "no_errors"            # 无错误
                ]
            },
            "format": {
                "name": "格式检查",
                "required": True,
                "checklist": [
                    "proper_structure",      # 结构正确
                    "consistent_format",      # 格式一致
                    "readable"              # 可读性
                ]
            },
            "safety": {
                "name": "安全检查",
                "required": True,
                "checklist": [
                    "no_dangerous_commands", # 无危险命令
                    "no_sensitive_data",     # 无敏感数据泄露
                    "permissions_safe"      # 权限安全
                ]
            },
            "completeness": {
                "name": "完整性检查",
                "required": True,
                "checklist": [
                    "addresses_task",        # 回应任务
                    "covers_requirements",   # 满足要求
                    "sufficient_detail"      # 细节充足
                ]
            },
            "logic": {
                "name": "逻辑检查",
                "required": False,  # 可选，耗时较长
                "checklist": [
                    "coherent",             # 逻辑连贯
                    "no_contradictions",     # 无矛盾
                    "reasonable"            # 合理
                ]
            },
            "consistency": {
                "name": "一致性检查",
                "required": False,
                "checklist": [
                    "consistent_with_context",  # 与上下文一致
                    "consistent_with_history",  # 与历史一致
                    "terminology_consistent"  # 术语一致
                ]
            }
        }
        
        # 质量阈值
        self.thresholds = {
            "pass_rate_high": 1.0,      # 100% 通过
            "pass_rate_good": 0.85,     # 85% 通过
            "pass_rate_min": 0.70       # 70% 通过（最低标准）
        }
    
    def check(self, result: Dict, task: str, context: Dict = None) -> Dict:
        """
        执行质量检查
        
        Args:
            result: 执行结果
            task: 原始任务
            context: 上下文信息（可选）
        
        Returns:
            检查结果字典
        """
        if context is None:
            context = {}
        
        # 执行所有检查
        all_checks = {}
        for check_id, check_config in self.check_levels.items():
            checks = self._run_check(
                check_id, check_config, result, task, context
            )
            all_checks[check_id] = checks
        
        # 计算总体通过率
        total_checks = sum(len(v) for v in all_checks.values())
        passed_checks = sum(
            sum(1 for check in v.values() if check)
            for v in all_checks.values()
        )
        pass_rate = passed_checks / total_checks if total_checks > 0 else 1.0
        
        # 确定总体状态
        status = self._determine_status(pass_rate)
        
        # 确定行动
        action = self._determine_action(status, pass_rate, result)
        
        return {
            "passed": action["proceed"],
            "pass_rate": round(pass_rate * 100, 1),
            "status": status,
            "all_checks": all_checks,
            "action": action["name"],
            "recommendation": action["recommendation"],
            "checks_summary": {
                "total": total_checks,
                "passed": passed_checks,
                "failed": total_checks - passed_checks
            },
            "checked_at": datetime.now().isoformat()
        }
    
    def _run_check(self, check_id: str, config: Dict, 
                   result: Dict, task: str, context: Dict) -> Dict[str, bool]:
        """执行单个检查级别"""
        
        checks = {}
        
        for check_item in config["checklist"]:
            check_method_name = f"_check_{check_item}"
            check_method = getattr(self, check_method_name, None)
            
            if check_method:
                checks[check_item] = check_method(result, task, context)
            else:
                # 检查方法不存在，默认通过
                checks[check_item] = True
        
        return checks
    
    def _determine_status(self, pass_rate: float) -> str:
        """确定状态"""
        if pass_rate >= 100:
            return "excellent"
        elif pass_rate >= 85:
            return "good"
        elif pass_rate >= 70:
            return "acceptable"
        else:
            return "failed"
    
    def _determine_action(self, status: str, pass_rate: float, result: Dict) -> Dict:
        """确定行动"""
        if status == "excellent":
            return {
                "name": "proceed",
                "proceed": True,
                "recommendation": "质量优秀，直接输出"
            }
        elif status == "good":
            return {
                "name": "proceed_with_warnings",
                "proceed": True,
                "recommendation": "质量良好，可直接输出"
            }
        elif status == "acceptable":
            return {
                "name": "proceed_with_minor_issues",
                "proceed": True,
                "recommendation": "质量可接受，存在次要问题，建议继续或上报"
            }
        else:
            return {
                "name": "self_correct_or_escalate",
                "proceed": False,
                "recommendation": "质量不达标，需要自我修正或上报 GM Agent"
            }
    
    # === 基础验证检查 ===
    def _check_execution_success(self, result: Dict, task: str, context: Dict) -> bool:
        """检查执行是否成功"""
        if not result:
            return False
        
        # 检查执行标记
        if result.get("executed"):
            return True
        
        # 检查错误字段
        if result.get("error"):
            return False
        
        # 检查成功标记
        if result.get("success", False) is False:
            return False
        
        return True
    
    def _check_result_exists(self, result: Dict, task: str, context: Dict) -> bool:
        """检查结果是否存在"""
        # 有内容
        if result.get("content"):
            return True
        
        # 有数据
        if result.get("data"):
            return True
        
        # 有结果
        if result.get("result"):
            return True
        
        # 有输出
        if result.get("output"):
            return True
        
        return False
    
    def _check_no_errors(self, result: Dict, task: str, context: Dict) -> bool:
        """检查无错误"""
        # 检查错误列表
        if result.get("errors") and len(result["errors"]) > 0:
            return False
        
        # 检查异常
        if result.get("exception"):
            return False
        
        # 检查失败标记
        if result.get("failed", False):
            return False
        
        return True
    
    # === 格式检查 ===
    def _check_proper_structure(self, result: Dict, task: str, context: Dict) -> bool:
        """检查结构正确"""
        # 结果应该是字典
        if not isinstance(result, dict):
            return False
        
        # 应该有基本字段
        # 实际结果在 result["result"] 或类似字段
        result_content = (
            result.get("result") or 
            result.get("content") or 
            result.get("output") or 
            result
        )
        
        # 结果内容应该存在
        if not result_content:
            return False
        
        return True
    
    def _check_consistent_format(self, result: Dict, task: str, context: Dict) -> bool:
        """检查格式一致"""
        # 对于 Henry，格式应该简洁清晰
        # 结果应该有清晰的字段
        required_fields = ["result", "status"]
        
        result_content = result.get("result", {})
        if isinstance(result_content, dict):
            # 检查是否有基本字段
            has_basic_info = any(
                field in result_content or result
                for field in ["content", "data", "output", "message"]
            )
            return has_basic_info
        
        return True  # 非字典结果不做严格检查
    
    def _check_readable(self, result: Dict, task: str, context: Dict) -> bool:
        """检查可读性"""
        # 结果应该包含可读的文本
        # 检查关键内容字段
        content = (
            result.get("content") or
            result.get("message") or
            str(result.get("result", ""))
        )
        
        # 应该有实际内容（不是空或只包含空白）
        if not content or not content.strip():
            return False
        
        # 应该是合理的长度（太短可能不完整）
        if len(content.strip()) < 10:
            return False
        
        return True
    
    # === 安全检查 ===
    def _check_no_dangerous_commands(self, result: Dict, task: str, context: Dict) -> bool:
        """检查无危险命令"""
        # 检查执行过的命令
        if result.get("commands"):
            dangerous_patterns = [
                "rm -rf /",
                "dd if=/dev/zero",
                ":(){ :|:& };:",
                "sudo rm -rf",
                "del /f /q"
            ]
            
            for command in result["commands"]:
                if isinstance(command, str):
                    for pattern in dangerous_patterns:
                        if pattern in command:
                            return False
        
        return True
    
    def _check_no_sensitive_data(self, result: Dict, task: str, context: Dict) -> bool:
        """检查无敏感数据泄露"""
        # 结果不应该包含敏感信息
        # 检查内容中是否包含密码、token 等
        sensitive_patterns = [
            r"password['\"]?\s*[:=]",
            r"api_key['\"]?\s*[:=]",
            r"secret['\"]?\s*[:=]",
            r"token['\"]?\s*[:=]",
            r"sk-[a-zA-Z0-9]{32,}"  # Stripe keys
        ]
        
        import re
        content = str(result)
        
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # 注意：如果任务本身就是关于敏感数据（如密码生成），则可以接受
                # 但需要明确的任务说明
                if not any(kw in task.lower() for kw in ["generate", "create", "show"]):
                    return False
        
        return True
    
    def _check_permissions_safe(self, result: Dict, task: str, context: Dict) -> bool:
        """检查权限安全"""
        # 检查是否建议了不安全的权限
        content = str(result)
        
        # 检查危险权限
        dangerous_perms = [
            "chmod 777",
            "chmod a=rwx",
            "sudo without password",
            "root user without restriction"
        ]
        
        for perm in dangerous_perms:
            if perm.lower() in content.lower():
                return False
        
        return True
    
    # === 完整性检查 ===
    def _check_addresses_task(self, result: Dict, task: str, context: Dict) -> bool:
        """检查回应任务"""
        # 结果应该回应任务要求
        # 简化：检查结果内容是否与任务相关
        task_words = set(task.lower().split())
        
        result_content = str(result.get("result", ""))
        result_words = set(result_content.lower().split())
        
        # 至少有一些重叠
        overlap = task_words.intersection(result_words)
        
        # 任务至少有一个词出现在结果中
        # 或者结果有明确的内容
        return len(overlap) > 0 or len(result_content) > 100
    
    def _check_covers_requirements(self, result: Dict, task: str, context: Dict) -> bool:
        """检查满足要求"""
        # 检查任务中的要求是否被满足
        # 简化：检查结果是否完整
        
        result_content = str(result.get("result", ""))
        
        # 结果应该有实质性内容
        if len(result_content.strip()) < 50:
            # 太短，可能不完整
            return False
        
        # 检查是否包含 "done", "completed", "finished" 等完成标记
        completion_markers = ["done", "completed", "finished", "success", "created", "generated"]
        has_completion = any(
            marker in result_content.lower()
            for marker in completion_markers
        )
        
        # 或者有实际的输出内容
        has_content = len(result_content) > 200
        
        return has_completion or has_content
    
    def _check_sufficient_detail(self, result: Dict, task: str, context: Dict) -> bool:
        """检查细节充足"""
        # 结果应该有足够的细节
        result_content = str(result.get("result", ""))
        
        # 基于任务复杂度检查细节
        # 简单任务可以简洁，复杂任务需要更多细节
        task_complexity = task.count(" ") + task.count("and") + task.count("then")
        
        min_length = {
            "simple": 50,    # 简单任务至少50字符
            "medium": 150,   # 中等任务至少150字符
            "complex": 300   # 复杂任务至少300字符
        }
        
        if task_complexity < 5:
            required_length = min_length["simple"]
        elif task_complexity < 10:
            required_length = min_length["medium"]
        else:
            required_length = min_length["complex"]
        
        return len(result_content.strip()) >= required_length
    
    # === 逻辑检查 ===
    def _check_coherent(self, result: Dict, task: str, context: Dict) -> bool:
        """检查逻辑连贯"""
        # 简化：结果内容应该逻辑通顺
        # 检查是否有自相矛盾
        content = str(result).lower()
        
        # 检查常见矛盾
        contradictions = [
            ("yes", "no"),
            ("true", "false"),
            ("succeeded", "failed"),
            ("completed", "not completed")
        ]
        
        for a, b in contradictions:
            if a in content and b in content:
                # 如果两个都在，检查是否在合理的上下文中
                # 简化：如果两个词的距离小于50字符，可能是矛盾
                pos_a = content.find(a)
                pos_b = content.find(b)
                if abs(pos_a - pos_b) < 50:
                    return False
        
        return True
    
    def _check_no_contradictions(self, result: Dict, task: str, context: Dict) -> bool:
        """检查无矛盾"""
        # 与 _check_coherent 类似
        # 检查结果内部的逻辑一致性
        return self._check_coherent(result, task, context)
    
    def _check_reasonable(self, result: Dict, task: str, context: Dict) -> bool:
        """检查合理"""
        # 检查结果是否合理
        # 简化：不应该有不可能的结果
        
        # 检查结果是否说"impossible"或类似词汇
        content = str(result).lower()
        
        impossible_indicators = [
            "impossible", "cannot be done", "not possible",
            "i don't know", "i cannot"
        ]
        
        for indicator in impossible_indicators:
            if indicator in content:
                # 除非任务本身就是询问可能性
                if "can" not in task.lower():
                    return False
        
        return True
    
    # === 一致性检查 ===
    def _check_consistent_with_context(self, result: Dict, task: str, context: Dict) -> bool:
        """检查与上下文一致"""
        # 检查结果是否与提供的上下文一致
        # 简化：如果有上下文中的约束，结果应该遵守
        
        if not context:
            return True  # 无上下文，无法检查
        
        # 检查语言风格是否一致
        if context.get("language"):
            expected_lang = context["language"]
            # 简化：不检查实际语言（需要NLP），只做标记
            pass
        
        return True
    
    def _check_consistent_with_history(self, result: Dict, task: str, context: Dict) -> bool:
        """检查与历史一致"""
        # 检查是否与之前的操作冲突
        # 简化：检查是否删除之前创建的文件等
        
        # 这个需要实际的历史数据
        # 简化：假设一致
        return True
    
    def _check_terminology_consistent(self, result: Dict, task: str, context: Dict) -> bool:
        """检查术语一致"""
        # 检查术语使用是否一致
        # 简化：不检查（需要NLP）
        return True


def main():
    """测试 Henry 自我质量检查"""
    checker = HenrySelfChecker()
    
    # 测试案例
    test_cases = [
        {
            "name": "优秀结果",
            "task": "Create a README file",
            "result": {
                "executed": True,
                "result": {
                    "content": "# Project Title\n\nThis is a README file.\n\n## Installation\n\nInstall dependencies with npm install.\n\n## Usage\n\nRun with npm start."
                }
            }
        },
        {
            "name": "不完整结果",
            "task": "Build a user authentication system",
            "result": {
                "executed": True,
                "result": {
                    "content": "Auth system created."
                }
            }
        },
        {
            "name": "有错误的结果",
            "task": "Read a file",
            "result": {
                "executed": True,
                "errors": ["File not found"],
                "result": {}
            }
        }
    ]
    
    print("=" * 80)
    print("Henry 自我质量检查系统测试")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print("-" * 80)
        print(f"任务: {test_case['task']}")
        print()
        
        result = checker.check(test_case['result'], test_case['task'])
        
        print(f"通过率: {result['pass_rate']}%")
        print(f"状态: {result['status']}")
        print(f"行动: {result['action']}")
        print(f"建议: {result['recommendation']}")
        print()
        print(f"检查汇总:")
        print(f"  总检查: {result['checks_summary']['total']}")
        print(f"  通过: {result['checks_summary']['passed']}")
        print(f"  失败: {result['checks_summary']['failed']}")
        print()
        
        # 显示失败的检查
        if result['checks_summary']['failed'] > 0:
            print("失败的检查:")
            for check_level, checks in result['all_checks'].items():
                for check_name, passed in checks.items():
                    if not passed:
                        print(f"  - {check_level}: {check_name}")
        print()


if __name__ == "__main__":
    main()
