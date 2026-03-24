#databricks/hilarious 

<mark style="background: #ABF7F7A6;">Exam Weight: 31% — Together with Section 2, this makes up over 60% of the exam. It focuses on using Spark SQL and PySpark to transform data, interacting with external systems, and composing queries using the medallion architecture (Bronze, Silver, Gold layers).</mark>


## 1.  Medallion Architecture (Bronze, Silver, Gold)

### Topic Overview

The **Medallion Architecture** (also called multi hop architecture) is a data design pattern that organizes your lakehouse into three distinct layers, each serving a specific purpose in the data pipeline. The Bronze layer captures raw, unprocessed data exactly as it arrives from source systems. The Silver layer contains cleaned, deduplicated, and conformed data that has been validated and standardized. The Gold layer holds business level aggregations, dimensional models, and analytics ready datasets prepared for BI tools and reporting.

This architecture is a foundational concept for the Databricks Certified Data Engineer Associate exam because it represents how real world data pipelines are built in enterprise lakehouse environments. Each layer enforces data quality at its stage, making it easy to identify where issues occur and to reprocess data if needed. The Medallion pattern works seamlessly with Databricks tools like Auto Loader for ingestion, Lakeflow Spark Declarative Pipelines for transformation, and Unity Catalog for governance.

The beauty of Medallion is simplicity combined with power. You don't need complex orchestration to implement it. Start with a raw data ingestion layer, add cleanup logic in the middle, and expose clean aggregates at the end. Each layer becomes a Delta table in your Unity Catalog, creating a clear lineage for governance and auditing. You can support both batch and streaming workloads within the same architecture, adapting your pipeline to how data actually arrives.

---

### Key Concepts

- **Bronze Layer: Raw Ingestion**
    
    The Bronze layer is where all raw data lands. It's append only, meaning data is never updated or deleted, only new records are added. This preserves the complete history of all data received from source systems. The Bronze layer uses tools like Auto Loader for streaming ingestion or COPY INTO for batch uploads. The goal is speed and completeness, not cleanliness. Data may have duplicates, null values, inconsistent formatting, and mixed data types. You preserve the data exactly as received because you might need to debug issues upstream. Bronze tables are typically partitioned by arrival date or source system for efficient querying and cleanup.
    
- **Silver Layer: Cleaned and Conformed**
    
    The Silver layer applies data quality rules and transformations to Bronze data. Here you deduplicate records, filter out invalid rows, standardize column names and data types, handle null values, and apply business logic rules. The Silver layer is where you join reference data to add context (for example, joining customer dimensions to a transactions table). Data in Silver is conformed meaning it follows organizational standards for naming, formatting, and structure. Silver tables are typically still quite granular (one row per business event) but clean and ready for analysis. This is also where you might quarantine bad data that fails quality checks, routing invalid records to a separate table for investigation.
    
- **Gold Layer: Business Aggregates**
    
    The Gold layer contains business level datasets. Data is heavily aggregated, modeled for specific use cases, and optimized for reporting and BI tools. Gold tables often follow a star schema or fact and dimension model. Examples include daily revenue summaries, customer lifetime value calculations, or a fact table of orders joined with dimension tables for products and dates. The Gold layer is what end users and BI tools query most frequently. Tables are typically heavily indexed and partitioned for fast query performance. You create Gold tables by aggregating and joining clean Silver data, computing business metrics and KPIs.
    
- **Streaming Through the Layers**
    
    Medallion Architecture supports real time streaming data. Bronze can ingest streaming events using Auto Loader (which internally uses Spark Structured Streaming). Data flows through Silver transformations in real time, and Gold aggregations update continuously. Lakeflow Spark Declarative Pipelines make this easy by letting you define a DAG of tables where each table can be either a streaming table or materialized view. A streaming table continuously processes new input data. A materialized view recomputes based on upstream changes. This allows you to push data through all three layers with low latency while maintaining the multi hop architecture benefits.
    
- **Lakeflow Spark Declarative Pipelines and Medallion Architecture**
    
    Lakeflow Spark Declarative Pipelines are built specifically to implement the Medallion pattern. You declare your pipeline as a set of SQL statements, each creating or updating a table. You mark Bronze tables as streaming tables ingesting from external sources. Silver tables transform Bronze data. Gold tables aggregate Silver data. Lakeflow automatically builds the dependency graph, runs only the necessary updates when source data changes, and provides built in error handling and recovery. The declarative approach means you focus on the data transformations, not on orchestration logic. Lakeflow also tracks data lineage through the layers automatically, which is crucial for governance and debugging.
    

---

### Code Examples

#### Bronze Layer: Auto Loader Ingestion (Python)

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define schema for incoming JSON events
schema = StructType([
    StructField("customer_id", StringType()),
    StructField("order_id", StringType()),
    StructField("amount", IntegerType()),
    StructField("timestamp", StringType())
])

# Auto Loader ingests raw JSON into bronze table
(spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/tmp/schema_location")
    .schema(schema)
    .load("/mnt/raw/orders/")
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/tmp/checkpoint")
    .option("mergeSchema", "true")
    .table("bronze_orders")
)
```

This code uses Auto Loader to stream JSON files from cloud storage into the bronze_orders table. Auto Loader automatically detects new files, parses them, and appends rows to the Delta table. The checkpointLocation tracks which files have been processed, preventing duplicates. mergeSchema allows the schema to evolve as new fields appear in incoming data.

#### Silver Layer: Cleaning and Deduplication (SQL)

```sql
CREATE OR REPLACE TABLE silver_orders AS
WITH deduplicated AS (
  SELECT 
    customer_id,
    order_id,
    amount,
    CAST(timestamp AS TIMESTAMP) AS order_timestamp,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY timestamp DESC) AS rn
  FROM bronze_orders
  WHERE customer_id IS NOT NULL
    AND order_id IS NOT NULL
    AND amount > 0
)
SELECT 
  customer_id,
  order_id,
  amount,
  order_timestamp,
  CURRENT_TIMESTAMP() AS processed_at
FROM deduplicated
WHERE rn = 1;
```

This SQL transformation reads from bronze_orders and applies data quality rules. It filters out rows with null keys or invalid amounts, casts timestamp to the correct type, deduplicates using a window function (keeping the most recent record per order_id), and adds a processed_at column for audit trails. The result is a clean, conformed silver table.

#### Gold Layer: Business Aggregation (SQL)

```sql
CREATE OR REPLACE TABLE gold_daily_revenue AS
SELECT 
  CAST(order_timestamp AS DATE) AS order_date,
  COUNT(DISTINCT customer_id) AS num_customers,
  COUNT(DISTINCT order_id) AS num_orders,
  SUM(amount) AS total_revenue,
  AVG(amount) AS avg_order_value,
  MIN(amount) AS min_order_value,
  MAX(amount) AS max_order_value
FROM silver_orders
GROUP BY CAST(order_timestamp AS DATE)
ORDER BY order_date DESC;
```

This Gold table aggregates clean Silver data to produce daily revenue metrics. A BI tool can query this table directly to show dashboards without needing to process millions of order rows. The aggregation reduces data volume and makes queries fast. You might create many Gold tables for different business perspectives (revenue, customer metrics, product analysis, etc.).

#### Complete Medallion Pipeline in Lakeflow Spark Declarative Pipelines (SQL)

```sql
-- Bronze: streaming table ingesting raw data
CREATE STREAMING TABLE bronze_orders
COMMENT "Raw orders data from source system"
AS
SELECT *
FROM cloud_files(
  "/mnt/raw/orders",
  "json",
  map("cloudFiles.schemaLocation", "/tmp/schema")
);

-- Silver: materialized view with cleaning logic
CREATE MATERIALIZED VIEW silver_orders
COMMENT "Cleaned and deduplicated orders"
AS
WITH deduplicated AS (
  SELECT 
    customer_id,
    order_id,
    amount,
    CAST(timestamp AS TIMESTAMP) AS order_timestamp,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY timestamp DESC) AS rn
  FROM STREAM(bronze_orders)
  WHERE customer_id IS NOT NULL
    AND amount > 0
)
SELECT 
  customer_id,
  order_id,
  amount,
  order_timestamp,
  CURRENT_TIMESTAMP() AS processed_at
