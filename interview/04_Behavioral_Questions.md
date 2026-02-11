# 🎯 Behavioral Interview Questions

> STAR Method và các tình huống phỏng vấn hành vi cho Data Engineer

---

## 📋 Mục Lục

1. [STAR Method Framework](#-star-method-framework)
2. [Leadership & Ownership](#-leadership--ownership)
3. [Problem Solving & Debugging](#-problem-solving--debugging)
4. [Collaboration & Communication](#-collaboration--communication)
5. [Handling Failure](#-handling-failure)
6. [Technical Decision Making](#-technical-decision-making)

---

## 📖 STAR Method Framework

### STAR Format

```
S - Situation
    Mô tả bối cảnh, context của vấn đề
    - Công ty/team nào?
    - Thời điểm nào?
    - Scale của hệ thống?

T - Task
    Trách nhiệm cụ thể của bạn là gì?
    - Bạn được giao làm gì?
    - Mục tiêu cần đạt?
    - Constraints?

A - Action
    Bạn đã làm gì cụ thể?
    - Các bước thực hiện
    - Quyết định kỹ thuật
    - Cách làm việc với người khác

R - Result
    Kết quả đạt được (có số liệu)
    - Metrics cải thiện
    - Business impact
    - Lessons learned
```

### Tips cho STAR

```
✅ NÊN:
- Dùng số liệu cụ thể: "Giảm 50% latency"
- Focus vào actions CỦA BẠN, không phải team
- Thể hiện thought process
- Kết thúc với lessons learned

❌ KHÔNG:
- Nói chung chung không chi tiết
- Chỉ nói về team, không nói về bản thân
- Thiếu kết quả đo lường được
- Đổ lỗi cho người khác khi thất bại
```

---

## 👑 Leadership & Ownership

### Q1: "Tell me about a project you led from start to finish"

**Sample Answer:**

```
Situation:
"At [Company], our data pipeline was processing 10GB/day 
but business was expanding to new markets, expecting 
100GB/day within 6 months."

Task:
"I was responsible for redesigning the entire ingestion 
layer to handle 10x scale with same team size."

Action:
"1. I analyzed current bottlenecks - found batch ETL 
   couldn't keep up with SLA
2. Researched streaming alternatives - evaluated Kafka, 
   Kinesis, Pulsar
3. Created RFC document, presented to team and stakeholders
4. Led implementation over 2 sprints:
   - Set up Kafka cluster (3 brokers, 12 partitions)
   - Migrated 5 data sources incrementally
   - Implemented monitoring with Prometheus + Grafana
5. Trained 2 junior engineers on new system"

Result:
"- Scaled from 10GB to 150GB/day successfully
- Reduced end-to-end latency from 1 hour to 5 minutes
- Zero data loss during migration
- System still running 2 years later with minimal maintenance"
```

### Q2: "Describe a time you took ownership of something outside your job description"

```
Situation:
"Our ML team was struggling with feature freshness - 
their models used stale data because they didn't have 
real-time access to our production database."

Task:
"Though not my formal responsibility, I saw an opportunity 
to bridge DE and ML needs."

Action:
"1. Initiated meeting with ML lead to understand requirements
2. Proposed streaming feature store concept
3. Built POC in 2 weeks using my 20% time:
   - Kafka → Flink → Redis for real-time features
   - Scheduled job → S3/Parquet for historical features
4. Presented to engineering leadership
5. Got buy-in for full implementation"

Result:
"- Feature freshness improved from 24h to 5 minutes
- ML model accuracy improved 12% due to fresher data
- Got recognized in engineering newsletter
- Became official Feature Store project owner"
```

### Q3: "Tell me about a time you disagreed with your manager"

```
Situation:
"My manager wanted to migrate to Hadoop for cost savings. 
I believed cloud-native solution would be better long-term."

Task:
"I needed to present an alternative viewpoint respectfully 
while backing it with data."

Action:
"1. First, I fully understood manager's perspective:
   - Cost reduction was priority (budget cut 30%)
   - Hadoop was proven technology
2. Did research over weekend:
   - Calculated 3-year TCO for both options
   - Included hidden costs: ops, hiring, training
   - Modeled query performance comparison
3. Scheduled 1:1 to present findings, not to 'win'
4. Asked: 'Can I share some additional data points?'
5. Proposed hybrid: Spark on cloud with spot instances"

Result:
"- Manager appreciated data-driven approach
- We went with modified cloud solution
- Achieved 40% cost reduction (better than Hadoop estimate)
- Relationship with manager actually strengthened"
```

---

## 🔧 Problem Solving & Debugging

### Q4: "Tell me about the most difficult bug you've debugged"

```
Situation:
"Production dashboard was showing wrong revenue numbers - 
$2M mismatch with finance team's reports."

Task:
"I was on-call and needed to find root cause immediately 
as CFO was using data for board meeting next morning."

Action:
"1. First 30 min: Gathered data
   - Compared our pipeline output vs source system
   - Found discrepancy started 3 days ago
2. Hour 1: Bisected the problem
   - Raw data: correct
   - Transformed data: wrong
   - Narrowed to specific dbt model
3. Hour 2: Found root cause
   - Recent PR changed join condition
   - Inner join → Left join (seemed innocent)
   - But caused duplicate rows for multi-currency orders
4. Hour 3: Fixed and validated
   - Reverted PR, backfilled 3 days
   - Added data quality test for uniqueness
   - Wrote post-mortem"

Result:
"- Fixed before board meeting (4am finish)
- Added 15 new dbt tests to prevent similar issues
- Implemented PR template with 'Impact on existing data' section
- Became go-to person for complex debugging"
```

### Q5: "Describe a time you improved system performance significantly"

```
Situation:
"Daily aggregation job grew from 30 min to 4 hours over 
6 months. Team was adding more upstream dependencies."

Task:
"Reduce job runtime to under 1 hour to meet SLA."

Action:
"1. Profiled Spark job:
   - 80% time in one shuffle stage
   - Data skew: one customer had 40% of all transactions
2. Implemented three optimizations:
   - Salted join key for large customer
   - Broadcast join for dimension tables
   - Converted to incremental model (process only new data)
3. Also added:
   - Partitioning by date
   - Z-ordering on customer_id
   - Pre-aggregation layer"

Result:
"- Runtime: 4 hours → 25 minutes (90% reduction)
- Cost: $200/day → $30/day (85% reduction)
- Scale: Can now handle 10x data growth
- Documented pattern for team reuse"
```

---

## 🤝 Collaboration & Communication

### Q6: "How do you explain technical concepts to non-technical stakeholders?"

```
Situation:
"Finance team requested real-time revenue dashboard. 
They didn't understand why it would take 3 months."

Task:
"Explain technical complexity and get buy-in for timeline."

Action:
"1. Avoided jargon - no 'streaming', 'latency', 'distributed'
2. Used analogy:
   'Currently we send mail daily (batch)
    You're asking for real-time phone calls (streaming)
    We need to install the phone lines first'
3. Drew simple diagram on whiteboard:
   - Current: Source → Wait 1 day → Dashboard
   - Proposed: Source → Kafka → Dashboard (~5 min delay)
4. Broke down timeline visibly:
   - Month 1: 'Install phone lines' (infrastructure)
   - Month 2: 'Train operators' (develop connectors)
   - Month 3: 'Test calls work' (testing + launch)
5. Offered trade-off:
   'We could do hourly refresh in 1 month - would that help?'"

Result:
"- Finance team understood and approved timeline
- They actually chose hourly refresh as MVP
- Project delivered on time
- Built strong relationship with finance stakeholders"
```

### Q7: "Tell me about a conflict with a coworker and how you resolved it"

```
Situation:
"Backend engineer wanted to write directly to my data warehouse 
for 'faster delivery'. This would bypass data quality checks."

Task:
"Protect data integrity while maintaining good relationship."

Action:
"1. First: Listened to understand their pressure
   - PM pushing for fast feature delivery
   - Our ingestion process 'too slow'
2. Acknowledged their concern:
   'I understand the pressure. Let's find a solution together.'
3. Explained my concern without blame:
   - Previous direct writes caused $50K reconciliation cost
   - Not saying 'no', saying 'let's find better way'
4. Proposed alternatives:
   - Option A: Add their endpoint to existing CDC pipeline
   - Option B: Create dedicated fast-path with basic validation
   - Option C: Pair program to speed up integration
5. We chose Option B together"

Result:
"- Feature delivered on time
- Data quality maintained
- Backend engineer became advocate for proper data flow
- Created 'fast-path' pattern for future urgent needs"
```

---

## 💥 Handling Failure

### Q8: "Tell me about a time you failed"

```
Situation:
"Migrated production database during business hours based 
on my recommendation that it would be 'quick and safe'."

Task:
"I was responsible for the migration plan and execution."

The Failure:
"Migration took 3 hours instead of estimated 30 minutes.
- Unexpected foreign key constraints
- Had to roll back twice
- Business lost $30K in blocked transactions"

What I Did After:
"1. Took full responsibility - didn't blame anyone
2. Wrote detailed post-mortem:
   - Root cause: Insufficient testing on production-like data
   - I was overconfident based on staging success
3. Proposed process changes:
   - Mandatory dry-run on production replica
   - All migrations during maintenance window
   - Runbook with explicit go/no-go criteria
4. Personally implemented migration automation framework"

Result:
"- Next 12 migrations: Zero incidents
- Framework now used by 5 teams
- Learned: 'Failing is okay, failing twice the same way is not'"
```

### Q9: "Describe a project that didn't go as planned"

```
Situation:
"Led data platform modernization - estimated 6 months, 
actually took 14 months."

What Went Wrong:
"1. Underestimated legacy complexity
2. Key engineer left mid-project
3. Requirements changed 3 times"

How I Adapted:
"1. Transparency with leadership:
   - Bi-weekly status updates
   - Re-scoped at month 4 (reduced features for phase 1)
2. Knowledge distribution:
   - Documented everything
   - Pair programming mandatory
   - No single points of failure
3. Requirements management:
   - Introduced change request process
   - Showed cost of scope creep explicitly"

Result:
"- Project completed (delayed but successful)
- New platform 5x faster than legacy
- Team learned realistic estimation:
  'Multiply initial estimate by 2.5 for migrations'"
```

---

## 🎯 Technical Decision Making

### Q10: "How do you choose between technologies?"

**Framework:**

```
My Evaluation Criteria:
1. Does it solve the problem? (Must-have)
2. Team familiarity (Learning curve)
3. Community & support (Long-term viability)
4. Total cost (License + Ops + Training)
5. Integration with existing stack
```

**Example Answer:**

```
Situation:
"Needed to choose between Airflow and Dagster for new 
orchestration platform."

My Evaluation:
"1. Problem fit: Both can orchestrate pipelines - tie
2. Team: 3 engineers knew Airflow, 0 knew Dagster
3. Community: Airflow larger, Dagster growing fast
4. Cost: Both open source, similar ops cost
5. Integration: Airflow had more existing operators

Additional factors:
- Our use case was asset-centric (Dagster strength)
- We wanted better testing (Dagster strength)
- Timeline was tight (Airflow advantage)"

Decision:
"Chose Airflow for Phase 1 (team velocity)
Planned Dagster POC for Phase 2 (future-ready)
Documented decision in ADR for future reference"
```

### Q11: "Tell me about a time you made a wrong technical decision"

```
Situation:
"Chose NoSQL (MongoDB) for analytics data because 
'flexible schema sounds good for changing requirements'."

Why It Was Wrong:
"1. Analytics queries needed joins - NoSQL is bad at this
2. Query patterns were actually predictable
3. Team had to learn new technology
4. Aggregation performance was poor"

What I Learned:
"1. 'Flexibility' has trade-offs
2. Understand query patterns BEFORE choosing database
3. Don't choose tech based on buzzwords
4. It's okay to admit mistake and pivot"

Action Taken:
"- After 6 months, migrated to PostgreSQL
- Wrote ADR documenting why NoSQL didn't work
- Created checklist for future database decisions"
```

---

## 📝 Quick Reference

### Common Questions Checklist

```
Leadership:
[ ] Project you led
[ ] Time you mentored someone
[ ] Decision you drove

Problem Solving:
[ ] Difficult bug
[ ] Performance improvement
[ ] Incident you handled

Collaboration:
[ ] Conflict resolution
[ ] Cross-team project
[ ] Explaining to non-technical

Failure:
[ ] Time you failed
[ ] Project that didn't go well
[ ] Wrong decision you made
```

### Power Phrases

```
Showing ownership:
- "I took responsibility for..."
- "I drove the decision to..."
- "I identified the opportunity and proposed..."

Showing collaboration:
- "I aligned stakeholders by..."
- "I brought together... and..."
- "I facilitated agreement on..."

Showing learning:
- "What I learned from this was..."
- "If I could do it again, I would..."
- "This changed how I approach..."
```

---

## 🔗 Liên Kết

- [Common Interview Questions](01_Common_Interview_Questions.md)
- [SQL Deep Dive](02_SQL_Deep_Dive.md)
- [System Design](03_System_Design.md)
- [Problem Solving Mindset](../mindset/03_Problem_Solving.md)

---

*Cập nhật: February 2026*
