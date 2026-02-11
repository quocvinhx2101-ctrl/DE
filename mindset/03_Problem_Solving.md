# 🔍 Problem Solving Mindset

> Phương pháp giải quyết vấn đề cho Data Engineer cấp cao

---

## 📋 Mục Lục

1. [Problem Analysis Framework](#-problem-analysis-framework)
2. [Debugging Mindset](#-debugging-mindset)
3. [Performance Investigation](#-performance-investigation)
4. [Incident Management](#-incident-management)
5. [Continuous Improvement](#-continuous-improvement)

---

## 🎯 Problem Analysis Framework

### Step 1: Define the Problem Clearly

**Bad problem statement:**
"The pipeline is broken"

**Good problem statement:**
"The daily sales pipeline has been failing for the past 3 days at the transformation step, causing sales reports to be delayed by 8 hours, affecting the finance team's daily standup."

**Problem Statement Template:**
```
WHAT: [What is happening vs what should happen]
WHEN: [When did it start, frequency, pattern]
WHERE: [Which system, environment, component]
IMPACT: [Who is affected, business impact]
```

### Step 2: Gather Data

**Questions to ask:**
```
1. What changed recently?
   - Code deployments
   - Configuration changes
   - Infrastructure changes
   - Data volume changes

2. What are the symptoms?
   - Error messages
   - Metrics (latency, throughput)
   - User complaints

3. What's the scope?
   - All data or specific subset
   - All time or specific period
   - All users or specific users
```

### Step 3: Form Hypotheses

**Prioritize by:**
```
1. Likelihood
   - Most common causes first
   - Recent changes first

2. Ease of testing
   - Quick to validate first
   - Non-destructive tests first

3. Impact if true
   - Critical issues first
```

### Step 4: Test and Validate

**Scientific approach:**
```
1. State hypothesis clearly
2. Predict expected outcome if true
3. Design test to validate
4. Execute test
5. Analyze results
6. Conclude or iterate
```

### Step 5: Implement Solution

**Solution criteria:**
```
- Addresses root cause (not just symptoms)
- Minimizes side effects
- Can be rolled back
- Is tested before production
```

---

## 🐛 Debugging Mindset

### The Debugging Mindset

**Principles:**
```
1. Trust nothing, verify everything
   - Don't assume configs are correct
   - Check actual values, not expected

2. Reproduce first
   - Can you recreate the issue?
   - If not, are you debugging the right thing?

3. Change one thing at a time
   - Multiple changes = confusion
   - Isolate variables

4. Binary search
   - Divide problem space in half
   - Find where things go wrong

5. Rubber duck debugging
   - Explain problem to someone (or something)
   - Often reveals the issue
```

### Common DE Debugging Scenarios

**1. Pipeline Failure**
```
Check in order:
1. Error logs (obvious issues)
2. Input data (schema changes, nulls, volume)
3. Resources (memory, disk, connections)
4. Dependencies (external APIs, databases)
5. Code changes (recent deployments)
```

**2. Data Quality Issues**
```
Check in order:
1. Source data (is it bad upstream?)
2. Transformation logic (joins, filters)
3. Data types (truncation, overflow)
4. Timing (race conditions, order)
5. Duplicates (reprocessing, CDC)
```

**3. Performance Degradation**
```
Check in order:
1. Data volume (did it increase?)
2. Query patterns (new queries?)
3. Resources (CPU, memory, I/O)
4. Indexes (missing, outdated stats)
5. Configuration (changed settings)
```

### Debugging Tools

**For Spark:**
```
1. Spark UI
   - Stage details
   - Task distribution
   - Memory usage

2. Event logs
   - Filter by executor
   - Look for skew

3. EXPLAIN
   - Query plan
   - Partition pruning
```

**For SQL:**
```
1. EXPLAIN ANALYZE
   - Actual vs estimated rows
   - Scan types
   - Bottleneck steps

2. Query profiler
   - Time per step
   - Resource usage

3. pg_stat_statements / query_log
   - Slow queries
   - Patterns
```

**For Kafka:**
```
1. Consumer lag
   - kafka-consumer-groups --describe

2. Partition distribution
   - kafka-topics --describe

3. Broker metrics
   - Under-replicated partitions
   - Active controllers
```

---

## ⚡ Performance Investigation

### Performance Investigation Framework

**Step 1: Baseline**
```
Before optimizing, measure:
- Current performance (latency, throughput)
- Resource usage (CPU, memory, I/O)
- Cost
```

**Step 2: Profile**
```
Find bottlenecks:
- Where is time spent?
- What resource is saturated?
- What's blocking?
```

**Step 3: Hypothesize**
```
Root cause categories:
1. Data skew
2. Inefficient algorithm
3. Resource constraints
4. I/O bottleneck
5. Network latency
6. Configuration issue
```

**Step 4: Optimize**
```
Optimization order:
1. Algorithm changes (10x-100x improvement)
2. Data structure changes (2x-10x)
3. Parallelization (linear scaling)
4. Caching (depends on hit rate)
5. Hardware (diminishing returns)
```

### Common Performance Issues

**1. Spark Data Skew**
```
Symptoms:
- One task takes much longer
- Most tasks finish fast
- Memory errors on some executors

Diagnosis:
df.groupBy("key").count().orderBy(desc("count")).show()

Solutions:
- Salting: Add random prefix to key
- Two-phase aggregation
- Broadcast join for small tables
- Repartition before join
```

**2. SQL Slow Queries**
```
Symptoms:
- Query takes minutes/hours
- High CPU on database
- Timeouts

Diagnosis:
EXPLAIN ANALYZE [query]

Common issues:
- Full table scan (add index)
- Cartesian join (missing join condition)
- Nested subquery (rewrite as CTE/join)
- Too many columns (select specific)
```

**3. Kafka Consumer Lag**
```
Symptoms:
- Growing lag
- Old data in topic
- Processing delays

Diagnosis:
kafka-consumer-groups --describe --group [group]

Solutions:
- Add more consumers
- Increase partitions
- Optimize processing
- Check for slow downstream
```

### Performance Monitoring Checklist

```
Daily checks:
[ ] Pipeline latency
[ ] Data freshness
[ ] Error rates
[ ] Resource utilization

Weekly checks:
[ ] Slow queries report
[ ] Cost by job
[ ] Storage growth
[ ] Capacity planning
```

---

## 🚨 Incident Management

### Incident Response Framework

**Severity Levels:**
```
SEV 1 (Critical):
- Complete outage
- Data loss
- Security breach
Response: Immediate, all-hands

SEV 2 (Major):
- Significant degradation
- Major feature unavailable
Response: Within 1 hour

SEV 3 (Minor):
- Minor degradation
- Workaround available
Response: Same business day

SEV 4 (Low):
- Cosmetic issues
- Non-blocking bugs
Response: Next sprint
```

### Incident Response Steps

**1. Detect**
```
Sources:
- Automated alerts
- User reports
- Monitoring dashboards
```

**2. Assess**
```
Quick questions:
- What's the impact?
- How many affected?
- Is it getting worse?
```

**3. Communicate**
```
- Notify stakeholders
- Set up war room
- Regular updates (every 30 min)
```

**4. Mitigate**
```
Priority: Stop the bleeding
- Rollback recent changes
- Scale up resources
- Divert traffic
- Manual workaround
```

**5. Resolve**
```
Fix root cause:
- Proper fix (may take longer)
- Test before deploying
- Monitor after deployment
```

**6. Post-mortem**
```
Within 48 hours:
- Timeline of events
- Root cause analysis
- Impact assessment
- Action items
```

### On-Call Best Practices

```
Preparation:
- Runbooks for common issues
- Access to all systems
- Escalation paths clear
- Phone charged, alerts working

During incident:
- Stay calm
- Document everything
- Ask for help early
- Focus on mitigation first

After incident:
- Blameless post-mortem
- Update runbooks
- Improve monitoring
```

### Post-Mortem Template

```markdown
# Incident: [Title]
Date: [Date]
Duration: [Start - End]
Impact: [Who/what affected]

## Summary
[2-3 sentence summary]

## Timeline
- HH:MM - Event happened
- HH:MM - Alert fired
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix deployed
- HH:MM - Incident resolved

## Root Cause
[What actually caused the issue]

## Impact
- Users affected: [number]
- Data affected: [scope]
- Business impact: [revenue, reputation]

## What Went Well
- Fast detection
- Good communication
- Quick rollback

## What Could Be Improved
- Monitoring gaps
- Slow escalation
- Missing runbook

## Action Items
1. [Action] - [Owner] - [Due date]
2. [Action] - [Owner] - [Due date]

## Lessons Learned
[Key takeaways]
```

---

## 🔄 Continuous Improvement

### Kaizen for Data Engineers

**Philosophy:**
```
Small, continuous improvements > Big, occasional changes

Daily:
- Fix one small thing
- Learn one new thing
- Improve one process

Weekly:
- Review metrics
- Identify bottlenecks
- Plan improvements

Monthly:
- Retrospective
- Set goals
- Measure progress
```

### Improvement Areas

**1. Code Quality**
```
- Code reviews
- Automated testing
- Documentation
- Refactoring
```

**2. Process**
```
- Reduce manual steps
- Automate repetitive tasks
- Improve monitoring
- Better alerting
```

**3. Knowledge**
```
- Learn new tools
- Study papers
- Attend conferences
- Share with team
```

**4. Systems**
```
- Performance optimization
- Cost reduction
- Reliability improvement
- Security hardening
```

### Metrics to Track

**Personal:**
```
- Bugs introduced vs caught
- Pipeline reliability
- Time to resolution
- Code review feedback
```

**Team:**
```
- Deployment frequency
- Lead time for changes
- Change failure rate
- Mean time to recovery
```

### Creating Improvement Culture

**As Individual:**
```
1. Lead by example
2. Share learnings
3. Celebrate small wins
4. Be open to feedback
```

**As Senior/Lead:**
```
1. Create safe environment
2. Allocate time for improvement
3. Recognize contributions
4. Document and share
```

---

## 💡 Mental Models for Problem Solving

### 1. Occam's Razor
```
"The simplest explanation is usually correct"

Apply:
- Check common issues first
- Don't assume complex failures
- Simple bugs are most common
```

### 2. Inversion
```
"Instead of asking how to succeed, ask how to fail"

Apply:
- What would break this system?
- How could this query be slow?
- What would cause data loss?
```

### 3. Second-Order Thinking
```
"Consider the consequences of consequences"

Apply:
- If I add this index, what else is affected?
- If I change this schema, who downstream breaks?
- If I optimize for speed, what do I sacrifice?
```

### 4. Circle of Competence
```
"Know what you know and what you don't"

Apply:
- Ask for help when outside expertise
- Build expertise deliberately
- Don't pretend to know
```

---

## 🔗 Liên Kết

- [Design Patterns](01_Design_Patterns.md)
- [Architectural Thinking](02_Architectural_Thinking.md)
- [Career Growth](04_Career_Growth.md)
- [Interview Prep](../interview/)

---

*Cập nhật: February 2026*