FROM deduplicated
WHERE rn = 1;

-- Gold: materialized view with business aggregations
CREATE MATERIALIZED VIEW gold_daily_revenue
COMMENT "Daily revenue summary for reporting"
AS
SELECT 
  CAST(order_timestamp AS DATE) AS order_date,
  COUNT(DISTINCT customer_id) AS num_customers,
  COUNT(DISTINCT order_id) AS num_orders,
  SUM(amount) AS total_revenue
FROM silver_orders
GROUP BY CAST(order_timestamp AS DATE);
```

This Lakeflow pipeline declares all three layers in one SQL notebook. The Bronze table streams raw data using Auto Loader (via the `cloud_files()` function). Silver reads from Bronze, cleans the data, and outputs a materialized view. Gold reads from Silver, aggregates, and outputs daily metrics. Lakeflow automatically manages dependencies and updates tables incrementally as new data arrives. The STREAM() function tells Lakeflow to process only new rows since the last update.

---

### Common Exam Scenarios

**Scenario 1: Choosing the Right Layer for Data Quality Checks**

Your company receives customer transaction data from a payment processor. The raw JSON sometimes contains duplicate events (the same transaction appears twice) and occasionally missing customer_id values. Where should you implement deduplication and filtering logic? The answer is Silver. Bronze should capture raw data exactly as received so you can debug upstream issues. The Silver layer is specifically designed for applying data quality rules. You deduplicate in Silver, filter out invalid records, and standardize formats. This keeps Bronze pure and makes troubleshooting easier if something goes wrong.

**Scenario 2: Determining Which Layer Feeds Your BI Dashboard**

Your analytics team needs to build a dashboard showing top 10 customers by revenue for the current month. Should they query Bronze, Silver, or Gold? The answer is Gold. Gold tables are pre aggregated and modeled specifically for reporting. A Gold table with customer lifetime value or monthly revenue per customer would make this dashboard instant to render. If they query Silver, they're scanning individual transaction rows and doing aggregations in Tableau or Power BI (slower and more expensive on compute). Bronze is for ingestion only. Always expose pre aggregated, business ready Gold tables to BI tools for best performance.

**Scenario 3: Implementing Streaming Data Through Medallion**

Your company wants real time revenue dashboards that update every minute instead of batch daily reports. How do you adapt the Medallion Architecture? Use Lakeflow Spark Declarative Pipelines with streaming tables and materialized views. Make Bronze a streaming table reading from Auto Loader (continuously processing new events). Make Silver a materialized view that applies transformations to each new batch of Bronze data. Make Gold a materialized view that aggregates Silver data. Lakeflow automatically orchestrates the flow: when new events arrive in Bronze, they flow through Silver transformations, which trigger Gold aggregations. You get real time freshness without manual orchestration. The multi layer structure ensures data quality at each step even with continuous updates.

---

### Key Takeaways

- Medallion Architecture organizes data into three layers: Bronze (raw append only), Silver (cleaned and conformed), and Gold (aggregated for business use). Each layer serves a distinct purpose in the pipeline.
- Bronze tables preserve raw data as is. Never transform Bronze data. Use Auto Loader or COPY INTO for ingestion and always append. Keep Bronze immutable so you can troubleshoot issues.
- Silver is where data quality rules live. Deduplicate, filter invalid rows, standardize column names and types, join reference data. Silver data is clean and conformed but still granular.
- Gold tables are aggregated and modeled for specific business purposes (star schema, fact tables, summary tables). BI tools and dashboards query Gold, never Silver or Bronze.
- Lakeflow Spark Declarative Pipelines are the native Databricks way to implement Medallion. They handle orchestration, incremental processing, error recovery, and lineage tracking automatically.

---

### Gotchas and Tips

<aside> 💡 **⚠️ Never Apply Quality Rules in Bronze** A common mistake is filtering or transforming data as it lands in Bronze. Resist this. Bronze is intentionally raw. If you filter out "bad" records in Bronze, you lose the ability to audit what was filtered and why. If upstream changes their data format and you need to replay history, you've lost the original data. Keep Bronze immutable. Quality rules belong in Silver.

</aside>

<aside> 💡 **⚠️ Gold Tables Are for Reporting, Not for Operational Queries** Highly aggregated Gold tables are perfect for dashboards but not for drilling down into details. If your BI dashboard needs "show me the transactions for customer X", you query Silver or Bronze, not a pre aggregated Gold table. Design Gold tables with your reporting use cases in mind, not as a general purpose view of the data.

</aside>

<aside> 💡 **⚠️ Deduplication Logic Depends on Your Business Key** When you deduplicate in Silver, use the right business key. If you deduplicate on order_id but a customer places two identical orders with the same id (yes, it happens), you've lost real data. Define your business key carefully. Use ROW_NUMBER() with a clear PARTITION BY clause and ORDER BY logic to keep the record you want (usually most recent or earliest depending on the use case).

</aside>

---

### Links and Resources

- [**What is the medallion lakehouse architecture?**](https://docs.databricks.com/aws/en/lakehouse/medallion) — Official guide to the Bronze, Silver, Gold layered data architecture.
- [**What is a data lakehouse?**](https://docs.databricks.com/aws/en/lakehouse/) — Overview of the lakehouse paradigm combining data lakes and data warehouses.
- [**Tutorial: Build an ETL pipeline**](https://docs.databricks.com/aws/en/getting-started/data-pipeline-get-started) — Hands on tutorial building a medallion architecture pipeline with Lakeflow.

---

## 2. Cluster Types and Configuration

### Topic Overview

Databricks provides multiple cluster types and compute options tailored to different workloads and use cases. Understanding when to use each cluster type is critical for the exam and for building efficient data pipelines. The main distinction is between **All Purpose Clusters** (interactive, long running), **Job Clusters** (ephemeral, job specific), and **SQL Warehouses** (SQL optimized). Beyond these, **Serverless Compute** removes the need for manual cluster management entirely.

All Purpose Clusters are created manually or via API and persist until you explicitly terminate them. They support multiple users and multiple notebooks running simultaneously, making them ideal for interactive development, ad hoc analysis, and exploratory work. You pay for the compute hours regardless of whether you are actively running code.

Job Clusters, by contrast, are created automatically when a job starts and terminated as soon as the job finishes. They are cost effective for production workloads because you only pay for the compute time the job actually runs. Job Cluster configuration is defined within the job specification, not independently. You cannot share a Job Cluster across multiple jobs—each job gets its own ephemeral cluster.

SQL Warehouses are specialized endpoints optimized for SQL queries and BI tools. They come in three flavors—Classic, Pro, and Serverless—and leverage **Photon**, a native vectorized query engine that accelerates SQL workloads. Serverless Compute is a managed option where Databricks handles cluster provisioning automatically, providing instant startup with no configuration overhead.

### Key Concepts

- **All Purpose vs Job Clusters**
    
    All Purpose Clusters persist until manually terminated and can run multiple workloads simultaneously. You create them manually via the UI or API and they continue to exist (and incur costs) even when idle. Job Clusters are ephemeral and lifecycle controlled—they spin up when a job starts and terminate when the job ends. All Purpose Clusters are for interactive work; Job Clusters are for scheduled production jobs. Job Clusters are more cost effective for automated workflows.
    
- **SQL Warehouses**
    
    SQL Warehouses are dedicated compute endpoints for SQL workloads and BI tool integration. They come in three tiers: Classic (cost effective), Pro (balanced), and Serverless (fully managed). All support Photon acceleration. SQL Warehouses are optimized for query execution and are the preferred choice for dashboards, BI tools, and SQL based reporting. They are not suitable for general purpose data engineering work like cluster creation for Spark jobs.
    
- **Serverless Compute**
    
    Serverless Compute is Databricks managed compute that requires zero configuration. It is available for SQL Warehouses, notebooks, and jobs. You do not need to specify cluster size, instance types, or worker counts—Databricks handles all provisioning automatically. Startup is instantaneous. You pay per unit of compute consumed (DBUs). Serverless is ideal when you want simplicity and do not want to manage cluster infrastructure.
    
- **Autoscaling**
    
    Autoscaling allows a cluster to dynamically adjust the number of worker nodes between a defined minimum and maximum. When demand increases, new workers are added. When demand decreases, workers are removed. You configure autoscaling by specifying min workers and max workers in the cluster specification. This optimizes cost by avoiding over provisioning while ensuring adequate capacity for workload spikes.
    
- **Cluster Policies**
    
    Cluster Policies are admin defined templates that restrict cluster configuration options. They enforce organizational standards like compute limits, runtime versions, and instance types. Users can only create clusters that conform to the policy. Policies reduce sprawl, enforce cost controls, and ensure compliance with organizational requirements.
    
- **Cluster Access Modes**
    
    Databricks supports three access modes: Shared (multiple users, Unity Catalog enforced for governance), Single User (cluster dedicated to one user, full isolation), and No Isolation Shared (legacy mode, no Unity Catalog enforcement). Shared mode is the modern default and required for Unity Catalog features. Single User is used when isolation and dedicated resources are needed. No Isolation Shared is deprecated.
    
- **Photon**
    
    Photon is Databricks native vectorized query engine that dramatically speeds up SQL and DataFrame operations. It is available on specific Databricks Runtime versions. When enabled, Photon optimizes query execution by processing data in columnar format, reducing CPU and memory usage. SQL Warehouses use Photon by default. You can enable Photon on All Purpose Clusters via configuration.
    
- **Single Node vs Multi Node Clusters**
    
    Single node clusters have no worker nodes—the driver executes tasks locally. They are useful for lightweight testing, prototyping, and single machine workloads. Multi node clusters have a driver and one or more worker nodes for distributed processing. Multi node clusters are required for production workloads and large scale data processing. Single node is cheaper but not suitable for parallelized work.
    
- **Instance Types, Spot Instances, and Init Scripts**
    
    Instance types define the CPU, memory, and storage of each node (e.g., i3.xlarge). Spot instances are discounted but subject to interruption—good for fault tolerant batch jobs. Init scripts are bash scripts that run when a cluster starts, used to install libraries, configure environment variables, or install software. Databricks Runtime versions determine the Apache Spark version and available libraries.

---

### Code Examples

All Purpose Cluster Configuration (JSON):

```json
{
  "cluster_name": "my-interactive-cluster",
  "spark_version": "15.4.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "driver_node_type_id": "i3.xlarge",
  "num_workers": 2,
  "autoscale": {
    "min_workers": 1,
    "max_workers": 4
  },
  "aws_attributes": {
    "use_spot_instances": true,
    "spot_bid_price_percent": 70
  },
  "init_scripts": [
    {
      "s3": {
        "destination": "s3://my-bucket/scripts/install-packages.sh"
      }
    }
  ],
  "access_mode": "SHARED",
  "photon_driver_node": true,
  "photon_worker_node": true
}
```

Job Cluster Configuration (via Databricks REST API concept):

```json
{
  "task_key": "process_data",
  "new_cluster": {
    "cluster_name": "job-cluster-process",
    "spark_version": "15.4.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 3,
    "aws_attributes": {
      "use_spot_instances": true
    }
  },
  "spark_python_task": {
    "python_file": "dbfs:/scripts/etl.py"
  }
}
```

SQL Query on SQL Warehouse with Photon:

```sql
-- Query executed on SQL Warehouse (Photon enabled)
SELECT 
    customer_id,
    SUM(order_amount) as total_spent,
    COUNT(*) as order_count,
    AVG(order_amount) as avg_order
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 100;
```

Programmatically checking cluster status (conceptual Python):

```python
# Using Databricks API to get cluster info
import requests

