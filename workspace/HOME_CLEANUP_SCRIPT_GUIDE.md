# 方案B 深度清理脚本使用指南

**脚本路径**: `/Users/henry/openclaw-system/workspace/home_cleanup.sh`
**清理方案**: 方案B（深度清理）
**预计节省空间**: ~10.1GB

---

## 📋 清理内容

### 1. 系统缓存清理（~9.9GB）
- `.cache/` 目录内容
- 可重新构建，无风险

### 2. macOS 系统文件清理
- 所有 `.DS_Store` 文件
- macOS 会自动重建

### 3. 历史文件清理
- `.Rhistory`
- `.autodarwin_history`
- `.cooragent_history`
- `.claude.json.backup`

### 4. 临时文件删除
- 第四次开物革命相关文件（直接删除）
- 临时脚本（*.py, *.txt, *.csv）直接删除

### 5. 不再使用的工具清理
- `.EasyOCR`
- `.antigravity`
- `.cherrystudio`
- `.codex`
- `.crawl4ai`
- `.doppler`
- `.eva_cache`
- `.expo`

### 6. 空项目目录清理
- `workspace/`（空）
- `react-demo/`（空）
- `metagpt_output/`（空）
- `cookiecutters/`（空）
- `embedchain/`（空）

---

## 🚀 使用方法

### 方式1：直接执行（推荐）

```bash
cd /Users/henry/openclaw-system/workspace
./home_cleanup.sh
```

### 方式2：使用 bash

```bash
bash /Users/henry/openclaw-system/workspace/home_cleanup.sh
```

---

## 📋 执行流程

1. **显示清理计划**
   - 列出将要删除的所有内容
   - 显示预计节省空间

2. **询问确认**
   - 需要输入 `yes` 才能继续
   - 按 Ctrl+C 可以取消

3. **执行清理**
   - 按步骤删除
   - 实时显示进度
   - 记录日志

4. **生成报告**
   - 显示清理结果
   - 显示日志文件位置

---

## ⚠️ 重要提醒

### 清理前检查

1. ✅ 确认已备份重要文件
2. ✅ 检查临时脚本是否有用的代码
3. ✅ 确认不再使用的工具可以删除

### 清理前手动检查

```bash
# 检查临时脚本内容
head -20 ~/migrations.py
head -20 ~/models.py

# 检查空目录
ls -la ~/workspace/
ls -la ~/react-demo/

# 检查将要删除的工具
ls -la ~/.EasyOCR/
ls -la ~/.antigravity/
```

---

## 📊 日志和报告

### 日志文件

清理过程中会生成日志文件：
```
~/.openclaw/clawos/workspace/cleanup_log_YYYYMMDD_HHMMSS.txt
```

日志包含：
- 清理时间
- 每个步骤的详细信息
- 删除的文件列表

### 清理报告

清理完成后，脚本会显示：
- 清理时间
- 日志文件位置
- 归档目录位置
- 清理后目录大小

---

## 🔄 恢复方法

### 如果误删除了重要文件

检查日志文件，查看删除了哪些文件：
```bash
cat ~/.openclaw/clawos/workspace/cleanup_log_*.txt
```

**注意**: 此脚本直接删除文件，不归档！请仔细确认后再执行！

---

## 🎯 预期效果

### 清理前

```
.claude          376M
.cursor           872M
.cache           9.9G
总空间占用:     ~11.1GB
```

### 清理后

```
.claude          376M
.cursor           872M
.cache           0B (重建后)
总空间占用:     ~1.2GB
节省空间:      ~10GB
```

---

## ⚙️ 脚本安全特性

1. ✅ **显示清理计划** - 执行前显示所有内容
2. ✅ **确认机制** - 需要输入 `yes` 才能继续
3. ✅ **日志记录** - 所有操作都记录到日志文件
4. ✅ **彩色输出** - 不同级别用不同颜色显示
5. ✅ **错误处理** - 遇到错误立即停止
6. ✅ **直接删除** - 临时文件直接删除（不归档）
7. ✅ **空目录检查** - 空目录才删除

---

## 🐛 故障排除

### 问题：权限错误

```bash
# 确保脚本有执行权限
chmod +x ~/.openclaw/clawos/workspace/home_cleanup.sh
```

### 问题：找不到目录

```bash
# 检查 HOME 配置是否正确
echo $HOME

# 应该输出: /Users/henry
```

### 问题：删除失败

```bash
# 检查文件是否被占用
lsof | grep [文件名]

# 或者手动删除后再重新运行脚本
```

---

## 📞 支持和反馈

如果遇到问题：

1. 检查日志文件
2. 查看此使用指南
3. 询问 Henry

---

**创建时间**: 2026-02-10 19:46
**脚本版本**: 1.0
**清理方案**: 方案B（深度清理）
