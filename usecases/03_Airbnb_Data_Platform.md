# Airbnb Data Platform Architecture

## Kiến Trúc Data Platform Của Airbnb - The Home-sharing Pioneer

---

## 🏢 TỔNG QUAN CÔNG TY

- **Quy mô:** 150+ triệu users, 7+ million listings
- **Operations:** 220+ countries and regions
- **Data challenges:** Highly seasonal, geographic, trust/safety critical
- **Open source contributions:** Airflow, Superset, Knowledge Repo

---

## 🏗️ TỔNG QUAN KIẾN TRÚC

```mermaid
graph TD
    subgraph Sources[" "]
        Sources_title["🏠 DATA SOURCES"]
        style Sources_title fill:none,stroke:none,color:#333,font-weight:bold
        S1[Booking Events]
        S2[Search Events]
        S3[Listing Updates]
        S4[Review Data]
        S5[Payment Transactions]
    end

    subgraph Ingestion[" "]
        Ingestion_title["📥 INGESTION LAYER"]
        style Ingestion_title fill:none,stroke:none,color:#333,font-weight:bold
        K["Apache Kafka<br/>Event streaming backbone"]
        AF["Apache Airflow<br/>Workflow orchestration<br/>✨ Airbnb created"]
    end

    subgraph Storage[" "]
        Storage_title["🗄️ STORAGE LAYER"]
        style Storage_title fill:none,stroke:none,color:#333,font-weight:bold
        DL[("S3 + Hive<br/>Raw/Bronze")]
        MN[("Minerva<br/>Metrics Gold Layer")]
        ZP[("Zipline<br/>ML Feature Store")]
    end

    subgraph Compute[" "]
        Compute_title["⚙️ COMPUTE LAYER"]
        style Compute_title fill:none,stroke:none,color:#333,font-weight:bold
        SP["Spark ETL"]
        PR["Presto SQL"]
        ML["Bighead<br/>ML Platform"]
    end

    subgraph Products[" "]
        Products_title["📊 DATA PRODUCTS"]
        style Products_title fill:none,stroke:none,color:#333,font-weight:bold
        SS["Superset<br/>✨ Airbnb created"]
        DP[Dataportal Discovery]
        AB[Experimentation / A/B]
    end

    S1 & S2 & S3 & S4 & S5 --> K
    K --> AF
    AF --> DL & MN & ZP
    DL & MN & ZP --> SP & PR & ML
    SP & PR & ML --> SS & DP & AB

    style K fill:#231f20,color:#fff
    style AF fill:#017cee,color:#fff
    style SS fill:#20a7c9,color:#fff
```

---

## 🔧 TECH STACK CHI TIẾT

### 1. Apache Airflow (Airbnb Created)

**Origin:** Airbnb created in 2014, open-sourced 2015, Apache top-level 2019

```mermaid
flowchart TD
    subgraph AIRFLOW [" "]
        direction TB
        A_TITLE["AIRFLOW ARCHITECTURE"]
        style A_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        subgraph COMPONENTS [" "]
            direction LR
            WS["Web Server<br>(UI)"]
            SCH["Scheduler<br>(DAG runs)"]
            EX["Executor<br>(Workers)"]
        end
        style COMPONENTS fill:none,stroke:none
        
        DB["Metadata DB<br>(PostgreSQL)"]
        
        WS --> DB
        SCH --> DB
        EX --> DB
    end
```

```python
# DAG EXAMPLE (Airbnb style):

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG(
    'daily_metrics',
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
) as dag:

    extract = PythonOperator(
        task_id='extract_bookings',
        python_callable=extract_bookings,
    )

    transform = PythonOperator(
        task_id='calculate_metrics',
        python_callable=calculate_metrics,
    )

    load = PythonOperator(
        task_id='load_to_warehouse',
        python_callable=load_data,
    )

    extract >> transform >> load
```

> **AIRFLOW AT AIRBNB:**
> 
> * **Scale:**
>   * 10,000s of DAGs
>   * 100,000s of tasks/day
>   * Manages all batch ETL
> 
> * **Key features used:**
>   * Dynamic DAG generation
>   * Task dependencies
>   * Backfill capabilities
>   * SLA monitoring

### 2. Minerva (Metrics Layer)

```mermaid
flowchart TD
    subgraph MINERVA [" "]
        direction TB
        M_TITLE["MINERVA<br>(Single source of truth for metrics)"]
        style M_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        MD["Metric Definitions<br>metric:<br>  name: bookings<br>  type: count<br>  source: fact_reservations<br>  dimensions: [country, platform, room_type]<br>  filters:<br>    - status = 'confirmed'"]
        
        CE["Computation Engine<br>- Aggregates metrics on demand<br>- Caches common queries<br>- Serves to Superset, APIs, notebooks"]
        
        MD --> CE
    end
```

> **KEY BENEFITS:**
> 
> 1. Single Source of Truth:
>    - "Bookings" defined once
>    - Everyone uses same definition
>    - No dashboard discrepancies
> 
> 2. Dimension Consistency:
>    - Standard dimensions across metrics
>    - Drill-down always works
>    - Comparable across reports
> 
> 3. Self-Service:
>    - Business users can explore
>    - No need to write SQL
>    - Governed access