cluster_id = "1234-567890-test123"
response = requests.get(
    f"<https://my-workspace.cloud.databricks.com/api/2.0/clusters/get>",
    params={"cluster_id": cluster_id},
    headers={"Authorization": f"Bearer {token}"}
)

cluster_info = response.json()
print(f"State: {cluster_info['state']}")
print(f"Driver node type: {cluster_info['driver_node_type_id']}")
print(f"Number of workers: {cluster_info['num_workers']}")
```

---

### Common Exam Scenarios

**Scenario 1: Choosing the Right Cluster for a Scheduled ETL Job**

You are designing a production ETL pipeline that runs every night at midnight. The job processes 500 GB of data using PySpark and takes about 30 minutes. Management wants to minimize compute costs. Which cluster type should you use and why? The answer is a **Job Cluster**. Job Clusters are created when the job starts and terminated when it finishes, so you only pay for the 30 minutes of actual computation time. An All Purpose Cluster would be wasteful because it would persist for 23.5 hours after the job completes, incurring charges even while idle. Serverless Compute is also a valid option if cost is the priority and you want to avoid cluster management entirely.

**Scenario 2: Interactive Development with Multiple Notebooks**

A data scientist is exploring a large dataset and needs to run multiple notebooks simultaneously while iterating on SQL queries and PySpark code. They need the cluster to remain available for several hours. Which cluster type should they use? The answer is an **All Purpose Cluster**. All Purpose Clusters support multiple users and long running workloads. They persist until manually terminated, making them ideal for interactive development. A Job Cluster would terminate immediately after the first notebook completes, interrupting the workflow.

**Scenario 3: SQL Dashboard Queries Timing Out**

A BI team has set up dashboards that query a large fact table with millions of rows. The queries are slow and frequently time out. The team wants to improve query performance without increasing infrastructure costs. What is the best solution? The answer is to use a **SQL Warehouse with Photon enabled**. SQL Warehouses are optimized for SQL workloads and BI tools. Photon is a vectorized query engine that dramatically accelerates SQL execution. SQL Warehouses come in Serverless, Pro, and Classic tiers, providing options for different budgets. This is the intended use case for SQL Warehouses.

### Key Takeaways

- Use **Job Clusters** for production scheduled workloads to minimize cost—they only run while the job executes.
- Use **All Purpose Clusters** for interactive development, prototyping, and collaborative work where you need the cluster to persist.
- Use **SQL Warehouses** with Photon for SQL heavy workloads, dashboards, and BI integrations.
- **Autoscaling** optimizes cost by dynamically adjusting worker count based on demand—configure min and max workers.
- **Serverless Compute** eliminates cluster configuration burden—Databricks manages provisioning, startup is instant, and you pay per compute unit.

### Gotchas and Tips

<aside> ⚠️ Job Clusters Cannot Be Shared. If you define a Job Cluster within a job specification, that cluster exists only for that job. You cannot reuse the same Job Cluster definition across multiple jobs. Each job gets its own ephemeral cluster. If you want to run multiple jobs on the same persistent cluster, use an All Purpose Cluster and configure the jobs to use it.

</aside>

<aside> ⚠️ Spot Instances Have Interruption Risk. While spot instances are cheaper (often 50-70% discount), cloud providers can reclaim them with minimal notice. Use spot instances for fault tolerant, retryable batch jobs. Avoid them for long running interactive sessions where interruption would be disruptive. You can mix spot and on demand instances on the same cluster for balance.

</aside>

<aside> ⚠️ All Purpose Clusters Keep Running and Accruing Costs Until Explicitly Terminated. Unlike Job Clusters which auto terminate, All Purpose Clusters persist indefinitely after creation. If you forget to terminate a cluster at the end of your day, you will be charged for the entire night. Always terminate interactive clusters when you are done. Some workspaces implement auto terminate policies after a period of inactivity (e.g., 30 minutes).

</aside>

---

### Links and Resources

- [**SQL warehouse sizing, scaling, and queuing**](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-behavior) — How SQL warehouses behave under load including auto scaling.
- [**Configure compute for jobs**](https://docs.databricks.com/aws/en/jobs/compute) — Selecting the right compute type for different job workloads.
- [**Connect to serverless compute**](https://docs.databricks.com/aws/en/admin/workspace-settings/serverless) — Enabling and configuring serverless compute in your workspace.

---

## 3. Lakeflow Spark Declarative Pipelines

### Topic Overview

Lakeflow Spark Declarative Pipelines (formerly known as Delta Live Tables) is a declarative framework for building reliable data pipelines on Databricks. Instead of writing imperative Spark code where you specify every step, you declare your desired end state—your target tables and their definitions—and the system handles the rest. This includes orchestration, dependency management, error handling, and data quality validation.

The declarative approach means you focus on what data you want, not how to compute it. Lakeflow Spark Declarative Pipelines automatically figures out the optimal execution order, handles retries, and ensures your data quality rules are enforced. This is especially powerful for building medallion architecture pipelines (Bronze, Silver, Gold) where you have many interdependent transformations.

Pipelines are defined in notebooks using SQL or Python and then deployed as pipeline objects in Databricks. You run them in either Development mode (for iteration) or Production mode (for reliable scheduled execution). The exam expects you to understand how to design pipelines, choose between Streaming Tables and Materialized Views, apply data quality expectations, and troubleshoot pipeline failures.

---

### Key Concepts

- What are Lakeflow Spark Declarative Pipelines?
    
    Lakeflow Spark Declarative Pipelines is a declarative data pipeline framework where you define tables using SQL `CREATE STREAMING TABLE` and `CREATE MATERIALIZED VIEW` statements (or Python equivalents). The framework automatically manages dependencies, scheduling, error handling, and data quality. Key benefits include simplified code, automatic optimization, built in data quality constraints, and production ready reliability out of the box.
    
- Streaming Tables vs Materialized Views
    
    Streaming Tables are append only tables optimized for incremental and streaming data. They process only new data since the last run (checkpoint), making them efficient for high volume sources like message buses. Materialized Views are recomputed from scratch on each pipeline run and are ideal for aggregations, deduplication, and transformations. Choose Streaming Tables for your Bronze layer (raw data ingestion) and consider Materialized Views for Silver and Gold layers depending on whether you need incremental processing or full recomputation.
    
- Expectations (data quality constraints)
    
    Expectations are data quality rules defined inline in your table definition using the syntax `CONSTRAINT name EXPECT (condition)`. Each expectation has an action: WARN logs violations to the event log but lets rows through, DROP filters out rows that violate the constraint, and FAIL stops the entire pipeline if violations are detected. Expectations are checked as data is processed, catching quality issues early in the pipeline.
    
- Triggered vs Continuous mode
    
    Triggered pipelines run once and complete, then stop. They are ideal for scheduled batch jobs (e.g., daily or hourly runs). Continuous pipelines run indefinitely, processing data as it arrives, making them suitable for real time streaming scenarios. Continuous pipelines have lower latency but consume compute resources continuously. Choose based on your use case: batch transformations use Triggered mode, streaming data ingestion uses Continuous mode.
    
- Development vs Production mode
    
    Development mode allows faster iteration: it enables retries on transient failures, uses smaller clusters, and is suited for testing and development. Production mode is optimized for reliability: it uses larger clusters if needed, has stricter error handling, and is configured for scheduled execution. You typically develop your pipeline in a Development cluster and then deploy it to run in Production mode on a schedule.
    
- Pipeline dependencies and DAG resolution
    
    Lakeflow Spark Declarative Pipelines automatically determines dependencies by analyzing your table definitions. If Table B reads from Table A, the pipeline knows A must compute first. The system builds a directed acyclic graph (DAG) and executes tables in the correct order. You don't manually specify orchestration—this automatic dependency resolution is a key advantage over traditional Spark jobs.
    

---

### Code Examples

**Creating a Streaming Table with Auto Loader**

```sql
CREATE STREAMING TABLE bronze_orders
COMMENT "Raw orders from cloud storage"
AS
SELECT *
FROM cloud_files(
  "s3://my-bucket/orders/",
  "csv",
  map(
    "cloudFiles.format", "csv",
    "header", "true"
  )
)
```

**Creating a Materialized View with Aggregation**

```sql
CREATE MATERIALIZED VIEW silver_orders_daily
COMMENT "Daily order summary"
AS
SELECT
  DATE(order_date) AS order_day,
  COUNT(*) AS total_orders,
  SUM(order_amount) AS total_revenue,
  AVG(order_amount) AS avg_order_amount
