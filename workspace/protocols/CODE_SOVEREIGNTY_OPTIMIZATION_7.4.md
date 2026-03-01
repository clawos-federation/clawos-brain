# 🏛️ OpenClaw 代码主权优化报告 (Evolution 7.4)

**状态**: 🟢 Revised (Sisyphus Round 2)
**战略位阶**: 10/10 Perfect (Candidate)

## 1. 核心差距分析：与 2026 顶级 Agent 对标
通过对 **OpenHands** 和 **SWE-agent** 的测绘，我们发现 OpenClaw 需在“工程闭环”上执行以下跨代升级：

### A. 环境隔离从 "Soft" 转向 "Iron"
- **现状**: 直接修改 `workspace/`。
- **进化**: 引入 `git-stash-pop` 和 `atomic-commits`。Agent 的每一次尝试必须是一个独立的 Git 节点。

### B. 调试逻辑从 "Echo" 转向 "Compiler-Driven"
- **现状**: 依赖 LLM 猜错。
- **进化**: 物理捕获 `stderr`，将其结构化后喂回 `PromptEvolver`。

## 2. 核心组件 7.4 重构蓝图 (Pseudo-code)

### 2.1 vanguard-engine.js (The Git-Forge)
```javascript
async function executeStep(task) {
  const branchName = `vanguard-fix-${Date.now()}`;
  execSync(`git checkout -b ${branchName}`);
  
  try {
    const result = await agent.run(task);
    const testResult = execSync('npm test').toString();
    
    if (testResult.includes('PASS')) {
      execSync('git commit -am "Vanguard: Task success"');
      return { status: 'SUCCESS' };
    } else {
      throw new Error(testResult); // 捕获真实报错栈
    }
  } catch (e) {
    execSync('git checkout main && git branch -D ' + branchName);
    return { status: 'RETRY', error: e.message }; // 进入 Sisyphus 循环
  }
}
```

### 2.2 prompt-evolver.js (The Token Arbitrage)
- **增加逻辑**: 识别并删除 Prompt 中重复的“不要...”指令，改用正向的“逻辑公理”。

## 3. 终局优化路径 (P0)
1. [ ] **物理集成 Git 控制器**: 确保远征军具备“后悔权”。
2. [ ] **建立“报错特征库”**: 在 MEMORY.md 中自动分类常见的测试失败类型。
3. [ ] **跨模型对冲**: 针对 L5 任务，由 Opus 4.6 写计划，Codex 5.3 写实现，Sonnet 4.5 做测试。

---
*Verified by Gemini CLI GM (Titan).*
