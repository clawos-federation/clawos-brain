# iMessage (imsg) 配置指南 - 2026-02-14

## ✅ 安装状态

```
工具: imsg v0.4.0
路径: /opt/homebrew/bin/imsg
状态: ✅ 已安装并可用
Skill: ✓ ready
```

---

## 🔐 权限配置（重要！）

### 1. Full Disk Access（必需）
```
系统偏好设置 → 隐私与安全性 → 完全磁盘访问权限
添加你的终端应用（Terminal.app 或 iTerm2）
```

### 2. Automation 权限（发送消息必需）
```
首次使用 imsg send 时会自动提示
允许终端控制 Messages.app
```

### 3. Messages.app 配置
```
确保 Messages.app 已登录 iCloud/iMessage 账户
```

---

## 📱 基本使用

### 1. 列出最近的聊天
```bash
# 列出最近 10 个聊天
imsg chats --limit 10 --json

# 列出最近 20 个聊天（不带 JSON）
imsg chats --limit 20
```

### 2. 查看聊天历史
```bash
# 查看特定聊天的最近 20 条消息
imsg history --chat-id 5292 --limit 20 --json

# 包含附件
imsg history --chat-id 5292 --limit 20 --attachments
```

### 3. 发送消息
```bash
# 发送文本消息
imsg send --to "lu_dongsheng@hotmail.com" --text "测试消息"

# 发送到手机号
imsg send --to "+8613701900881" --text "你好"

# 发送带图片的消息
imsg send --to "lu_dongsheng@hotmail.com" --text "看这张图" --file /path/to/image.jpg

# 指定服务类型（iMessage/SMS）
imsg send --to "+8613701900881" --text "测试" --service sms
```

### 4. 监听聊天（实时）
```bash
# 实时监听特定聊天的新消息
imsg watch --chat-id 5292 --attachments
```

---

## 🎯 你当前的聊天列表

根据测试，你最近的聊天有：

| ID | 标识符 | 服务 | 最后消息时间 |
|----|--------|------|--------------|
| 5292 | lu_dongsheng@hotmail.com | iMessage | 2026-02-14 14:47 |
| 2305 | +8613701900881 | iMessage | 2026-02-14 09:18 |
| 5291 | +85261750254 | iMessage | 2026-01-31 01:29 |
| 689 | +8617317855559 | iMessage | 2025-10-22 04:39 |
| 245 | +8613801488780 | iMessage | 2025-07-02 01:12 |

---

## 💡 通过 Henry 使用 iMessage

### 示例对话
```
你: "查看最近的消息"
我: [执行 imsg chats --limit 10]

你: "给 lu_dongsheng@hotmail.com 发消息说'你好'"
我: [执行 imsg send --to "lu_dongsheng@hotmail.com" --text "你好"]

你: "查看和 +8613701900881 的聊天记录"
我: [执行 imsg history --chat-id 2305 --limit 20]
```

---

## ⚠️ 注意事项

1. **隐私敏感** - iMessage 包含私人对话，使用时注意隐私
2. **发送确认** - 发送消息前会显示确认提示
3. **服务类型** - 区分 iMessage（蓝色）和 SMS（绿色）
4. **附件路径** - 发送文件需要提供完整路径

---

## 🔧 高级用法

### 搜索消息
```bash
# 搜索包含特定文本的消息
imsg history --chat-id 5292 --json | jq '.[] | select(.text | contains("关键词"))'
```

### 导出聊天记录
```bash
# 导出为 JSON
imsg history --chat-id 5292 --limit 100 --json > chat_export.json

# 导出为纯文本
imsg history --chat-id 5292 --limit 100 > chat_export.txt
```

### 批量操作
```bash
# 批量发送（谨慎使用）
for msg in "消息1" "消息2" "消息3"; do
  imsg send --to "+8613701900881" --text "$msg"
  sleep 1
done
```

---

## 🎨 OpenClaw 集成

### 配置文件
位置: `/opt/homebrew/lib/node_modules/openclaw/skills/imsg/SKILL.md`

### 调用方式
- 通过 `read` 工具读取 skill 文件
- 使用 `exec` 执行 imsg 命令
- 返回格式化的结果

---

## 📊 测试结果

| 功能 | 状态 | 说明 |
|------|------|------|
| 安装 | ✅ | v0.4.0 |
| 列出聊天 | ✅ | 成功列出 5 个聊天 |
| 查看历史 | ⏳ | 需测试 |
| 发送消息 | ⏳ | 需要权限确认 |
| 监听模式 | ⏳ | 需测试 |

---

## 🚀 下一步

1. **测试发送消息**
   ```bash
   imsg send --to "你的邮箱或手机" --text "测试"
   ```

2. **测试查看历史**
   ```bash
   imsg history --chat-id 5292 --limit 10
   ```

3. **配置监听**（可选）
   ```bash
   imsg watch --chat-id 5292
   ```

---

*配置时间: 2026-02-14 22:50*
*状态: ✅ 已就绪*
