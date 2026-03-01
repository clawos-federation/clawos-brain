# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## iMessage (imsg)

### 配置状态
- ✅ **CLI工具**: /opt/homebrew/bin/imsg v0.4.0
- ✅ **读取权限**: 已有 Full Disk Access
- ✅ **数据库访问**: ~/Library/Messages/chat.db 可读
- ⚠️ **发送权限**: 需要 Automation 权限（在系统偏好设置中配置）

### 常用联系人
```
Chat ID 5292 - lu_dongsheng@hotmail.com (最近对话)
Chat ID 2305 - +8613701900881
Chat ID 5291 - +85261750254
```

### 常用命令
```bash
# 列出最近对话
imsg chats --limit 10

# 查看对话历史
imsg history --chat-id 5292 --limit 20

# 发送消息
imsg send --to "lu_dongsheng@hotmail.com" --text "测试消息"

# 监听新消息
imsg watch --chat-id 5292
```

### 权限配置
1. **Full Disk Access** (已有)
   - 系统偏好设置 > 隐私与安全性 > 完全磁盘访问权限
   - 添加: Terminal.app (或你使用的终端)

2. **Automation** (如需发送功能)
   - 系统偏好设置 > 隐私与安全性 > 自动化
   - 允许 Terminal 控制 Messages.app

---

## 之前的示例内容

### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod

---

Add whatever helps you do your job. This is your cheat sheet.
