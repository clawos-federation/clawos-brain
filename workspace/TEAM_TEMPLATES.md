# 🎭 Team Templates - Orchestration 6.6.1

预制专家团队模板，用于动态组建团队。

---

## 📋 模板列表

### 1. 产品开发冲刺队 (dev-sprint)
**适用场景**: 新功能开发、产品迭代

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 任务拆解、里程碑、验收标准 |
| 开发 | DevAgent | 代码实现 |
| 测试 | TestAgent | 测试矩阵、回归测试 |
| 协调 | Henry | 进度播报、阻塞协调 |

**触发条件**:
- 任务包含: "开发"、"实现"、"新功能"
- 复杂度: 高
- 估计时间: >2小时

---

### 2. Bug 火线修复队 (bug-fix)
**适用场景**: 线上问题、紧急修复

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 定级(P0/P1)、止血方案 |
| 开发 | DevAgent | 修复实现 |
| 测试 | TestAgent | 复现验证、边界测试 |
| 调研 | ResearchAgent | 查已知坑、兼容性 |
| 协调 | Henry | 对外同步、变更记录 |

**触发条件**:
- 任务包含: "bug"、"修复"、"问题"
- 优先级: P0/P1
- 紧急程度: 高

---

### 3. 架构评审队 (arch-review)
**适用场景**: 技术方案、架构决策

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 架构方案 A/B、取舍 |
| 调研 | ResearchAgent | 竞品/技术路线对比 |
| 验证 | DevAgent | PoC 实现 |
| 风险 | TestAgent | 可测性、性能风险 |
| 协调 | Henry | 决策纪要 |

**触发条件**:
- 任务包含: "架构"、"方案"、"设计"
- 影响范围: 系统级

---

### 4. 合规审查队 (compliance)
**适用场景**: 法律、合规、隐私

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 风险评估 |
| 法律 | LegalAgent | 法律条款分析 |
| 调研 | ResearchAgent | 法规研究 |
| 协调 | Henry | 合规报告 |

**触发条件**:
- 任务包含: "法律"、"合规"、"隐私"、"条款"

---

### 5. 研究探索队 (research)
**适用场景**: 技术调研、竞品分析

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 研究方向 |
| 调研 | ResearchAgent | 深度分析 |
| 验证 | DevAgent | PoC (可选) |
| 协调 | Henry | 研究报告 |

**触发条件**:
- 任务包含: "调研"、"研究"、"分析"

---

### 6. 代码质量提升队 (code-quality)
**适用场景**: 代码重构、技术债务清理、性能优化

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 重构范围、风险评估 |
| 开发 | DevAgent | 重构实现、代码优化 |
| 测试 | TestAgent | 回归测试、性能验证 |
| 调研 | ResearchAgent | 最佳实践、工具选型 |
| 协调 | Henry | 变更记录、进度同步 |

**触发条件**:
- 任务包含: "重构"、"优化"、"技术债"、"代码质量"、"性能"
- 代码行数: >500行
- 影响模块: >3个

**工作流程**:
1. GM 分析代码现状，制定重构计划
2. ResearchAgent 调研最佳实践
3. DevAgent 执行重构
4. TestAgent 验证功能完整性
5. Henry 同步变更记录

---

### 7. 知识生产队 (knowledge-production)
**适用场景**: 文档撰写、知识库建设、文章创作、教程编写

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 内容架构、质量标准 |
| 调研 | ResearchAgent | 素材收集、事实核查 |
| 创作 | DevAgent | 代码示例、技术实现 |
| 审校 | TestAgent | 内容验证、链接检查 |
| 协调 | Henry | 发布管理、版本控制 |

**触发条件**:
- 任务包含: "文档"、"文章"、"教程"、"知识库"、"博客"
- 输出类型: Markdown、PDF、HTML
- 预计字数: >1000字

**子场景模板**:

#### 7.1 技术文档 (tech-doc)
- API 文档
- 架构文档
- 部署指南
- 开发手册

**特殊要求**: 代码示例可运行、命令可验证

#### 7.2 知识文章 (article)
- 技术博客
- 行业分析
- 最佳实践
- 案例研究

**特殊要求**: 数据准确、引用完整、逻辑清晰

#### 7.3 教程指南 (tutorial)
- 入门教程
- 进阶指南
- 实战项目
- 视频脚本

**特殊要求**: 步骤可复现、难度渐进、示例完整

#### 7.4 知识库建设 (knowledge-base)
- FAQ 编写
- 故障排查手册
- 运维手册
- 培训材料

**特殊要求**: 结构化、可搜索、易维护

