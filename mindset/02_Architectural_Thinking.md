# 🏛️ Architectural Thinking

> Tư duy kiến trúc cho Senior/Staff Data Engineer

---

## 📋 Mục Lục

1. [First Principles Thinking](#-first-principles-thinking)
2. [Trade-off Analysis](#-trade-off-analysis)
3. [Scale Thinking](#-scale-thinking)
4. [System Design Mindset](#-system-design-mindset)
5. [Technology Selection](#-technology-selection)

---

## 🎯 First Principles Thinking

### Concept

Phân tích vấn đề về những thành phần cơ bản nhất thay vì dựa vào analogies.

```
Analogy-based (Bad):
"Company X uses Kafka, we should too"

First Principles (Good):
1. What problem are we solving?
2. What are the fundamental requirements?
3. What are the constraints?
4. What solutions fit these constraints?
```

### Framework: 5 Whys

```
Problem: Pipeline is slow

Why 1: Processing takes too long
Why 2: Spark job has data skew
Why 3: One partition has 80% of data
Why 4: Partition key is user_type
Why 5: 80% of users are "free" tier

Root Cause: Poor partition key choice
Solution: Use composite key or salting
```

### Questions to Ask

**Before building anything:**
```
1. What problem are we actually solving?
   - Is this the real problem or symptom?
   
2. Who are the users?
   - What are their needs?
   - What's their technical level?
   
3. What are the constraints?
   - Budget
   - Timeline
   - Team skills
   - Existing systems
   
4. What does success look like?
   - Metrics to measure
   - Timeline for success
   
5. What are the risks?
   - What could go wrong?
   - What's the impact?
```

---

## ⚖️ Trade-off Analysis

### Core Trade-offs

**1. Latency vs Throughput**
```
Low Latency:
- Stream processing
- In-memory storage
- More expensive
- Use for: Real-time dashboards

High Throughput:
- Batch processing
- Disk storage
- Cost-effective
- Use for: Historical analytics
```

**2. Consistency vs Availability**
```
Strong Consistency:
- All reads see latest write
- May be unavailable during partitions
- Use for: Financial transactions

Eventual Consistency:
- Reads may be stale temporarily
- Always available
- Use for: Social media feeds
```

**3. Accuracy vs Speed**
```
High Accuracy:
- Exact counts
- Full reprocessing
- Use for: Financial reports

Approximate (Speed):
- HyperLogLog for unique counts
- Sampling
- Use for: Real-time metrics
```

**4. Build vs Buy**
```
Build:
+ Full control
+ Custom to needs
+ No vendor lock-in
- Time to build
- Maintenance burden
- Opportunity cost

Buy/SaaS:
+ Quick to deploy
+ Managed service
+ Best practices built-in
- Less flexibility
- Vendor lock-in
- Ongoing cost
```

### Trade-off Matrix Template

| Opt A | Opt B | Opt C | Weight |  |
|---|---|---|---|---|
| Performance | 5 | 3 | 4 | 0.25 |
| Cost | 2 | 4 | 3 | 0.20 |
| Maintainability | 3 | 4 | 4 | 0.20 |
| Team skills | 4 | 2 | 3 | 0.15 |
| Time | 3 | 5 | 4 | 0.10 |
| Scalability | 5 | 3 | 4 | 0.10 |
| Weighted Total | 3.65 | 3.40 | 3.60 |  |

---

## 📈 Scale Thinking

### Orders of Magnitude

**Data Volume:**
```
KB  → Single file
MB  → Large file, single machine
GB  → Database table, needs indexing
TB  → Distributed storage needed
PB  → Complex architecture, partitioning critical
EB  → Top tech companies only
```

**Request Rate:**
```
1/min     → Cron job
1/sec     → Simple API
100/sec   → Need caching
10K/sec   → Load balancing, multiple nodes
100K/sec  → Complex architecture
1M/sec    → Custom solutions
```

### Scaling Strategies

**Vertical Scaling (Scale Up):**
```
Before: 16 CPU, 64GB RAM
After:  64 CPU, 256GB RAM

Pros:
- Simple
- No code changes
- Works for some use cases

Cons:
- Has limits
- Expensive
- Single point of failure
```

**Horizontal Scaling (Scale Out):**
```
Before: 1 node
After:  10 nodes

Pros:
- Theoretically unlimited
- Fault tolerant
- Cost-effective

Cons:
- More complex
- Network overhead
- Coordination needed
```

### Capacity Planning

**Back-of-envelope Calculations:**
```
Example: Design storage for user events

Assumptions:
- 10M daily active users
- 50 events/user/day
- 1KB per event

Daily volume:
10M × 50 × 1KB = 500GB/day

Monthly: 500GB × 30 = 15TB
Yearly: 15TB × 12 = 180TB

With 3x replication: 540TB
With 20% growth: 650TB first year

Conclusion: Need data lake, not traditional DB
```

**Rule of Thumb:**
```
Always plan for:
- 3x current load (normal growth)
- 10x for peak events
- 100x for viral/unexpected

If current design can't handle 3x:
→ Start redesigning now
```

---

## 🧩 System Design Mindset

### High-Level Design Steps

```
1. UNDERSTAND
   - Clarify requirements
   - Identify constraints
   - Define scope

2. DESIGN
   - Start with high-level architecture
   - Identify core components
   - Define data flow

3. DEEP DIVE
   - Pick 2-3 critical components
   - Design in detail
   - Address edge cases

4. EVALUATE
   - Identify bottlenecks
   - Consider failure modes
   - Plan for scale
```

### Component Selection Principles

**1. Use the right tool for the job**
```
Not: "We use Kafka for everything"

But: 
- Real-time events → Kafka
- API gateway → Kong/AWS API GW
- Caching → Redis
- Search → Elasticsearch
- OLAP → ClickHouse/Snowflake
```

**2. Minimize moving parts**
```
More components = More failure points

Questions:
- Can we combine these two services?
- Do we really need this queue?
- Can the warehouse handle this transformation?
```

**3. Plan for failure**
```
What if X fails?
- Message queue → Messages in dead letter
- Database → Failover to replica
- API → Circuit breaker, fallback
- Pipeline → Retry, alert, manual intervention
```

### Architectural Patterns to Know

**1. Event-Driven Architecture**
```
Benefits:
- Loose coupling
- Scalability
- Auditability

When to use:
- Multiple consumers
- Async processing okay
- Need event replay
```

**2. Microservices vs Monolith**
```
Monolith:
- Simple to deploy
- Easier debugging
- Good for small teams

Microservices:
- Independent scaling
- Technology flexibility
- Good for large teams
```

**3. Data Lake vs Data Warehouse**
```
Data Lake:
- All data types
- Schema on read
- Cheap storage

Data Warehouse:
- Structured only
- Schema on write
- Optimized queries
```

---

## 🔧 Technology Selection

### Evaluation Framework

**1. Functional Requirements**
```
Does it solve our problem?
- Feature checklist
- Performance benchmarks
- Integration capabilities
```

**2. Non-Functional Requirements**
```
- Scalability: Can it grow with us?
- Reliability: What's the SLA?
- Security: Compliance, encryption
- Maintainability: Ops burden
```

**3. Organizational Fit**
```
- Team skills: Can we operate it?
- Community: Is it well-supported?
- Vendor: Is the company stable?
- Cost: TCO over 3 years
```

### Red Flags

**Technology:**
```
- No active community
- Single maintainer
- No major companies using in production
- Poor documentation
- No breaking change policy
```

**Vendor:**
```
- Lock-in with no exit path
- Pricing not transparent
- Poor support responsiveness
- Frequent breaking changes
```

### Proof of Concept (POC)

**POC Checklist:**
```
1. Define success criteria upfront
2. Use realistic data volume
3. Test edge cases
4. Measure actual performance
5. Evaluate ops experience
6. Time-box to 2-4 weeks
7. Document findings
```

**POC Report Template:**
```
Technology: [Name]
Use Case: [What we're evaluating]

Criteria Results:
- Performance: [Metric vs Target]
- Scalability: [Test results]
- Usability: [Team feedback]
- Cost: [Estimated TCO]

Pros:
- ...

Cons:
- ...

Recommendation: [Go/No-go/More evaluation]
```

---

## 🎓 Developing Architectural Skills

### How to Learn

**1. Study existing architectures:**
```
- Read company tech blogs
- Study open source projects
- Review architecture diagrams
- Attend conference talks
```

**2. Practice design:**
```
- System design interviews (even for practice)
- Document your own systems
- Review others' designs
- Propose alternatives
```

**3. Learn from failures:**
```
- Post-mortems
- Incident reports
- What could have been prevented?
```

### Resources

**Books:**
- Designing Data-Intensive Applications
- System Design Interview (vol 1 & 2)
- Building Microservices
- Data Mesh

**Practice:**
- System Design Primer (GitHub)
- Educative.io courses
- Draw your company's architecture

---

## 📝 Architecture Decision Records (ADR)

### Template

```markdown
# ADR-001: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the background?]

## Decision
[What did we decide?]

## Consequences
[What are the implications?]

### Positive
- ...

### Negative
- ...

### Neutral
- ...

## Alternatives Considered
[What else did we evaluate?]
```

### Example

```markdown
# ADR-003: Use Apache Iceberg for Data Lake

## Status
Accepted

## Context
We need a table format for our data lake that supports:
- ACID transactions
- Schema evolution
- Time travel
- Partition evolution

## Decision
Use Apache Iceberg as our table format.

## Consequences

### Positive
- ACID transactions on S3
- Easy schema changes
- Works with multiple engines (Spark, Flink, Trino)

### Negative
- Learning curve for team
- Metadata overhead
- Need to manage maintenance operations

## Alternatives Considered
1. Delta Lake - Good but Databricks-centric
2. Apache Hudi - More complex, upsert-focused
3. Raw Parquet - No ACID, no schema evolution
```

---

## 🔗 Liên Kết

- [Design Patterns](01_Design_Patterns.md)
- [Problem Solving](03_Problem_Solving.md)
- [Career Growth](04_Career_Growth.md)
- [System Design Interview](03_System_Design.md)

---

*Cập nhật: February 2026*
