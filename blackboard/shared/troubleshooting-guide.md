# ClawOS 故障排查手册

---

## 🔴 紧急问题

### 问题 1: OpenClaw 无法启动

**症状**:
```bash
$ openclaw start
Error: Cannot start OpenClaw
```

**检查**:
```bash
# 1. 检查端口占用
lsof -i :3000

# 2. 检查配置文件
openclaw config validate

# 3. 查看详细日志
openclaw logs --level debug
```

**解决**:
```bash
# 杀死占用进程
kill -9 $(lsof -t -i :3000)

# 修复配置
openclaw config fix

# 重新启动
openclaw start
```

---

### 问题 2: GM 持续超时

**症状**: 所有任务都超时

**检查**:
```bash
# 1. 检查 GM token 消耗
openclaw stats tokens | grep gm

# 2. 检查 summary.md
ls ~/clawos/blackboard/tasks/*/summary.md

# 3. 检查 research-pm 权限
cat ~/openclaw-system/clawos/openclaw.json | grep -A5 '"gm"' | grep allowAgents
```

**解决**:
```bash
# 方案 1: 添加 research-pm 到 allowAgents
vim ~/openclaw-system/clawos/openclaw.json
# 在 allowAgents 中添加 "research-pm"

# 方案 2: 创建缺失的 summary.md
~/openclaw-system/clawos/scripts/generate-summary.sh ~/clawos/blackboard/tasks/{task-id}

# 方案 3: 重启 OpenClaw
openclaw gateway restart
```

---

### 问题 3: 节点失去连接

**症状**: Federation 节点离线

**检查**:
```bash
# 1. 检查网络
ping {节点IP}

# 2. 检查 OpenClaw
ssh {节点IP} "openclaw status"

# 3. 检查 token
openclaw federation token show
```

**解决**:
```bash
# 方案 1: 重启节点 OpenClaw
ssh {节点IP} "openclaw gateway restart"

# 方案 2: 重新生成 token
openclaw federation token regenerate --node {node-id}

# 方案 3: 更新配置
# 在节点上更新 federation.json 中的 token
```

---

## 🟡 常见问题

### 问题 4: Assistant 响应慢

**症状**: 响应时间 >10s

**检查**:
```bash
# 1. 检查系统负载
top -l 1 | grep "CPU usage"

# 2. 检查 OpenClaw 进程
ps aux | grep openclaw

# 3. 检查网络延迟
ping api.openai.com
```

**解决**:
```bash
# 方案 1: 重启 OpenClaw
openclaw gateway restart

# 方案 2: 清理日志
rm ~/clawos/logs/*.log.old

# 方案 3: 升级硬件/网络
```

---

### 问题 5: Token 消耗过高

**症状**: 成本超出预期

**检查**:
```bash
# 1. 查看消耗统计
openclaw stats tokens --by-agent

# 2. 查看最近调用
openclaw logs --grep "tokens" | tail -20

# 3. 检查是否有循环调用
openclaw logs --grep "loop" | tail -10
```

**解决**:
```bash
# 方案 1: 启用 Prompt Cache
vim ~/openclaw-system/clawos/openclaw.json
# 添加 cache 配置

# 方案 2: 精简 SOUL 文件
vim ~/openclaw-system/clawos/souls/command/gm.soul.md
# 删除冗余内容

# 方案 3: 调整模型分配
vim ~/openclaw-system/clawos/config/model-mapping.json
# 使用更便宜的模型
```

---

### 问题 6: Blackboard 数据丢失

**症状**: 任务数据不完整

**检查**:
```bash
# 1. 检查目录权限
ls -la ~/clawos/blackboard/

# 2. 检查磁盘空间
df -h ~/clawos/

# 3. 检查同步状态
openclaw blackboard status
```

**解决**:
```bash
# 方案 1: 修复权限
chmod -R 755 ~/clawos/blackboard/

# 方案 2: 从备份恢复
cp -r ~/clawos/blackboard.backup/* ~/clawos/blackboard/

# 方案 3: 从主脑同步
openclaw blackboard pull --force
```

---

## 🟢 性能优化

### 优化 1: 减少 Token 消耗

**方法**:
1. 启用 Prompt Cache（降 90%）
2. 精简 SOUL 文件（降 60%）
3. 使用便宜的模型

**验证**:
```bash
# 启用前
openclaw stats tokens | grep "Total"

# 启用后
openclaw stats tokens | grep "Total"

# 预期: 减少 50-90%
```

---

### 优化 2: 加快响应速度

**方法**:
1. 使用本地模型（关键任务）
2. 启用缓存
3. 批处理任务

**验证**:
```bash
# 测试响应时间
time openclaw agent run gm --task "测试"

# 预期: <30s
```

---

### 优化 3: 提高可靠性

**方法**:
1. 添加健康检查 cron
2. 设置自动重启
3. 配置告警

**配置**:
```bash
# 添加 cron
crontab -e

# 每 5 分钟检查一次
*/5 * * * * ~/openclaw-system/clawos/scripts/health-check.sh >> ~/clawos/logs/health.log 2>&1
```

---

## 🔧 工具和脚本

### 诊断脚本

```bash
# 完整诊断
~/openclaw-system/clawos/scripts/health-check.sh

# 监控日志
tail -f ~/clawos/logs/monitor.log

# 查看错误
grep -i "error\|fail" ~/clawos/logs/*.log | tail -20
```

### 重置脚本

```bash
# 重置 Blackboard
rm -rf ~/clawos/blackboard/*
mkdir -p ~/clawos/blackboard/{tasks,gm,shared,roles}

# 重置配置
cp ~/openclaw-system/clawos/openclaw.json.backup ~/openclaw-system/clawos/openclaw.json

# 重启 OpenClaw
openclaw gateway restart
```

---

## 📞 获取帮助

### 日志收集

```bash
# 收集所有日志
tar -czf clawos-logs-$(date +%Y%m%d).tar.gz ~/clawos/logs/

# 收集配置
tar -czf clawos-config-$(date +%Y%m%d).tar.gz ~/openclaw-system/clawos/config/

# 收集状态
openclaw status > clawos-status.txt
```

### 联系支持

- GitHub Issues: https://github.com/openclaw/openclaw/issues
- Discord: https://discord.com/invite/clawd
- 文档: https://docs.openclaw.ai

---

**版本**: 1.0
**最后更新**: 2026-02-26
