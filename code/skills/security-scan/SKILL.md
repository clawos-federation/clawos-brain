# security-scan Skill

> 安全扫描 Skill，为 securityagent Agent 提供代码安全和配置审计能力。

---

## 概述

| 属性 | 值 |
|------|-----|
| **ID** | security-scan |
| **版本** | 1.0.0 |
| **类别** | Security |
| **依赖 Agent** | securityagent |
| **权限级别** | 只读 |

---

## 功能

### 核心能力

| 能力 | 工具/命令 | 说明 |
|------|-----------|------|
| **依赖扫描** | `npm audit`, `pip-audit` | 检查依赖漏洞 |
| **代码扫描** | `semgrep`, `codeql` | 静态代码分析 |
| **密钥检测** | `gitleaks`, `trufflehog` | 检测泄露的密钥 |
| **配置审计** | `checkov`, `tfsec` | IaC 安全检查 |
| **容器扫描** | `trivy` | 容器镜像漏洞扫描 |

### 扫描类型

#### 1. 依赖漏洞扫描

```bash
# Node.js
npm audit --json

# Python
pip-audit --format json

# 输出格式
{
  "vulnerabilities": [
    {
      "package": "lodash",
      "version": "4.17.15",
      "severity": "high",
      "cve": "CVE-2020-8203",
      "recommendation": "升级到 4.17.19+"
    }
  ]
}
```

#### 2. 密钥泄露检测

```bash
# 使用 gitleaks
gitleaks detect --source . --format json

# 常见泄露类型
- AWS Access Keys
- GitHub Tokens
- API Keys
- Private Keys
- Database Credentials
```

#### 3. 代码安全扫描

```bash
# 使用 semgrep
semgrep --config auto --json .

# 检测规则
- SQL 注入
- XSS 跨站脚本
- 命令注入
- 路径遍历
- 敏感数据暴露
```

---

## 安全检查清单

### 代码安全

| 检查项 | 风险等级 | 检测方法 |
|--------|----------|----------|
| SQL 注入 | 高 | semgrep 规则 |
| XSS 漏洞 | 高 | semgrep 规则 |
| 命令注入 | 高 | semgrep 规则 |
| 硬编码密钥 | 高 | gitleaks |
| 不安全的反序列化 | 高 | codeql |
| 路径遍历 | 中 | semgrep 规则 |

### 配置安全

| 检查项 | 风险等级 | 检测方法 |
|--------|----------|----------|
| 开放的端口 | 中 | checkov |
| 过宽的 IAM 权限 | 高 | checkov |
| 未加密的存储 | 高 | tfsec |
| 公开访问的 S3 | 高 | checkov |
| 弱密码策略 | 中 | 配置审计 |

---

## 安全规则

### ✅ 允许的操作

- 读取代码文件
- 执行扫描命令
- 读取配置文件
- 生成报告

### ❌ 禁止的操作

- 修改任何代码文件
- 修改配置文件
- 执行修复操作
- 删除文件
- 提交代码

---

## 输出报告格式

```json
{
  "scanId": "scan-20260224-001",
  "timestamp": "2026-02-24T22:00:00Z",
  "target": "./src",
  "summary": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 10,
    "total": 17
  },
  "findings": [
    {
      "id": "VULN-001",
      "type": "sql-injection",
      "severity": "high",
      "file": "src/db/queries.js",
      "line": 42,
      "description": "潜在的 SQL 注入漏洞",
      "recommendation": "使用参数化查询",
      "references": ["https://owasp.org/www-community/attacks/SQL_Injection"]
    }
  ],
  "compliance": {
    "OWASP-Top-10": {
      "status": "fail",
      "failedChecks": ["A03:2021 - Injection"]
    }
  }
}
```

---

## 使用场景

### 场景 1: PR 安全审查

```markdown
任务: 对即将合并的 PR 进行安全扫描

执行步骤:
1. 检出 PR 分支
2. npm audit / pip-audit
3. gitleaks detect
4. semgrep --config auto
5. 生成安全报告
6. 发布到 PR 评论
```

### 场景 2: 定期安全审计

```markdown
任务: 每周执行完整的安全审计

执行步骤:
1. 扫描所有依赖
2. 代码安全分析
3. 配置审计
4. 生成趋势报告
5. 上报到 blackboard
```

---

## 与其他 Skills 的协作

| Skill | 协作方式 |
|-------|----------|
| `git-operations` | 在 PR 创建前执行安全扫描 |
| `quality-check` | 安全扫描作为质量门禁的一部分 |
| `error-escalation` | 发现高危漏洞时立即上报 |
| `blackboard` | 将扫描结果写入共享黑板 |

---

## 风险等级定义

| 等级 | 定义 | 处理时限 |
|------|------|----------|
| **Critical** | 可被直接利用，造成严重损失 | 立即修复 |
| **High** | 存在明显漏洞，可能被利用 | 24小时内 |
| **Medium** | 潜在风险，需要评估 | 1周内 |
| **Low** | 最佳实践建议 | 下次迭代 |

---

## 工具安装

```bash
# Gitleaks - 密钥检测
brew install gitleaks

# Semgrep - 代码扫描
brew install semgrep

# Trivy - 容器扫描
brew install trivy

# Checkov - IaC 扫描
pip install checkov
```

---

*此 Skill 为 securityagent Agent 提供只读安全扫描能力，不执行任何修复操作。*
