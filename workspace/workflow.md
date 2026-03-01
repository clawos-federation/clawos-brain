# OpenClaw Enterprise Workflow

## Overview

This document describes the complete workflow for OpenClaw's multi-agent architecture, including Henry (Assistant) and GM Agent (General Manager).

---

## 🏢 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     User (Chairman)                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Strategic Coordination Layer                │
│                                                          │
│  Henry (Assistant) + GM Agent (General Manager)           │
│                                                          │
│  ┌─────────────────────┬─────────────────────────────┐    │
│  │ Henry              │ GM Agent                 │    │
│  │ - Quick理解       │ - Deep分析              │    │
│  │ - Simple tasks    │ - Complex tasks         │    │
│  │ - Coordination    │ - Quality Guardian      │    │
│  └─────────────────────┴─────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌─────────────┐   ┌─────────────┐   ┌─────────────────┐
│ Simple Tasks│   │ Complex    │   │ Quality Gate   │
│             │   │ Tasks     │   │ (Mandatory)   │
└──────┬──────┘   └─────┬───────┘   └───────┬─────────┘
       │                 │                 │
       ↓                 ↓                 ↓
  ┌─────────────────────────────────────────────────┐
  │         Specialized Agents (百花齐放)           │
  │                                             │
  │  DevAgent  LegalAgent  MarketingAgent  ...     │
  └─────────────────────────────────────────────────┘
```

---

## 🎯 Core Decision Matrix

### Task Classification

| Task Type | Complexity | Risk | Agents Involved | Handler |
|------------|------------|-------|-----------------|---------|
| **Simple** | ≤3 steps | Low | 1 | Henry |
| **Moderate** | 3-5 steps | Medium | 1-2 | Henry → GM (optional) |
| **Complex** | >5 steps | High | 2+ | GM Agent |

### Henry's Decision Tree

```python
def classify_task(task):
    """Classify task and determine handler"""
    
    # 1. Quick first principles understanding
    intent = quick_understand(task)
    
    # 2. Assess complexity
    if task.steps <= SIMPLE_THRESHOLD:
        return {"handler": "Henry", "type": "simple"}
    
    # 3. Assess risk
    if task.risk_level == "high":
        return {"handler": "GM Agent", "type": "complex"}
    
    # 4. Assess scope
    if len(task.domains) > 1:
        return {"handler": "GM Agent", "type": "complex"}
    
    # Default: Henry handles
    return {"handler": "Henry", "type": "moderate"}
```

---

## 📋 Complete Workflow Steps

### Step 1: User Request
```
User Input: "Build a customer portal for our support team"
```

### Step 2: Henry's Initial Screening

```python
# Henry's processing
def henry_initial_screening(request):
    
    # 1. Quick first principles understanding (3 levels)
    intent = quick_first_principles(request, depth=3)
    
    # 2. Socratic clarification (if needed)
    if intent.ambiguity > AMBIGUITY_THRESHOLD:
        questions = generate_socratic_questions(intent)
        response = ask_user(questions)
        intent = update_intent(response)
    
    # 3. Complexity assessment
    complexity = assess_complexity(intent)
    
    # 4. Route decision
    if complexity <= SIMPLE_THRESHOLD:
        return handle_simple_task(intent)
    else:
        return escalate_to_gm_agent(intent)
```

**Example Output**:
```
Intent: "Build customer portal for support team"
Understanding:
  - Core problem: Support team needs centralized customer view
  - Success criteria: Single dashboard showing customer history
  - Constraints: 2-month timeline, $X budget

Classification: COMPLEX (>3 steps, multi-domain)
Escalation: GM Agent
```

---

### Step 3: GM Agent Activation

```python
def gm_agent_activation(context):
    
    # 1. Deep first principles (5+ levels)
    deep_analysis = deep_first_principles(context.intent, depth=5)
    
    # 2. Strategic planning
    plan = create_strategic_plan(deep_analysis)
    
    # 3. Identify specialized agents
    agents = identify_agents(deep_analysis)
    
    # 4. Create execution plan
    execution_plan = create_execution_plan(deep_analysis, agents)
    
    return {
        "analysis": deep_analysis,
        "plan": plan,
        "agents": agents,
        "execution_plan": execution_plan
    }
```

**Example Output**:
```
Deep Analysis:
  - Business Problem: Fragmented customer data across systems
  - Root Cause: No unified customer 360 view
  - Key Requirements:
    * Customer profile aggregation
    * Ticket history
    * Communication logs
    * AI-powered insights

Strategic Plan:
  - Phase 1 (2 weeks): Data aggregation layer
  - Phase 2 (3 weeks): UI/UX development
  - Phase 3 (1 week): AI insights integration
  - Phase 4 (1 week): Testing and deployment

