# iMessage 集成配置示例

## OpenClaw + iMessage 集成方案

### 1. 基础配置 (已完成 ✅)

**工具**: imsg CLI v0.4.0
**状态**: 已安装并可用
**权限**: Full Disk Access ✅

### 2. 使用场景

#### 场景 A: Henry 主动通知
```python
# 在 OpenClaw 中使用
from skills.imsg import send_message

# 发送通知
send_message(
    to="lu_dongsheng@hotmail.com",
    text="🔔 任务完成提醒：AIchemist 项目已部署"
)
```

#### 场景 B: 用户通过 iMessage 控制
```python
# 监听 iMessage 指令
watch_messages(chat_id=5292, callback=handle_command)

def handle_command(message):
    if "状态" in message:
        return get_system_status()
    elif "部署" in message:
        return deploy_project()
```

### 3. 常用命令（通过 imsg-quick）

```bash
# 列出对话
./imsg-quick chats

# 查看历史
./imsg-quick history 5292

# 发送消息
./imsg-quick send lu_dongsheng@hotmail.com "测试消息"

# 监听新消息
./imsg-quick watch 5292
```

### 4. 权限配置清单

- [x] Full Disk Access (Terminal.app)
- [ ] Automation (Terminal 控制 Messages.app) - **需要手动配置**
- [x] Messages.app 运行中

### 5. 安全建议

1. **不要在消息中发送敏感信息**（API keys、密码等）
2. **定期清理历史消息**（如果包含敏感信息）
3. **仅信任的联系人**使用远程控制功能

### 6. 集成到 OpenClaw

#### 方法 1: 作为 Skill 使用
```python
# 在 OpenClaw 中直接调用
import subprocess

result = subprocess.run(
    ["imsg", "send", "--to", "lu_dongsheng@hotmail.com", "--text", "通知内容"],
    capture_output=True,
    text=True
)
```

#### 方法 2: 通过 Skill 文件
参考: `/opt/homebrew/lib/node_modules/openclaw/skills/imsg/SKILL.md`

### 7. 测试流程

```bash
# 1. 测试读取
./imsg-quick test

# 2. 测试发送（需要先配置 Automation 权限）
./imsg-quick send lu_dongsheng@hotmail.com "来自 Henry 的测试"

# 3. 测试监听
./imsg-quick watch 5292
```

---

## 下一步

1. **配置 Automation 权限**（如需发送功能）
   - 系统偏好设置 > 隐私与安全性 > 自动化
   - 勾选 Terminal 控制 Messages.app

2. **测试发送功能**
   ```bash
   ./imsg-quick send lu_dongsheng@hotmail.com "测试"
   ```

3. **集成到日常工作流**
   - 项目完成通知
   - 系统告警通知
   - 远程指令执行

---

*配置时间: 2026-02-14 23:50*
*状态: 基础功能可用 ✅*
