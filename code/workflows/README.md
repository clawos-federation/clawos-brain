# Lobster 工作流定义

**版本**: 2.0.0

---

## coding-task.yaml

```yaml
name: coding-task
description: 软件开发任务工作流

input:
  description: string
  language: string="auto"
  constraints: string[]

steps:
  - id: analyze
    role: analyst-code
    action: analyze
    params:
      description: "${input.description}"
    output:
      as: analysis
      
  - id: implement
    role: creator-code
    action: implement
    params:
      analysis: "${steps.analyze.output}"
      language: "${input.language}"
    output:
      as: code
      
  - id: review
    role: critic-code
    action: review
    params:
      code: "${steps.implement.output}"
    output:
      as: review
      
  - condition: "${steps.review.output.score < 8}"
    action: loop-back
    target: implement
    feedback: "${steps.review.output.issues}"
    maxIterations: 3
    
  - id: test
    role: executor-test
    action: test
    params:
      code: "${steps.implement.output}"
    output:
      as: test-results

output:
  code: "${steps.implement.output}"
  review: "${steps.review.output}"
  tests: "${steps.test.output}"
```

---

## writing-task.yaml

```yaml
name: writing-task
description: 内容创作任务工作流

input:
  topic: string
  style: string="professional"
  length: number=1000
  audience: string="general"

steps:
  - id: research
    role: analyst-research
    action: research
    params:
      topic: "${input.topic}"
    output:
      as: research
      
  - id: outline
    role: analyst-writing
    action: outline
    params:
      research: "${steps.research.output}"
      length: "${input.length}"
    output:
      as: outline
      
  - id: write
    role: creator-writing
    action: write
    params:
      outline: "${steps.outline.output}"
      style: "${input.style}"
      audience: "${input.audience}"
    output:
      as: content
      
  - id: review
    role: critic-writing
    action: review
    params:
      content: "${steps.write.output}"
    output:
      as: review
      
  - condition: "${steps.review.output.score < 8}"
    action: loop-back
    target: write
    feedback: "${steps.review.output.issues}"
    maxIterations: 3

output:
  content: "${steps.write.output}"
  review: "${steps.review.output}"
```

---

## research-task.yaml

```yaml
name: research-task
description: 调研分析任务工作流

input:
  topic: string
  depth: string="medium"  # shallow, medium, deep
  sources: string[]=[]

steps:
  - id: analyze
    role: analyst-research
    action: analyze
    params:
      topic: "${input.topic}"
      depth: "${input.depth}"
      sources: "${input.sources}"
    output:
      as: analysis
      
  - id: synthesize
    role: connector-research
    action: synthesize
    params:
      analysis: "${steps.analyze.output}"
    output:
      as: synthesis
      
  - id: verify
    role: critic-research
    action: verify
    params:
      synthesis: "${steps.synthesize.output}"
    output:
      as: verification
      
  - condition: "${steps.verify.output.score < 8}"
    action: loop-back
    target: analyze
    feedback: "${steps.verify.output.recommendations}"
    maxIterations: 2

output:
  analysis: "${steps.analyze.output}"
  synthesis: "${steps.synthesize.output}"
  verification: "${steps.verify.output}"
```

---

## 前端开发工作流

```yaml
name: frontend-task
description: 前端开发任务工作流

steps:
  - id: analyze
    role: analyst-frontend
    action: analyze
    output:
      as: analysis
      
  - id: implement
    role: creator-frontend
    action: implement
    params:
      analysis: "${steps.analyze.output}"
    output:
      as: code
      
  - id: review
    role: critic-code
    action: review
    params:
      code: "${steps.implement.output}"
    output:
      as: review
      
  - condition: "${steps.review.output.score < 8}"
    action: loop-back
    target: implement
    maxIterations: 3
```

---

## 后端开发工作流

```yaml
name: backend-task
description: 后端开发任务工作流

steps:
  - id: analyze
    role: analyst-backend
    action: analyze
    output:
      as: analysis
      
  - id: implement
    role: creator-backend
    action: implement
    params:
      analysis: "${steps.analyze.output}"
    output:
      as: code
      
  - id: review
    role: critic-code
    action: review
    output:
      as: review
      
  - condition: "${steps.review.output.score < 8}"
    action: loop-back
    target: implement
    maxIterations: 3
    
  - id: test
    role: executor-test
    action: test
    output:
      as: tests
```

---

**ClawOS Lobster Workflows v2**
