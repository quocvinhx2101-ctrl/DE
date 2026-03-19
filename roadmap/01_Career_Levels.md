# 🗺️ Data Engineering Career Roadmap

> Lộ trình phát triển sự nghiệp từ Beginner đến Staff/Principal Data Engineer

---

## 📊 Career Levels Overview

**DATA ENGINEERING CAREER PATH**

| Level | Years | Focus | Impact |
|---|---|---|---|
| Beginner | 0-1 | Learn fundamentals | Individual tasks |
| Junior | 1-2 | Build with guidance | Feature level |
| Mid | 2-4 | Independent delivery | Project level |
| Senior | 4-7 | Lead and mentor | Team level |
| Staff | 7-10 | Technical strategy | Org level |
| Principal | 10+ | Industry leadership | Company level |

---

## 🌱 Beginner (0-1 years)

### Mục Tiêu
- Hiểu data engineering là gì
- Nắm vững fundamentals
- Build first data pipelines

### Skills Required

**Programming:**
```
Python:
- Variables, data types, control flow
- Functions và modules
- File I/O
- Libraries: pandas, requests

SQL:
- SELECT, WHERE, GROUP BY
- JOINs (INNER, LEFT, RIGHT)
- Aggregations (COUNT, SUM, AVG)
- Subqueries
```

**Data Concepts:**
```
- Data types (structured, semi, unstructured)
- Databases vs data warehouses
- ETL process basics
- Data formats (CSV, JSON, Parquet)
```

**Tools to Learn:**
```
- Git basics
- Command line
- One database (PostgreSQL recommended)
- One cloud (start with free tier)
```

### Learning Path (3-6 months)

**Month 1-2: Foundations**
```
Week 1-2: Python basics
- DataCamp/Codecademy Python course
- Practice with small scripts

Week 3-4: SQL fundamentals
- SQLZoo or Mode Analytics SQL tutorial
- Practice on PostgreSQL locally

Week 5-6: Data formats and tools
- Work with CSV, JSON
- Learn pandas basics
- Git version control

Week 7-8: First ETL pipeline
- Extract from API → Transform with Python → Load to DB
- Document your process
```

**Month 3-4: Cloud Introduction**
```
- Sign up for AWS/GCP free tier
- Learn object storage (S3/GCS)
- Deploy simple pipeline to cloud
- Understand IAM basics
```

**Month 5-6: Project Focus**
```
- Build end-to-end personal project
- Document on GitHub
- Write blog post about learnings
```

### Sample Projects
1. COVID data dashboard (API → PostgreSQL → visualization)
2. Weather data collector (daily cron job)
3. Personal finance tracker

---

## 🌿 Junior (1-2 years)

### Mục Tiêu
- Work on production pipelines
- Understand data quality
- Collaborate with team

### Skills Required

**Programming:**
```
Python:
- OOP basics
- Error handling
- Unit testing
- Virtual environments

SQL:
- Window functions
- CTEs
- Query optimization basics
- Stored procedures
```

**Data Engineering:**
```
- Batch processing concepts
- Data validation
- Scheduling (cron, basic orchestration)
- Logging and monitoring basics
```

**Tools to Learn:**
```
- Apache Spark basics
- Airflow (or similar orchestrator)
- Docker fundamentals
- Cloud services expansion
```

### Learning Path (12 months)

**Quarter 1: Spark & Big Data**
```
- Learn Spark fundamentals
- Understand distributed computing
- Practice with real datasets (1GB+)
- Compare with pandas for performance
```

**Quarter 2: Orchestration**
```
- Learn Airflow deeply
- Build DAGs with dependencies
- Error handling and retries
- Monitoring and alerting
```

**Quarter 3: Cloud Data Stack**
```
- Learn cloud data warehouse (Snowflake/BigQuery)
- Understand storage vs compute separation
- Cost optimization basics
- Data security fundamentals
```

**Quarter 4: Production Skills**
```
- CI/CD for data pipelines
- Infrastructure as Code basics
- Incident response
- Documentation practices
```