FROM bronze_orders
WHERE order_date IS NOT NULL
GROUP BY DATE(order_date)
```

**Expectations / Data Quality Constraints**

```sql
CREATE STREAMING TABLE silver_customers
CONSTRAINT valid_email EXPECT (email LIKE '%@%.%') ON VIOLATION DROP
CONSTRAINT positive_age EXPECT (age > 0) ON VIOLATION FAIL
CONSTRAINT not_null_id EXPECT (customer_id IS NOT NULL) ON VIOLATION WARN
AS
SELECT *
FROM bronze_customers
```

**Python API Equivalent for Creating Streaming Tables**

```python
from databricks.sdk.python.dlt import create_streaming_table, expect
from pyspark.sql.functions import col

@create_streaming_table
def bronze_orders():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .load("s3://my-bucket/orders/")
    )

@create_streaming_table
@expect("valid_amount", "order_amount > 0", "DROP")
def silver_orders():
    return spark.sql("SELECT * FROM bronze_orders")
```

**Full Medallion Architecture Example (Bronze / Silver / Gold)**

```sql
-- BRONZE LAYER: Raw data ingestion
CREATE STREAMING TABLE bronze_events
AS
SELECT *
FROM cloud_files(
  "s3://events/raw/",
  "json"
);

-- SILVER LAYER: Cleaned and deduplicated
CREATE STREAMING TABLE silver_events
CONSTRAINT valid_timestamp EXPECT (event_time IS NOT NULL) ON VIOLATION DROP
AS
SELECT
  event_id,
  event_time,
  user_id,
  event_type,
  _metadata.file_modification_time AS ingestion_time
FROM bronze_events
QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY _metadata.file_modification_time DESC) = 1;

-- GOLD LAYER: Business metrics
CREATE MATERIALIZED VIEW gold_user_activity
AS
SELECT
  user_id,
  DATE(event_time) AS activity_date,
  COUNT(*) AS event_count,
  COUNT(DISTINCT event_type) AS distinct_events
