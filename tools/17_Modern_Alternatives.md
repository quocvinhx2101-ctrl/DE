# 🚀 Modern Orchestration Alternatives

> Dagster, Mage.ai, SQLMesh - Các công cụ orchestration thế hệ mới

---

## 📋 Mục Lục

1. [Overview & Comparison](#-overview--comparison)
2. [Dagster Complete Guide](#-dagster-complete-guide)
3. [Mage.ai Complete Guide](#-mageai-complete-guide)
4. [SQLMesh Complete Guide](#-sqlmesh-complete-guide)
5. [Migration Strategies](#-migration-strategies)

---

## 📊 Overview & Comparison

### Quick Comparison

| Feature | Airflow | Dagster | Mage.ai | SQLMesh |
|---------|---------|---------|---------|---------|
| **Focus** | Task orchestration | Data assets | Data pipelines | SQL transformations |
| **Paradigm** | Task-centric | Asset-centric | Block-based | Model-centric |
| **Learning Curve** | Medium | Medium | Low | Low |
| **UI** | Functional | Excellent | Excellent | Good |
| **Testing** | Manual setup | Built-in | Built-in | Built-in |
| **Price** | Free/Managed | Free/Cloud | Free/Cloud | Free |
| **Best For** | General orchestration | DE teams | ML + DE | SQL-heavy teams |

### When to Choose What

```
Choose AIRFLOW if:
├── Team already knows it well
├── Need 500+ operators ecosystem
├── General workflow orchestration (not just data)
└── Need mature, battle-tested solution

Choose DAGSTER if:
├── Building from scratch
├── Want asset-centric thinking
├── Need excellent testing/observability
└── Multiple environments (dev/staging/prod)

Choose MAGE if:
├── Need fast prototyping
├── Team includes data scientists
├── Want visual pipeline building
└── Streaming + batch in one tool

Choose SQLMESH if:
├── Primarily SQL transformations
├── Want dbt alternative with virtual environments
└── Need column-level lineage
└── Care about CI/CD for SQL
```

---

## 🔷 Dagster Complete Guide

### What is Dagster?

```
Dagster = Data Orchestrator focused on Assets

Core Concepts:
├── Assets: "What" you're producing (tables, models, files)
├── Ops: "How" you produce it (functions)
├── Jobs: Collection of ops to run together
├── Resources: External connections (databases, APIs)
├── Sensors: React to external events
└── Schedules: Time-based triggers
```

### Asset-Centric vs Task-Centric

```python
# AIRFLOW (Task-centric): "Do these things"
with DAG("etl_pipeline"):
    extract = PythonOperator(task_id="extract", ...)
    transform = PythonOperator(task_id="transform", ...)
    load = PythonOperator(task_id="load", ...)
    extract >> transform >> load

# DAGSTER (Asset-centric): "Produce these things"
@asset
def raw_orders(orders_api: OrdersAPI) -> pd.DataFrame:
    """Raw orders from API"""
    return orders_api.fetch_orders()

@asset
def cleaned_orders(raw_orders: pd.DataFrame) -> pd.DataFrame:
    """Cleaned and validated orders"""
    return clean_data(raw_orders)

@asset
def daily_revenue(cleaned_orders: pd.DataFrame) -> pd.DataFrame:
    """Daily revenue aggregation"""
    return cleaned_orders.groupby("date").agg({"revenue": "sum"})
```

### Installation & Setup

```bash
# Install Dagster
pip install dagster dagster-webserver dagster-duckdb dagster-dbt

# Create new project
dagster project scaffold --name my_data_platform

# Project structure
my_data_platform/
├── my_data_platform/
│   ├── __init__.py
│   ├── assets/
│   │   ├── __init__.py
│   │   ├── raw_assets.py
│   │   └── transformed_assets.py
│   ├── resources/
│   │   └── __init__.py
│   ├── jobs/
│   │   └── __init__.py
│   └── definitions.py
├── pyproject.toml
└── setup.py

# Run development server
dagster dev
```

### Defining Assets

```python
# my_data_platform/assets/raw_assets.py
from dagster import asset, AssetIn, DailyPartitionsDefinition
import pandas as pd

# Simple asset
@asset(
    description="Raw orders from API",
    group_name="raw",
    compute_kind="python"
)
def raw_orders(context) -> pd.DataFrame:
    """Fetch orders from Orders API"""
    context.log.info("Fetching orders...")
    df = fetch_from_api("/orders")
    context.log.info(f"Fetched {len(df)} orders")
    return df

# Partitioned asset
@asset(
    partitions_def=DailyPartitionsDefinition(start_date="2024-01-01"),
    group_name="raw"
)
def partitioned_events(context) -> pd.DataFrame:
    """Daily events partitioned by date"""
    partition_date = context.asset_partition_key_for_output()
    return fetch_events_for_date(partition_date)

# Asset with dependencies
@asset(
    ins={"orders": AssetIn("raw_orders")},
    group_name="staging"
)
def stg_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """Cleaned orders with validation"""
    df = orders.copy()
    df = df.dropna(subset=["order_id", "customer_id"])
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df
```

### Resources (Connections)

```python
# my_data_platform/resources/__init__.py
from dagster import ConfigurableResource
from dagster_duckdb import DuckDBResource
import snowflake.connector

class SnowflakeResource(ConfigurableResource):
    account: str
    user: str
    password: str
    warehouse: str
    database: str
    
    def get_connection(self):
        return snowflake.connector.connect(
            account=self.account,
            user=self.user,
            password=self.password,
            warehouse=self.warehouse,
            database=self.database
        )

# Usage in assets
@asset
def snowflake_table(snowflake: SnowflakeResource) -> None:
    conn = snowflake.get_connection()
    # Use connection...
```

### Testing in Dagster

```python
# tests/test_assets.py
from dagster import materialize
from my_data_platform.assets import raw_orders, stg_orders

def test_stg_orders():
    """Test staging orders transformation"""
    # Create test input
    test_orders = pd.DataFrame({
        "order_id": [1, 2, None],
        "customer_id": [100, 200, 300],
        "order_date": ["2024-01-01", "2024-01-02", "2024-01-03"]
    })
    
    # Run asset
    result = materialize(
        assets=[stg_orders],
        input_values={"raw_orders": test_orders}
    )
    
    # Assert
    assert result.success
    output_df = result.output_for_node("stg_orders")
    assert len(output_df) == 2  # Null order_id removed
    assert output_df["order_date"].dtype == "datetime64[ns]"
```

### Dagster + dbt Integration

```python
from dagster_dbt import DbtCliResource, dbt_assets

# Point to dbt project
dbt_project_dir = Path(__file__).parent / "dbt_project"

@dbt_assets(manifest=dbt_project_dir / "target" / "manifest.json")
def my_dbt_assets(context, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

# In definitions.py
defs = Definitions(
    assets=[*my_dbt_assets],
    resources={
        "dbt": DbtCliResource(project_dir=dbt_project_dir)
    }
)
```

---

## 🧙 Mage.ai Complete Guide

### What is Mage?

```
Mage = Hybrid notebook + pipeline tool

Key Features:
├── Block-based pipelines (visual + code)
├── Real-time + batch in one tool
├── Built-in data profiling
├── Easy ML integration
├── Streaming support
└── Beautiful UI
```

### Installation & Setup

```bash
# Install Mage
pip install mage-ai

# Create new project
mage init my_mage_project

# Start development server
cd my_mage_project
mage start

# Access UI at http://localhost:6789

# Project structure
my_mage_project/
├── pipelines/
│   └── example_pipeline/
│       ├── __init__.py
│       ├── metadata.yaml
│       └── transformers/
├── data_loaders/
├── data_exporters/
├── transformers/
├── io_config.yaml
└── metadata.yaml
```

### Building Pipelines

```python
# data_loaders/load_orders.py
from mage_ai.io.file import FileIO
import pandas as pd

if 'data_loader' not in dir():
    from mage_ai.data_preparation.decorators import data_loader

@data_loader
def load_orders(*args, **kwargs) -> pd.DataFrame:
    """
    Load orders from CSV file
    """
    return pd.read_csv('s3://bucket/orders.csv')

# transformers/clean_orders.py
if 'transformer' not in dir():
    from mage_ai.data_preparation.decorators import transformer

@transformer
def clean_orders(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """
    Clean and validate orders data
    
    Args:
        df: Raw orders DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    # Remove nulls
    df = df.dropna(subset=['order_id', 'customer_id'])
    
    # Validate dates
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Add computed columns
    df['order_year'] = df['order_date'].dt.year
    
    return df

# data_exporters/export_to_warehouse.py
from mage_ai.io.snowflake import Snowflake

if 'data_exporter' not in dir():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_to_snowflake(df: pd.DataFrame, *args, **kwargs) -> None:
    """
    Export to Snowflake warehouse
    """
    config = kwargs['configuration']
    
    with Snowflake.with_config(config) as loader:
        loader.export(
            df,
            schema='staging',
            table_name='orders',
            if_exists='replace'
        )
```

### Streaming Pipelines

```python
# Mage supports streaming natively
# pipelines/streaming_pipeline/

# data_loaders/kafka_consumer.py
from mage_ai.streaming.sources.kafka import KafkaSource

@data_loader
def load_from_kafka(*args, **kwargs) -> dict:
    """
    Consume messages from Kafka topic
    """
    source = KafkaSource(
        topic='events',
        bootstrap_servers='localhost:9092',
        consumer_group='mage-consumer'
    )
    
    for message in source.batch_read():
        yield message

# transformers/process_event.py
@transformer
def process_event(message: dict, *args, **kwargs) -> dict:
    """
    Process individual event
    """
    event = message['value']
    
    # Enrich event
    event['processed_at'] = datetime.now().isoformat()
    event['event_hour'] = parse_timestamp(event['timestamp']).hour
    
    return event

# data_exporters/sink_to_redis.py
@data_exporter
def sink_to_redis(event: dict, *args, **kwargs) -> None:
    """
    Sink processed events to Redis
    """
    redis_client.hset(
        f"event:{event['event_id']}",
        mapping=event
    )
```

### Mage CLI Commands

```bash
# Run pipeline
mage run my_project pipeline_name

# Test pipeline
mage test my_project pipeline_name

# Deploy to cloud
mage deploy

# Sync with dbt
mage integrate dbt --project-path ./dbt_project
```

---

## 🔧 SQLMesh Complete Guide

### What is SQLMesh?

```
SQLMesh = Modern dbt alternative

Key Innovations:
├── Virtual Data Environments (instant branch testing)
├── Smart change detection (only run what changed)
├── Built-in CI/CD
├── Column-level lineage
├── Python + SQL mixed models
└── Plan-Apply workflow
```

### Installation & Setup

```bash
# Install SQLMesh
pip install sqlmesh

# Initialize project
sqlmesh init my_project --sql-dialect snowflake

# Project structure
my_project/
├── config.yaml
├── models/
│   ├── staging/
│   │   └── stg_orders.sql
│   └── marts/
│       └── daily_revenue.sql
├── macros/
├── tests/
└── seeds/

# Start UI
sqlmesh ui
```

### Configuration

```yaml
# config.yaml
gateways:
  local:
    connection:
      type: duckdb
      database: db.duckdb
  
  prod:
    connection:
      type: snowflake
      account: xy12345
      user: ${SNOWFLAKE_USER}
      password: ${SNOWFLAKE_PASSWORD}
      warehouse: analytics_wh
      database: analytics

default_gateway: local

model_defaults:
  dialect: snowflake
  start: 2024-01-01
```

### Writing Models

```sql
-- models/staging/stg_orders.sql
MODEL (
    name staging.stg_orders,
    kind INCREMENTAL_BY_TIME_RANGE (
        time_column order_date
    ),
    cron '@daily',
    grain order_id
);

SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    status,
    @execution_time AS loaded_at
FROM raw.orders
WHERE order_date BETWEEN @start_date AND @end_date;

-- models/marts/daily_revenue.sql
MODEL (
    name marts.daily_revenue,
    kind FULL,
    cron '@daily',
    grain (order_date)
);

SELECT
    order_date,
    COUNT(DISTINCT order_id) AS order_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_order_value
FROM staging.stg_orders
WHERE status = 'completed'
GROUP BY order_date;
```

### Virtual Data Environments

```bash
# Create virtual environment (instant, no data copy!)
sqlmesh plan dev

# This shows:
# 1. What will change
# 2. Which tables affected
# 3. Preview of changes

# Apply to dev environment
sqlmesh apply dev

# Test in dev (queries use virtual layer)
sqlmesh fetchdf "SELECT * FROM dev.marts.daily_revenue LIMIT 10"

# Promote to prod
sqlmesh plan prod
sqlmesh apply prod
```

### Python Models

```python
# models/ml/customer_features.py
import typing as t
from sqlmesh import model
import pandas as pd

@model(
    "ml.customer_features",
    kind="full",
    columns={
        "customer_id": "INT",
        "lifetime_value": "DECIMAL(18,2)",
        "order_frequency": "DECIMAL(10,4)",
        "last_order_days_ago": "INT"
    }
)
def execute(
    context,
    start_date: t.Optional[str] = None,
    end_date: t.Optional[str] = None
) -> pd.DataFrame:
    """
    Calculate customer features for ML models
    """
    orders_df = context.fetchdf("""
        SELECT customer_id, order_date, amount
        FROM staging.stg_orders
    """)
    
    features = orders_df.groupby('customer_id').agg({
        'amount': 'sum',
        'order_date': ['count', 'max']
    })
    
    features.columns = ['lifetime_value', 'order_frequency', 'last_order_date']
    features['last_order_days_ago'] = (
        pd.Timestamp.now() - features['last_order_date']
    ).dt.days
    
    return features.reset_index()
```

### SQLMesh CLI Commands

```bash
# Plan changes (show what will happen)
sqlmesh plan

# Apply changes
sqlmesh apply

# Run specific model
sqlmesh run --model marts.daily_revenue

# Generate lineage
sqlmesh lineage marts.daily_revenue

# Diff two environments
sqlmesh diff prod dev

# Run tests
sqlmesh test

# Create table diff report
sqlmesh table_diff staging.stg_orders staging.stg_orders --on order_id
```

---

## 🔄 Migration Strategies

### Airflow → Dagster

```python
# Step 1: Keep Airflow running
# Step 2: Build new assets in Dagster
# Step 3: Run both in parallel
# Step 4: Gradually move workloads
# Step 5: Decommission Airflow

# Mapping concepts:
# Airflow DAG         → Dagster Job
# Airflow Task        → Dagster Op/Asset
# Airflow Connection  → Dagster Resource
# Airflow Variable    → Dagster Config
# Airflow XCom        → Dagster IO Manager
```

### dbt → SQLMesh

```bash
# SQLMesh can import dbt projects directly!
sqlmesh init --dbt-path ./dbt_project

# This creates:
# 1. config.yaml from dbt profiles
# 2. Models migrated (SQL compatible)
# 3. Tests migrated
# 4. Seeds migrated

# Run with dbt compatibility
sqlmesh plan --enable-dbt-compatible-mode
```

### Gradual Migration Pattern

```
Week 1-2: Pilot
├── Choose 1 simple pipeline
├── Rebuild in new tool
├── Run in parallel
└── Compare results

Week 3-4: Validate
├── Run both for 2 weeks
├── Compare outputs
├── Fix discrepancies
└── Document learnings

Week 5-8: Migrate
├── Move pipelines batch by batch
├── Start with less critical
├── Keep rollback option
└── Update documentation

Week 9+: Cleanup
├── Decommission old tool
├── Train team
├── Optimize new setup
└── Document best practices
```

---

## 🔗 Liên Kết

- [Apache Airflow Guide](08_Apache_Airflow_Complete_Guide.md)
- [Prefect & Dagster](09_Prefect_Dagster_Complete_Guide.md)
- [dbt Complete Guide](07_dbt_Complete_Guide.md)
- [Data Quality Tools](10_Data_Quality_Tools_Guide.md)

---

*Cập nhật: February 2026*
