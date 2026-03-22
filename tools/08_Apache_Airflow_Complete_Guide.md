# 🌊 Apache Airflow - Complete Guide

> **"Programmatically Author, Schedule and Monitor Workflows"**

---

## 📑 Mục Lục

1. [Giới Thiệu & Lịch Sử](#-giới-thiệu--lịch-sử)
2. [Kiến Trúc Chi Tiết](#-kiến-trúc-chi-tiết)
3. [Core Concepts](#-core-concepts)
4. [DAGs & Operators](#-dags--operators)
5. [TaskFlow API](#-taskflow-api)
6. [Advanced Features](#-advanced-features)
7. [Hands-on Code Examples](#-hands-on-code-examples)
8. [Use Cases Thực Tế](#-use-cases-thực-tế)
9. [Best Practices](#-best-practices)
10. [Production Operations](#-production-operations)

---

## 🌟 Giới Thiệu & Lịch Sử

### Airflow là gì?

Apache Airflow là một **workflow orchestration platform** cho phép programmatically define, schedule, và monitor complex data pipelines. Airflow sử dụng DAGs (Directed Acyclic Graphs) để represent workflows và Python để define chúng.

### Lịch Sử Phát Triển

**2014** - Created tại Airbnb bởi Maxime Beauchemin
- Giải quyết complexity của data pipelines tại Airbnb
- Alternative cho cron jobs

**2015** - Open-sourced by Airbnb

**2016** - Joined Apache Incubator

**2019** - Graduated thành Apache Top-Level Project

**2020** - Airflow 2.0 released
- TaskFlow API
- Full REST API
- Smart Sensors
- Improved UI

**2021** - Airflow 2.1-2.2
- Better Kubernetes support
- XCom improvements

**2022** - Airflow 2.3-2.4
- Grid view
- Dynamic task mapping

**2023** - Airflow 2.5-2.7
- Dataset-driven scheduling
- Object Storage support
- Better observability

**2024** - Airflow 2.8-2.9
- Edge Labels
- Improved UI
- Better Dataset support

**2025** - Airflow 3.1.0 (December)
- AIP-72: Task Execution Interface redesign
- Improved Asset/Dataset features
- Better Kubernetes Executor
- Native Iceberg integration
- Enhanced observability

### Tại sao Airflow thắng?

**vs Cron jobs:**
- Dependency management
- Retry logic
- Monitoring UI
- Alerting
- Backfill support

**vs Luigi:**
- Larger community
- Better UI
- More operators
- Better documentation

**vs Jenkins:**
- Built for data pipelines
- Python-native
- Time-based scheduling
- Data awareness

### Key Statistics

- 15,000+ GitHub stars
- 800+ contributors
- Most popular workflow orchestrator
- Used by: Airbnb, Spotify, Twitter, PayPal, Lyft

---

## 🏗️ Kiến Trúc Chi Tiết

### Component Architecture


```mermaid
flowchart TD
    subgraph ARCH [" "]
        direction TB
        A_TITLE["Airflow Architecture"]
        style A_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        WS["Web Server<br>• Flask-based UI<br>• DAG visualization<br>• Task logs<br>• REST API"]
        MD["Metadata Database<br>(PostgreSQL/MySQL)<br>• DAG definitions<br>• Task states<br>• XComs<br>• Variables, Connections"]
        SCH["Scheduler<br>• Parses DAG files<br>• Determines task dependencies<br>• Queues tasks for execution<br>• Monitors task states"]
        
        subgraph EXC ["Executor"]
            direction LR
            E1["Local<br>Executor<br>(development)"]
            E2["Celery<br>Executor<br>(distributed)"]
            E3["Kubernetes<br>Executor<br>(cloud-native)"]
        end
        
        subgraph WRK ["Workers"]
            direction LR
            W1["Worker 1<br>(tasks)"]
            W2["Worker 2<br>(tasks)"]
            W3["Worker 3<br>(tasks)"]
            WN["Worker N<br>(tasks)"]
        end
        
        WS --> MD
        MD --> SCH
        SCH --> EXC
        EXC --> WRK
    end
```
```

### Executor Types

```
Executor Comparison:
> **Executor Comparison**
> 
> * **LocalExecutor**
>   * Single machine
>   * Multiple processes
>   * Good for: Development, small workloads
> 
> * **CeleryExecutor**
>   * Distributed workers
>   * Redis/RabbitMQ as broker
>   * Good for: Horizontal scaling, production
> 
> * **KubernetesExecutor**
>   * Each task = one Pod
>   * Dynamic resource allocation
>   * Good for: Cloud-native, variable workloads
> 
> * **CeleryKubernetesExecutor**
>   * Hybrid: Celery for fast tasks
>   * Kubernetes for heavy tasks
>   * Good for: Mixed workloads


### DAG File Processing

DAG Parsing Flow:
```mermaid
flowchart TD
    subgraph PARSE [" "]
        direction TB
        P_TITLE["DAG Parsing Flow"]
        style P_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        P1["1. DAG files in dags/ folder<br>my_dag.py, another_dag.py, utils/"]
        P2["2. Scheduler parses files every N seconds<br>(dag_dir_list_interval)"]
        P3["3. DagBag created with all DAG objects"]
        P4["4. Metadata stored in database<br>• DAG structure<br>• Task dependencies<br>• Schedule"]
        P5["5. Scheduler creates DagRuns based on schedule"]
        
        P1 --> P2 --> P3 --> P4 --> P5
    end
```


---

## 📚 Core Concepts

### 1. DAG (Directed Acyclic Graph)

```python
from airflow import DAG
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['team@company.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='my_etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline',
    schedule_interval='0 6 * * *',  # 6 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'production'],
    max_active_runs=1,
)
```

### 2. Task States


Task Lifecycle:
```mermaid
flowchart LR
    subgraph LIFE [" "]
        direction TB
        L_TITLE["Task Lifecycle"]
        style L_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        subgraph FLOW [" "]
            direction LR
            N["none"] --> S["scheduled"] --> Q["queued"] --> R["running"] --> SU["success"]
            
            R --> F["failed"] --> U["up_for_retry"] --> RE["retry"]
            Q --> RM["removed"]
            S --> UF["upstream_failed"]
            S --> SK["skipped"]
        end
        
        COLORS["State Colors in UI:<br>• Green: Success<br>• Red: Failed<br>• Yellow: Running<br>• Orange: Up for retry<br>• Pink: Skipped<br>• Light green: Queued"]
        style COLORS fill:none,stroke:none,text-align:left
        
        FLOW ~~~ COLORS
    end
```


### 3. XCom (Cross-Communication)

```python
# Push XCom
def push_data(**context):
    data = {'key': 'value', 'count': 100}
    context['ti'].xcom_push(key='my_data', value=data)
    # Or return directly (auto-pushed as 'return_value')
    return data

# Pull XCom
def pull_data(**context):
    data = context['ti'].xcom_pull(
        task_ids='push_task',
        key='my_data'
    )
    print(f"Received: {data}")
```

### 4. Variables & Connections

```python
from airflow.models import Variable
from airflow.hooks.base import BaseHook

# Variables (key-value store)
api_key = Variable.get("api_key")
config = Variable.get("config", deserialize_json=True)

# Connections (database, API credentials)
conn = BaseHook.get_connection("my_postgres")
print(f"Host: {conn.host}, Port: {conn.port}")
```

### 5. Sensors

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.sensors.sql import SqlSensor

# Wait for file
file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input.csv',
    poke_interval=60,
    timeout=3600,
    mode='poke',  # or 'reschedule'
)

# Wait for another DAG
external_sensor = ExternalTaskSensor(
    task_id='wait_for_upstream',
    external_dag_id='upstream_dag',
    external_task_id='final_task',
    timeout=7200,
)

# Wait for data in table
sql_sensor = SqlSensor(
    task_id='wait_for_data',
    conn_id='postgres_conn',
    sql="SELECT COUNT(*) FROM orders WHERE date = '{{ ds }}'",
    success=lambda rows: rows[0][0] > 0,
)
```

---

## 🔧 DAGs & Operators

### Common Operators

**Python Operator:**
```python
from airflow.operators.python import PythonOperator

def my_function(param1, **context):
    execution_date = context['ds']
    print(f"Running for {execution_date} with {param1}")
    return "success"

python_task = PythonOperator(
    task_id='python_task',
    python_callable=my_function,
    op_kwargs={'param1': 'value1'},
    dag=dag,
)
```

**Bash Operator:**
```python
from airflow.operators.bash import BashOperator

bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Date: {{ ds }}" && ./run_script.sh {{ params.input }}',
    params={'input': '/data/file.csv'},
    dag=dag,
)
```

**SQL Operators:**
```python
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator

postgres_task = PostgresOperator(
    task_id='run_query',
    postgres_conn_id='postgres_default',
    sql="""
        INSERT INTO summary
        SELECT date, COUNT(*) 
        FROM events 
        WHERE date = '{{ ds }}'
        GROUP BY date
    """,
)

snowflake_task = SnowflakeOperator(
    task_id='snowflake_query',
    snowflake_conn_id='snowflake_default',
    sql='queries/transform.sql',  # from sql/ folder
)
```

**Branch Operator:**
```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    if context['ds_nodash'][-2:] == '01':  # First of month
        return 'monthly_task'
    return 'daily_task'

branch_task = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_branch,
)
```

### Task Dependencies

```python
# Using >> and <<
task1 >> task2 >> task3
task1 >> [task2, task3] >> task4
[task1, task2] >> task3

# Using set_upstream/set_downstream
task2.set_upstream(task1)
task3.set_downstream(task4)

# Chain helper
from airflow.models.baseoperator import chain
chain(task1, task2, task3, task4)

# Cross dependencies
from airflow.models.baseoperator import cross_downstream
cross_downstream([task1, task2], [task3, task4])
# Creates: task1 >> task3, task1 >> task4, task2 >> task3, task2 >> task4
```

---

## 🎯 TaskFlow API

### Basic TaskFlow (Airflow 2.0+)

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='taskflow_etl',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['taskflow'],
)
def taskflow_etl():
    
    @task()
    def extract():
        """Extract data from source"""
        data = {"users": 100, "orders": 500}
        return data
    
    @task()
    def transform(data: dict):
        """Transform data"""
        transformed = {
            "total_users": data["users"],
            "total_orders": data["orders"],
            "avg_orders_per_user": data["orders"] / data["users"]
        }
        return transformed
    
    @task()
    def load(data: dict):
        """Load data to destination"""
        print(f"Loading: {data}")
    
    # Define dependencies through function calls
    extracted = extract()
    transformed = transform(extracted)
    load(transformed)

# Instantiate DAG
taskflow_etl_dag = taskflow_etl()
```

### Dynamic Task Mapping

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='dynamic_tasks',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
def dynamic_task_example():
    
    @task()
    def get_partitions():
        """Return list of partitions to process"""
        return ['partition_1', 'partition_2', 'partition_3', 'partition_4']
    
    @task()
    def process_partition(partition: str):
        """Process each partition"""
        print(f"Processing {partition}")
        return f"Processed {partition}"
    
    @task()
    def aggregate(results: list):
        """Aggregate all results"""
        print(f"Aggregating {len(results)} results")
        return results
    
    # Dynamic task mapping - creates N parallel tasks
    partitions = get_partitions()
    processed = process_partition.expand(partition=partitions)
    aggregate(processed)

dynamic_dag = dynamic_task_example()
```

### Mixing TaskFlow with Traditional Operators

```python
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

@dag(
    dag_id='mixed_dag',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
def mixed_pipeline():
    
    # Traditional operator
    download = BashOperator(
        task_id='download_data',
        bash_command='wget https://example.com/data.csv -O /tmp/data.csv',
    )
    
    @task()
    def validate_data():
        import pandas as pd
        df = pd.read_csv('/tmp/data.csv')
        if len(df) == 0:
            raise ValueError("Empty dataset!")
        return len(df)
    
    # SQL operator
    load_sql = PostgresOperator(
        task_id='load_to_postgres',
        postgres_conn_id='postgres_default',
        sql="""
            COPY staging.data FROM '/tmp/data.csv' CSV HEADER;
        """,
    )
    
    @task()
    def notify(row_count: int):
        print(f"Pipeline completed with {row_count} rows")
    
    # Define flow
    validated = validate_data()
    download >> validated >> load_sql
    notify(validated)

mixed_pipeline_dag = mixed_pipeline()
```

---

## 🚀 Advanced Features

### Datasets (Data-Aware Scheduling)

```python
from airflow import Dataset
from airflow.decorators import dag, task
from datetime import datetime

# Define datasets
orders_dataset = Dataset("s3://bucket/orders/")
customers_dataset = Dataset("s3://bucket/customers/")

# Producer DAG
@dag(
    dag_id='producer_dag',
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
)
def producer():
    
    @task(outlets=[orders_dataset])
    def produce_orders():
        # Write data to S3
        print("Producing orders data")
    
    produce_orders()

# Consumer DAG - triggered when datasets are updated
@dag(
    dag_id='consumer_dag',
    schedule=[orders_dataset, customers_dataset],  # Triggered when BOTH updated
    start_date=datetime(2024, 1, 1),
)
def consumer():
    
    @task()
    def process_data():
        print("Processing orders and customers")
    
    process_data()

producer_dag = producer()
consumer_dag = consumer()
```

### Task Groups

```python
from airflow.decorators import dag, task, task_group
from datetime import datetime

@dag(dag_id='task_groups_example', schedule_interval='@daily', start_date=datetime(2024, 1, 1))
def task_groups_dag():
    
    @task_group(group_id='extract_group')
    def extract():
        @task()
        def extract_orders():
            return "orders"
        
        @task()
        def extract_customers():
            return "customers"
        
        return extract_orders(), extract_customers()
    
    @task_group(group_id='transform_group')
    def transform(orders, customers):
        @task()
        def transform_orders(data):
            return f"transformed_{data}"
        
        @task()
        def transform_customers(data):
            return f"transformed_{data}"
        
        return transform_orders(orders), transform_customers(customers)
    
    @task()
    def load(transformed_data):
        print(f"Loading: {transformed_data}")
    
    extracted = extract()
    transformed = transform(*extracted)
    load(transformed)

task_groups_dag()
```

### Custom Operators

```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class MyCustomOperator(BaseOperator):
    
    template_fields = ('query', 'params')
    
    @apply_defaults
    def __init__(
        self,
        query: str,
        params: dict = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.query = query
        self.params = params or {}
    
    def execute(self, context):
        self.log.info(f"Executing query: {self.query}")
        self.log.info(f"With params: {self.params}")
        
        # Your custom logic here
        result = self._run_query()
        
        # Push to XCom
        context['ti'].xcom_push(key='result', value=result)
        
        return result
    
    def _run_query(self):
        # Custom implementation
        return {"status": "success"}
```

### Callbacks & SLA

```python
from airflow.decorators import dag, task
from datetime import datetime, timedelta

def on_success_callback(context):
    """Called when task succeeds"""
    ti = context['ti']
    print(f"Task {ti.task_id} succeeded!")

def on_failure_callback(context):
    """Called when task fails"""
    ti = context['ti']
    exception = context.get('exception')
    # Send alert, create ticket, etc.
    print(f"Task {ti.task_id} failed: {exception}")

def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """Called when SLA is missed"""
    print(f"SLA missed for tasks: {task_list}")

@dag(
    dag_id='callbacks_example',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    default_args={
        'on_success_callback': on_success_callback,
        'on_failure_callback': on_failure_callback,
        'sla': timedelta(hours=2),
    },
    sla_miss_callback=sla_miss_callback,
)
def callbacks_dag():
    
    @task()
    def important_task():
        # Task that must complete within SLA
        pass
    
    important_task()

callbacks_dag()
```

---

## 💻 Hands-on Code Examples

### Complete ETL Pipeline

```python
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta
import pandas as pd
import json

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['data-team@company.com'],
}

@dag(
    dag_id='etl_orders_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline for orders',
    schedule_interval='0 6 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'orders', 'production'],
    max_active_runs=1,
)
def etl_orders_pipeline():
    
    @task()
    def extract_from_postgres(ds: str) -> dict:
        """Extract orders from source database"""
        hook = PostgresHook(postgres_conn_id='source_postgres')
        
        query = f"""
            SELECT order_id, customer_id, product_id, 
                   quantity, unit_price, order_date
            FROM orders
            WHERE order_date = '{ds}'
        """
        
        df = hook.get_pandas_df(query)
        
        # Return as JSON for XCom
        return {
            'data': df.to_json(),
            'row_count': len(df)
        }
    
    @task()
    def transform_orders(extracted: dict) -> dict:
        """Apply business transformations"""
        df = pd.read_json(extracted['data'])
        
        # Business logic
        df['total_amount'] = df['quantity'] * df['unit_price']
        df['order_category'] = df['total_amount'].apply(
            lambda x: 'large' if x > 1000 else 'medium' if x > 100 else 'small'
        )
        
        # Data quality checks
        if df['total_amount'].isna().any():
            raise ValueError("Null values found in total_amount")
        
        return {
            'data': df.to_json(),
            'row_count': len(df),
            'total_revenue': float(df['total_amount'].sum())
        }
    
    @task()
    def load_to_warehouse(transformed: dict, ds: str):
        """Load to data warehouse"""
        df = pd.read_json(transformed['data'])
        
        hook = PostgresHook(postgres_conn_id='warehouse_postgres')
        engine = hook.get_sqlalchemy_engine()
        
        # Upsert logic
        df.to_sql(
            name='fct_orders',
            con=engine,
            schema='analytics',
            if_exists='append',
            index=False,
            method='multi'
        )
        
        return transformed['row_count']
    
    @task()
    def write_to_s3(transformed: dict, ds: str):
        """Archive to S3"""
        s3_hook = S3Hook(aws_conn_id='aws_default')
        
        key = f"orders/date={ds}/orders.json"
        s3_hook.load_string(
            string_data=transformed['data'],
            key=key,
            bucket_name='data-lake-bucket',
            replace=True
        )
        
        return key
    
    @task()
    def send_notification(row_count: int, s3_path: str, ds: str):
        """Send completion notification"""
        message = f"""
        ETL Pipeline Completed for {ds}
        - Rows processed: {row_count}
        - S3 path: {s3_path}
        """
        print(message)
        # Could send to Slack, email, etc.
    
    # Define DAG flow
    extracted = extract_from_postgres()
    transformed = transform_orders(extracted)
    loaded_count = load_to_warehouse(transformed)
    s3_path = write_to_s3(transformed)
    send_notification(loaded_count, s3_path)

# Instantiate DAG
etl_orders_dag = etl_orders_pipeline()
```

### dbt Integration

```python
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from datetime import datetime

@dag(
    dag_id='dbt_pipeline',
    schedule_interval='0 7 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
def dbt_pipeline():
    
    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command='cd /opt/dbt && dbt deps',
    )
    
    dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command='cd /opt/dbt && dbt seed --target prod',
    )
    
    dbt_run_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command='cd /opt/dbt && dbt run --target prod --select staging',
    )
    
    dbt_run_marts = BashOperator(
        task_id='dbt_run_marts',
        bash_command='cd /opt/dbt && dbt run --target prod --select marts',
    )
    
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/dbt && dbt test --target prod',
    )
    
    dbt_docs = BashOperator(
        task_id='dbt_docs',
        bash_command='cd /opt/dbt && dbt docs generate --target prod',
    )
    
    dbt_deps >> dbt_seed >> dbt_run_staging >> dbt_run_marts >> dbt_test >> dbt_docs

dbt_pipeline_dag = dbt_pipeline()
```

### Spark Job Orchestration

```python
from airflow.decorators import dag, task
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from datetime import datetime

@dag(
    dag_id='spark_etl',
    schedule_interval='0 */2 * * *',  # Every 2 hours
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
def spark_etl_pipeline():
    
    # Wait for data
    wait_for_data = S3KeySensor(
        task_id='wait_for_data',
        bucket_name='raw-data-bucket',
        bucket_key='events/{{ ds }}/*.parquet',
        wildcard_match=True,
        timeout=3600,
        poke_interval=60,
    )
    
    # Run Spark job
    spark_job = SparkSubmitOperator(
        task_id='spark_transform',
        application='/opt/spark-jobs/transform.py',
        conn_id='spark_default',
        conf={
            'spark.executor.memory': '4g',
            'spark.executor.cores': '2',
            'spark.executor.instances': '10',
        },
        application_args=['--date', '{{ ds }}'],
    )
    
    @task()
    def validate_output(ds: str):
        """Validate Spark job output"""
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        
        s3 = S3Hook(aws_conn_id='aws_default')
        keys = s3.list_keys(
            bucket_name='processed-data-bucket',
            prefix=f'events/date={ds}/'
        )
        
        if not keys:
            raise ValueError(f"No output files for {ds}")
        
        return len(keys)
    
    wait_for_data >> spark_job >> validate_output()

spark_dag = spark_etl_pipeline()
```

---

## 🎯 Use Cases Thực Tế

### 1. Data Warehouse ETL


```mermaid
flowchart LR
    subgraph DWH [" "]
        direction TB
        D_TITLE["Typical DWH ETL Pipeline"]
        style D_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        SRC["Sources"] --> STG["Staging"] --> DW["Data Warehouse"]
        
        subgraph DAG ["Airflow DAG"]
            direction LR
            T1["Extract<br>Tasks"] --> T2["Stage<br>Tables"] --> T3["Transform<br>(dbt)"] --> T4["Load<br>Marts"] --> T5["Quality<br>Tests"]
        end
        
        META["Schedule: Daily at 6 AM<br>Dependencies: Wait for source data freshness<br>Alerting: Slack on failure"]
        style META fill:none,stroke:none,text-align:left
        
        SRC ~~~ DAG
        DAG ~~~ META
    end
```


### 2. ML Pipeline Orchestration


```mermaid
flowchart TD
    subgraph ML [" "]
        direction TB
        M_TITLE["ML Training Pipeline"]
        style M_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        subgraph DAG ["Weekly DAG"]
            direction LR
            T1["Extract<br>Data"] --> T2["Feature<br>Eng"] --> T3["Train<br>Model"] --> T4["Evaluate<br>Model"]
            
            T4 --> C["Compare<br>with<br>Production"]
            
            C --> D1["Deploy<br>(if better)"]
            C --> D2["Rollback<br>(if worse)"]
            C --> D3["Alert<br>Team"]
        end
    end
```


### 3. Real-time + Batch Hybrid


```mermaid
flowchart TD
    subgraph HYB [" "]
        direction TB
        H_TITLE["Hybrid Processing Pipeline"]
        style H_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        RT["Real-time (Kafka + Flink):<br>Events ──► Kafka ──► Flink ──► Real-time Views"]
        style RT fill:none,stroke:none,text-align:left
        
        subgraph BATCH ["Batch (Airflow orchestrated): Daily Reconciliation DAG"]
            direction LR
            T1["Compact<br>Events"] --> T2["Reconcile<br>Counts"] --> T3["Update<br>Historical<br>View"]
        end
        
        RT ~~~ BATCH
    end
```


---

## ✅ Best Practices

### 1. DAG Design

```python
# ✅ GOOD: Idempotent tasks
@task()
def load_data(ds: str):
    # Delete then insert - same result on re-run
    hook.run(f"DELETE FROM table WHERE date = '{ds}'")
    hook.run(f"INSERT INTO table SELECT * FROM staging WHERE date = '{ds}'")

# ❌ BAD: Non-idempotent
@task()
def load_data():
    # Appends on every run - different results
    hook.run("INSERT INTO table SELECT * FROM staging")
```

### 2. Testing

```python
# Test DAG loading
def test_dag_loading():
    from airflow.models import DagBag
    dag_bag = DagBag(dag_folder='dags/', include_examples=False)
    assert len(dag_bag.import_errors) == 0
    assert 'my_dag' in dag_bag.dags

# Test task logic
def test_transform_function():
    input_data = {'orders': [1, 2, 3]}
    result = transform_orders(input_data)
    assert 'total_count' in result
```

### 3. Performance

```python
# ✅ Avoid heavy imports at top level
@task()
def process_data():
    import pandas as pd  # Import inside task
    import heavy_library
    # ...

# ✅ Use pool to limit concurrency
@task(pool='limited_resource_pool')
def heavy_task():
    pass

# ✅ Use priority_weight for important tasks
@task(priority_weight=10)
def critical_task():
    pass
```

### 4. Configuration

```python
# ✅ Use Variables for dynamic config
api_endpoint = Variable.get("api_endpoint")

# ✅ Use Connections for credentials (not hardcoded)
hook = PostgresHook(postgres_conn_id='my_postgres')

# ✅ Use Jinja templating for dates
sql = "SELECT * FROM table WHERE date = '{{ ds }}'"
```

---

## 🏭 Production Operations

### Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'

x-airflow-common: &airflow-common
  image: apache/airflow:2.8.0
  environment:
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
  depends_on:
    - postgres
    - redis

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data

  redis:
    image: redis:latest

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - 8080:8080

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler

  airflow-worker:
    <<: *airflow-common
    command: celery worker

volumes:
  postgres-db-volume:
```

### Kubernetes (Helm)

```yaml
# values.yaml
executor: KubernetesExecutor

airflow:
  image:
    repository: apache/airflow
    tag: 2.8.0

postgresql:
  enabled: true

redis:
  enabled: false  # Not needed for K8s executor

dags:
  gitSync:
    enabled: true
    repo: git@github.com:company/airflow-dags.git
    branch: main
    wait: 60

workers:
  resources:
    limits:
      cpu: 2
      memory: 4Gi
```

### Monitoring

```
Key Metrics:
• DAG parse time
• Task duration
• Task failures
• Pool slot usage
• Scheduler loop duration
• Database connections

Recommended Stack:
• StatsD for metrics
• Prometheus + Grafana for dashboards
• PagerDuty/OpsGenie for alerting
```

---

## 📚 Resources

### Official
- Apache Airflow: https://airflow.apache.org/
- Documentation: https://airflow.apache.org/docs/
- GitHub: https://github.com/apache/airflow

### Learning
- Astronomer Academy: https://academy.astronomer.io/
- Airflow Summit talks

### Managed Services
- Astronomer (Cloud)
- Google Cloud Composer
- Amazon MWAA
| Azure Data Factory (Airflow support)

---

## 💡 Nhận định từ thực tế (Senior Advice)

1. **Airflow là "Con Voi" (Nặng nề & Khó nuôi):**
   Bạn không thể cài Airflow lên 1 con EC2 t2.micro và mong nó chạy ổn. Nó cần PostgreSQL, Redis, Scheduler, Webserver, Worker. Nếu team bạn có dưới 3 người và chỉ cần chạy 10 script Python mỗi ngày, **đừng dùng Airflow**. Hãy dùng GitHub Actions, Cron, hoặc dbt Cloud scheduler. Chỉ dùng Airflow khi bạn có \>50 DAGs và cần gỡ rối các quan hệ phụ thuộc chéo (inter-dependencies).
2. **Managed services over Self-hosting:**
   Chăm sóc cluster Airflow chạy ổn định (ko chết schedule, không kẹt task ở trạng thái `queued`, không OOM) là một công việc toàn thời gian. Nếu có ngân sách, hãy mua **Astronomer** (xịn nhất), hoặc AWS MWAA / GCP Cloud Composer. Trừ khi bạn rẻ nhân công hơn rẻ tiền server (rất hiếm).
3. **Dagster / Prefect đang nổi lên:**
   Airflow ra đời 2014, kiến trúc nó đã cũ dù bản 3.0 đang cố cấu trúc lại. Nếu bạn làm dự án mới từ đầu (greenfield), hãy nghía qua **Dagster**. Dagster coi "Data Assets" là trung tâm (trực quan hoá data hơn là task), và build-in CI/CD test cực mạnh, giải quyết hầu hết các nỗi đau mà dev Airflow đang phải chịu.

---

> **Document Version**: 1.0  
> **Last Updated**: December 31, 2025  
> **Airflow Version**: 3.1.0
