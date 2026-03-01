# OpenClaw 会话问题分析报告

## 执行时间
2026-02-14 17:20

## 一、OpenClaw 安装检查

### 结果：**只有 1 份安装**

| 项目 | 值 |
|------|-----|
| 安装位置 | `/opt/homebrew/lib/node_modules/openclaw` |
| 版本 | `2026.2.12` |
| 二进制文件 | `/opt/homebrew/bin/openclaw` (符号链接) |
| npm 全局包 | `openclaw@2026.2.12`, `clawhub@0.4.0` |

**结论**: 没有重复安装，版本统一。

---

## 二、之前修复报告检查

### 目录: `/Users/dongshenglu/openclaw-system/workspace/reports/`

| 目录 | 内容 |
|------|------|
| `session-path-fix-2026-02-14-135027` | 空 (仅占位) |
| `session-path-fix-2026-02-14-135041` | sessions.cleaned.json, sessions.json.bak |
| `session-path-fix-2026-02-14-135054` | 完整报告 + 证据文件 |

### 修复尝试内容

之前的 GM Agent 进行了以下修复：
1. **normalizeMainKey 强化** - 对非法字符进行清洗
2. **显式 key 写入前 canonical rebuild** - 防止坏 key 直写
3. **sessions.json 清脏** - 移除非 canonical keys

### 问题：修复不彻底

之前的修复没有解决：
1. `channel` 字段错误 (`whatsapp` 而非 `webchat`)
2. `sessionFile` 绝对路径问题（上游 Bug）
3. `agent:henry:mainwww.` 这个坏 key 仍然存在

---

## 三、已执行的修复

### 修复 1: sessionFile 绝对路径 → 相对文件名

**问题**: `sessions.json` 中的 `sessionFile` 存储的是绝对路径：
```
/Users/dongshenglu/.openclaw/agents/henry/sessions/d631caa5-...jsonl
```

**修复后**: 只保留文件名
```
d631caa5-29a3-4dbf-9b80-62f399ecea15.jsonl
```

**备份**: `sessions.json.bak-absolute-path`

### 修复 2: channel 字段错误

**问题**: `agent:henry:main` 的 `channel` 是 `whatsapp`，但实际使用的是 `webchat`

**修复**: 将 `channel` 设置为 `deliveryContext.channel` 的值

**备份**: `sessions.json.bak-channel`

### 修复 3: 删除无效 session key

**问题**: `agent:henry:mainwww.` 是无效的 session key（带点）

**修复**: 删除此条目

**备份**: `sessions.json.bak-badkeys`

---

## 四、最终状态

```json
{
  "agent:henry:main": {
    "channel": "webchat",
    "sessionFile": "d631caa5-29a3-4dbf-9b80-62f399ecea15.jsonl"
  },
  "agent:henry:ac9edaf9ebee0c272f265628451ed46914e3e490bd2bcb36bc27fdbd5f522ace": {
    "channel": "webchat",
    "sessionFile": "cfef5f8e-d449-4d0d-a5db-bf7fbb097b15.jsonl"
  }
}
```

✅ 所有 sessionFile 都是相对路径
✅ 所有 channel 都是 webchat
✅ 所有 session keys 都是有效格式

---

## 五、上游 Bug 分析

### Bug 1: sessionFile 写入绝对路径

**位置**: OpenClaw 源码 `resolveSessionTranscriptPath()`

**问题**: 
```javascript
// paths-CnE9bV4t.js:36
function resolvePathWithinSessionsDir(sessionsDir, candidate) {
    ...
    return resolvedCandidate;  // 返回绝对路径！
}
```

**影响**: 当 `nextEntry.sessionFile = nextSessionFile` 赋值时，写入的是绝对路径。

**建议修复**: 返回相对文件名而非绝对路径
```javascript
return path.basename(resolvedCandidate);  // 应该只返回文件名
```

### Bug 2: channel 字段不一致

**问题**: `channel` 字段在某些情况下被设置为错误值（如 `whatsapp`），与实际使用的 `deliveryContext.channel` 不一致。

**建议**: 在写入 sessions.json 时，始终从 `deliveryContext.channel` 同步 `channel` 字段。

---

## 六、建议

### 短期（用户可操作）

1. **定期清理 sessions.json**：
   ```bash
   # 检查并修复 sessionFile 绝对路径
   python3 -c "
   import json, os
   p = os.path.expanduser('~/.openclaw/agents/henry/sessions/sessions.json')
   d = json.load(open(p))
   for k, e in d.items():
       if e.get('sessionFile', '').startswith('/'):
           e['sessionFile'] = os.path.basename(e['sessionFile'])
   json.dump(d, open(p, 'w'), indent=2)
   "
   ```

2. **监控错误日志**：
   ```bash
   grep "Session file path must be within sessions directory" /tmp/openclaw/*.log
   ```

### 长期（需要上游修复）

1. **向 OpenClaw 提交 Issue/PR**：
   - `resolvePathWithinSessionsDir` 应该返回相对路径
   - `channel` 字段应该与 `deliveryContext.channel` 同步

2. **升级 OpenClaw**：
   - 关注新版本是否修复此问题

---

## 七、验证步骤

重启 Gateway 并测试：

```bash
# 1. 重启
openclaw gateway restart

# 2. 打开 TUI
openclaw tui

# 3. 发送测试消息
# 应该不再出现 "Session file path must be within sessions directory" 错误
# TUI 状态栏应该显示 "session main" 而非 "whatsapp:g-agent-henry-main"
```

---

## 八、文件清单

### 备份文件
- `sessions.json.bak-1771046200` - 最早备份
- `sessions.json.bak-mainwww-fix` - mainwww 修复前
- `sessions.json.bak-absolute-path` - 绝对路径修复前
- `sessions.json.bak-channel` - channel 修复前
- `sessions.json.bak-badkeys` - 删除坏 key 前

### 当前有效文件
- `sessions.json` - 已修复的版本