### Key Milestones
- [ ] Shipped 5+ pipelines to production
- [ ] Fixed production incidents independently
- [ ] Participated in code reviews
- [ ] Mentored by senior engineer

---

## 🌳 Mid Level (2-4 years)

### Mục Tiêu
- Own end-to-end features
- Design solutions independently
- Start mentoring juniors

### Skills Required

**Architecture:**
```
- Data modeling (dimensional, data vault)
- Storage strategies (hot/warm/cold)
- Batch vs streaming trade-offs
- API design for data services
```

**Advanced Technical:**
```
- Advanced Spark optimization
- Streaming fundamentals (Kafka)
- dbt for transformations
- Data quality frameworks
```

**Soft Skills:**
```
- Technical writing
- Meeting facilitation
- Cross-team collaboration
- Estimation and planning
```

### Learning Path (24 months)

**Year 1: Technical Depth**
```
Months 1-3: Advanced Data Modeling
- Read "The Data Warehouse Toolkit"
- Implement dimensional models
- Learn slowly changing dimensions

Months 4-6: Streaming Introduction
- Learn Kafka fundamentals
- Build first streaming pipeline
- Understand exactly-once semantics

Months 7-9: Modern Data Stack
- Master dbt
- Learn data quality tools
- Implement data contracts

Months 10-12: Performance & Scale
- Optimize expensive pipelines
- Handle 10x data growth
- Cost optimization projects
```

**Year 2: Technical Breadth & Leadership**
```
Months 1-3: Data Platform Thinking
- Understand self-service analytics
- Build reusable components
- API design for data

Months 4-6: Observability
- Implement comprehensive monitoring
- Build data quality dashboards
- Incident management processes

Months 7-9: Team Contribution
- Mentor 1-2 juniors
- Lead small projects
- Improve team processes

Months 10-12: Senior Preparation
- System design practice
- Technical presentations
- Cross-team projects
```

### Key Milestones
- [ ] Designed and implemented major feature
- [ ] Mentored junior engineers
- [ ] Led technical discussions
- [ ] Presented at team/company level
- [ ] Handled complex production issues

---

## 🌲 Senior (4-7 years)

### Mục Tiêu
- Lead projects and teams
- Make architectural decisions
- Influence org-wide practices

### Skills Required

**Architecture & Strategy:**
```
- Complex system design
- Build vs buy decisions
- Technology evaluation
- Migration strategies
- Scalability planning
```

**Leadership:**
```
- Project leadership
- Mentoring multiple engineers
- Hiring and interviewing
- Stakeholder management
- Technical roadmaps
```

**Business Impact:**
```
- Understand business metrics
- Cost-benefit analysis
- ROI justification
- Cross-functional collaboration
```

### Responsibilities

**Technical:**
| Senior DE Role |
|---|
| 40% Hands-on coding |
| 30% Design and architecture |
| 20% Mentoring and review |
| 10% Planning and communication |

**Day-to-Day:**
- Design complex data systems
- Review PRs and provide feedback
- Guide juniors/mids on approach
- Collaborate with stakeholders
- Drive technical decisions
- Document architecture decisions

### Learning Path (3 years)

**Year 1: Architecture Mastery**
```
- Read "Designing Data-Intensive Applications"
- Lead major architecture project
- Evaluate and introduce new technology
- Build team best practices
```

**Year 2: Leadership Skills**
```
- Lead cross-team initiative
- Mentor 3+ engineers
- Participate in hiring
- Present at external meetups
```

**Year 3: Business & Strategy**
```
- Understand company strategy
- Build business relationships
- Drive significant cost savings
- Influence org-wide decisions
```

### Key Milestones
- [ ] Led project with 3+ engineers
- [ ] Made impactful architecture decision
- [ ] Mentored engineer to promotion
- [ ] Reduced costs by 20%+
- [ ] Spoke at external conference

---

## 🏔️ Staff/Principal (7+ years)

### Mục Tiêu
- Set technical direction
- Solve hardest problems
- Impact across organization

### Staff vs Principal