FROM silver_events
GROUP BY user_id, DATE(event_time);
```

---

### Common Exam Scenarios

**Scenario 1: Choosing Between Streaming Table and Materialized View for Silver Layer**

You have a Bronze layer with raw customer data arriving every minute from an S3 bucket. Your Silver layer needs to deduplicate records by customer_id and keep only the latest entry. Your Gold layer reports use this deduplicated data for daily aggregations. Should you use a Streaming Table or Materialized View for the Silver layer deduplication?

Answer: Use a Materialized View for the Silver deduplication layer. Although the Bronze layer is a Streaming Table (appending raw data), the Silver layer performs deduplication using ROW_NUMBER(), which requires full dataset access. Deduplication is a transformation best handled by a Materialized View that recomputes the full state. The Streaming Table would be inefficient here because deduplication cannot be done incrementally you need to see all records to identify the latest one per customer. The Materialized View will recompute from the Bronze Streaming Table on each pipeline run, ensuring accurate deduplication.

**Scenario 2: Handling Data Quality Violations in a Pipeline**

Your pipeline ingests transaction data with an expectation that transaction_amount > 0. Recently, a data source bug sent transactions with null amounts. You want to log these violations for investigation but prevent bad data from reaching downstream tables. Which constraint action would you use: WARN, DROP, or FAIL?

Answer: Use DROP. WARN only logs violations and still passes bad data downstream. FAIL would stop the entire pipeline, blocking valid transactions too. DROP filters out rows that fail the constraint, so valid transactions continue flowing while bad ones are removed. The violations are still logged in the pipeline event log, giving you a record of what was filtered. This is the right choice when you want to enforce a quality rule without halting the pipeline.

**Scenario 3: Pipeline Execution Order with Dependencies**

You define three tables in a notebook: bronze_customers (reads from S3), silver_customers (reads from bronze_customers), and gold_customer_metrics (reads from silver_customers). You don't explicitly order the table definitions in your notebook. Does Lakeflow Spark Declarative Pipelines still execute them in the correct order?

Answer: Yes. Lakeflow Spark Declarative Pipelines automatically analyzes table definitions to determine dependencies and builds a DAG. The order of table definitions in the notebook does not matter. The system will always execute bronze_customers first, then silver_customers, then gold_customer_metrics, regardless of how they appear in the notebook. This automatic dependency resolution is a core advantage you declare what you want, and the system figures out the execution order.

---

### Key Takeaways

- Lakeflow Spark Declarative Pipelines uses declarative SQL/Python to define tables, not imperative code. You declare the desired end state and the system handles orchestration.
- Use Streaming Tables for append only, incremental data (Bronze layer). Use Materialized Views for aggregations and full state computation (Silver and Gold layers).
- Expectations enforce data quality with three actions: WARN (log only), DROP (filter bad rows), FAIL (stop pipeline).
- Dependencies are automatic the system analyzes table definitions and executes in the correct order. You don't manually define DAGs.
- Triggered mode for batch jobs (runs once), Continuous mode for streaming (runs indefinitely). Development mode for iteration, Production mode for scheduled reliable execution.

---

### Gotchas and Tips

<aside> ⚠️ Streaming Tables are append only. If you need to update or delete records, use a Materialized View instead. Streaming Tables cannot handle upsert patterns use change data feed (CDF) or manual delta merge operations for that.

</aside>

<aside> ⚠️ Don't overuse FAIL constraints. A single FAIL constraint will stop the entire pipeline if triggered. Use DROP or WARN for non critical quality issues, and reserve FAIL for truly critical data requirements that should block the pipeline.

</aside>

<aside> ⚠️ Materialized Views recompute fully on each run. If you have a large Materialized View that does expensive aggregations, consider moving it to Continuous mode with Auto Scaling, or use a Streaming Table if possible. Full recomputation can be costly at scale.

</aside>

---

### Links and Resources

- [**Lakeflow Spark Declarative Pipelines**](https://docs.databricks.com/aws/en/ldp/) — Main documentation page for Lakeflow Spark Declarative Pipelines (formerly DLT).
- [**Lakeflow Spark Declarative Pipelines concepts**](https://docs.databricks.com/aws/en/ldp/concepts) — Core concepts including datasets, flows, and pipeline modes.
- [**Develop pipeline code with Python**](https://docs.databricks.com/aws/en/ldp/developer/python-dev) — Python API reference for building declarative pipelines.
- [**Develop pipeline code with SQL**](https://docs.databricks.com/aws/en/ldp/developer/sql-dev) — SQL syntax for defining streaming tables and materialized views.

---

## 4. Implementing Data Pipelines with Lakeflow

### Topic Overview

Lakeflow Spark Declarative Pipelines provide a declarative way to build data pipelines in Databricks. Instead of writing imperative code that describes how to transform data step by step, you define what data you want to process and what transformations to apply. The pipeline engine handles scheduling, fault tolerance, and incremental processing automatically. This makes it easier to build reliable, maintainable data pipelines that scale.

A Lakeflow pipeline consists of one or more notebooks that contain SQL or Python code defining tables. Each notebook contains table definitions using statements like `CREATE OR REFRESH STREAMING TABLE` or `CREATE OR REPLACE MATERIALIZED VIEW`. The pipeline orchestrates these notebooks, manages dependencies between tables, and handles data quality checks. Pipelines integrate directly with Unity Catalog, storing results in a specified catalog and schema with full governance and lineage tracking.

For the exam, you need to understand how to configure pipelines, implement change data capture with APPLY CHANGES, choose between SCD Type 1 and Type 2, understand refresh modes, monitor pipelines through event logs, and handle errors gracefully. You should also be able to work with multi notebook pipelines and understand how they integrate with Unity Catalog.

---

### Key Concepts

- Pipeline Configuration and Setup
    
    A Lakeflow pipeline is configured with a name, target catalog and schema (catalog.schema), cluster configuration, and paths to source notebooks. You create a pipeline through the Databricks UI, REST API, or Databricks Asset Bundles. The pipeline specifies which notebooks contain table definitions. When you trigger a pipeline run, Databricks executes the notebooks in dependency order, creates or updates the target tables, and tracks the run in the event log. You can configure the pipeline to run on a schedule, trigger on external events, or run manually.
    
- APPLY CHANGES for Change Data Capture (CDC)
    
    APPLY CHANGES is a Lakeflow operation that processes change data capture (CDC) feeds. It takes a stream of inserts, updates, and deletes from a source table (or view) and applies them to a target table. The syntax is `APPLY CHANGES INTO target_table FROM source_table KEYS (primary_key_cols) SEQUENCE BY (sequence_col)`. The `KEYS` clause specifies the column(s) that uniquely identify a record. The `SEQUENCE BY` clause specifies a column that orders the changes (usually a timestamp or version number). APPLY CHANGES handles idempotency, so replaying the same changes twice produces the same result.
    
- SCD Type 1 vs Type 2
    
    Slowly Changing Dimension (SCD) Type 1 overwrites old values with new ones. When a record is updated, the previous value is lost. This is the default behavior. SCD Type 2 tracks history by creating new rows for each change, keeping the old and new values. You activate SCD Type 2 by adding `STORED AS SCD TYPE 2` to the table definition. With Type 2, the target table gets additional columns like `__start_version`, `__end_version`, `__current` that track when a record was active. Choose Type 1 when you only care about the current state. Choose Type 2 when you need to analyze how data has changed over time.
    
- Full Refresh vs Incremental Refresh
    
    A full refresh reprocesses all data from the source. Every time the pipeline runs, it reads the entire source and rebuilds the target table. This is simple but expensive for large datasets. An incremental refresh processes only new data since the last successful run. Lakeflow tracks a checkpoint that marks how far the pipeline has progressed, so the next run only reads new records. Streaming tables in Lakeflow always use incremental refresh. Materialized views can be configured for full or incremental refresh depending on the query.
    
- Pipeline Event Logs and Monitoring
    
    Every pipeline run generates events that are stored in a system managed event log table. This table contains information about pipeline start and stop times, table updates, data quality check results, and any errors that occurred. The event log is located at `system.pipelines.lineage` or in a pipeline specific catalog/schema. You can query the event log to understand pipeline performance, debugging issues, and tracking data lineage. The event log includes timestamps, table names, row counts, and error details if a pipeline fails.
    
- Multi Notebook Pipelines
    
    A single pipeline can contain definitions from multiple notebooks. Each notebook defines one or more tables. The pipeline engine automatically resolves dependencies between tables across notebooks. If Notebook A defines a staging table and Notebook B defines a gold table that reads from that staging table, the pipeline will execute Notebook A first, then Notebook B. You organize notebooks logically by layer (bronze, silver, gold) or by business domain. Multi notebook pipelines make code more modular and easier to maintain than putting everything in a single notebook.
    

---

### Code Examples

**APPLY CHANGES with SCD Type 1 (Overwrite)**

```sql
-- In a Lakeflow pipeline notebook
CREATE OR REFRESH STREAMING TABLE customers AS
APPLY CHANGES INTO live.customers
FROM raw_customers_cdc
KEYS (customer_id)
SEQUENCE BY event_timestamp
WHEN MATCHED AND operation = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

**APPLY CHANGES with SCD Type 2 (Track History)**

```sql
-- In a Lakeflow pipeline notebook
CREATE OR REFRESH STREAMING TABLE customers_history
STORED AS SCD TYPE 2 AS
APPLY CHANGES INTO live.customers_history
FROM raw_customers_cdc
KEYS (customer_id)
SEQUENCE BY event_timestamp
WHEN MATCHED AND operation = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

**Multi Notebook Pipeline: Bronze Layer**

```sql
-- Notebook: 01_bronze_ingest.sql
-- Ingests raw data from cloud storage
CREATE OR REFRESH STREAMING TABLE orders_bronze AS
SELECT
  *,
  _metadata.file_path,
  _metadata.file_modification_time
