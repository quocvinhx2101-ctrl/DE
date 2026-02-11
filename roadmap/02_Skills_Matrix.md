# 📊 Data Engineering Skills Matrix

> Ma trận kỹ năng theo level và domain cho Data Engineer

---

## 🎯 Skill Levels

```
Level 1 (Awareness):    Biết concept, chưa làm thực tế
Level 2 (Beginner):     Làm được với hướng dẫn
Level 3 (Intermediate): Làm được độc lập
Level 4 (Advanced):     Optimize, troubleshoot, mentor
Level 5 (Expert):       Design, innovate, industry lead
```

---

## 💻 Programming Skills

### Python

```
                        Jr    Mid    Sr    Staff
Basic syntax            3     4      4     5
OOP                     2     3      4     4
Functional programming  1     2      3     4
Async/Concurrency       1     2      3     4
Testing (pytest)        2     3      4     4
Packaging               1     2      3     4
Performance profiling   1     2      3     4
```

**Junior Focus:**
- Functions, classes, modules
- pandas, numpy basics
- File I/O, JSON/CSV parsing
- Basic error handling

**Mid Focus:**
- Decorators, context managers
- Unit testing, mocking
- Type hints
- Package management

**Senior Focus:**
- Async patterns (asyncio)
- Memory optimization
- Profiling and debugging
- Code architecture

### SQL

```
                        Jr    Mid    Sr    Staff
Basic queries           3     4      5     5
JOINs                   2     4      5     5
Window functions        1     3      4     5
CTEs/Subqueries         2     3      4     5
Query optimization      1     2      4     5
DDL/Schema design       1     3      4     5
Stored procedures       1     2      3     4
```

**Junior Focus:**
- SELECT, WHERE, GROUP BY
- Basic JOINs
- Simple aggregations
- Data types

**Mid Focus:**
- Window functions
- Complex JOINs
- CTEs
- EXPLAIN plans

**Senior Focus:**
- Query optimization
- Index strategy
- Partitioning
- Advanced analytics functions

### Spark

```
                        Jr    Mid    Sr    Staff
DataFrame API           1     3      4     5
Spark SQL               1     3      4     5
RDD operations          1     2      3     4
Performance tuning      1     2      4     5
Memory management       1     2      3     4
Spark Streaming         1     2      3     4
PySpark/Scala           1     3      4     4
```

**Junior Focus:**
- DataFrame basics
- Read/write operations
- Simple transformations

**Mid Focus:**
- Complex joins
- UDFs
- Caching strategies
- Broadcast variables

**Senior Focus:**
- Partition optimization
- Skew handling
- Memory tuning
- Custom data sources

---

## 🏗️ Architecture Skills

### Data Modeling

```
                        Jr    Mid    Sr    Staff
Normalization           2     3      4     5
Dimensional modeling    1     3      4     5
Data vault              1     2      3     4
Schema design           1     3      4     5
SCD types               1     3      4     4
Graph modeling          1     1      2     3
```

**Junior Focus:**
- Basic normalization (1NF, 2NF, 3NF)
- Primary/foreign keys
- Basic entity relationships

**Mid Focus:**
- Star/snowflake schema
- Fact and dimension tables
- SCD Type 1, 2, 3
- Denormalization trade-offs

**Senior Focus:**
- Data vault methodology
- Multi-source integration
- Schema evolution
- Performance-driven design

### Distributed Systems

```
                        Jr    Mid    Sr    Staff
CAP theorem             1     2      4     5
Partitioning            1     2      4     5
Replication             1     2      3     4
Consistency models      1     2      3     5
Fault tolerance         1     2      3     4
Consensus algorithms    1     1      2     3
```

**Junior Focus:**
- Basic understanding of distributed concepts
- Why data is distributed

**Mid Focus:**
- Partitioning strategies
- Trade-offs between systems
- Basic failure handling

**Senior Focus:**
- System design for scale
- Consistency vs availability decisions
- Cross-region architectures

### System Design

```
                        Jr    Mid    Sr    Staff
Component selection     1     2      4     5
Trade-off analysis      1     2      4     5
Scalability planning    1     2      3     5
Cost estimation         1     2      3     4
Reliability design      1     2      3     4
Security architecture   1     2      3     4
```

---

## 🔧 Tools & Technologies

### Orchestration

```
                        Jr    Mid    Sr    Staff
Airflow basics          1     3      4     5
DAG design              1     3      4     5
Operators/Hooks         1     2      4     5
Dagster/Prefect         1     2      3     4
Error handling          1     3      4     5
Monitoring              1     2      4     5
```

### Streaming

```
                        Jr    Mid    Sr    Staff
Kafka basics            1     2      4     5
Kafka Connect           1     2      3     4
Flink/Spark Streaming   1     2      3     4
Exactly-once            1     2      3     5
Windowing               1     2      3     4
State management        1     2      3     4
```

### Cloud Platforms

```
AWS:                    Jr    Mid    Sr    Staff
S3                      1     3      4     5
Glue                    1     2      3     4
Redshift                1     2      3     4
EMR                     1     2      3     4
Lambda                  1     2      3     4
IAM                     1     2      3     4

GCP:                    Jr    Mid    Sr    Staff
GCS                     1     3      4     5
BigQuery                1     3      4     5
Dataflow                1     2      3     4
Dataproc                1     2      3     4
Pub/Sub                 1     2      3     4
```

