#!/usr/bin/env python3
"""
ClawOS 消息队列系统
实现 Agent 间标准化通信
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from enum import Enum

# ============================================================================
# 消息类型定义
# ============================================================================

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

class Priority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AgentRef:
    agent: str
    tier: str
    session: Optional[str] = None

@dataclass
class Message:
    version: str
    id: str
    trace_id: str
    from_agent: AgentRef
    to_agent: AgentRef
    type: MessageType
    priority: Priority
    timestamp: str
    ttl: int
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self):
        return {
            "version": self.version,
            "id": self.id,
            "traceId": self.trace_id,
            "from": asdict(self.from_agent),
            "to": asdict(self.to_agent),
            "type": self.type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "payload": self.payload,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        return cls(
            version=data["version"],
            id=data["id"],
            trace_id=data["traceId"],
            from_agent=AgentRef(**data["from"]),
            to_agent=AgentRef(**data["to"]),
            type=MessageType(data["type"]),
            priority=Priority(data["priority"]),
            timestamp=data["timestamp"],
            ttl=data["ttl"],
            payload=data["payload"],
            metadata=data["metadata"]
        )

# ============================================================================
# 消息队列
# ============================================================================

class MessageQueue:
    """基于文件系统的消息队列"""
    
    def __init__(self, base_path: str = "~/clawos/blackboard"):
        self.base_path = Path(base_path).expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_inbox_path(self, agent_id: str) -> Path:
        """获取 Agent 的 inbox 路径"""
        inbox = self.base_path / agent_id / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        return inbox
    
    def _get_processed_path(self, agent_id: str) -> Path:
        """获取已处理消息路径"""
        processed = self.base_path / agent_id / "processed"
        processed.mkdir(parents=True, exist_ok=True)
        return processed
    
    def send(self, message: Message) -> str:
        """
        发送消息到目标 Agent 的 inbox
        
        Args:
            message: 消息对象
        
        Returns:
            消息 ID
        """
        inbox = self._get_inbox_path(message.to_agent.agent)
        msg_file = inbox / f"{message.id}.json"
        
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(message.to_dict(), f, indent=2, ensure_ascii=False)
        
        return message.id
    
    def receive(self, agent_id: str, limit: int = 10) -> List[Message]:
        """
        从 Agent 的 inbox 接收消息
        
        Args:
            agent_id: Agent ID
            limit: 最大消息数
        
        Returns:
            消息列表
        """
        inbox = self._get_inbox_path(agent_id)
        messages = []
        
        for msg_file in sorted(inbox.glob("*.json"))[:limit]:
            try:
                with open(msg_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    msg = Message.from_dict(data)
                    
                    # 检查是否过期
                    if not self._is_expired(msg):
                        messages.append(msg)
                    else:
                        # 删除过期消息
                        msg_file.unlink()
            except Exception as e:
                print(f"Error reading message {msg_file}: {e}")
        
        return messages
    
    def ack(self, agent_id: str, message_id: str):
        """
        确认消息已处理，移动到 processed 目录
        
        Args:
            agent_id: Agent ID
            message_id: 消息 ID
        """
        inbox = self._get_inbox_path(agent_id)
        processed = self._get_processed_path(agent_id)
        
        src = inbox / f"{message_id}.json"
        dst = processed / f"{message_id}.json"
        
        if src.exists():
            src.rename(dst)
    
    def _is_expired(self, message: Message) -> bool:
        """检查消息是否过期"""
        msg_time = datetime.fromisoformat(message.timestamp)
        now = datetime.now(msg_time.tzinfo)
        age_seconds = (now - msg_time).total_seconds()
        return age_seconds > message.ttl

# ============================================================================
# 消息构建器
# ============================================================================

class MessageBuilder:
    """消息构建器"""
    
    def __init__(self, from_agent: str, from_tier: str, session: Optional[str] = None):
        self.from_agent = AgentRef(
            agent=from_agent,
            tier=from_tier,
            session=session
        )
        self.trace_id = str(uuid.uuid4())
    
    def request(self, to_agent: str, to_tier: str, action: str, 
                params: dict, priority: Priority = Priority.NORMAL,
                deadline: Optional[str] = None) -> Message:
        """构建请求消息"""
        payload = {
            "action": action,
            "params": params
        }
        if deadline:
            payload["deadline"] = deadline
        
        return Message(
            version="1.0",
            id=str(uuid.uuid4()),
            trace_id=self.trace_id,
            from_agent=self.from_agent,
            to_agent=AgentRef(agent=to_agent, tier=to_tier),
            type=MessageType.REQUEST,
            priority=priority,
            timestamp=datetime.now().isoformat(),
            ttl=3600,
            payload=payload,
            metadata={}
        )
    
    def response(self, to_agent: str, to_tier: str, request_id: str,
                 status: str, result: Any, error: Optional[str] = None) -> Message:
        """构建响应消息"""
        return Message(
            version="1.0",
            id=str(uuid.uuid4()),
            trace_id=self.trace_id,
            from_agent=self.from_agent,
            to_agent=AgentRef(agent=to_agent, tier=to_tier),
            type=MessageType.RESPONSE,
            priority=Priority.NORMAL,
            timestamp=datetime.now().isoformat(),
            ttl=3600,
            payload={
                "requestId": request_id,
                "status": status,
                "result": result,
                "error": error
            },
            metadata={}
        )
    
    def notification(self, to_agent: str, to_tier: str, event: str,
                     message: str, progress: Optional[dict] = None,
                     priority: Priority = Priority.NORMAL) -> Message:
        """构建通知消息"""
        payload = {
            "event": event,
            "message": message
        }
        if progress:
            payload["progress"] = progress
        
        return Message(
            version="1.0",
            id=str(uuid.uuid4()),
            trace_id=self.trace_id,
            from_agent=self.from_agent,
            to_agent=AgentRef(agent=to_agent, tier=to_tier),
            type=MessageType.NOTIFICATION,
            priority=priority,
            timestamp=datetime.now().isoformat(),
            ttl=86400,  # 通知保留更久
            payload=payload,
            metadata={}
        )
    
    def error(self, to_agent: str, to_tier: str, request_id: str,
              code: str, message: str, recoverable: bool = True,
              suggestion: Optional[str] = None) -> Message:
        """构建错误消息"""
        return Message(
            version="1.0",
            id=str(uuid.uuid4()),
            trace_id=self.trace_id,
            from_agent=self.from_agent,
            to_agent=AgentRef(agent=to_agent, tier=to_tier),
            type=MessageType.ERROR,
            priority=Priority.HIGH,
            timestamp=datetime.now().isoformat(),
            ttl=86400,
            payload={
                "requestId": request_id,
                "code": code,
                "message": message,
                "recoverable": recoverable,
                "suggestion": suggestion
            },
            metadata={}
        )

# ============================================================================
# 便捷函数
# ============================================================================

def send_task_request(from_agent: str, from_tier: str, 
                      to_agent: str, to_tier: str,
                      task_type: str, task_description: str,
                      task_params: dict = None) -> str:
    """发送任务请求"""
    builder = MessageBuilder(from_agent, from_tier)
    queue = MessageQueue()
    
    msg = builder.request(
        to_agent=to_agent,
        to_tier=to_tier,
        action="task.assign",
        params={
            "type": task_type,
            "description": task_description,
            "params": task_params or {}
        }
    )
    
    return queue.send(msg)


def send_progress_notification(from_agent: str, from_tier: str,
                               to_agent: str, to_tier: str,
                               event: str, message: str,
                               current: int, total: int) -> str:
    """发送进度通知"""
    builder = MessageBuilder(from_agent, from_tier)
    queue = MessageQueue()
    
    msg = builder.notification(
        to_agent=to_agent,
        to_tier=to_tier,
        event=event,
        message=message,
        progress={
            "current": current,
            "total": total,
            "percent": round(current / total * 100, 1) if total > 0 else 0
        }
    )
    
    return queue.send(msg)


def check_inbox(agent_id: str, process: bool = True) -> List[dict]:
    """检查并返回 inbox 中的消息"""
    queue = MessageQueue()
    messages = queue.receive(agent_id)
    
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "from": msg.from_agent.agent,
            "type": msg.type.value,
            "priority": msg.priority.value,
            "payload": msg.payload,
            "timestamp": msg.timestamp
        })
        
        if process:
            queue.ack(agent_id, msg.id)
    
    return result


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ClawOS Message Queue")
    parser.add_argument("--send", help="Send a test message")
    parser.add_argument("--check", help="Check inbox for agent")
    parser.add_argument("--from", dest="from_agent", help="From agent")
    parser.add_argument("--to", dest="to_agent", help="To agent")
    parser.add_argument("--message", help="Message content")
    
    args = parser.parse_args()
    
    if args.check:
        messages = check_inbox(args.check, process=False)
        print(json.dumps(messages, indent=2, ensure_ascii=False))
    
    elif args.send and args.from_agent and args.to_agent:
        msg_id = send_task_request(
            from_agent=args.from_agent,
            from_tier="command",
            to_agent=args.to_agent,
            to_tier="pm",
            task_type="test",
            task_description=args.message or "Test message"
        )
        print(f"Message sent: {msg_id}")
    
    else:
        parser.print_help()
