# ClawOS 进化引擎配置

**版本**: 2.0.0
**更新时间**: 2026-02-25

---

## 进化节奏

### 每日自动化

```yaml
# .github/workflows/daily-harvest.yml
name: Daily Knowledge Harvest
on:
  schedule:
    - cron: '0 19 * * *'  # UTC 19:00 = 北京时间 03:00

jobs:
  harvest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Harvest Knowledge
        run: |
          # 各节点知识收割
          echo "Harvesting knowledge from all nodes..."
          
      - name: Update Skills
        run: |
          # platform-pm 更新 skills/
          echo "Updating skills..."
          
      - name: Commit Changes
        run: |
          git config user.name "clawos-evolution"
          git config user.email "evolution@clawos.ai"
          git add .
          git diff --quiet && git diff --staged --quiet || git commit -m "chore: daily knowledge harvest"
          git push
```

### 每周进化

```yaml
# .github/workflows/weekly-evolution.yml
name: Weekly Evolution
on:
  schedule:
    - cron: '0 18 * * 0'  # UTC 18:00 周日 = 北京时间 02:00

jobs:
  evolve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Extract Role Memories
        run: |
          # 从各节点提取角色记忆
          python3 scripts/extract_memories.py
          
      - name: Evaluate Performance
        run: |
          # 评估各角色性能
          python3 scripts/evaluate_roles.py
          
      - name: Update Capabilities
        run: |
          # 更新 capabilities.json
          python3 scripts/update_capabilities.py
          
      - name: Cross-pollinate
        run: |
          # 跨节点知识受粉
          python3 scripts/cross_pollinate.py
          
      - name: Generate Report
        run: |
          # 生成进化周报
          python3 scripts/generate_weekly_report.py
          
      - name: Create PR
        uses: peter-evans/create-pull-request@v5
        with:
          title: "chore: weekly evolution"
          body: "自动进化周更新"
          branch: evolution/weekly
```

### 记忆持久化

```yaml
# .github/workflows/memory-to-github.yml
name: Memory to GitHub
on:
  workflow_dispatch:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: memory
          
      - name: Sync Memories
        run: |
          # 从 MemOS 同步到 GitHub
          python3 scripts/sync_memories.py
          
      - name: Commit
        run: |
          git config user.name "clawos-memory"
          git add memory/
          git diff --quiet && git diff --staged --quiet || git commit -m "chore: memory sync"
          git push
```

---

## 性能阈值

| 等级 | 评分 | 行动 |
|------|------|------|
| excellent | ≥ 9.0 | 标记为专家角色 |
| good | ≥ 8.0 | 正常使用 |
| acceptable | ≥ 7.5 | 观察 |
| needsImprovement | ≥ 7.0 | 触发优化 |
| replace | < 7.0 | 候选替换 |

---

## 角色淘汰规则

```yaml
淘汰条件:
  - 连续4周 avgScore < 7.0
  - 连续10个任务评分 < 7.5
  - Boss 手动标记淘汰

淘汰流程:
  1. platform-pm 标记为"候选淘汰"
  2. 生成淘汰报告
  3. Boss 审批
  4. 存档旧 SOUL.md
  5. 引入挑战者或重写
```

---

## 挑战者机制

```yaml
挑战者引入:
  频率: 每季度 1-2 个
  来源: ClawHub 或 自定义
  
竞争流程:
  1. 挑战者与现有角色并行执行相同任务
  2. 30天评估期
  3. 比较 avgScore
  4. 胜者合并进化
```

---

## 跨节点受粉

```yaml
受粉规则:
  - 只传递底层模式，不传递领域知识
  - 例如：编程节点的 critic-code 批判技巧 → 写作节点
  - 受粉后需要验证效果
  - 失败可回滚
```

---

## 进化报告模板

```markdown
# ClawOS 进化周报

**周期**: {start_date} - {end_date}

## 任务统计
- 总任务数: {total}
- 成功率: {success_rate}
- 平均评分: {avg_score}

## 角色性能 Top 5
| 角色 | 评分 | 任务数 | 趋势 |
|------|------|--------|------|
| ... | ... | ... | ↑↓→ |

## 角色性能 Bottom 3
| 角色 | 评分 | 问题 | 建议 |
|------|------|------|------|
| ... | ... | ... | ... |

## 新增经验
- {experience_1}
- {experience_2}

## 跨节点受粉
- {pollination_1}

## 需要 Boss 决策
- [ ] {decision_1}
- [ ] {decision_2}

---
*自动生成 by ClawOS Evolution Engine*
```