### Data Quality

```
                        Jr    Mid    Sr    Staff
Data validation         1     3      4     5
Great Expectations      1     2      3     4
dbt tests               1     2      4     5
Data contracts          1     2      3     4
Monitoring              1     2      3     4
Alerting                1     2      3     4
```

---

## 🤝 Soft Skills

### Communication

```
                        Jr    Mid    Sr    Staff
Technical writing       2     3      4     5
Presentations           1     2      4     5
Stakeholder mgmt        1     2      3     5
Cross-team collab       1     2      4     5
Documentation           2     3      4     5
```

### Leadership

```
                        Jr    Mid    Sr    Staff
Mentoring               1     2      4     5
Code review             2     3      4     5
Project planning        1     2      3     4
Decision making         1     2      4     5
Influence               1     2      3     5
Hiring                  1     1      3     4
```

### Problem Solving

```
                        Jr    Mid    Sr    Staff
Debugging               2     3      4     5
Root cause analysis     1     2      4     5
Trade-off analysis      1     2      4     5
System thinking         1     2      3     5
Strategic thinking      1     1      3     4
```

---

## 📈 Self-Assessment Template

### Current State Assessment

Rate yourself 1-5 for each skill:

**Programming:**
```
[ ] Python basics:        ___/5
[ ] Python advanced:      ___/5
[ ] SQL basics:           ___/5
[ ] SQL advanced:         ___/5
[ ] Spark:                ___/5
```

**Data Engineering:**
```
[ ] Data modeling:        ___/5
[ ] ETL/ELT:              ___/5
[ ] Data quality:         ___/5
[ ] Orchestration:        ___/5
[ ] Streaming:            ___/5
```

**Infrastructure:**
```
[ ] Cloud platforms:      ___/5
[ ] Docker/K8s:           ___/5
[ ] CI/CD:                ___/5
[ ] Monitoring:           ___/5
```

**Soft Skills:**
```
[ ] Communication:        ___/5
[ ] Leadership:           ___/5
[ ] Problem solving:      ___/5
```

### Gap Analysis

Compare your scores to target level:

| Python | 3 | 4 | 1 |
|---|---|---|---|
| SQL | 3 | 5 | 2 |
| Spark | 2 | 4 | 2 |
| Data Modeling | 2 | 4 | 2 |
| Cloud | 2 | 4 | 2 |

### Action Plan

**Top 3 priorities:**
1. ______________________ (Gap: ___)
2. ______________________ (Gap: ___)
3. ______________________ (Gap: ___)

**Learning schedule:**
```
Week 1-4:   Priority #1 focus
Week 5-8:   Priority #2 focus
Week 9-12:  Priority #3 focus
Week 13:    Reassess and adjust
```

---

## 🎯 Level-Up Checklist

### Junior → Mid

**Technical:**
- [ ] Spark proficient (build complex jobs)
- [ ] SQL window functions mastered
- [ ] Orchestration tool expert (Airflow)
- [ ] Cloud basics (storage, compute)
- [ ] Data quality practices

**Delivery:**
- [ ] Shipped 10+ pipelines to production
- [ ] Handled production incidents
- [ ] Contributed to team standards
- [ ] Improved existing systems

### Mid → Senior

**Technical:**
- [ ] System design capability
- [ ] Performance optimization expert
- [ ] Multiple technology stacks
- [ ] Architecture documentation
- [ ] Security best practices

**Leadership:**
- [ ] Mentored junior engineers
- [ ] Led project with 2+ people
- [ ] Made impactful tech decisions
- [ ] Presented to stakeholders
- [ ] Drove team improvements

### Senior → Staff

**Technical:**
- [ ] Cross-team technical strategy
- [ ] Novel solution design
- [ ] Technology evaluation and selection
- [ ] Industry-level expertise

**Organizational:**
- [ ] Multi-team influence
- [ ] Mentored seniors
- [ ] Executive communication
- [ ] Engineering culture impact
- [ ] External recognition

---

## 📚 Skill Development Resources

### Programming

**Python:**
- Fluent Python (book)
- Python Cookbook (book)
- Real Python website

**SQL:**
- LeetCode SQL problems
- Use The Index, Luke (website)
- PostgreSQL documentation

### Data Engineering

**Fundamentals:**
- Designing Data-Intensive Applications
- The Data Warehouse Toolkit
- Fundamentals of Data Engineering

**Modern Stack:**
- dbt documentation
- Apache Kafka documentation
- Apache Spark: The Definitive Guide

### System Design

**Books:**
- System Design Interview vol 1 & 2
- DDIA (mentioned above)

**Practice:**
- System Design Primer (GitHub)
- Educative.io courses

---

## 🔗 Liên Kết

- [Career Levels](01_Career_Levels.md)
- [Learning Resources](03_Learning_Resources.md)
- [Fundamentals](../fundamentals/)
- [Tools](../tools/)

---

*Cập nhật: February 2026*
