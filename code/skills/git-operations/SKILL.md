# git-operations Skill

> Git 版本控制操作 Skill，为 github-ops Agent 提供标准化 Git 工作流支持。

---

## 概述

| 属性 | 值 |
|------|-----|
| **ID** | git-operations |
| **版本** | 1.0.0 |
| **类别** | System |
| **依赖 Agent** | github-ops |
| **权限级别** | 中等 |

---

## 功能

### 核心能力

| 能力 | 命令示例 | 说明 |
|------|----------|------|
| **分支管理** | `git branch`, `git checkout` | 创建、切换、删除分支 |
| **提交管理** | `git add`, `git commit`, `git amend` | 暂存、提交、修改提交 |
| **远程操作** | `git push`, `git pull`, `git fetch` | 与远程仓库同步 |
| **合并变基** | `git merge`, `git rebase` | 分支合并和变基 |
| **历史查看** | `git log`, `git diff`, `git show` | 查看提交历史和差异 |
| **状态检查** | `git status`, `git stash` | 检查工作区状态 |

### 工作流模板

#### 1. 功能分支工作流

```bash
# 创建功能分支
git checkout -b feature/{feature-name}

# 开发完成后提交
git add .
git commit -m "feat: {description}"

# 推送到远程
git push -u origin feature/{feature-name}

# 创建 PR (使用 gh CLI)
gh pr create --title "{title}" --body "{description}"
```

#### 2. 紧急修复工作流

```bash
# 从 main 创建 hotfix 分支
git checkout main
git pull
git checkout -b hotfix/{issue-id}

# 修复并提交
git add .
git commit -m "fix: {description}"

# 推送并创建 PR
git push -u origin hotfix/{issue-id}
gh pr create --title "Hotfix: {title}" --body "{description}"
```

---

## 安全规则

### ✅ 允许的操作

- `git add`, `git commit`, `git push`
- `git branch`, `git checkout`, `git merge`
- `git pull`, `git fetch`, `git clone`
- `git log`, `git diff`, `git status`
- `gh` CLI 命令 (GitHub 操作)

### ❌ 禁止的操作

- `git push --force` (强制推送到 main/master)
- `git reset --hard` (硬重置后推送)
- `git clean -fd` (删除未跟踪文件)
- 删除 main/master 分支
- 修改 .git/config 中的敏感信息

---

## 使用场景

### 场景 1: 创建 PR

```markdown
任务: 为新功能创建 Pull Request

执行步骤:
1. git status 确认无未提交更改
2. git checkout -b feature/new-feature
3. git add . && git commit -m "feat: new feature"
4. git push -u origin feature/new-feature
5. gh pr create --title "New Feature" --body "Description"
```

### 场景 2: 同步主分支

```markdown
任务: 将 main 分支的最新更改合并到当前分支

执行步骤:
1. git fetch origin
2. git merge origin/main
3. 解决冲突（如有）
4. git push
```

---

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `merge conflict` | 分支冲突 | 手动解决冲突后 `git add` + `git commit` |
| `diverged branches` | 分支历史不同 | `git rebase` 或 `git merge` |
| `push rejected` | 远程有新提交 | `git pull --rebase` 后再 push |
| `detached HEAD` | 不在分支上 | `git checkout {branch}` |

---

## 与其他 Skills 的协作

| Skill | 协作方式 |
|-------|----------|
| `coding-workflow` | 在代码开发完成后执行 Git 操作 |
| `quality-check` | 在 PR 创建前执行质量检查 |
| `error-escalation` | Git 操作失败时上报 |

---

## 输出格式

```json
{
  "operation": "git-push",
  "branch": "feature/new-feature",
  "status": "success",
  "commitHash": "abc1234",
  "prUrl": "https://github.com/owner/repo/pull/123"
}
```

---

*此 Skill 为 github-ops Agent 提供标准化的 Git 操作能力。*