Required Agents:
  - DevAgent (Full-stack development)
  - LegalAgent (Data privacy compliance)
  - ResearchAgent (AI tools evaluation)

Timeline: 7 weeks
Budget Estimate: $X
```

---

### Step 4: Agent Distribution (百花齐放)

```python
def distribute_tasks(execution_plan):
    """Distribute tasks to specialized agents"""
    
    distributions = {}
    
    for agent_type, tasks in execution_plan.tasks.items():
        agent = get_agent(agent_type)
        
        # Create task assignment
        assignment = {
            "agent": agent_type,
            "tasks": tasks,
            "deadline": task.deadline,
            "quality_standards": get_quality_standards(agent_type),
            "dependencies": task.dependencies,
            "checkpoints": create_checkpoints(tasks)
        }
        
        distributions[agent_type] = assignment
    
    return distributions
```

**Example Task Assignment**:
```
=== DevAgent Assignment ===

Mission: Build customer portal frontend and backend

Requirements:
  1. Customer profile aggregation (APIs from CRM, Support, Billing)
  2. Ticket history display
  3. Communication logs viewer
  4. AI insights panel

Timeline:
  - Week 1-2: Backend APIs
  - Week 3-4: Frontend
  - Week 5: Integration
  - Week 6: Testing

Quality Standards:
  - Code coverage > 80%
  - Security review required
  - Performance benchmark: < 200ms response

Dependencies:
  - LegalAgent: Data privacy guidelines (Week 1)
  - ResearchAgent: AI tool selection (Week 2)
```

---

### Step 5: Parallel Execution

```python
def parallel_execution(distributions):
    """Execute tasks in parallel"""
    
    results = {}
    
    # Execute all agents in parallel
    futures = {}
    for agent_type, assignment in distributions.items():
        futures[agent_type] = submit_task(agent_type, assignment)
    
    # Collect results as they complete
    for agent_type in futures:
        results[agent_type] = wait_for_result(futures[agent_type])
    
    return results
```

**Execution Timeline**:
```
Week 1:
  ├─ DevAgent: Backend API development
  ├─ LegalAgent: Data privacy policy review ⏳
  └─ ResearchAgent: AI tools evaluation ⏳

Week 2-3:
  ├─ DevAgent: Frontend development (on track)
  ├─ LegalAgent: Compliance guidelines ✅ (Week 1)
  └─ ResearchAgent: AI recommendations ✅ (Week 2)

Week 4-5:
  ├─ DevAgent: Integration testing (blocked by LegalAgent ✅)
  └─ MarketingAgent: User training materials (newly added)

Week 6:
  └─ DevAgent: Final testing and deployment
```

---

### Step 6: Quality Gate (Mandatory)

```python
def mandatory_quality_gate(results):
    """All outputs must pass GM Agent quality gate"""
    
    quality_reports = {}
    
    for agent_type, work in results.items():
        report = gm_agent.review(work, agent_type)
        quality_reports[agent_type] = report
        
        if not report["passed"]:
            # Return for revision
            return {
                "action": "RETURN",
                "agent": agent_type,
                "feedback": report["feedback"],
                "required_score": 7
            }
    
    return {
        "action": "APPROVE",
        "quality_reports": quality_reports,
        "overall_score": calculate_overall_score(quality_reports)
    }
```

**Example Quality Report**:
```
=== DevAgent Quality Report ===

Overall Score: 7.8/10 ✅ PASSED

Dimensions:
├─ Accuracy: 8.5/10
├─ Completeness: 7.5/10
├─ Professionalism: 7.8/10
├─ Risk Assessment: 7.2/10
└─ Maintainability: 7.8/10

Feedback:
✅ Strengths:
   - Clean architecture
   - Good test coverage (85%)
   - Comprehensive API documentation

⚠️ Improvements:
   - Edge case handling for rate limiting
   - Error messages could be more descriptive

💡 Suggestions:
   - Consider GraphQL for flexible data fetching
   - Add caching layer for frequently accessed data
```

---

### Step 7: Strategic Innovation

```python
def strategic_innovation(results):
    """Identify improvement opportunities"""
    
    insights = []
    
    # Pattern recognition
    if is_recurring_pattern(results):
        insights.append({
            "type": "automation",
            "description": "Similar APIs detected, suggest code generation template",
            "impact": "Reduce future development time by 30%"
        })
    
    # Knowledge management
    if hasvaluable_insights(results):
        insights.append({
            "type": "knowledge_base",
            "description": "Document AI tool evaluation for future reference",
            "action": "Add to knowledge base"
        })
    
    return insights
```

**Example Innovation Insights**:
```
=== Strategic Innovation Report ===

1. 🔄 Automation Opportunity
   Description: DevAgent created 5 similar CRUD APIs
   Recommendation: Create reusable API generation template
   Impact: 40% faster API development in future