FROM cloud_files(
  '/mnt/raw/orders',
  'parquet',
  map('cloudFiles.schemaLocation', '/mnt/checkpoints/orders')
)
```

**Multi Notebook Pipeline: Silver Layer (depends on Bronze)**

```sql
-- Notebook: 02_silver_transform.sql
-- Transforms and cleanses bronze data
CREATE OR REFRESH STREAMING TABLE orders_silver AS
SELECT
  order_id,
  customer_id,
  order_date,
  amount,
  CAST(amount AS DECIMAL(10, 2)) AS amount_clean,
  _metadata.file_path,
  CURRENT_TIMESTAMP() AS processed_at
FROM live.orders_bronze
WHERE amount > 0
AND order_date IS NOT NULL
```

**Querying Pipeline Event Logs**

```sql
-- Query pipeline execution history
SELECT
  event_id,
  timestamp,
  details:table_name AS table_name,
  details:rows_written AS rows_written,
  details:state AS state,
  details:error_msg AS error_msg
FROM system.pipelines.lineage
WHERE details:pipeline_id = 'your_pipeline_id'
ORDER BY timestamp DESC
LIMIT 10
```

**Python API: APPLY CHANGES (PySpark)**

```python
# In a Lakeflow pipeline notebook using PySpark
from pyspark.sql import functions as F

# Read CDC feed (example: from Delta table)
cdc_df = spark.readStream.option(
    "ignoreChanges", "true"
).table("raw.customers_cdc")

# Write to target with APPLY CHANGES
(cdc_df
  .writeStream
  .option("mergeSchema", "true")
  .mode("append")
  .option("checkpointLocation", "/checkpoints/customers")
  .table("silver.customers")
)
```

---

### Common Exam Scenarios

**Scenario 1: Choosing Between SCD Type 1 and Type 2**

Your organization tracks customer data. The source system sends updates whenever a customer's address or phone number changes. You are building a Lakeflow pipeline to load this data into a silver layer table. You need to support two use cases: (1) a dashboard that shows the current state of all customers, and (2) an audit report showing when each customer's address changed. Which SCD type should you use?

The correct answer is SCD Type 2. Type 2 preserves history, so you can track when address changes occurred and generate audit reports. For the dashboard, you can filter to `__current = true` to get the current state. If you used Type 1, the old address would be overwritten and the audit trail would be lost. Type 1 is fine if you only need the current state.

**Scenario 2: Handling Data Dependency Failures in Multi Notebook Pipelines**

Your pipeline consists of three notebooks: (1) Bronze layer that reads from cloud storage, (2) Silver layer that cleans the bronze data, (3) Gold layer that creates aggregations for reporting. The Silver notebook fails due to a schema mismatch in the source data. What happens to the Gold layer?

The correct answer is the Gold layer does not run. Lakeflow detects the dependency: Gold depends on Silver, which depends on Bronze. When Silver fails, the pipeline stops and does not attempt to run Gold. This prevents cascading errors and corrupt data in downstream tables. You must fix the schema mismatch in the Silver notebook and retry the pipeline.

**Scenario 3: Incremental Processing with APPLY CHANGES**

Your source system sends CDC records to a Delta table at `raw.customer_changes`. Each row has an `operation` column (INSERT, UPDATE, DELETE) and an `event_time` timestamp. You run the Lakeflow pipeline every hour. On the first run, it processes 1,000 changes. On the second run an hour later, there are 800 new changes. How many total rows does the pipeline read from `raw.customer_changes` on the second run?

The correct answer is approximately 800 rows (only the new changes). Lakeflow maintains a checkpoint that tracks the `event_time` of the last processed record. On the second run, it reads only records with `event_time` later than the checkpoint. This incremental approach scales to large datasets. If you needed to reprocess all changes, you could reset the checkpoint, but that is rare.

---

### Key Takeaways

Lakeflow Spark Declarative Pipelines simplify data pipeline creation by letting you declaratively define tables instead of writing orchestration code. The pipeline engine handles dependencies, scheduling, and fault tolerance.

APPLY CHANGES processes CDC feeds from a source table and applies inserts, updates, and deletes to a target table. The KEYS clause specifies the primary key and SEQUENCE BY specifies the ordering column.

Use SCD Type 1 when you only need the current state of data. Use SCD Type 2 when you need to track history and analyze how data has changed over time.

Incremental refresh processes only new data since the last checkpoint, making pipelines efficient for large datasets. Full refresh reprocesses all data and is useful for rebuilds or corrections.

Pipeline event logs provide visibility into runs, row counts, data quality results, and errors. Use them to monitor pipeline health and debug issues.

---

### Gotchas and Tips

**Warning: APPLY CHANGES Requires Ordering**

If your source data does not have a reliable sequence column (timestamp or version), APPLY CHANGES may apply changes in the wrong order, leading to data corruption. Always ensure the SEQUENCE BY column accurately reflects the order in which changes occurred.

**Warning: SCD Type 2 Storage Overhead**

SCD Type 2 tables use additional storage because they keep all historical versions. For tables with frequent updates and long retention, this can become expensive. Monitor table size and consider archiving old versions.

**Warning: Checkpoint Reset Destroys State**

If you manually reset a pipeline checkpoint, the next run will reprocess all data from the beginning. This is rarely needed and can cause duplicates. Only reset checkpoints if you are intentionally rebuilding the table.

---

### Links and Resources

- [**Develop Lakeflow Spark Declarative Pipelines**](https://docs.databricks.com/aws/en/ldp/develop) — Guide to developing and testing pipeline code.
- [**Tutorial: Build an ETL pipeline with Lakeflow**](https://docs.databricks.com/aws/en/getting-started/data-pipeline-get-started) — Hands on walkthrough building a complete data pipeline.
- [**Run pipelines in a workflow**](https://docs.databricks.com/aws/en/ldp/workflows) — How to orchestrate Lakeflow pipelines using Lakeflow Jobs.

---

## 5. DDL and DML Features

### Topic Overview

DDL and DML are the core languages for managing data in Databricks. DDL (Data Definition Language) creates and modifies table structures, while DML (Data Manipulation Language) handles data operations like inserts, updates, and deletes. What makes Databricks special is that Delta Lake extends both with powerful features like time travel, atomic transactions, and upsert operations that aren't available with traditional data warehouses.

For the Associate exam, you need to understand how to create and modify tables, query data at different versions, optimize table performance, and use MERGE for upsert patterns. The exam heavily tests your knowledge of Delta specific capabilities like time travel and OPTIMIZE/VACUUM commands.

These commands are used every day in production data pipelines. Understanding them well means you can build efficient, maintainable data solutions and debug issues when they arise.

---

### Key Concepts

- MERGE INTO: The Upsert Pattern
    
    MERGE INTO combines INSERT, UPDATE, and DELETE into a single atomic operation. You specify a condition to match rows in the target table. When rows match, you can UPDATE them. When they don't match, you can INSERT new rows. You can even DELETE rows that match certain conditions. This is essential for loading slowly changing dimensions and handling incremental updates from source systems.
    
- CREATE OR REPLACE TABLE (CRAS)
    
    CRAS atomically replaces table content while preserving the Delta log and table history. Unlike DROP and recreate, CRAS is atomic (all or nothing) and maintains the table's version history. This is useful for full refresh patterns and batch rebuilds. The table metadata (location, schema) stays the same.
    
- Time Travel: Querying Historical Data
    
    Delta Lake stores a detailed log of every transaction. You can query data as it was at any point in time using VERSION AS OF (by version number) or TIMESTAMP AS OF (by date/time). You can also restore a table to a previous version. This is critical for debugging data issues and recovering from mistakes.
    
- OPTIMIZE: Compacting Files
    
    Each write to a Delta table creates one or more Parquet files. Over time, lots of small files accumulate, slowing down queries. OPTIMIZE rewrites the table into larger files. You can optionally add ZORDER BY to physically order data by specific columns, which improves query performance on those columns. OPTIMIZE is not automatic but should run periodically.
    
- VACUUM: Cleaning Up Old Files
    
    When you delete rows or overwrite partitions, old Parquet files are no longer referenced by the Delta log but still exist on disk. VACUUM removes these orphaned files. The default retention window is 7 days (so you can still time travel). Setting retention too low can break time travel queries. VACUUM reduces storage costs but requires careful planning.
    
- Temporary and Global Temp Views
    
    Temp views are session scoped, meaning they exist only for your current session or notebook run. Global temp views live in the global_temp schema and can be accessed across notebooks running on the same cluster. Neither type creates actual table metadata in the metastore. They're useful for intermediate transformations and data exploration.
    
- DESCRIBE HISTORY: Tracking Table Versions
    
    DESCRIBE HISTORY shows every transaction on a Delta table: version number, timestamp, operation (INSERT, UPDATE, DELETE, MERGE, etc.), user who made the change, and more. This is invaluable for auditing and understanding what happened to your data.
    
- INSERT OVERWRITE vs INSERT INTO
    
    INSERT INTO appends new rows. INSERT OVERWRITE replaces all data in the table (or partitions if specified). For partitioned tables, you can overwrite specific partitions only. INSERT OVERWRITE is useful for periodic batch loads where you know the full dataset for a time period.
    

---

### Code Examples

**MERGE INTO: The Classic Upsert Pattern**

```sql
MERGE INTO customers t
USING new_customers s
ON t.customer_id = s.customer_id
WHEN MATCHED AND s.is_deleted = true THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