```
Staff Engineer:
- Scope: Multiple teams
- Focus: Technical excellence
- Impact: Department level

Principal Engineer:
- Scope: Entire organization
- Focus: Technical strategy
- Impact: Company level
```

### Skills Required

**Technical Strategy:**
```
- Multi-year technical vision
- Technology portfolio management
- Industry trend awareness
- Innovation leadership
```

**Organizational Impact:**
```
- Build engineering culture
- Define standards and practices
- Influence without authority
- Executive communication
```

**Business Acumen:**
```
- Understand P&L
- Strategic partnerships
- Competitive landscape
- Customer perspective
```

### Responsibilities

| Staff/Principal Role |
|---|
| 30% Solving hardest technical problems |
| 25% Technical strategy and vision |
| 25% Mentoring and growing leaders |
| 20% Organizational influence |

**Activities:**
- Define multi-year technical roadmap
- Solve cross-org technical challenges
- Build and evolve engineering practices
- Mentor senior engineers to staff
- Partner with executives on strategy
- Represent company externally

### Path to Staff

**Option 1: Depth → Breadth**
```
1. Become expert in one area
2. Expand to adjacent areas
3. Connect expertise across teams
4. Drive org-wide improvements
```

**Option 2: IC → Leadership → IC**
```
1. Strong IC foundation
2. Try management (optional)
3. Return to IC track
4. Apply leadership skills technically
```

### Key Milestones
- [ ] Defined multi-team technical strategy
- [ ] Solved company-wide problem
- [ ] Mentored senior → staff transition
- [ ] Industry recognition (talks, writing)
- [ ] Executive-level relationships

---

## 🔄 IC vs Management Track

### Comparison

| Jr → Mid → Sr → Staff → Principal |
|---|
| Focus: |
| - Technical depth |
| - Solving hard problems |
| - Technical influence |
| - Mentoring |
| Jr → Mid → Sr → Manager → Director → VP |
| Focus: |
| - People management |
| - Team performance |
| - Hiring/firing |
| - Business outcomes |

### Questions to Ask Yourself

**Consider IC if:**
- Love solving technical problems
- Prefer deep focus time
- Want to stay hands-on
- Enjoy mentoring 1:1
- Find energy in building

**Consider Management if:**
- Love building teams
- Enjoy process improvement
- Want organizational impact
- Find energy in people
- Comfortable with ambiguity

### Hybrid Options

```
Tech Lead:
- 60% technical, 40% leadership
- Lead project, not people
- Common stepping stone

Engineering Manager:
- 30% technical, 70% people
- Manage team of 5-10
- Can transition back to IC

Staff Engineer:
- 80% technical, 20% leadership
- Influence without authority
- Senior IC path
```

---

## 📈 Salary Benchmarks (US, 2025)

```
Level          Salary Range         Equity (4-year)
+-------------+-------------------+------------------+
| Junior      | $90K - $130K      | $0 - $50K        |
| Mid         | $120K - $170K     | $20K - $100K     |
| Senior      | $160K - $220K     | $50K - $200K     |
| Staff       | $200K - $280K     | $100K - $400K    |
| Principal   | $250K - $350K+    | $200K - $800K+   |
+-------------+-------------------+------------------+

Notes:
- FAANG/Big Tech: Add 30-50%
- Startups: Lower base, higher equity
- Remote: May adjust for location
```

---

## 🎯 Action Items by Level

### For Beginners
1. Complete SQL course this month
2. Build first pipeline next month
3. Create GitHub portfolio
4. Apply for junior roles

### For Juniors
1. Identify knowledge gaps
2. Find a mentor
3. Contribute to team projects
4. Start preparing for mid-level

### For Mid Level
1. Take on ownership of larger scope
2. Start mentoring
3. Build T-shaped skills
4. Practice system design

### For Senior
1. Define technical vision for team
2. Build relationships across org
3. Grow team members
4. Consider staff trajectory

---

## 🔗 Liên Kết

- [Skills Details](02_Skills_Matrix.md)
- [Learning Resources](03_Learning_Resources.md)
- [Interview Prep](../interview/)
- [Mindset](../mindset/)

---

*Cập nhật: February 2026*
