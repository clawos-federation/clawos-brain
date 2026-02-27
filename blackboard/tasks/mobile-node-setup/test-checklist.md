# ClawOS Federation 测试清单

## 节点连接测试

### Mac mini (主脑)
```bash
# 检查 OpenClaw 状态
openclaw status

# 检查 Federation
openclaw federation status

# 生成节点 token
openclaw federation token generate --node mobile
```

### MacBook (移动节点)
```bash
# 安装后测试
openclaw status

# 测试连接主脑
ping dongsheng-mac-mini.local

# 测试 OpenClaw 端口
nc -zv dongsheng-mac-mini.local 3000

# 测试 Federation
openclaw federation ping
```

---

## Agent 功能测试

### 测试 assistant
在 MacBook 上：
```
对 assistant 说："测试移动节点连接"
```

预期响应：
```
移动节点 (mobile) 已连接到 ClawOS Federation
当前节点: MacBook
主脑状态: 在线
```

### 测试跨节点协作
在 MacBook 上：
```
对 assistant 说："让 coding 节点写一个 hello world"
```

预期流程：
```
MacBook (mobile) → GM → coding-pm → code worker → 完成
```

---

## 记忆同步测试

### 测试 Blackboard 同步
```bash
# 在 Mac mini 上写入测试
echo "test from mac mini" > ~/clawos/blackboard/shared/test.txt

# 在 MacBook 上读取
cat ~/clawos/blackboard/shared/test.txt

# 预期: 显示 "test from mac mini"
```

### 测试记忆召回
在 MacBook 上：
```
对 assistant 说："我们今天做了什么优化？"
```

预期响应：
```
今天完成了 Opus 优化：
1. GM <5k tokens
2. validator <5k tokens
...
```

---

## 性能测试

### 测试 GM 响应时间
```bash
# 提交简单任务
time openclaw task submit "检查系统状态"

# 预期: <30s
```

### 测试 token 消耗
```bash
# 查看 token 统计
openclaw stats tokens

# 预期: GM <5k, validator <5k
```

---

## 故障恢复测试

### 测试节点离线
1. 关闭 MacBook OpenClaw
2. 在 Mac mini 上提交任务
3. 重启 MacBook OpenClaw
4. 检查任务是否继续

### 测试网络中断
1. 断开 MacBook 网络
2. 在 MacBook 上操作（应该降级为本地模式）
3. 恢复网络
4. 检查同步状态

---

## 成功标准

| 测试项 | 预期结果 | 实际结果 |
|--------|----------|----------|
| 节点连接 | ✅ | - |
| Agent 响应 | ✅ | - |
| Blackboard 同步 | ✅ | - |
| 记忆召回 | ✅ | - |
| GM tokens | <5k | - |
| 响应时间 | <30s | - |

---

**测试完成后**: 填写实际结果，汇报给 dongsheng