This statement handles three cases: if a customer exists and is marked deleted, remove it; if they exist, update their record; if they don't exist, insert them. The * syntax matches all columns automatically.

**Time Travel Queries**

```sql
-- Query data at version 5
SELECT * FROM orders VERSION AS OF 5;

-- Query data from a specific timestamp
SELECT * FROM orders TIMESTAMP AS OF '2025-01-01 10:00:00';

-- Restore table to version 3
RESTORE TABLE orders TO VERSION AS OF 3;
```

These queries let you debug data issues by seeing what the table looked like in the past. RESTORE is useful if you accidentally deleted important data.

**OPTIMIZE and VACUUM**

```sql
-- Compact small files into larger ones
OPTIMIZE sales_data;

-- Optimize and Z-order by region for faster region-based queries
OPTIMIZE sales_data ZORDER BY (region);

-- Remove orphaned files older than 7 days (default)
VACUUM sales_data;

-- Remove files older than 30 days (requires change)
VACUUM sales_data RETAIN 30 DAYS;
```

**CREATE OR REPLACE TABLE (CRAS)**

```sql
-- Rebuild gold table atomically
CREATE OR REPLACE TABLE gold.customer_summary AS
SELECT 
  customer_id,
  COUNT(*) as order_count,
  SUM(amount) as total_spent
FROM silver.orders
GROUP BY customer_id;
```

**Temporary and Global Temp Views**

```sql
-- Create a temp view (session scoped)
CREATE OR REPLACE TEMP VIEW customer_purchases AS
SELECT customer_id, COUNT(*) as purchases
FROM orders
GROUP BY customer_id;

-- Create a global temp view (accessible across notebooks on same cluster)
CREATE OR REPLACE GLOBAL TEMP VIEW recent_orders AS
SELECT * FROM orders
WHERE order_date >= current_date() - 7;

-- Access global temp view
SELECT * FROM global_temp.recent_orders;
```

**DESCRIBE HISTORY**

```sql
-- View table version history
DESCRIBE HISTORY customers;

-- Results show: version, timestamp, user_id, operation, etc.
-- Example row:
-- version=5, timestamp=2025-01-15 14:30:00, operation=MERGE, 
-- user=analyst@company.com
```

---

### Common Exam Scenarios

**Scenario 1: Handling Late Arriving Dimensions**

You're loading customer data daily from an upstream system. Some updates arrive days late (a customer changes their address). You can't use INSERT OVERWRITE because you'd lose rows that arrived early. You need to handle updates to existing customers and inserts for new ones in a single operation. Answer: Use MERGE INTO to match on customer_id. If matched, update all columns. If not matched, insert the new row. This ensures your customers table stays current and handles late arrivals gracefully.

**Scenario 2: Recovering from a Data Pipeline Error**

Yesterday morning at 9 AM your data pipeline ran but had a bug that corrupted the gold orders table. You've already fixed the code, but you need to recover the table to its state before the bad run. You know DESCRIBE HISTORY can show you the version numbers and timestamps. Answer: Query DESCRIBE HISTORY to find the version just before 9 AM. Then use RESTORE TABLE orders TO VERSION AS OF <version_number>. The table is restored atomically and you can safely rerun today's load.

**Scenario 3: Slow Queries on a Large Table**

Your transactions table has grown to billions of rows. Queries that filter by region take longer than expected. You notice the table has many small files (result of 100 daily inserts). Answer: Run OPTIMIZE transactions ZORDER BY (region) to compact files and physically organize data by region. This reduces the number of files Spark has to read and allows Z-order clustering to skip entire files based on the region predicate. Queries improve significantly.

---

### Key Takeaways

- MERGE INTO is the primary upsert pattern in Databricks. It's atomic and handles INSERT, UPDATE, and DELETE in one statement. Master the syntax and when to use each WHEN clause.
- Time travel is a Delta Lake superpower. Query data at any point in time using VERSION AS OF or TIMESTAMP AS OF. Use RESTORE to recover the entire table to a previous state.
- OPTIMIZE and VACUUM are maintenance operations. OPTIMIZE compacts files and improves query performance. VACUUM removes orphaned files and reduces storage. Always understand the retention window before running VACUUM.
- CREATE OR REPLACE TABLE is atomic and preserves table history unlike DROP and recreate. Use it for periodic full rebuilds of summary tables.
- Temporary views are session scoped and useful for intermediate work. Global temp views live in the global_temp schema and work across notebooks on the same cluster.

---

### Gotchas and Tips

<aside> ⚠️ VACUUM breaks time travel. If you VACUUM with a short retention window (like 1 day), you can no longer query old versions or restore beyond that window. Always understand the tradeoff between storage savings and historical data access before running VACUUM.

</aside>

<aside> ⚠️ INSERT INTO is append only, INSERT OVERWRITE replaces. It's easy to mix these up. If you need to reload historical data, use INSERT OVERWRITE on the target partition or table. If you're appending new data, use INSERT INTO.

</aside>

<aside> ⚠️ Temp views don't create metadata. They're only available in your session and don't show up in SHOW TABLES (unless you filter for temp tables). Global temp views persist across notebooks but only for the cluster lifetime. When the cluster terminates, they vanish.

</aside>

---

### Links and Resources