### 3. Apache Superset (Airbnb Created)

**Origin:** Airbnb created, now Apache top-level project

> **SUPERSET FEATURES:**
> 
> * **Dashboard Components:** Line, Bar, Pie, Map charts
> * **Features:**
>   * SQL Lab (explore data)
>   * 40+ visualization types
>   * Semantic layer (metrics/dimensions)
>   * Role-based access control
>   * Alerts and reports
> * **Connectors:** Presto/Trino, PostgreSQL, MySQL, BigQuery, Druid

### 4. Zipline (Feature Store)

```mermaid
flowchart TD
    subgraph ZIPLINE [" "]
        direction TB
        Z_TITLE["ZIPLINE<br>(Declarative Feature Engineering)"]
        style Z_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        FD["Feature Definition<br>class HostFeatures(Feature):<br>    source = Source.HIVE_TABLE('fact_listings')<br>    keys = ['host_id']<br>    total_listings = Feature(...)<br>    avg_rating = Feature(...)"]
        
        subgraph STORES [" "]
            direction LR
            OS1["Offline Store<br>(Hive/S3)<br>- Training"]
            OS2["Online Store<br>(Redis)<br>- Serving"]
        end
        style STORES fill:none,stroke:none
        
        FD --> OS1
        FD --> OS2
    end
```

> **TRAINING vs SERVING:**
> 
> * **Training (Offline):**
>   * Historical features at specific timestamps
>   * Point-in-time correctness
>   * Large batch retrieval
> 
> * **Serving (Online):**
>   * Latest feature values
>   * Low latency (<10ms)
>   * Key-value lookup

---

## 🎯 KEY DATA PRODUCTS

### 1. Search Ranking

**WHAT - Mục tiêu:**
- Match guests với relevant listings
- Maximize booking conversion
- Personalize results for each user
- Balance guest satisfaction và host fairness

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph SEARCH [" "]
        direction TB
        S_TITLE["SEARCH RANKING PIPELINE"]
        style S_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        QRY["User Search Query"]
        QU["Query Understanding<br>- Location parsing<br>- Date normalization<br>- Intent detection"]
        CR["Candidate Retrieval<br>- Elasticsearch (listings)<br>- Geo filtering<br>- Availability check"]
        RM["Ranking Model<br>- Guest features (Zipline)<br>- Listing features (Zipline)<br>- Context features (real-time)<br>- GBDT/Neural ranking model"]
        BR["Business Rules<br>- Diversity (location, price)<br>- Fairness constraints<br>- Superhost boost"]
        RES["Search Results"]
        
        QRY --> QU
        QU --> CR
        CR --> RM
        RM --> BR
        BR --> RES
    end
```

> **FEATURES USED:**
> 
> * **Guest features:** Search history, Booking history, Price sensitivity
> * **Listing features:** Reviews and ratings, Response rate, Instant book available, Photos quality score
> * **Context features:** Search location, Check-in/out dates, Number of guests
```

**WHY - Lý do & Impact:**
- 2x increase in booking conversion
- Better guest-listing matching
- Hosts get more qualified leads
- Foundation for entire marketplace

---

### 2. Dynamic Pricing (Smart Pricing)

**WHAT - Mục tiêu:**
- Help hosts optimize pricing
- Maximize host earnings
- Increase booking rates for hosts
- Data-driven pricing recommendations

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph SMART [" "]
        direction TB
        S_TITLE["SMART PRICING"]
        style S_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        IF["Input Features:<br>├── Historical booking data<br>├── Seasonal patterns<br>├── Local events (concerts, conferences)<br>├── Competitor pricing<br>├── Listing characteristics<br>└── Lead time to check-in"]
        style IF fill:none,stroke:none,text-align:left
        
        ML["ML Model (per listing)<br>- Demand forecasting<br>- Price elasticity estimation<br>- Optimal price calculation"]
        
        REC["Price Recommendations<br>Mon($89), Tue($89), Wed($95), Thu($95), Fri($129), Sat($149), Sun($119)<br>Events detected: [Conference: +20%]"]
        
        IF --> ML
        ML --> REC
    end
```
```

**WHY - Lý do & Impact:**
- 20% increase in host earnings for adopters
- Higher booking rates
- Reduced price anxiety for hosts
- Marketplace efficiency

---

### 3. Trust & Safety

**WHAT - Mục tiêu:**
- Protect guests và hosts
- Detect fraud before it happens
- Enable safe marketplace
- Maintain community trust

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph TRUST [" "]
        direction TB
        T_TITLE["TRUST & SAFETY"]
        style T_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        subgraph INPUTS [" "]
            direction LR
            IV["Identity<br>Verification"]
            RS["Risk Scoring<br>(Booking)"]
        end
        style INPUTS fill:none,stroke:none
        
        EVAL["Real-time Risk Evaluation<br><br>Signals:<br>- Account age<br>- Verification status<br>- Payment method<br>- Device fingerprint<br>- Behavioral patterns<br>- Message content (NLP)<br><br>Actions:<br>- Approve<br>- Require verification<br>- Manual review<br>- Block"]
        
        INPUTS --> EVAL
    end