**工作流程**:
1. GM 确定内容架构和目标读者
2. ResearchAgent 收集素材、核实信息
3. DevAgent 编写核心内容（含代码示例）
4. TestAgent 验证技术准确性
5. Henry 格式化、发布管理

---

### 8. 稳定性保障队 (ops-reliability)
**适用场景**: 部署发布、监控告警、回滚演练、平台稳定性问题

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 发布策略、风险门禁、回滚决策 |
| 稳定性 | SREAgent | 部署、监控、告警、回滚执行 |
| 测试 | TestAgent | 回归验证、发布后冒烟 |
| 调研 | ResearchAgent | 根因定位、方案比较 |
| 协调 | Henry | 进度播报、事件沟通 |

**触发条件**:
- 任务包含: "部署"、"发布"、"监控"、"告警"、"回滚"、"稳定性"

---

### 9. 产品落地队 (product-delivery)
**适用场景**: 需求拆解、验收标准定义、迭代计划

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 目标与优先级决策 |
| 产品 | ProductAgent | PRD/用户故事/验收标准 |
| 调研 | ResearchAgent | 竞品与可行性分析 |
| 开发 | DevAgent | 技术方案与工时评估 |
| 协调 | Henry | 对外同步与收口 |

**触发条件**:
- 任务包含: "需求"、"PRD"、"验收标准"、"迭代计划"、"优先级"

---

### 10. 数据增长队 (data-growth)
**适用场景**: 指标设计、埋点、A/B、效果复盘

| 角色 | Agent | 职责 |
|------|-------|------|
| 统筹 | GM | 目标指标与实验策略 |
| 数据 | DataAgent | 指标定义、埋点方案、分析报告 |
| 开发 | DevAgent | 埋点实现、数据通路 |
| 测试 | TestAgent | 数据正确性校验 |
| 协调 | Henry | 结果沟通与复盘纪要 |

**触发条件**:
- 任务包含: "指标"、"埋点"、"A/B"、"实验"、"数据分析"

---

## 🚦 任务路由规则

```json
{
  "rules": [
    {
      "pattern": ["开发", "实现", "新功能"],
      "template": "dev-sprint",
      "priority": "high"
    },
    {
      "pattern": ["bug", "修复", "问题", "崩溃"],
      "template": "bug-fix",
      "priority": "critical"
    },
    {
      "pattern": ["架构", "方案", "设计"],
      "template": "arch-review",
      "priority": "high"
    },
    {
      "pattern": ["法律", "合规", "隐私"],
      "template": "compliance",
      "priority": "high"
    },
    {
      "pattern": ["调研", "研究", "分析"],
      "template": "research",
      "priority": "normal"
    },
    {
      "pattern": ["重构", "优化", "技术债", "代码质量", "性能"],
      "template": "code-quality",
      "priority": "high"
    },
    {
      "pattern": ["文档", "文章", "教程", "知识库", "博客", "API文档", "README"],
      "template": "knowledge-production",
      "priority": "normal"
    },
    {
      "pattern": ["部署", "发布", "监控", "告警", "回滚", "稳定性", "SRE"],
      "template": "ops-reliability",
      "priority": "high"
    },
    {
      "pattern": ["需求", "PRD", "验收标准", "迭代计划", "优先级"],
      "template": "product-delivery",
      "priority": "high"
    },
    {
      "pattern": ["指标", "埋点", "A/B", "实验", "数据分析"],
      "template": "data-growth",
      "priority": "normal"
    }
  ],
  "sub_scenarios": {
    "knowledge-production": {
      "tech-doc": ["API", "架构文档", "部署", "开发手册"],
      "article": ["博客", "分析", "实践", "案例"],
      "tutorial": ["教程", "指南", "入门", "实战"],
      "knowledge-base": ["FAQ", "排查", "运维", "培训"]
    }
  },
  "default": {
    "simple": "gm",
    "complex": "gm"
  }
}
```

---

## 📝 使用方式

Henry 在接收到任务时：

1. **所有任务**: 先做接待与澄清，再转交 GM
2. **复杂任务** (开发、修复): 
   - Henry 识别任务类型并打包上下文
   - GM 匹配团队模板
   - GM Spawn 相应 agents
   - GM 协调执行与验收
   - Henry 负责对用户同步与收口

---

## 🔄 动态组建流程

```
用户任务 → Henry (triage)
    ↓
识别复杂度 → 匹配模板
    ↓
Spawn GM (统筹)
    ↓
GM Spawn DevAgent/TestAgent/...
    ↓
并行执行 → 汇总
    ↓
GM 审批 → Henry 返回结果
```

---

*版本: Orchestration 6.6.1*  
*创建时间: 2026-02-15*