- [**SQL language reference**](https://docs.databricks.com/aws/en/sql/language-manual/) — Complete SQL reference for Databricks including all DDL and DML statements.
- [**Upsert into a Delta Lake table using merge**](https://docs.databricks.com/aws/en/delta/merge) — MERGE INTO syntax, schema evolution, and advanced use cases.
- [**Update table schema**](https://docs.databricks.com/aws/en/delta/update-schema) — How to add, rename, and drop columns using DDL and DML.

---

## 6. PySpark DataFrame Aggregations

### Topic Overview

PySpark DataFrames provide a powerful set of aggregation methods that let you compute summaries across groups of data. Whether you're calculating totals, averages, or ranking records within groups, the aggregation API gives you the tools to express complex analytical queries efficiently. These operations are central to data processing tasks in Databricks, from simple counts to advanced window functions.

The core of PySpark aggregation revolves around groupBy() to partition data and agg() to apply aggregate functions. Understanding when to use built in functions versus window functions versus pivot operations is critical for writing efficient, readable code that passes the exam.

This topic covers the core aggregation API, window functions for ranking and running calculations, pivot tables for reshaping data, and multi dimensional aggregations with cube() and rollup(). You'll see exam questions asking you to choose the right aggregation method for a given scenario.

---

### Key Concepts

- groupBy() and agg() Basics
    
    The groupBy() method returns a GroupedData object that represents rows grouped by one or more columns. You must chain an aggregation function (like agg(), count(), or sum()) to trigger the computation. The agg() method accepts multiple functions at once using column expressions from pyspark.sql.functions. This lets you compute several aggregates in a single pass over the data, which is more efficient than computing them separately.
    
- Window Functions
    
    Window functions compute values over a specified range of rows (a window) without reducing the result set size. Define a window using Window.partitionBy().orderBy() and apply functions like F.row_number(), F.rank(), F.lag(), F.lead(), or even F.sum().over(window). Useful for ranking items within groups, finding top N records, or computing running totals.
    
- pivot() for Data Reshaping
    
    The pivot() method rotates rows into columns. Typically used with groupBy() to transform long format data into wide format. Example: df.groupBy("category").pivot("month").sum("revenue") creates columns for each month with summed revenue values.
    
- cube() and rollup() for OLAP Analysis
    
    Both cube() and rollup() compute aggregates at multiple levels of grouping. rollup() creates subtotals in a hierarchical manner (parent to child). cube() computes aggregates for all possible combinations of columns (more granular but also more expensive). Use rollup() when you need hierarchical totals. Use cube() when you need to analyze across all dimension combinations.
    
- Column Aliasing and Renaming
    
    Use .alias("new_name") to rename aggregation results. This is especially important when using multiple aggregation functions on the same column, as default names become verbose (e.g., sum(revenue) instead of auto generated names). Good naming makes your results readable and your code easier to maintain.
    
- Sorting Aggregated Results
    
    After aggregation, use orderBy() or sort() to order the results. These methods work on the aggregated DataFrame just like on any other DataFrame. Common exam scenarios ask you to find top N values after grouping and aggregating, which usually requires sorting first.
    

---

### Code Examples

#### Basic groupBy with Multiple Aggregations

```python
from pyspark.sql import functions as F

# Group by product category and calculate multiple aggregates
df.groupBy("category").agg(
    F.count("*").alias("total_orders"),
    F.sum("amount").alias("total_revenue"),
    F.avg("amount").alias("avg_order_value"),
    F.min("amount").alias("min_order"),
    F.max("amount").alias("max_order")
).show()
```

#### Window Function for Running Total and Rank

```python
from pyspark.sql.window import Window
from pyspark.sql import functions as F

# Define window partitioned by customer, ordered by date
window_spec = Window.partitionBy("customer_id").orderBy("purchase_date")

df_with_window = df.withColumn(
    "running_total", F.sum("amount").over(window_spec)
).withColumn(
    "purchase_rank", F.rank().over(window_spec)
).withColumn(
    "previous_amount", F.lag("amount", 1).over(window_spec)
).withColumn(
    "next_amount", F.lead("amount", 1).over(window_spec)
)

df_with_window.show()
```

#### Pivot Table Example

```python
# Transform long format data to wide format
# Input: rows with (product, month, revenue)
# Output: columns for each month with revenue as values

pivoted_df = df.groupBy("product").pivot("month").sum("revenue")
pivoted_df.show()

# You can specify the values for the pivot column to limit columns
pivoted_df = df.groupBy("product").pivot("month", ["Jan", "Feb", "Mar"]).sum("revenue")
pivoted_df.show()
```

#### Finding Top N per Group using row_number()

```python
from pyspark.sql.window import Window
from pyspark.sql import functions as F

# Get the top 3 products by revenue within each region
window_spec = Window.partitionBy("region").orderBy(F.desc("revenue"))

top_products = df.withColumn(
    "rank", F.row_number().over(window_spec)
).filter(F.col("rank") <= 3)

top_products.show()

# Note: use row_number() for strict ranking (1,2,3)
# Use rank() for ties (1,1,3) or dense_rank() for ties (1,1,2)
```

#### Equivalent SQL Comparison

```sql
-- PySpark groupBy().agg() equivalent
SELECT 
  category,
  COUNT(*) as total_orders,
  SUM(amount) as total_revenue,
  AVG(amount) as avg_order_value
FROM orders
GROUP BY category;

-- Window function equivalent
SELECT 
  customer_id,
  purchase_date,
  amount,
  SUM(amount) OVER (PARTITION BY customer_id ORDER BY purchase_date) as running_total,
  RANK() OVER (PARTITION BY customer_id ORDER BY purchase_date) as purchase_rank
FROM orders;

-- Pivot equivalent
SELECT *
FROM (
  SELECT product, month, revenue FROM sales
)
PIVOT (
  SUM(revenue) FOR month IN ('Jan', 'Feb', 'Mar')
);
```

---

### Common Exam Scenarios

#### Scenario 1: Counting Distinct Values with Multiple Aggregates

Question: You have an orders table with columns (customer_id, product_id, order_amount, order_date). Your task is to group by product_id and calculate the total revenue, number of distinct customers, and count of orders.

Solution: Use groupBy("product_id") with agg() and apply F.sum("order_amount"), F.countDistinct("customer_id"), and F.count("*"). The key is using countDistinct() to count unique customers, not total orders. Many candidates forget that a regular count() would count all rows, not distinct customers.

#### Scenario 2: Finding Top N Records per Group

Question: You need to find the top 2 highest selling products (by total sales amount) within each region. The data has (region, product, sales_amount).

Solution: First aggregate by region and product using groupBy().agg() to sum sales. Then use a window function with Window.partitionBy("region").orderBy(F.desc("total_sales")) and F.row_number() to rank within each region. Filter where rank <= 2. This is a two step process: aggregate first, then rank. Confusing the order (trying to rank before aggregating) is a common mistake.

#### Scenario 3: Pivoting Data for Cross Tabulation

Question: You have sales data with (salesperson, quarter, amount). You need to reshape it so each quarter becomes a column showing that salesperson's sales for that quarter.

Solution: Use df.groupBy("salesperson").pivot("quarter").sum("amount"). The pivot() method automatically creates columns for each unique value in the quarter column. If you want to control which columns appear (and their order), pass a list: .pivot("quarter", ["Q1", "Q2", "Q3", "Q4"]). Note that pivot operations can be memory intensive with high cardinality columns, which is why specifying values upfront is often recommended.

---

### Key Takeaways

- groupBy() always requires a downstream aggregation function like agg(), count(), or sum(). Forgetting this is a common mistake that will cause your code to not execute.
- Use agg() with multiple functions (F.sum(), F.avg(), F.count(), etc.) to compute several aggregates in a single pass, which is more efficient than chaining multiple groupBy operations.
- Window functions compute over a specified range without reducing row count. They're essential for ranking, running totals, and comparing rows within groups.
- Choose the right ranking function: row_number() gives 1,2,3; rank() gives 1,1,3; dense_rank() gives 1,1,2. Know the difference for exam questions.
- pivot() reshapes data from long to wide format. Always specify the pivot values as a list to control columns and avoid memory issues.

---

### Gotchas and Tips

<aside> ⚠️ Gotcha 1: Forgetting to chain an aggregation function after groupBy(). If you write df.groupBy("category") without calling agg() or count(), the code won't fail but it also won't compute anything. Always follow groupBy() with an aggregation method.

</aside>

<aside> ⚠️ Gotcha 2: Confusing count() with countDistinct(). The count() function counts rows. The countDistinct() function counts unique values. Many candidates use count() when they meant to count distinct customers or products, leading to wrong results.

</aside>

<aside> ⚠️ Gotcha 3: Using pivot() on high cardinality columns. If the pivot column has thousands of unique values, the operation becomes very memory intensive or even fails. Always specify the pivot values explicitly as a list to limit the output columns.

</aside>

---

### Links and Resources

- [**Tutorial: Query and visualize data from a notebook**](https://docs.databricks.com/aws/en/getting-started/quick-start) — Getting started tutorial covering DataFrame operations and visualizations.
- [**Higher-order functions**](https://docs.databricks.com/aws/en/semi-structured/higher-order-functions) — Working with complex data types using TRANSFORM, FILTER, and AGGREGATE.