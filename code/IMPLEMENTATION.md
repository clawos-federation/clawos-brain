# ClawOS 实施计划 v2

**版本**: 2.0.0
**基于**: v1 规划 + v2 架构

---

## Phase 0：地基（第1-2周）

### 目标
单节点（服务器）跑通最基本闭环，验证核心体验

### Day 1-2: 环境搭建

```bash
# 1. 服务器准备
# 选项A: Oracle Cloud Free Tier (免费)
# 选项B: DigitalOcean $5 Droplet

# 2. 安装 OpenClaw
sudo npm i -g openclaw@latest
openclaw onboard

# 3. 安全配置
openclaw doctor
openclaw token:rotate --force
```

### Day 3-4: Command 层

```bash
# 1. 创建目录结构
mkdir -p ~/clawos/{blackboard,memory}
mkdir -p ~/.openclaw/clawos/clawos/{souls,lib,config}

# 2. 复制 v2 框架
# - ROLE.md
# - registry/capabilities.json
# - protocols/MESSAGE.md
# - frameworks/REACT.md
# - architecture/MEMORY.md
# - lib/*.py

# 3. 配置 Telegram
openclaw configure --section messaging
```

### Day 5-7: 基本闭环

```yaml
# 测试流程
1. 用户发消息给 assistant
2. assistant 3秒确认
3. 转发 gm
4. gm 任命 writing-pm
5. writing-pm 召唤 creator-writing
6. 完成任务
7. 通知用户

# 验收标准
- 3秒内收到确认
- 45分钟内完成任务
- 有进度更新
- 主动通知完成
```

---

## Phase 1：完整服务器节点（第3-4周）

### Week 1: 记忆系统

```bash
# 1. 安装 SimpleMem
pip install simplemem

# 2. 安装 EverMemOS
git clone https://github.com/EverMind-AI/EverMemOS
cd EverMemOS && docker compose up -d

# 3. 接入 OpenClaw
# - 任务前召回记忆
# - 任务后保存记忆
```

### Week 2: 质量闭环

```yaml
# 1. Validator 配置
# - 独立质检
# - JSON 评分格式
# - 打回机制（最多3次）

# 2. Lobster 工作流
# - coding-task.yaml
# - writing-task.yaml
# - validation-loop.yaml

# 3. 多用户测试
# - 两个账号同时使用
# - 验证隔离性
```

### 验收
- [ ] 记忆跨会话有效
- [ ] 质检闭环跑通
- [ ] 10个并发用户正常

---

## Phase 2：专业节点（第5-8周）

### Week 5-6: 编程节点

```yaml
# MacBook 配置
device: MacBook Pro
model: deepseek/deepseek-v3

# 创建专属仓库
gh repo create clawos-node-coding

# 角色
- coding-pm
- analyst-code
- creator-code
- critic-code

# 独立运行2周
# 收集成功率数据
```

### Week 7-8: 写作/量化节点

```yaml
# 写作节点
device: Windows PC
model: anthropic/claude-opus-4-6
memory: EverMemOS + SimpleMem

# 量化节点
device: GitHub Codespace
model: anthropic/claude-sonnet-4-6
注意: 第一个月只做模拟盘！

# Risk Manager
- 硬规则硬编码
- 只读+通知权限
- 人工确认阈值
```

### 验收
- [ ] 三节点独立稳定运行
- [ ] 基本跨节点任务分发成功
- [ ] 量化模拟盘运行正常

---

## Phase 3：联邦协作（第9-12周）

### Week 9-10: GitHub DNA

```bash
# 1. 创建联邦组织
gh org create clawos-federation

# 2. 创建仓库
- clawos-brain (总仓)
- clawos-node-server
- clawos-node-coding
- clawos-node-writing
- clawos-node-quant

# 3. 配置 GitHub Actions
- daily-harvest.yml
- weekly-sync.yml
- memory-to-github.yml
```

### Week 11-12: 跨节点协作

```yaml
# 1. MemOS 接入
# 需要 Redis
docker run -d redis

# 2. Cloudflare R2
# 作为共享黑板
# 月成本 ~$0

# 3. 记忆双向同步
# - 节点 → GitHub (周日 02:00)
# - GitHub → 节点 (周日 04:00)
```

### 验收
- [ ] 系统一周无人工干预
- [ ] 自动完成5+任务
- [ ] 进化日志有记录

---

## Phase 4：自治进化（第3个月起）

### 持续优化

```yaml
# 1. EvoAgentX 接入
# 工作流自动优化

# 2. 挑战者机制
# 每季度引入1-2个挑战者

# 3. 真实量化
# 从总资产1%开始

# 4. 多渠道
# WhatsApp + Discord + Telegram
```

---

## 里程碑检查表

### Phase 0 完成
- [ ] 3秒响应
- [ ] 基本任务完成
- [ ] 主动通知

### Phase 1 完成
- [ ] 记忆系统运行
- [ ] 质检闭环
- [ ] 多用户隔离

### Phase 2 完成
- [ ] 三节点运行
- [ ] 跨节点任务
- [ ] 量化模拟盘

### Phase 3 完成
- [ ] GitHub DNA 运行
- [ ] 自动进化启动
- [ ] 一周无人值守

---

## 每日检查

```bash
# 检查系统状态
openclaw status

# 检查任务状态
cat ~/clawos/blackboard/tasks/*/status.md

# 检查记忆队列
cat ~/clawos/blackboard/roles/memory-queue.json

# 检查进化日志
git log --oneline -10
```

---

## 回滚计划

```bash
# 如果出问题
1. 停止所有 Agent
2. git checkout 上一个稳定版本
3. 重启 Gateway
4. 人工介入处理
```

---

**ClawOS 实施计划 v2**
