# Tech Leadership for Staff+ Data Engineers

> From "write great code" to "make the team write great code" — taught through real scenarios and decision frameworks you'll actually face.

(Từ "viết code giỏi" → "giúp team viết code giỏi" — qua scenario thực tế và framework ra quyết định)

---

## 📋 Mục Lục

1. [Staff+ Roles — What Actually Changes](#staff-roles--what-actually-changes)
2. [Technical Strategy — How to Write One That Matters](#technical-strategy)
3. [Influence Without Authority — The Core Skill](#influence-without-authority)
4. [Decision Making — Real Scenarios](#decision-making--real-scenarios)
5. [Mentoring & Growing Others](#mentoring--growing-others)
6. [Anti-Patterns (With War Stories)](#anti-patterns-with-war-stories)

---

## Staff+ Roles — What Actually Changes

### The Day Your Job Changes

**Scene:** You've been a Senior DE for 3 years. You're promoted to Staff DE. Your manager says: "Congrats! Now figure out what you should be doing."

Nobody tells you this, but here's what changes:

```
SENIOR DE:
  Monday: Pick up JIRA ticket → Code → PR → Deploy → Next ticket
  Success metric: "My pipeline is reliable, fast, and well-tested"
  Scope: Your pipelines, your domain

STAFF DE:
  Monday: Review 3 design docs → Facilitate architecture discussion → 
          1:1 with junior → Draft RFC for platform migration → 
          Write 40 lines of code for a POC
  Success metric: "The org ships better data pipelines because of me"
  Scope: 2-3 teams, cross-cutting concerns, org-wide standards
```

### The 4 Archetypes (Which One Are You?)

| Archetype | Day-to-day | Best for | Example |
|-----------|-----------|----------|---------|
| **Tech Lead** | Guide one team's direction. Partner with EM/PM | People who like ownership of a team | "I own the data platform roadmap and keep 6 engineers productive" |
| **Architect** | Cross-team standards. Long-term (6-24 month) decisions | Systems thinkers who see patterns across teams | "I designed our company-wide data contract standard across 4 domains" |
| **Solver** | Hardest problems. Sent where teams are stuck | Deep experts who love debugging | "Team X's pipeline was failing for 2 weeks. I found a race condition in their Spark shuffle" |
| **Right Hand** | CTO's delegate. Org process improvement | Generalists who can context-switch | "I evaluated 3 warehouse vendors, led the POC, and presented to the board" |

> 💡 Most Staff DEs start as **Tech Lead**, evolve toward **Architect** as scope expands. The **Solver** archetype is rare and usually reserved for people with exceptional depth in one area (e.g., query optimization, distributed systems).

---

## Technical Strategy

### Scenario: Your CTO Asks "What's Our Data Strategy?"

You're in a meeting with the CTO and VP Engineering. CTO says: "Our data infrastructure is a mess. Multiple teams complaining. What's the plan?"

You have 2 options:

```
Option A (what juniors do):
  "We should migrate to Snowflake and adopt dbt."
  
  This is a TECHNOLOGY answer. It answers HOW but not WHY.
  CTO will ask: "OK but why? What problem does that solve? How much? Timeline?"
  You don't have answers.

Option B (what Staff does):
  Opens a strategy document with:
  1. Current pain points (with numbers)
  2. Vision (where we should be in 18 months)
  3. Phased roadmap (what we do each quarter)
  4. Success metrics (how we measure progress)
  5. Investment required (headcount, infrastructure cost)
  6. Risks and mitigations
```

### Template With Real Numbers

```markdown
# Data Platform Strategy 2026

## Executive Summary

Our data infrastructure is holding back 4 product teams. Pipelines fail 3x/week,
data requests take 3 weeks to fulfill, and we have no data quality framework.
This strategy addresses these problems in 3 phases over 18 months, requiring 
$120K additional annual cloud cost and 2 additional hires.

## Current State (with evidence)

| Metric | Current | Industry Benchmark | Gap |
|--------|---------|-------------------|-----|
| Pipeline reliability | 92% | 99.5% | Critical |
| Time to fulfill data request | 3 weeks | 2-3 days | Critical |
| Data incidents per month | 5 | < 1 | High |
| Self-serve analytics adoption | 0% | 60% | High |
| Infrastructure: | Single EC2 Airflow, PostgreSQL warehouse | Managed services | — |

## Root Cause Analysis

1. **No orchestration resilience**: Airflow runs on a single EC2 instance. 
   When it goes down, all 15 pipelines stop. Last month: 14 hours downtime.
   
2. **Warehouse not built for analytics**: PostgreSQL handles OLTP well but 
   analytical queries on 500M+ rows take 40+ minutes. Analysts give up.
   
3. **No data quality layer**: We discover bad data when the CFO notices wrong 
   numbers on the dashboard. Zero automated checks.

4. **Central team bottleneck**: 3 DEs serving 10 product teams. 
   Average 15 tickets in backlog = 3-week wait time.

## Phased Roadmap

### Phase 1: Foundation (Q1-Q2) — "Stop the bleeding"
Focus: Reliability + Quality

| Initiative | Effort | Impact | Owner |
|-----------|--------|--------|-------|
| Migrate Airflow to MWAA (managed) | 3 weeks | Pipeline reliability 92% → 99% | @staff-de |
| Implement Great Expectations on top 5 pipelines | 4 weeks | Data incidents 5/mo → 2/mo | @senior-de-1 |
| Setup DataHub catalog | 2 weeks | Data discovery time 2h → 5min | @senior-de-2 |

**Cost:** $3K/mo additional (MWAA)
**Success gate:** Reliability > 98%, incidents < 3/mo → proceed to Phase 2

### Phase 2: Capability (Q3-Q4) — "Enable the business"
Focus: Performance + Self-serve

| Initiative | Effort | Impact | Owner |
|-----------|--------|--------|-------|
| Migrate warehouse to BigQuery | 8 weeks | Query time 40min → 30sec | @staff-de + @new-hire-1 |
| Adopt dbt for transform layer | 6 weeks | Transform dev time -50% | @senior-de-1 |
| Launch Metabase for self-serve BI | 3 weeks | Self-serve adoption 0% → 30% | @new-hire-2 |
| Streaming layer (Kafka) for 2 real-time use cases | 8 weeks | Real-time capability | @senior-de-2 |

**Cost:** $12K/mo additional (BigQuery + Kafka)
**Hire:** +1 DE (mid-level), +1 Analytics Engineer
**Success gate:** Self-serve > 30%, query < 1min → proceed to Phase 3

### Phase 3: Scale (2027 H1) — "Decentralize"
Focus: Domain ownership + Advanced

| Initiative | Effort | Impact | Owner |
|-----------|--------|--------|-------|
| Data Mesh pilot (2 domains) | 12 weeks | Request backlog -60% | @staff-de |
| Iceberg migration | 8 weeks | Storage cost -30%, time travel | @senior-de-1 |
| ML feature store (Feast) | 8 weeks | ML model training from days → hours | @new-hire-1 |

**Success gate:** Backlog < 5 tickets, 2 domains self-serve

## Investment Summary

| | Current (annual) | After Phase 3 (annual) |
|---|---|---|
| Cloud infrastructure | $36K | $180K |
| Headcount (fully loaded) | $450K (3 DEs) | $750K (5 DEs + 1 AE) |
| **Total** | **$486K** | **$930K** |
| Data incidents/year | 60 (×$5K avg cost each = $300K) | 12 (×$5K = $60K) |
| Request backlog cost | 15 requests × 3 weeks × $2K opportunity cost = $90K | -80% |
| **Net ROI** | | **$930K investment saves ~$330K/yr in incidents + unblocks 4 product teams** |

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| BigQuery migration takes longer than 8 weeks | High | Delayed Phase 2 | Start with 3 most critical tables, migrate rest in parallel |
| Hiring takes 3+ months | High | Delayed Phase 2/3 | Start hiring NOW, overlap with Phase 1 |
| Team resistance to dbt | Medium | Low adoption | Pair with most enthusiastic engineer first, build internal champions |
| Data Mesh cultural resistance | High | Failed Phase 3 | Pilot with willing domain only, don't force unwilling teams |
```

> 💡 **Why this format works:** It answers every question the CTO will ask BEFORE they ask it. Budget? Row 3. Timeline? Phase headings. Risk? Last section. What if it fails? Success gates between phases — if Phase 1 doesn't hit targets, we don't spend Phase 2 money.

---

### Technology Radar: How to Evaluate New Tools

Don't evaluate tools in isolation. Use this framework:

```
For every new tool, answer:
1. What SPECIFIC problem does this solve that we can't solve today?
2. What does it REPLACE? (If nothing, it's adding complexity, not solving a problem)
3. Who maintains it after initial setup? (Is that person hired yet?)
4. What happens if this vendor dies in 2 years? (Lock-in risk)
5. Can we do a 2-week POC to verify claims? (Never trust benchmarks you didn't run)
```

---

## Influence Without Authority

### Scenario: Getting Team X to Adopt Your Framework

You've built a data quality framework. It's genuinely good. You want all 4 data teams to adopt it. Problem: you have **zero authority** over those teams.

```
What DOESN'T work:
  Email: "Hi everyone, please adopt the new DQ framework I built."
  Result: Ignored. Everyone is busy with their own priorities.

What DOESN'T work either:
  Escalate to CTO: "Can you tell teams to use my framework?"
  Result: Teams adopt it grudgingly, half-heartedly, and it falls apart in 2 months.

What WORKS:
```

### The 5-Step Influence Playbook

```
Step 1: FIND A CHAMPION
  → Don't try to convince everyone. Find ONE person in ONE team 
    who has the same problem your framework solves.
  → "Hey Sarah, I noticed your team had 3 data incidents last month. 
    I built something that would've caught all 3. Want to try it?"
  
Step 2: MAKE IT TRIVIAL TO ADOPT
  → Don't: "Here's a 50-page doc. Read it and implement."
  → Do: "Add this one line to your dbt_project.yml. That's it."
  → The lower the adoption cost, the faster it spreads.

Step 3: SHOW RESULTS ON SARAH'S TEAM
  → After 2 weeks: "Sarah's team caught 4 issues before production. 
    Zero data incidents this sprint."
  → Other teams hear about it in standup. They get curious.

Step 4: LET THEM COME TO YOU
  → "Hey, Sarah mentioned you have a DQ tool? Can you show us?"
  → Now THEY'RE asking. You're not pushing anymore.

Step 5: FORMALIZE IT
  → Once 2-3 teams use it voluntarily, propose it as an org standard.
  → "3 teams adopted this. Data incidents dropped 70%. 
    Should we make this the standard?"
  → CTO says: "Obviously yes."
```

### Writing Effective RFCs

When you need org-wide buy-in for a technical decision, write an RFC:

```markdown
# RFC-2026-003: Migrate to Apache Iceberg Table Format

## Status: PROPOSED → UNDER REVIEW → ACCEPTED
## Author: @your-name
## Reviewers: @team-leads, @architect, @cto
## Deadline for comments: 2026-02-28

## Problem Statement (not "what I want to build" but "what hurts today")

We cannot do UPSERT on our Parquet data lake. Every incremental update 
requires full table rewrite. For our 500GB orders table, this means:
- 4-hour nightly job (was 20 min when the table was small)
- $800/month in Spark compute for rewrites alone  
- No ability to handle late-arriving data without re-running full pipeline

## Proposed Solution

Migrate from raw Parquet to Apache Iceberg, which supports:
- Row-level MERGE/UPSERT (no full rewrite)
- Schema evolution without data migration
- Time travel for debugging
- Partition evolution (change partitioning without rewriting)

## Alternatives Considered (this is the most important section)

| | Iceberg | Delta Lake | Hudi | Stay with Parquet |
|---|---|---|---|---|
| UPSERT | ✅ MERGE INTO | ✅ MERGE INTO | ✅ UPSERT | ❌ Full rewrite |
| Vendor lock-in | None (open) | Databricks-centric | LinkedIn-centric | None |
| Catalog | Nessie, Glue, REST | Unity Catalog | — | N/A |
| Community | Growing fast | Largest | Smaller | Mature |
| **My recommendation** | **✅ Best fit** | Good but lock-in risk | Overkill for us | Not viable |

**Why Iceberg over Delta:** We use Spark + Trino. Iceberg has first-class 
support for both. Delta's best features (Unity Catalog, Liquid Clustering) 
require Databricks, which we don't use and don't plan to adopt.

## Migration Plan (phased, not big-bang)

Phase 1 (2 weeks): New tables created as Iceberg
Phase 2 (4 weeks): Migrate top 5 tables (by query frequency)
Phase 3 (8 weeks): Migrate remaining 50 tables, retire Parquet path

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Team learning curve | 2-week productivity dip | Pair programming + lunch-and-learn |
| BI tool compatibility | Some tools need Iceberg connector | Verified: Metabase + Superset support Iceberg via Trino |
| Migration bugs | Data corruption during conversion | Run old + new in parallel for 1 week, compare outputs |

## Open Questions (I want YOUR input)

1. Which Iceberg catalog should we use? (Glue vs Nessie vs REST)
2. Should we migrate the dev environment first or go straight to staging?
3. Any tables that should NOT be migrated? (edge cases?)

## How to Give Feedback

Comment on this doc by Feb 28. If you disagree with the recommendation, 
I want to hear it NOW, not after we've started migration.

Silence = consent. If you don't comment, you agree.
```

> 💡 **The "Alternatives Considered" section is everything.** If your RFC doesn't compare alternatives fairly, reviewers will question whether you actually evaluated options or just pitched your favorite tool. Show you considered and rejected alternatives for specific, documented reasons.

---

## Decision Making — Real Scenarios

### The Reversibility Framework

**The Reversibility Framework:**

| | **LOW IMPACT** | **HIGH IMPACT** |
|---|---|---|
| **REVERSIBLE** | **"Just do it"**<br>- Decide in < 1 day<br>- Ex: Which linter to use | **"Experiment"**<br>- Time-box POC: 2 weeks<br>- Measure results<br>- Ex: Try Dagster for 1 pipeline |
| **IRREVERSIBLE** | **"Write it down"**<br>- Light RFC, 1 week<br>- Document rationale<br>- Ex: Naming convention | **"Full process"**<br>- RFC + POC + committee<br>- Stakeholder alignment (1-3 mos)<br>- Ex: Choose warehouse (Snowflake vs BQ) |

### Scenario: PM Wants Real-Time Dashboard

**The ask:** "We need a real-time dashboard showing order counts per minute."

**Junior response:** "Sure, I'll set up Kafka + Flink + Redis + WebSocket." (3 months of work)

**Staff response:**

```
Step 1: Understand the ACTUAL need

  You: "When you say real-time, what do you mean?"
  PM:  "I want to see orders as they come in"
  You: "How quickly? Sub-second? Or is 1-minute refresh OK?"
  PM:  "1 minute is fine"
  You: "How many people will view this dashboard?"
  PM:  "Just the ops team, maybe 5 people"
  You: "Does it need to be 100% accurate or approximate?"
  PM:  "Approximate is fine for monitoring"

Step 2: Present options with tradeoffs

  Option A: Real-time streaming (Kafka + Flink + Redis)
  - Latency: sub-second
  - Effort: 3 months
  - Cost: $3K/mo additional infra
  - Maintenance: Flink expertise required (we don't have it)
  
  Option B: Micro-batch (dbt + BigQuery scheduled every 1 min)
  - Latency: 1 minute
  - Effort: 1 week
  - Cost: $50/mo additional (BigQuery on-demand)
  - Maintenance: dbt, which we already know
  
  Option C: Database polling (Metabase auto-refresh on PostgreSQL)
  - Latency: 15 seconds
  - Effort: 2 days
  - Cost: $0 (existing infra)
  - Maintenance: None
  
  Recommendation: Option C. It satisfies the actual requirement (1-minute 
  refresh for 5 users) with 2 days effort instead of 3 months.

Step 3: If PM pushes back

  PM: "But I want REAL real-time"
  You: "Sure, we can do that. Here's what it costs:
    - 3 months of engineering time ($75K opportunity cost)
    - $3K/month ongoing infrastructure
    - Delay Project Y by 1 quarter
    
    Option C gives you 15-second refresh in 2 days.
    The gap between 15 seconds and sub-second — is that worth $75K?"
  
  PM: "...let's do Option C."
```

### Saying "No" Without Saying No

```
❌ "No, we can't do that"
   → Sounds like you're blocking. PM escalates to your manager.

❌ "Sure, we'll figure it out"
   → You're over-committing. In 3 months: "Why isn't it done?"

✅ "Yes, and here are the tradeoffs"
   → You're enabling an INFORMED decision. PM chooses, you execute.
   → If they choose the expensive option, at least everyone agreed on the cost.
   → If it fails, the decision was shared, not yours alone.
```

---

## Mentoring & Growing Others

### The 1:1 Anti-Pattern

```
Bad 1:1 (most common):
  You: "How's it going?"
  Mentee: "Good"
  You: "Any blockers?"
  Mentee: "Nope"
  You: "OK cool, keep it up"
  
  Duration: 5 minutes. Value: zero.
```

### The Framework That Actually Works

```
Monthly 1:1 structure (30 min):

1. CELEBRATE (5 min)
   "What did you ship this month that you're proud of?"
   → Builds confidence. Makes them articulate their own wins.

2. STRUGGLE (10 min)
   "What was the hardest thing? Where did you get stuck?"
   → This is where learning happens. Dig into the struggle.
   → Don't solve it for them. Ask: "What did you try? What would you try next?"

3. GROWTH (10 min)
   "What skill do you want to develop next?"
   → Connect it to a specific upcoming project.
   → "You want to learn Spark? Great — next sprint has a batch migration task.
     I'll assign it to you instead of doing it myself."

4. FEEDBACK (5 min)
   ONE specific, actionable feedback point. Not five. One.
   → "Your pipeline code is solid. I noticed you jumped straight to coding 
     without writing a design doc. Next project, spend 30 minutes writing 
     a design doc first. I'll review it with you before you start coding."
```

### Delegation: The Hardest Skill

```
WHY it's hard:

  "I can write this Spark job in 2 hours. If I delegate it to Junior DE, 
  it'll take them 2 days plus 3 hours of my review time."
  
  Correct. And you should STILL delegate it.
  
  Because:
  - 2 hours of YOUR time = $200 (Staff salary)
  - 2 days of THEIR time = $400 (Junior salary) + $600 (learning value)
  - Next time they encounter a similar task: 4 hours instead of 2 days
  - After 5 delegated tasks: they don't need you anymore
  
  Your job is to make yourself unnecessary for individual tasks
  so you can focus on tasks only YOU can do.

WHAT to delegate:
  ✅ Tasks that stretch them (just outside their comfort zone)
  ✅ Tasks where your review adds value (they learn from your feedback)
  ❌ Tasks where only YOU have the context (org-wide architecture decisions)
  ❌ Crisis response (delegate after the crisis, not during)

HOW to delegate:
  ❌ "Build the data quality framework" (too vague, they'll guess wrong)
  ✅ "Build a framework that:
      - Runs Great Expectations checks on every dbt model
      - Alerts Slack when checks fail
      - Has a dashboard showing pass/fail rates
      Here are 3 examples of what good looks like: [links]
      Draft a design doc by Friday. We'll review together Monday."
```

---

## Anti-Patterns (With War Stories)

### Anti-Pattern 1: The Hero Coder

```
Story: Staff DE at a Series B startup. Wrote 80% of the data platform 
himself. Brilliant code. Complex, elegant, clever.

Then he went on vacation for 2 weeks.

3 pipelines broke. Nobody could debug his Scala monadic abstractions.
The team reverted to manual CSV exports for a financial report.
CTO to VP Eng: "We have a bus factor of 1. This is a risk."

Staff DE returned to find his perfectly architected system
being discussed as a candidate for "simplification."

Lesson: Code that only you can understand is a LIABILITY, not an asset.

Fix:
✅ Write code a mid-level engineer can maintain
✅ If the design is complex, write a design doc explaining WHY
✅ Pair program on critical paths — at least 2 people must understand it
✅ Your code review bar: "Would someone with 2 years experience get this?"
```

### Anti-Pattern 2: The Architecture Astronaut

```
Story: Staff DE presented a 40-slide architecture for a "unified data 
platform" with event sourcing, CQRS, data mesh, real-time feature store,
and a custom query engine.

Current state: 3 DEs, PostgreSQL, 10 pipelines, 50GB total data.

CTO: "This is a beautiful architecture... for a 500-person company.
We're 60 people. We need something we can build in 3 months."

Lesson: Design for 10x your current scale, NOT 1000x.

Fix:
✅ "What's the simplest thing that solves the problem TODAY?"
✅ Design for 10x growth, not 1000x. If you have 50GB, design for 500GB.
✅ Ship iteratively — Phase 1 in 3 months, Phase 2 when Phase 1 is proven.
✅ Every component should be replaceable. Don't build a cathedral.
```

### Anti-Pattern 3: The Ivory Tower

```
Story: Staff DE published an RFC for migrating to Iceberg.
No discussion, no feedback. 2 weeks later: "RFC accepted (no comments)."

Started migration. Week 3: Team Lead of Analytics says "Wait, our BI tool 
doesn't support Iceberg." Senior DE says "I have concerns about the catalog 
choice but didn't want to argue."

Migration rolled back. 3 weeks wasted.

Lesson: "No comments on RFC" ≠ "everyone agrees." 
It means "nobody read it" or "nobody felt safe disagreeing."

Fix:
✅ Actively seek disagreement: "What am I wrong about?"
✅ Name specific reviewers + set a deadline
✅ Schedule a 30-min discussion meeting (not just "comment on doc")
✅ "Silence = consent, but I'd rather hear dissent now than discover 
   problems after we've started building"
```

---

## Summary: What Makes a Great Staff+ DE

```
Technical:    Sets direction, doesn't just follow it
              Simplifies, doesn't over-engineer
              Writes LESS code that has MORE impact

Leadership:   Enables others to ship, doesn't ship everything alone
              Influences through results, not authority
              Makes decisions explicit and documented

Communication: Translates between CTO-speak and engineer-speak
               Says "yes, and here are the tradeoffs"
               Writes strategy docs that non-engineers can understand

Growth:       Mentors by asking questions, not giving answers
              Delegates to develop people, even when it's slower
              Measures success by team capability, not personal output
```

---

## Liên Kết

- [Architectural Thinking](02_Architectural_Thinking.md) — design skills that Staff DEs need
- [Problem Solving](03_Problem_Solving.md) — debugging mindset at scale
- [Career Growth](04_Career_Growth.md) — the career ladder leading to Staff+
- [Stakeholder Communication](../business/04_Stakeholder_Communication.md) — presenting to non-technical leaders

---

*Staff+ DE = Multiplier. Your impact is measured not by the code you write, but by the code the team writes BECAUSE of you.*

*Updated: February 2026*