2. 📚 Knowledge Management
   Description: ResearchAgent's AI tool evaluation is valuable
   Action: Add to knowledge base under "AI Tools Selection"

3. ⚡ Performance Optimization
   Description: Frontend loading could be improved
   Recommendation: Implement lazy loading
   Impact: 50% faster initial page load
```

---

### Step 8: Henry's Summary to User

```python
def henry_summary(gm_result):
    """Create user-friendly summary"""
    
    summary = {
        "status": "completed" if gm_result.passed else "in_progress",
        "highlights": [
            "Customer portal completed",
            "All quality gates passed (7.8/10)",
            "Innovation opportunities identified"
        ],
        "deliverables": gm_result.deliverables,
        "timeline": gm_result.timeline,
        "next_steps": gm_result.recommendations
    }
    
    return present_to_user(summary)
```

**Example User Summary**:
```
=== Task Completion Summary ===

✅ Status: Completed

📊 Overview:
- Customer portal built and deployed
- All quality gates passed (7.8/10)
- Timeline: 6 weeks (on schedule)

🚀 Key Deliverables:
1. Customer 360 dashboard
2. Ticket management system
3. AI-powered insights

💡 Innovation Opportunities:
- API generation template (40% faster future development)
- Knowledge base entry (AI tool selection)

📋 Next Steps:
- Review AI tool evaluation for other projects
- Plan Phase 2: Advanced analytics (optional)
```

---

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ 1. User Request                                     │
│     "Build a customer portal"                       │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Henry - Initial Screening                        │
│     - Quick understanding (3 levels)               │
│     - Complexity assessment                        │
│     - Route decision                             │
└─────────────────────────┬───────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ Simple     │   │ Complex        │   │ Quality Gate   │
│ Tasks      │   │ Tasks          │   │ (Mandatory)   │
│ (Henry)    │   │ (GM Agent)     │   │ (GM Agent)    │
└──────┬──────┘   └───────┬───────┘   └───────┬─────────┘
       │                 │                 │
       ↓                 ↓                 ↓
  ┌──────────┐   ┌─────────────────┐   ┌─────────────────┐
  │ Execute  │   │ Deep Analysis  │   │ Review All     │
  │ Directly │   │ Strategic Plan │   │ Outputs        │
  └──────────┘   └───────┬───────┘   └───────┬─────────┘
                          │                 │
                          ↓                 ↓
                  ┌─────────────────┐   ┌─────────────────┐
                  │ Agent          │   │ Pass/Fail       │
                  │ Distribution   │   │ (7/10)         │
                  └───────┬───────┘   └───────┬─────────┘
                          │                 │
                          ↓                 ↓
                  ┌─────────────────┐   ┌─────────────────┐
                  │ Parallel       │   │ Strategic      │
                  │ Execution      │   │ Innovation     │
                  └───────┬───────┘   └───────┬─────────┘
                          │                 │
                          └────────┬────────┘
                                   ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Henry - User Summary                               │
│     - Status: Completed                             │
│     - Deliverables: List                           │
│     - Innovation: Opportunities                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Performance Metrics

### Henry Metrics
| Metric | Target | Actual |
|--------|---------|--------|
| Response Time | < 2s | - |
| Task Classification Accuracy | > 90% | - |
| Tool Selection Accuracy | > 95% | - |

### GM Agent Metrics
| Metric | Target | Actual |
|--------|---------|--------|
| Quality Gate Pass Rate | > 85% | - |
| Average Quality Score | > 7.5/10 | - |
| Innovation Insights Generated | > 3/task | - |
| Revision Rate | < 20% | - |

### Overall System Metrics
| Metric | Target | Actual |
|--------|---------|--------|
| Complex Task Completion | > 90% | - |
| Average Timeline Adherence | > 95% | - |
| User Satisfaction | > 4.5/5 | - |

---

## 🎯 Key Decision Points

### 1. When to Trigger GM Agent?
- Task steps > 3
- Multi-domain (>1 agent required)
- High risk (legal, financial, security)
- Strategic importance

### 2. When to Escalate from GM to User?
- Requirements unclear
- Budget insufficient
- Technical feasibility concerns
- Resource constraints

### 3. When to Reject Output?
- Quality score < 7/10
- Critical security issues
- Business logic errors
- Incomplete requirements

---

## 📁 Related Documents

| Document | Description |
|---------|-------------|
| `SOUL.md` | Shared soul (traits) |
| `IDENTITY.md` | Multi-domain identity |
| `agents/henry.md` | Henry detailed spec |
| `agents/gm_agent.md` | GM Agent detailed spec |

---

**Version**: 1.0
**Status**: ✅ Ready
**Last Updated**: 2026-02-10