```

> **WHY - Lý do & Impact:**
> 
> 1. **Fraud Prevention:**
>    - 50%+ reduction in fraud losses
>    - Higher guest/host confidence
>    - Critical for marketplace trust
>    - Brand protection
>    - Account takeover
>    - Fake listings
> 
> 2. **Content Moderation:**
>    - Message screening
>    - Photo validation
>    - Review authenticity
> 
> 3. **Host Quality:**
>    - Response prediction
>    - Cancellation risk
>    - Superhost eligibility
```

### 4. Experimentation Platform (ERF)

```
```mermaid
flowchart TD
    subgraph ERF [" "]
        direction TB
        E_TITLE["ERF (Experiment Reporting Framework)"]
        style E_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        SETUP["Experiment Setup<br>- Name: 'New Search Ranking v2'<br>- Population: 10% of users<br>- Variants: Control, Treatment<br>- Primary metric: Booking conversion<br>- Guardrail metrics: Cancellation rate, CS tickets"]
        
        ASSIGN["Assignment Service<br>- Deterministic assignment (user_id hash)<br>- Consistent across sessions<br>- Logging to Kafka"]
        
        ANAL["Analysis Pipeline (Spark)<br>- Join assignments with outcomes<br>- Statistical tests<br>- Segment analysis<br>- Novelty effect detection"]
        
        DASH["Dashboard (Superset)<br>- Treatment effect: +2.3% bookings<br>- Confidence: 95%<br>- Sample size: adequate<br>- Recommendation: SHIP IT"]
        
        SETUP --> ASSIGN
        ASSIGN --> ANAL
        ANAL --> DASH
    end
```
```

---

## 🛠️ AIRBNB OPEN SOURCE CONTRIBUTIONS

```
> **AIRBNB OSS ECOSYSTEM:**
> 
> * **Data Engineering:**
>   * Apache Airflow (Workflow orchestration - Apache top-level)
>   * Apache Superset (Data visualization - Apache top-level)
>   * Knowledge Repo (Knowledge management)
>   * Aerosolve (ML library)
> 
> * **Frontend:**
>   * Visx (Visualization components)
>   * React-dates (Date picker)
>   * Lottie (Animation library)
> 
> * **Infrastructure:**
>   * Nerve (Service discovery)
>   * Synapse (Service registry)
```

---

## 📊 SCALE & NUMBERS

```
AIRBNB BY THE NUMBERS:

Data Volume:
- 50+ PB in data warehouse
- 10,000s of Airflow DAGs
- 100,000s of Airflow tasks/day

Analytics:
- 1000s of metrics in Minerva
- 10,000s of Superset dashboards
- 100s of concurrent Presto queries

ML:
- 1000s of features in Zipline
- 100s of ML models in production
- 10,000s of experiments/year
```

---

## 🔑 KEY LESSONS

### 1. Workflow Orchestration Matters
- Airflow created because no good options existed
- Became industry standard
- DAGs as code is powerful paradigm

### 2. Metrics Layer is Critical
- Minerva ensures consistency
- "Single version of truth"
- Empowers self-service analytics

### 3. Feature Stores Enable ML at Scale
- Zipline manages feature complexity
- Same features for training and serving
- Point-in-time correctness essential

### 4. Democratize Data Access
- Superset for visualization
- SQL as universal language
- Governance through tools

---

## 🔗 OPEN-SOURCE REPOS (Verified)

Airbnb (qua Maxime Beauchemin) đóng góp 2 trong số các tools phổ biến nhất:

| Repo | Stars | Mô Tả |
|------|-------|--------|
| [apache/airflow](https://github.com/apache/airflow) | 44k⭐ | Workflow orchestration — **Airbnb tạo ra** (2014). Industry standard. Có Docker Compose & Helm chart chính thức. |
| [apache/superset](https://github.com/apache/superset) | 70k⭐ | Data visualization/BI — **Airbnb tạo ra** (Maxime Beauchemin). Có `docker-compose.yml` trong repo. |

> 💡 **Hands-on:** Cả 2 repos đều có Docker Compose setup cho local development. `apache/airflow` có thư mục `chart/` cho Helm deployment trên K8s.

---

## 📚 REFERENCES

**Engineering Blog:**
- Airbnb Tech Blog: https://medium.com/airbnb-engineering

**Key Articles:**
- Minerva: https://medium.com/airbnb-engineering/airbnb-metric-computation-with-minerva-part-1-the-design-philosophy-c14e07fabd21
- Zipline: https://medium.com/airbnb-engineering/zipline-airbnbs-declarative-feature-engineering-framework-b7c71bf32b0
- Superset: https://superset.apache.org/

**Talks:**
- How Airbnb Standardized Metric Computation at Scale
- Building Data Democracy at Airbnb

---

*Document Version: 1.1*
*Last Updated: February 2026*
