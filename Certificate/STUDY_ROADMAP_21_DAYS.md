# Databricks Certified Data Engineer Associate — 21-Day Study Roadmap

> **Exam Format:** 45 MCQ | 90 minutes | 70% to pass (~32/45 correct)
> **Section Weights:** §2 Ingestion (30%) + §3 Processing (31%) = **61%** | §4 Production (18%) | §1 Platform (10%) | §5 Governance (11%)

---

## Strategy Overview

| Phase | Days | Focus | Goal |
|-------|------|-------|------|
| **Foundation** | 1–7 | Platform + Ingestion + Delta Core | Lock in the 40% (§1 + §2) |
| **Processing** | 8–14 | Transformations + Streaming + Pipelines | Lock in the 31% (§3) |
| **Production & Governance** | 15–19 | Jobs + CI/CD + Unity Catalog + Sharing | Lock in the 29% (§4 + §5) |
| **Mock & Review** | 20–21 | Full-length practice + weak-spot drilling | Go from 70% → 85%+ |

---

## Phase 1: Foundation & Ingestion (Days 1–7)

### Day 1 — Lakehouse Platform & Compute
**Read:**
- [01_Lakehouse_Platform.md](file:///data/DE/Fun/Certificate/Claude/01_Lakehouse_Platform.md) (full)
- [Hilarious §1](file:///data/DE/Fun/Certificate/Hilarious/Section%201%20%20Databricks%20Intelligence%20Platform.md) — skim "Cluster Types" section

**Master these concepts:**
- [ ] Control Plane vs Data Plane (what lives where?)
- [ ] All-Purpose vs Job Cluster vs SQL Warehouse — when to use each
- [ ] Serverless: Python/SQL only, instant start, no config
- [ ] Photon: vectorized engine, enabled by default on SQL Warehouses

**Exam Trap Drill:**
- [ ] "Which cluster type minimizes cost for a nightly ETL?" → **Job Cluster** (ephemeral, auto-terminate)
- [ ] "Serverless supports Scala?" → **No** (Python & SQL only)
- [ ] "All-Purpose Cluster idle cost?" → **Keeps running until manually terminated**

---

### Day 2 — Delta Lake Core
**Read:**
- [05_Delta_Lake_Core.md](file:///data/DE/Fun/Certificate/Claude/05_Delta_Lake_Core.md) (full)

**Master these concepts:**
- [ ] Transaction Log (`_delta_log/`) — JSON commit files + periodic Parquet checkpoints
- [ ] ACID guarantees on object storage (what each letter means in Delta context)
- [ ] Time Travel: `VERSION AS OF n` vs `TIMESTAMP AS OF 'ts'`
- [ ] `VACUUM` default = 168 hours (7 days). Cannot time-travel past vacuum threshold
- [ ] Schema Enforcement (reject bad writes) vs Schema Evolution (`mergeSchema = true`)

**Exam Trap Drill:**
- [ ] "VACUUM with 0 hours retention?" → Destroys Time Travel, only for emergencies
- [ ] "Schema enforcement happens at ___?" → **Write time** (not read)
- [ ] "What stores Delta metadata?" → **Transaction Log** (not Hive Metastore)

---

### Day 3 — Auto Loader (Theory + Syntax)
**Read:**
- [04_Auto_Loader.md](file:///data/DE/Fun/Certificate/Claude/04_Auto_Loader.md) (full)
- [Hilarious §2](file:///data/DE/Fun/Certificate/Hilarious/Section%202%20Development%20and%20Ingestion.md) — "Auto Loader Sources" + "Auto Loader Syntax" sections

**Master these concepts:**
- [ ] `cloudFiles` format — entry point for Auto Loader
- [ ] Directory Listing (default, scans dir) vs File Notification (cloud events, scales better)
- [ ] `cloudFiles.schemaLocation` — **required** for streaming
- [ ] Schema evolution modes: `addNewColumns` (default), `rescue`, `failOnNewColumns`, `none`
- [ ] `_rescued_data` column — captures unrecognized fields in rescue mode
- [ ] Auto Loader vs COPY INTO: streaming vs one-time batch

**Exam Trap Drill:**
- [ ] "Auto Loader without schemaLocation?" → **Pipeline fails**
- [ ] "One-time historical load of 5 years of Parquet?" → **COPY INTO** (not Auto Loader)
- [ ] "Millions of files arriving per hour, latency increasing?" → Switch to **File Notification mode**

---

### Day 4 — Notebooks & Databricks Connect
**Read:**
- [03_Notebooks_Debugging.md](file:///data/DE/Fun/Certificate/Claude/03_Notebooks_Debugging.md) (full)
- [Hilarious §2](file:///data/DE/Fun/Certificate/Hilarious/Section%202%20Development%20and%20Ingestion.md) — "Databricks Connect" + "Notebooks Functionality" sections

**Master these concepts:**
- [ ] `%run` (same context, shares variables, must be alone in cell) vs `dbutils.notebook.run()` (separate context, returns string)
- [ ] Magic commands: `%python`, `%sql`, `%scala`, `%r`, `%md`, `%sh`, `%fs`
- [ ] Widgets: `text`, `dropdown`, `combobox`, `multiselect` — `dbutils.widgets.get("key")`
- [ ] Databricks Connect v2: `DatabricksSession.builder` (not `SparkSession.builder`), thin client, no local Spark needed
- [ ] Temp views bridge languages: create in SQL → read in Python with `spark.table()`

**Exam Trap Drill:**
- [ ] "Share variables between notebooks?" → **`%run`** (not `dbutils.notebook.run()`)
- [ ] "%run mixed with other code in a cell?" → **Error** (must be alone)
- [ ] "Run Spark from local IDE without Spark installed?" → **Databricks Connect**

---

### Day 5 — Optimization & Data Layout
**Read:**
- [02_Optimization_DataLayout.md](file:///data/DE/Fun/Certificate/Claude/02_Optimization_DataLayout.md) (full)

**Master these concepts:**
- [ ] **Liquid Clustering** replaces both Partitioning AND Z-Ordering (the modern answer)
- [ ] `CLUSTER BY (col1, col2)` — set on table creation, Databricks auto-maintains
- [ ] Why Partitioning is legacy: small-file problem, over-partitioning, can't change after creation
- [ ] Predictive Optimization: Databricks auto-runs OPTIMIZE and VACUUM (Enterprise feature)
- [ ] `OPTIMIZE table_name` — compacts small files into larger ones

**Exam Trap Drill:**
- [ ] "Best data layout for a new table with high-cardinality filter columns?" → **Liquid Clustering**
- [ ] "Change partition column on existing partitioned table?" → **Cannot** (must recreate)
- [ ] "Who runs OPTIMIZE automatically?" → **Predictive Optimization** (not manual cron)

---

### Day 6 — Structured Streaming
**Read:**
- [06_Structured_Streaming.md](file:///data/DE/Fun/Certificate/Claude/06_Structured_Streaming.md) (full)

**Master these concepts:**
- [ ] Micro-batch architecture — streaming = series of small batch jobs
- [ ] Trigger modes:
  - `trigger(availableNow=True)` — process all available, then **stop** (preferred for batch-like streaming)
  - `trigger(once=True)` — **legacy**, replaced by availableNow
  - `trigger(processingTime="5 minutes")` — periodic micro-batches
  - No trigger = continuous processing
- [ ] Checkpointing: tracks offset, **required** for exactly-once guarantees
- [ ] Watermarking: `withWatermark("eventTime", "10 minutes")` — handles late data
- [ ] Output modes: `append` (new rows only), `complete` (full result), `update` (changed rows)

**Exam Trap Drill:**
- [ ] "`trigger(once=True)` vs `trigger(availableNow=True)`?" → **availableNow** is preferred, processes all micro-batches; `once` processes only one
- [ ] "Move checkpoint to new location?" → **Breaks exactly-once**, reprocesses from start
- [ ] "Aggregate streaming query output mode?" → **`complete`** (replaces full result)

---

### Day 7 — Phase 1 Review & Practice
**Do:**
- [ ] Re-read your ❌ marked traps from Days 1–6
- [ ] Answer ExamTopics Questions 1–15 from [Examtopics Databricks.txt](file:///data/DE/Fun/Examtopics%20Databricks.txt)
- [ ] For each wrong answer: identify the Claude file, re-read the relevant section
- [ ] Create a personal "wrong answers" cheat sheet

**Self-test (answer without looking):**
- [ ] Name 3 compute types and when to use each
- [ ] Explain Delta Transaction Log in 2 sentences
- [ ] Write Auto Loader PySpark syntax from memory (format, schemaLocation, checkpointLocation)
- [ ] Explain the difference between `trigger(once=True)` and `trigger(availableNow=True)`

---

## Phase 2: Processing & Transformations (Days 8–14)

### Day 8 — Medallion Architecture
**Read:**
- [07_Medallion_Architecture.md](file:///data/DE/Fun/Certificate/Claude/07_Medallion_Architecture.md) (full)
- [Hilarious §3](file:///data/DE/Fun/Certificate/Hilarious/Section%203%20Data%20Processing%20%26%20Transformations.md) — "Medallion Architecture" section

**Master these concepts:**
- [ ] Bronze = raw, append-only, never transform here
- [ ] Silver = cleaned, deduplicated, conformed, quality rules applied here
- [ ] Gold = aggregated, business-ready, star schema, BI tools query this
- [ ] Where does deduplication happen? → **Silver** (not Bronze, not Gold)
- [ ] Where does `ROW_NUMBER()` dedup logic belong? → **Silver**

**Exam Trap Drill:**
- [ ] "Filter invalid records in Bronze?" → **No** — Bronze is raw, quality checks go in Silver
- [ ] "BI dashboard queries which layer?" → **Gold** (pre-aggregated)
- [ ] "Most granular clean data?" → **Silver** (one event per row, clean)

---

### Day 9 — SQL & PySpark Operations
**Read:**
- [08_SQL_PySpark_Operations.md](file:///data/DE/Fun/Certificate/Claude/08_SQL_PySpark_Operations.md) (full)

**Master these concepts:**
- [ ] `MERGE INTO` (upsert): `WHEN MATCHED THEN UPDATE`, `WHEN NOT MATCHED THEN INSERT`
- [ ] `count(*)` counts all rows, `count(col)` skips NULLs, `count_if(condition)` counts matching
- [ ] Array functions: `explode()`, `collect_list()`, `array_contains()`, `size()`
- [ ] Higher-order functions: `TRANSFORM`, `FILTER`, `EXISTS` — operate on arrays without exploding
- [ ] `spark.sql()` vs `spark.table()`: sql executes arbitrary SQL; table returns a DataFrame directly

**Exam Trap Drill:**
- [ ] "`count(status)` on a column with NULLs?" → **Skips NULLs** (use `count(*)` for all rows)
- [ ] "Upsert pattern?" → **MERGE INTO** (not INSERT + UPDATE separately)
- [ ] "`count_if(status = 'active')` vs `count(*) WHERE status = 'active'`?" → Same result, but `count_if` is more concise in SELECT

---

### Day 10 — Lakeflow Declarative Pipelines (DLT)
**Read:**
- [09_Lakeflow_Declarative_Pipelines.md](file:///data/DE/Fun/Certificate/Claude/09_Lakeflow_Declarative_Pipelines.md) (full)
- [Hilarious §3](file:///data/DE/Fun/Certificate/Hilarious/Section%203%20Data%20Processing%20%26%20Transformations.md) — "Lakeflow Spark Declarative Pipelines" section

**Master these concepts:**
- [ ] Declarative = define WHAT, not HOW. System handles orchestration
- [ ] **Streaming Table** = append-only, incremental (Bronze)
- [ ] **Materialized View** = recomputed fully each run (Silver/Gold aggregations)
- [ ] Expectations: `EXPECT (condition)` → actions: `WARN`, `DROP ROW`, `FAIL UPDATE`
- [ ] `STREAM()` function — reads only new data since last update
- [ ] Pipeline modes: Triggered (batch, runs once) vs Continuous (real-time)
- [ ] Development vs Production mode

**Exam Trap Drill:**
- [ ] "Streaming Table for deduplication?" → **No** — use Materialized View (needs full dataset)
- [ ] "FAIL on non-critical quality issue?" → **Bad practice** — use DROP or WARN
- [ ] "Does notebook order matter in pipeline?" → **No** — auto-resolves dependencies via DAG

---

### Day 11 — Implementing Pipelines & CDC (APPLY CHANGES)
**Read:**
- [Hilarious §3](file:///data/DE/Fun/Certificate/Hilarious/Section%203%20Data%20Processing%20%26%20Transformations.md) — "Implementing Data Pipelines with Lakeflow" section (APPLY CHANGES, SCD Types)

**Master these concepts:**
- [ ] `APPLY CHANGES INTO target FROM source KEYS (pk) SEQUENCE BY (ts)` — CDC processing
- [ ] SCD Type 1: overwrites old values (default) — only current state
- [ ] SCD Type 2: `STORED AS SCD TYPE 2` — tracks history with `__start_version`, `__end_version`, `__current`
- [ ] Full Refresh vs Incremental Refresh — Streaming Tables always incremental
- [ ] Pipeline Event Logs — track row counts, errors, execution times

**Exam Trap Drill:**
- [ ] "Need audit trail of address changes?" → **SCD Type 2** (Type 1 loses history)
- [ ] "Silver fails in multi-notebook pipeline, what happens to Gold?" → **Gold doesn't run** (dependency failure)
- [ ] "Second pipeline run reads how many rows?" → **Only new rows** (incremental via checkpoint)

---

### Day 12 — Performance & Spark UI
**Read:**
- [12_Performance_SparkUI.md](file:///data/DE/Fun/Certificate/Claude/12_Performance_SparkUI.md) (full)
- [Hilarious §2](file:///data/DE/Fun/Certificate/Hilarious/Section%202%20Development%20and%20Ingestion.md) — "Debugging Tools" section

**Master these concepts:**
- [ ] Spark UI: stages, tasks, shuffle, spill — where to find bottlenecks
- [ ] OOM (Out of Memory): too much data on one executor → repartition or increase memory
- [ ] SQL Warehouse scaling: **Size** (vertical, bigger nodes) vs **Scaling range** (horizontal, more clusters for concurrency)
- [ ] Driver Logs vs Executor Logs — driver has print()/exceptions, executors have task-level info
- [ ] System tables: `system.access.audit`, `system.compute.clusters`

**Exam Trap Drill:**
- [ ] "Slow Spark job, where to look?" → **Spark UI** (check stages, shuffles, spill)
- [ ] "More concurrent SQL queries?" → **Increase scaling range** (not warehouse size)
- [ ] "Where do print() statements appear?" → **Driver logs**

---

### Day 13 — Cluster Types Deep Dive
**Read:**
- [Hilarious §3](file:///data/DE/Fun/Certificate/Hilarious/Section%203%20Data%20Processing%20%26%20Transformations.md) — "Cluster Types and Configuration" section

**Master these concepts:**
- [ ] Autoscaling: min_workers / max_workers — dynamic cost optimization
- [ ] Cluster Policies: admin-defined templates, enforce standards
- [ ] Access Modes: Shared (multi-user, UC enforced), Single User (isolated), No Isolation (legacy)
- [ ] Spot Instances: cheaper but interruptible — use for fault-tolerant batch
- [ ] Single-Node cluster: driver only, no workers — for lightweight testing

**Exam Trap Drill:**
- [ ] "Job Cluster shared across multiple jobs?" → **No** — each job gets its own ephemeral cluster
- [ ] "All-Purpose Cluster idle overnight?" → **Still incurring costs** (must manually terminate)
- [ ] "Streaming job on Spot instances?" → **Risky** — use On-Demand for long-running streams

---

### Day 14 — Phase 2 Review & Practice
**Do:**
- [ ] Re-read your ❌ marked traps from Days 8–13
- [ ] Answer ExamTopics Questions 16–35 from [Examtopics Databricks.txt](file:///data/DE/Fun/Examtopics%20Databricks.txt)
- [ ] Map each wrong answer to the corresponding Claude file
- [ ] Update your "wrong answers" cheat sheet

**Self-test (answer without looking):**
- [ ] Draw the Medallion Architecture (Bronze → Silver → Gold) and list what happens at each layer
- [ ] Write MERGE INTO syntax from memory
- [ ] Explain Streaming Table vs Materialized View in ≤3 sentences
- [ ] What does `APPLY CHANGES INTO ... STORED AS SCD TYPE 2` do?

---

## Phase 3: Production & Governance (Days 15–19)

### Day 15 — Jobs & Workflows
**Read:**
- [10_Jobs_Workflows.md](file:///data/DE/Fun/Certificate/Claude/10_Jobs_Workflows.md) (full)
- [Hilarious §4](file:///data/DE/Fun/Certificate/Hilarious/Section%204%20Productionizing%20Data%20Pipelines.md) — "Workflow Deployment, Repair, and Rerun" section

**Master these concepts:**
- [ ] Jobs = DAGs of tasks with dependencies (`depends_on`)
- [ ] Task types: Notebook, Python, SQL, Lakeflow Pipeline, dbt, JAR
- [ ] **Repair & Rerun**: reruns only failed tasks + downstream — preserves run ID
- [ ] **Task Values**: `dbutils.jobs.taskValues.set(key, value)` / `.get(key)` — ephemeral, per-run
- [ ] Job Cluster vs Existing Cluster for jobs (Job Cluster = production best practice)
- [ ] `max_concurrent_runs` — prevents backlog

**Exam Trap Drill:**
- [ ] "Job fails at task 3 of 5, minimal compute waste?" → **Repair & Rerun** (not Run Now)
- [ ] "Task values persist after job?" → **No** — ephemeral, cleared on each run
- [ ] "Cron `0 0 2 * * ?`?" → **2 AM daily**

---

### Day 16 — DABs & CI/CD
**Read:**
- [11_Asset_Bundles_CICD.md](file:///data/DE/Fun/Certificate/Claude/11_Asset_Bundles_CICD.md) (full)
- [Hilarious §4](file:///data/DE/Fun/Certificate/Hilarious/Section%204%20Productionizing%20Data%20Pipelines.md) — "DAB" + "Asset Bundle Structure" sections

**Master these concepts:**
- [ ] DABs = Infrastructure as Code for Databricks (YAML-based `databricks.yml`)
- [ ] Commands: `validate` → `deploy` → `run`
- [ ] **Targets** for environment management: `--target dev`, `--target prod` (same config, different params)
- [ ] Variables: `${var.name}` — environment-specific overrides in targets
- [ ] `include:` directive for modular configs
- [ ] Git Repos: can clone/branch/commit/push/pull — but **merge must happen outside** (GitHub/GitLab)

**Exam Trap Drill:**
- [ ] "Deploy same pipeline to dev and prod?" → **DABs with targets** (not manual UI duplication)
- [ ] "Merge branches in Databricks Repos?" → **Cannot** — merge in external Git provider
- [ ] "Version control for deployment configs?" → **DABs in Git** (not manual UI changes)

---

### Day 17 — Unity Catalog & Permissions
**Read:**
- [13_Unity_Catalog.md](file:///data/DE/Fun/Certificate/Claude/13_Unity_Catalog.md) (full)
- [Hilarious §5](file:///data/DE/Fun/Certificate/Hilarious/Section%205%20Data%20Governance%20%26%20Quality.md) — "Managed vs External Tables" + "Permissions and Roles" sections

**Master these concepts:**
- [ ] 3-level namespace: `catalog.schema.table`
- [ ] **Managed Table**: UC controls metadata + data → DROP deletes both
- [ ] **External Table**: UC controls metadata only → DROP keeps data files
- [ ] Permission chain: `USE CATALOG` + `USE SCHEMA` + `SELECT` — **all three required**
- [ ] `GRANT SELECT ON SCHEMA x TO group` — inherits to all current + future tables
- [ ] Ownership: creator = owner by default, transfer with `ALTER ... OWNER TO`

**Exam Trap Drill:**
- [ ] "User has SELECT but can't query?" → Missing **USE CATALOG** or **USE SCHEMA**
- [ ] "DROP managed table?" → Data **deleted** from storage
- [ ] "DROP external table?" → Data **stays** in cloud storage
- [ ] "Grant access to future tables?" → `GRANT SELECT ON SCHEMA` (not individual tables)

---

### Day 18 — Delta Sharing, Lineage, Federation & Audit
**Read:**
- [14_Delta_Sharing_Lineage.md](file:///data/DE/Fun/Certificate/Claude/14_Delta_Sharing_Lineage.md) (full)
- [Hilarious §5](file:///data/DE/Fun/Certificate/Hilarious/Section%205%20Data%20Governance%20%26%20Quality.md) — "Audit Logs" + "Lineage" + "Delta Sharing" + "Lakehouse Federation" sections

**Master these concepts:**
- [ ] **Delta Sharing**: open protocol, read-only, no data copying
  - D2D (Databricks ↔ Databricks) vs D2O (Databricks → external tools via bearer token)
  - Provider pays storage, Recipient pays compute
- [ ] **Lineage**: automatic in UC, table-level + column-level, upstream/downstream
  - `system.access.table_lineage` — query programmatically
- [ ] **Lakehouse Federation**: query external DBs (Postgres, MySQL, Snowflake) without copying
  - Connection → Foreign Catalog → query with `catalog.schema.table` syntax
  - **Read-only** + **query pushdown**
- [ ] **Audit Logs**: `system.access.audit` — 90-day default retention
  - Key columns: `event_time`, `identity`, `action_name`, `request_params`

**Exam Trap Drill:**
- [ ] "Share data with non-Databricks partner?" → **D2O Delta Sharing** (bearer token)
- [ ] "Who pays for shared data compute?" → **Recipient**
- [ ] "Find who accessed a table?" → Query `system.access.audit`
- [ ] "Rename column, what might break?" → Check **downstream lineage**

---

### Day 19 — Phase 3 Review & Practice
**Do:**
- [ ] Re-read your ❌ marked traps from Days 15–18
- [ ] Answer ExamTopics Questions 36–60 from [Examtopics Databricks.txt](file:///data/DE/Fun/Examtopics%20Databricks.txt)
- [ ] Map each wrong answer to the corresponding Claude file
- [ ] Update your "wrong answers" cheat sheet

**Self-test (answer without looking):**
- [ ] Explain Repair & Rerun vs Run Now in ≤2 sentences
- [ ] Write a GRANT statement that gives a group read access to all tables in a schema
- [ ] Name the 3 objects needed for Delta Sharing (Share, Recipient, Provider)
- [ ] What does Lakehouse Federation NOT support? (write operations)

---

## Phase 4: Mock Testing & Final Review (Days 20–21)

### Day 20 — Full Mock Exam + Gap Analysis
**Do:**
- [ ] Time yourself: 90 minutes, all 60+ questions in [Examtopics Databricks.txt](file:///data/DE/Fun/Examtopics%20Databricks.txt)
- [ ] Score yourself honestly (aim ≥ 70% = 32/45)
- [ ] Categorize every wrong answer by section:

| Section | Target | Your Score | Gap |
|---------|--------|-----------|-----|
| §1 Platform (10%) | 4-5 Q | ? | ? |
| §2 Ingestion (30%) | 13-14 Q | ? | ? |
| §3 Processing (31%) | 14 Q | ? | ? |
| §4 Production (18%) | 8 Q | ? | ? |
| §5 Governance (11%) | 5 Q | ? | ? |

- [ ] For each gap, re-read the corresponding Claude file section
- [ ] Focus remaining time on your **2 weakest sections**

---

### Day 21 — Trap Review + Confidence Building
**Morning — Kill your weak spots:**
- [ ] Re-read ONLY the sections you got wrong on Day 20
- [ ] Re-attempt the wrong questions without looking at answers
- [ ] If still wrong → read the Hilarious file for that section (different explanation style helps)

**Afternoon — Speed drill the top exam traps:**

> [!CAUTION]
> These are the most commonly missed concepts. If you can answer all of these correctly, you're ready.

| # | Trap Question | Correct Answer |
|---|--------------|----------------|
| 1 | Serverless supports Scala? | No — Python & SQL only |
| 2 | VACUUM 0 hours? | Destroys Time Travel |
| 3 | Auto Loader without schemaLocation? | Fails immediately |
| 4 | `trigger(once=True)` vs `availableNow=True`? | availableNow processes ALL micro-batches |
| 5 | Dedup in Bronze? | No — dedup in Silver |
| 6 | `count(col)` with NULLs? | Skips NULLs |
| 7 | Streaming Table for dedup? | No — use Materialized View |
| 8 | FAIL expectation on non-critical data? | Bad practice — use DROP |
| 9 | SCD Type 1 tracks history? | No — Type 2 does |
| 10 | Repair & Rerun restarts whole job? | No — only failed tasks + downstream |
| 11 | Merge in Databricks Git Repos? | Can't — merge in external Git |
| 12 | SELECT granted but access denied? | Missing USE CATALOG or USE SCHEMA |
| 13 | DROP managed table? | Deletes data from storage |
| 14 | DROP external table? | Data stays in cloud storage |
| 15 | Delta Sharing write access? | No — read-only always |
| 16 | Lakehouse Federation write? | No — read-only |
| 17 | BI dashboard queries Bronze? | No — Gold layer |
| 18 | Liquid Clustering replaces what? | Both Partitioning AND Z-Ordering |
| 19 | Audit logs default retention? | 90 days |
| 20 | `%run` shares variables? | Yes — same execution context |

**Evening:**
- [ ] Skim your "wrong answers" cheat sheet one final time
- [ ] Get a good night's sleep 🧠

---

## Quick Reference: File-to-Section Map

| Exam Section | Claude Files | Hilarious File |
|---|---|---|
| §1 Platform (10%) | [01](file:///data/DE/Fun/Certificate/Claude/01_Lakehouse_Platform.md), [02](file:///data/DE/Fun/Certificate/Claude/02_Optimization_DataLayout.md), [03](file:///data/DE/Fun/Certificate/Claude/03_Notebooks_Debugging.md) | [§1](file:///data/DE/Fun/Certificate/Hilarious/Section%201%20%20Databricks%20Intelligence%20Platform.md) |
| §2 Ingestion (30%) | [04](file:///data/DE/Fun/Certificate/Claude/04_Auto_Loader.md), [05](file:///data/DE/Fun/Certificate/Claude/05_Delta_Lake_Core.md), [06](file:///data/DE/Fun/Certificate/Claude/06_Structured_Streaming.md) | [§2](file:///data/DE/Fun/Certificate/Hilarious/Section%202%20Development%20and%20Ingestion.md) |
| §3 Processing (31%) | [07](file:///data/DE/Fun/Certificate/Claude/07_Medallion_Architecture.md), [08](file:///data/DE/Fun/Certificate/Claude/08_SQL_PySpark_Operations.md), [09](file:///data/DE/Fun/Certificate/Claude/09_Lakeflow_Declarative_Pipelines.md), [12](file:///data/DE/Fun/Certificate/Claude/12_Performance_SparkUI.md) | [§3](file:///data/DE/Fun/Certificate/Hilarious/Section%203%20Data%20Processing%20%26%20Transformations.md) |
| §4 Production (18%) | [10](file:///data/DE/Fun/Certificate/Claude/10_Jobs_Workflows.md), [11](file:///data/DE/Fun/Certificate/Claude/11_Asset_Bundles_CICD.md) | [§4](file:///data/DE/Fun/Certificate/Hilarious/Section%204%20Productionizing%20Data%20Pipelines.md) |
| §5 Governance (11%) | [13](file:///data/DE/Fun/Certificate/Claude/13_Unity_Catalog.md), [14](file:///data/DE/Fun/Certificate/Claude/14_Delta_Sharing_Lineage.md) | [§5](file:///data/DE/Fun/Certificate/Hilarious/Section%205%20Data%20Governance%20%26%20Quality.md) |

---

> [!TIP]
> **The 80/20 Rule:** §2 + §3 account for **61%** of the exam. If you master Auto Loader, Delta Lake, Medallion Architecture, MERGE INTO, and Lakeflow Pipelines, you're already more than halfway to passing. Don't over-index on §1 Platform (only 10%).

> [!IMPORTANT]
> **Active Recall > Passive Reading:** After reading each file, close it and try to answer the "Exam Trap Drill" questions from memory. If you can't, re-read just that section. This single habit will double your retention.
