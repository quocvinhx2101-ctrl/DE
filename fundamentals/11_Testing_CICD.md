# Data Testing & CI/CD - Complete Guide

## Testing Strategies, Pipeline CI/CD, Quality Gates, và Test Automation

---

## PHẦN 1: DATA TESTING FUNDAMENTALS

### 1.1 Why Test Data Pipelines?

Data pipelines fail in ways different from traditional software:
- **Schema changes**: Upstream changes break pipelines
- **Data drift**: Data distribution changes over time
- **Volume anomalies**: Unexpected data volumes
- **Quality degradation**: Gradual decrease in quality
- **Freshness issues**: Late or missing data

### 1.2 Types of Data Tests

```
DATA TESTING PYRAMID:

            /\
           /  \
          / E2E\       End-to-end tests
         /------\      (Full pipeline runs)
        /        \
       /Integration\   Integration tests
      /--------------\ (Component interactions)
     /                \
    /    Unit Tests    \  Unit tests
   /--------------------\ (Transform logic)
  /                      \
 /      Data Quality      \ Data quality tests
/---------------------------\(Expectations on data)

COVERAGE:
- Data Quality: Run continuously on production data
- Unit Tests: Run on every commit
- Integration: Run on PRs and before deploy
- E2E: Run on staging before production deploy
```

### 1.3 Test Categories

```
1. SCHEMA TESTS
   - Column existence
   - Data types
   - Nullable constraints
   - Primary key uniqueness

2. DATA QUALITY TESTS
   - Null checks
   - Range validation
   - Pattern matching
   - Referential integrity

3. BUSINESS LOGIC TESTS
   - Transformation correctness
   - Aggregation accuracy
   - Business rule validation

4. PERFORMANCE TESTS
   - Query execution time
   - Resource utilization
   - Scalability

5. PIPELINE TESTS
   - Idempotency
   - Recovery from failure
   - Data lineage accuracy
```

---

## PHẦN 2: UNIT TESTING FOR DATA

### 2.1 Testing Transformations

```python
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from datetime import datetime

# Transformation function to test
def calculate_customer_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate customer metrics from transactions"""
    metrics = df.groupby('customer_id').agg(
        total_orders=('order_id', 'nunique'),
        total_revenue=('amount', 'sum'),
        avg_order_value=('amount', 'mean'),
        first_order_date=('order_date', 'min'),
        last_order_date=('order_date', 'max')
    ).reset_index()
    
    metrics['days_as_customer'] = (
        metrics['last_order_date'] - metrics['first_order_date']
    ).dt.days
    
    return metrics


# Unit tests
class TestCustomerMetrics:
    
    @pytest.fixture
    def sample_orders(self):
        return pd.DataFrame({
            'order_id': [1, 2, 3, 4, 5],
            'customer_id': ['A', 'A', 'B', 'B', 'B'],
            'amount': [100.0, 150.0, 200.0, 50.0, 100.0],
            'order_date': pd.to_datetime([
                '2024-01-01', '2024-01-15', 
                '2024-01-01', '2024-01-10', '2024-01-20'
            ])
        })
    
    def test_customer_count(self, sample_orders):
        result = calculate_customer_metrics(sample_orders)
        assert len(result) == 2
    
    def test_total_orders_per_customer(self, sample_orders):
        result = calculate_customer_metrics(sample_orders)
        customer_a = result[result['customer_id'] == 'A']
        assert customer_a['total_orders'].values[0] == 2
    
    def test_total_revenue_calculation(self, sample_orders):
        result = calculate_customer_metrics(sample_orders)
        customer_b = result[result['customer_id'] == 'B']
        assert customer_b['total_revenue'].values[0] == 350.0
    
    def test_avg_order_value(self, sample_orders):
        result = calculate_customer_metrics(sample_orders)
        customer_a = result[result['customer_id'] == 'A']
        assert customer_a['avg_order_value'].values[0] == 125.0
    
    def test_days_as_customer(self, sample_orders):
        result = calculate_customer_metrics(sample_orders)
        customer_a = result[result['customer_id'] == 'A']
        assert customer_a['days_as_customer'].values[0] == 14
    
    def test_empty_dataframe(self):
        empty_df = pd.DataFrame(columns=[
            'order_id', 'customer_id', 'amount', 'order_date'
        ])
        result = calculate_customer_metrics(empty_df)
        assert len(result) == 0
    
    def test_output_schema(self, sample_orders):
        result = calculate_customer_metrics(sample_orders)
        expected_columns = [
            'customer_id', 'total_orders', 'total_revenue',
            'avg_order_value', 'first_order_date', 'last_order_date',
            'days_as_customer'
        ]
        assert list(result.columns) == expected_columns
```

### 2.2 PySpark Testing

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from chispa import assert_df_equality

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .master("local[2]") \
        .appName("unit-tests") \
        .getOrCreate()

# Transformation to test
def transform_sales(df):
    """Clean and enrich sales data"""
    return df \
        .filter(col("amount") > 0) \
        .withColumn("amount_usd", col("amount") * col("exchange_rate")) \
        .withColumn("sale_month", date_trunc("month", col("sale_date")))


class TestSalesTransform:
    
    def test_filters_negative_amounts(self, spark):
        # Arrange
        input_data = [
            (1, 100.0, 1.0, "2024-01-15"),
            (2, -50.0, 1.0, "2024-01-16"),
            (3, 200.0, 1.0, "2024-01-17")
        ]
        schema = StructType([
            StructField("id", IntegerType()),
            StructField("amount", DoubleType()),
            StructField("exchange_rate", DoubleType()),
            StructField("sale_date", StringType())
        ])
        input_df = spark.createDataFrame(input_data, schema) \
            .withColumn("sale_date", to_date("sale_date"))
        
        # Act
        result = transform_sales(input_df)
        
        # Assert
        assert result.count() == 2
        assert result.filter(col("amount") < 0).count() == 0
    
    def test_calculates_usd_amount(self, spark):
        input_data = [(1, 100.0, 1.5, "2024-01-15")]
        schema = ["id", "amount", "exchange_rate", "sale_date"]
        input_df = spark.createDataFrame(input_data, schema) \
            .withColumn("sale_date", to_date("sale_date"))
        
        result = transform_sales(input_df)
        
        amount_usd = result.select("amount_usd").first()[0]
        assert amount_usd == 150.0
    
    def test_adds_sale_month(self, spark):
        input_data = [(1, 100.0, 1.0, "2024-01-15")]
        schema = ["id", "amount", "exchange_rate", "sale_date"]
        input_df = spark.createDataFrame(input_data, schema) \
            .withColumn("sale_date", to_date("sale_date"))
        
        result = transform_sales(input_df)
        
        sale_month = result.select("sale_month").first()[0]
        assert str(sale_month) == "2024-01-01"
    
    def test_full_transformation(self, spark):
        # Input
        input_data = [
            (1, 100.0, 1.0, "2024-01-15"),
            (2, 200.0, 1.5, "2024-01-20")
        ]
        input_df = spark.createDataFrame(
            input_data, 
            ["id", "amount", "exchange_rate", "sale_date"]
        ).withColumn("sale_date", to_date("sale_date"))
        
        # Expected output
        expected_data = [
            (1, 100.0, 1.0, "2024-01-15", 100.0, "2024-01-01"),
            (2, 200.0, 1.5, "2024-01-20", 300.0, "2024-01-01")
        ]
        expected_df = spark.createDataFrame(
            expected_data,
            ["id", "amount", "exchange_rate", "sale_date", "amount_usd", "sale_month"]
        ).withColumn("sale_date", to_date("sale_date")) \
         .withColumn("sale_month", to_date("sale_month"))
        
        # Act
        result = transform_sales(input_df)
        
        # Assert with chispa
        assert_df_equality(result, expected_df, ignore_row_order=True)
```

### 2.3 SQL Testing with dbt

```yaml
# dbt schema.yml with tests
version: 2

models:
  - name: fact_orders
    description: "Order fact table"
    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - unique
          - not_null
      
      - name: customer_id
        description: "Foreign key to customer"
        tests:
          - not_null
          - relationships:
              to: ref('dim_customer')
              field: customer_id
      
      - name: order_amount
        description: "Order total amount"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
      
      - name: order_status
        description: "Current order status"
        tests:
          - accepted_values:
              values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
      
      - name: order_date
        tests:
          - not_null
          - dbt_utils.not_null_proportion:
              at_least: 0.99

    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - order_id
            - order_date
      
      - dbt_utils.recency:
          datepart: day
          field: order_date
          interval: 1
```

```sql
-- Custom dbt test: tests/assert_positive_revenue.sql
{% test positive_revenue(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} < 0

{% endtest %}

-- tests/assert_referential_integrity.sql
{% test assert_referential_integrity(model, column, parent_model, parent_column) %}

SELECT child.*
FROM {{ model }} child
LEFT JOIN {{ parent_model }} parent
  ON child.{{ column }} = parent.{{ parent_column }}
WHERE parent.{{ parent_column }} IS NULL
  AND child.{{ column }} IS NOT NULL

{% endtest %}
```

---

## PHẦN 3: DATA QUALITY TESTING

### 3.1 Great Expectations

```python
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest

# Initialize context
context = gx.get_context()

# Create expectation suite
suite_name = "sales_data_quality"
context.add_or_update_expectation_suite(suite_name)

# Build expectations
validator = context.get_validator(
    batch_request=RuntimeBatchRequest(
        datasource_name="pandas",
        data_connector_name="default",
        data_asset_name="sales",
        runtime_parameters={"batch_data": df}
    ),
    expectation_suite_name=suite_name
)

# Schema expectations
validator.expect_table_columns_to_match_ordered_list(
    column_list=["order_id", "customer_id", "amount", "order_date", "status"]
)

# Column expectations
validator.expect_column_values_to_not_be_null(column="order_id")
validator.expect_column_values_to_be_unique(column="order_id")

validator.expect_column_values_to_not_be_null(column="amount")
validator.expect_column_values_to_be_between(
    column="amount", 
    min_value=0, 
    max_value=1000000
)

validator.expect_column_values_to_be_in_set(
    column="status",
    value_set=["pending", "confirmed", "shipped", "delivered", "cancelled"]
)

# Distribution expectations
validator.expect_column_mean_to_be_between(
    column="amount",
    min_value=50,
    max_value=500
)

validator.expect_column_proportion_of_unique_values_to_be_between(
    column="customer_id",
    min_value=0.01,
    max_value=1.0
)

# Row count expectations
validator.expect_table_row_count_to_be_between(
    min_value=1000,
    max_value=10000000
)

# Save suite
validator.save_expectation_suite(discard_failed_expectations=False)

# Run validation and get results
checkpoint = context.add_or_update_checkpoint(
    name="sales_checkpoint",
    validations=[{
        "batch_request": batch_request,
        "expectation_suite_name": suite_name
    }]
)

results = checkpoint.run()

# Check if passed
if not results.success:
    failed_expectations = [
        r for r in results.run_results.values() 
        if not r["success"]
    ]
    raise DataQualityError(f"Quality checks failed: {failed_expectations}")
```

### 3.2 Custom Data Quality Framework

```python
from dataclasses import dataclass
from typing import Callable, List, Any
from enum import Enum

class Severity(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class QualityCheck:
    name: str
    description: str
    check_func: Callable
    severity: Severity = Severity.ERROR
    
@dataclass
class CheckResult:
    check_name: str
    passed: bool
    message: str
    severity: Severity
    details: dict = None

class DataQualityFramework:
    def __init__(self):
        self.checks: List[QualityCheck] = []
        self.results: List[CheckResult] = []
    
    def add_check(self, check: QualityCheck):
        self.checks.append(check)
    
    def not_null(self, df, column: str, threshold: float = 1.0) -> CheckResult:
        null_count = df[column].isnull().sum()
        total_count = len(df)
        null_ratio = null_count / total_count if total_count > 0 else 0
        passed = (1 - null_ratio) >= threshold
        
        return CheckResult(
            check_name=f"not_null_{column}",
            passed=passed,
            message=f"Column {column}: {null_count} nulls ({null_ratio:.2%})",
            severity=Severity.ERROR,
            details={"null_count": null_count, "null_ratio": null_ratio}
        )
    
    def unique(self, df, column: str) -> CheckResult:
        total = len(df)
        unique = df[column].nunique()
        duplicates = total - unique
        passed = duplicates == 0
        
        return CheckResult(
            check_name=f"unique_{column}",
            passed=passed,
            message=f"Column {column}: {duplicates} duplicate values",
            severity=Severity.ERROR,
            details={"total": total, "unique": unique, "duplicates": duplicates}
        )
    
    def in_range(self, df, column: str, min_val: float, max_val: float) -> CheckResult:
        out_of_range = df[(df[column] < min_val) | (df[column] > max_val)]
        count = len(out_of_range)
        passed = count == 0
        
        return CheckResult(
            check_name=f"in_range_{column}",
            passed=passed,
            message=f"Column {column}: {count} values outside [{min_val}, {max_val}]",
            severity=Severity.ERROR,
            details={"out_of_range_count": count}
        )
    
    def referential_integrity(self, df, column: str, 
                              reference_df, reference_column: str) -> CheckResult:
        reference_values = set(reference_df[reference_column])
        orphans = df[~df[column].isin(reference_values)]
        count = len(orphans)
        passed = count == 0
        
        return CheckResult(
            check_name=f"referential_integrity_{column}",
            passed=passed,
            message=f"Column {column}: {count} orphan records",
            severity=Severity.ERROR,
            details={"orphan_count": count}
        )
    
    def freshness(self, df, column: str, max_delay_hours: int) -> CheckResult:
        from datetime import datetime, timedelta
        
        max_date = df[column].max()
        cutoff = datetime.now() - timedelta(hours=max_delay_hours)
        passed = max_date >= cutoff
        
        return CheckResult(
            check_name=f"freshness_{column}",
            passed=passed,
            message=f"Latest {column}: {max_date}, cutoff: {cutoff}",
            severity=Severity.CRITICAL,
            details={"max_date": str(max_date), "cutoff": str(cutoff)}
        )
    
    def run_all(self, df, **kwargs) -> List[CheckResult]:
        results = []
        for check in self.checks:
            try:
                result = check.check_func(df, **kwargs)
                result.severity = check.severity
                results.append(result)
            except Exception as e:
                results.append(CheckResult(
                    check_name=check.name,
                    passed=False,
                    message=f"Check failed with error: {str(e)}",
                    severity=Severity.CRITICAL
                ))
        
        self.results = results
        return results
    
    def raise_on_failure(self):
        failed_critical = [r for r in self.results 
                         if not r.passed and r.severity == Severity.CRITICAL]
        failed_error = [r for r in self.results 
                       if not r.passed and r.severity == Severity.ERROR]
        
        if failed_critical:
            raise CriticalDataQualityError(failed_critical)
        if failed_error:
            raise DataQualityError(failed_error)


# Usage
dq = DataQualityFramework()

dq.add_check(QualityCheck(
    name="order_id_not_null",
    description="Order ID should never be null",
    check_func=lambda df: dq.not_null(df, "order_id"),
    severity=Severity.CRITICAL
))

dq.add_check(QualityCheck(
    name="order_id_unique",
    description="Order ID should be unique",
    check_func=lambda df: dq.unique(df, "order_id"),
    severity=Severity.ERROR
))

dq.add_check(QualityCheck(
    name="amount_positive",
    description="Amount should be positive",
    check_func=lambda df: dq.in_range(df, "amount", 0, float('inf')),
    severity=Severity.ERROR
))

results = dq.run_all(df)
dq.raise_on_failure()
```

### 3.3 Anomaly Detection

```python
import pandas as pd
import numpy as np
from scipy import stats

class DataAnomalyDetector:
    def __init__(self, history_df: pd.DataFrame):
        self.history = history_df
    
    def check_volume_anomaly(self, current_count: int, 
                             metric_name: str = "row_count",
                             threshold_std: float = 3.0) -> dict:
        """Check if current volume is anomalous based on history"""
        historical_counts = self.history[metric_name]
        
        mean = historical_counts.mean()
        std = historical_counts.std()
        
        z_score = (current_count - mean) / std if std > 0 else 0
        is_anomaly = abs(z_score) > threshold_std
        
        return {
            "metric": metric_name,
            "current_value": current_count,
            "historical_mean": mean,
            "historical_std": std,
            "z_score": z_score,
            "is_anomaly": is_anomaly,
            "message": f"{'ANOMALY: ' if is_anomaly else ''}Count {current_count} "
                       f"(z-score: {z_score:.2f})"
        }
    
    def check_distribution_drift(self, current_df: pd.DataFrame, 
                                  column: str,
                                  p_value_threshold: float = 0.05) -> dict:
        """Check if distribution has drifted using KS test"""
        historical_values = self.history[column].dropna()
        current_values = current_df[column].dropna()
        
        statistic, p_value = stats.ks_2samp(historical_values, current_values)
        
        is_drift = p_value < p_value_threshold
        
        return {
            "column": column,
            "ks_statistic": statistic,
            "p_value": p_value,
            "is_drift": is_drift,
            "message": f"{'DRIFT DETECTED: ' if is_drift else ''}"
                       f"KS statistic: {statistic:.4f}, p-value: {p_value:.4f}"
        }
    
    def check_null_rate_change(self, current_df: pd.DataFrame,
                                column: str,
                                max_change: float = 0.1) -> dict:
        """Check if null rate has changed significantly"""
        historical_null_rate = self.history[column].isnull().mean()
        current_null_rate = current_df[column].isnull().mean()
        
        change = abs(current_null_rate - historical_null_rate)
        is_anomaly = change > max_change
        
        return {
            "column": column,
            "historical_null_rate": historical_null_rate,
            "current_null_rate": current_null_rate,
            "change": change,
            "is_anomaly": is_anomaly,
            "message": f"{'ANOMALY: ' if is_anomaly else ''}"
                       f"Null rate changed by {change:.2%}"
        }


# Usage
detector = DataAnomalyDetector(historical_stats_df)

# Check volume
volume_result = detector.check_volume_anomaly(len(current_df))
if volume_result["is_anomaly"]:
    send_alert(f"Volume anomaly detected: {volume_result['message']}")

# Check distribution
for column in ["amount", "quantity"]:
    drift_result = detector.check_distribution_drift(current_df, column)
    if drift_result["is_drift"]:
        send_alert(f"Distribution drift in {column}: {drift_result['message']}")
```

---

## PHẦN 4: INTEGRATION TESTING

### 4.1 Pipeline Integration Tests

```python
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

class TestSalesPipeline:
    """Integration tests for sales pipeline"""
    
    @pytest.fixture
    def pipeline(self):
        from pipelines.sales_pipeline import SalesPipeline
        return SalesPipeline(config={
            "source": "test_source",
            "target": "test_target",
            "env": "test"
        })
    
    @pytest.fixture
    def sample_source_data(self, spark):
        return spark.createDataFrame([
            (1, "A", 100.0, "2024-01-15"),
            (2, "B", 200.0, "2024-01-16"),
            (3, "A", 150.0, "2024-01-17")
        ], ["order_id", "customer_id", "amount", "order_date"])
    
    def test_pipeline_extracts_data(self, pipeline, sample_source_data):
        with patch.object(pipeline, '_read_source', return_value=sample_source_data):
            result = pipeline.extract()
            assert result.count() == 3
    
    def test_pipeline_transforms_data(self, pipeline, sample_source_data):
        result = pipeline.transform(sample_source_data)
        
        # Check schema
        assert "amount_usd" in result.columns
        assert "processed_at" in result.columns
        
        # Check row count preserved
        assert result.count() == sample_source_data.count()
    
    def test_pipeline_loads_data(self, pipeline, sample_source_data, tmp_path):
        pipeline.config["target_path"] = str(tmp_path)
        
        transformed = pipeline.transform(sample_source_data)
        pipeline.load(transformed)
        
        # Verify data was written
        loaded = spark.read.parquet(str(tmp_path))
        assert loaded.count() == 3
    
    def test_full_pipeline_run(self, pipeline, sample_source_data, tmp_path):
        pipeline.config["target_path"] = str(tmp_path)
        
        with patch.object(pipeline, '_read_source', return_value=sample_source_data):
            result = pipeline.run()
            
            assert result["status"] == "success"
            assert result["rows_processed"] == 3
    
    def test_pipeline_idempotency(self, pipeline, sample_source_data, tmp_path):
        """Running pipeline twice should produce same result"""
        pipeline.config["target_path"] = str(tmp_path)
        
        with patch.object(pipeline, '_read_source', return_value=sample_source_data):
            pipeline.run()
            first_count = spark.read.parquet(str(tmp_path)).count()
            
            pipeline.run()  # Run again
            second_count = spark.read.parquet(str(tmp_path)).count()
            
            assert first_count == second_count
    
    def test_pipeline_handles_empty_source(self, pipeline, spark, tmp_path):
        empty_df = spark.createDataFrame([], pipeline.source_schema)
        pipeline.config["target_path"] = str(tmp_path)
        
        with patch.object(pipeline, '_read_source', return_value=empty_df):
            result = pipeline.run()
            
            assert result["status"] == "success"
            assert result["rows_processed"] == 0
```

### 4.2 Testing với Test Containers

```python
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.kafka import KafkaContainer
from testcontainers.localstack import LocalStackContainer

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:14") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def kafka_container():
    with KafkaContainer() as kafka:
        yield kafka

@pytest.fixture(scope="session")
def localstack_container():
    with LocalStackContainer() as localstack:
        yield localstack

class TestDatabaseIntegration:
    
    def test_extract_from_postgres(self, postgres_container):
        # Setup
        engine = create_engine(postgres_container.get_connection_url())
        
        # Create test data
        with engine.connect() as conn:
            conn.execute("""
                CREATE TABLE orders (
                    id INT PRIMARY KEY,
                    amount DECIMAL(10,2)
                )
            """)
            conn.execute("INSERT INTO orders VALUES (1, 100.00), (2, 200.00)")
        
        # Test extraction
        from pipelines.extract import PostgresExtractor
        extractor = PostgresExtractor(postgres_container.get_connection_url())
        result = extractor.extract("SELECT * FROM orders")
        
        assert len(result) == 2
    
    def test_kafka_consumer(self, kafka_container):
        from confluent_kafka import Producer, Consumer
        
        # Setup producer
        producer = Producer({
            'bootstrap.servers': kafka_container.get_bootstrap_server()
        })
        
        # Send test messages
        for i in range(10):
            producer.produce('test-topic', f'message-{i}'.encode())
        producer.flush()
        
        # Test consumer
        from pipelines.consumers import OrderConsumer
        consumer = OrderConsumer(kafka_container.get_bootstrap_server())
        messages = consumer.consume('test-topic', timeout=10)
        
        assert len(messages) == 10


class TestS3Integration:
    
    def test_s3_upload_download(self, localstack_container):
        import boto3
        
        # Setup S3 client pointing to LocalStack
        s3 = boto3.client(
            's3',
            endpoint_url=localstack_container.get_url(),
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
        
        # Create bucket
        s3.create_bucket(Bucket='test-bucket')
        
        # Test upload
        from pipelines.storage import S3Storage
        storage = S3Storage(
            endpoint_url=localstack_container.get_url(),
            bucket='test-bucket'
        )
        
        storage.upload_dataframe(test_df, 'data/test.parquet')
        
        # Verify
        result = storage.download_dataframe('data/test.parquet')
        assert len(result) == len(test_df)
```

---

## PHẦN 5: CI/CD FOR DATA PIPELINES

### 5.1 GitHub Actions Pipeline

```yaml
# .github/workflows/data-pipeline-ci.yml
name: Data Pipeline CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.10'
  SPARK_VERSION: '3.4.0'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install linting tools
        run: |
          pip install flake8 black isort mypy
      
      - name: Run linters
        run: |
          flake8 src/ tests/
          black --check src/ tests/
          isort --check-only src/ tests/
          mypy src/
  
  unit-tests:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Cache pip packages
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('requirements.txt') }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: coverage.xml
  
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Java (for Spark)
        uses: actions/setup-java@v3
        with:
          java-version: '11'
          distribution: 'temurin'
      
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-test.txt
      
      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres
        run: |
          pytest tests/integration/ -v --timeout=300
  
  dbt-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dbt
        run: pip install dbt-postgres
      
      - name: Run dbt tests
        working-directory: ./dbt_project
        env:
          DBT_PROFILES_DIR: .
        run: |
          dbt deps
          dbt compile
          dbt test --select test_type:schema
  
  deploy-staging:
    runs-on: ubuntu-latest
    needs: [integration-tests, dbt-tests]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      
      - name: Deploy to staging
        run: |
          ./scripts/deploy.sh staging
      
      - name: Run smoke tests
        run: |
          pytest tests/smoke/ -v --env=staging
  
  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      
      - name: Deploy to production
        run: |
          ./scripts/deploy.sh production
      
      - name: Run production validation
        run: |
          pytest tests/smoke/ -v --env=production
      
      - name: Notify on success
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {"text": "✅ Pipeline deployed to production successfully"}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### 5.2 Airflow DAG Testing

```python
import pytest
from airflow.models import DagBag
from datetime import datetime

@pytest.fixture
def dagbag():
    return DagBag(dag_folder="dags/", include_examples=False)

class TestDAGIntegrity:
    
    def test_no_import_errors(self, dagbag):
        """Verify no import errors in DAGs"""
        assert len(dagbag.import_errors) == 0, \
            f"DAG import errors: {dagbag.import_errors}"
    
    def test_dag_count(self, dagbag):
        """Verify expected number of DAGs"""
        assert len(dagbag.dags) >= 1
    
    def test_dag_has_tags(self, dagbag):
        """All DAGs should have tags"""
        for dag_id, dag in dagbag.dags.items():
            assert dag.tags is not None and len(dag.tags) > 0, \
                f"DAG {dag_id} has no tags"
    
    def test_dag_has_owner(self, dagbag):
        """All DAGs should have an owner"""
        for dag_id, dag in dagbag.dags.items():
            assert dag.owner != 'airflow', \
                f"DAG {dag_id} has default owner"
    
    def test_dag_has_description(self, dagbag):
        """All DAGs should have descriptions"""
        for dag_id, dag in dagbag.dags.items():
            assert dag.description is not None, \
                f"DAG {dag_id} has no description"


class TestSalesDAG:
    
    @pytest.fixture
    def sales_dag(self, dagbag):
        return dagbag.dags.get("sales_pipeline")
    
    def test_dag_exists(self, sales_dag):
        assert sales_dag is not None
    
    def test_task_count(self, sales_dag):
        assert len(sales_dag.tasks) >= 3
    
    def test_task_dependencies(self, sales_dag):
        """Verify expected task dependencies"""
        extract_task = sales_dag.get_task("extract")
        transform_task = sales_dag.get_task("transform")
        load_task = sales_dag.get_task("load")
        
        # extract -> transform -> load
        assert transform_task in extract_task.downstream_list
        assert load_task in transform_task.downstream_list
    
    def test_default_args(self, sales_dag):
        assert sales_dag.default_args.get("retries") >= 1
        assert sales_dag.default_args.get("email_on_failure") == True
    
    def test_schedule(self, sales_dag):
        assert sales_dag.schedule_interval is not None
```

### 5.3 Quality Gates

```python
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class GateStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class QualityGate:
    name: str
    description: str
    check_func: callable
    blocking: bool = True  # If True, fails the pipeline

@dataclass
class GateResult:
    gate: QualityGate
    status: GateStatus
    details: Dict

class QualityGateRunner:
    def __init__(self):
        self.gates: List[QualityGate] = []
        self.results: List[GateResult] = []
    
    def add_gate(self, gate: QualityGate):
        self.gates.append(gate)
    
    def run_all(self, context: Dict) -> bool:
        """Run all quality gates, return True if all blocking gates pass"""
        all_passed = True
        
        for gate in self.gates:
            try:
                passed = gate.check_func(context)
                status = GateStatus.PASSED if passed else GateStatus.FAILED
                
                self.results.append(GateResult(
                    gate=gate,
                    status=status,
                    details={"passed": passed}
                ))
                
                if not passed and gate.blocking:
                    all_passed = False
                    
            except Exception as e:
                self.results.append(GateResult(
                    gate=gate,
                    status=GateStatus.FAILED,
                    details={"error": str(e)}
                ))
                if gate.blocking:
                    all_passed = False
        
        return all_passed
    
    def get_report(self) -> str:
        lines = ["Quality Gate Report", "=" * 50]
        
        for result in self.results:
            status_emoji = "✅" if result.status == GateStatus.PASSED else "❌"
            blocking = "[BLOCKING]" if result.gate.blocking else "[WARNING]"
            lines.append(f"{status_emoji} {blocking} {result.gate.name}")
            lines.append(f"   {result.gate.description}")
            lines.append(f"   Details: {result.details}")
        
        return "\n".join(lines)


# Define quality gates
gates = QualityGateRunner()

gates.add_gate(QualityGate(
    name="row_count_check",
    description="Ensure minimum row count is met",
    check_func=lambda ctx: ctx["row_count"] >= ctx["min_rows"],
    blocking=True
))

gates.add_gate(QualityGate(
    name="null_rate_check",
    description="Ensure null rate below threshold",
    check_func=lambda ctx: ctx["null_rate"] <= 0.01,
    blocking=True
))

gates.add_gate(QualityGate(
    name="freshness_check",
    description="Data should be fresh",
    check_func=lambda ctx: ctx["max_date"] >= ctx["freshness_cutoff"],
    blocking=True
))

gates.add_gate(QualityGate(
    name="duplicate_check",
    description="No duplicate primary keys",
    check_func=lambda ctx: ctx["duplicate_count"] == 0,
    blocking=True
))

gates.add_gate(QualityGate(
    name="volume_anomaly",
    description="Volume should not be anomalous",
    check_func=lambda ctx: abs(ctx["volume_zscore"]) < 3,
    blocking=False  # Warning only
))

# Run gates
context = {
    "row_count": 10000,
    "min_rows": 1000,
    "null_rate": 0.005,
    "max_date": datetime.now(),
    "freshness_cutoff": datetime.now() - timedelta(hours=24),
    "duplicate_count": 0,
    "volume_zscore": 1.5
}

if gates.run_all(context):
    print("All quality gates passed!")
    proceed_with_deployment()
else:
    print(gates.get_report())
    raise QualityGateFailure("Blocking quality gates failed")
```

---

## PHẦN 6: BEST PRACTICES

### 6.1 Testing Checklist

```
PRE-COMMIT:
□ Linting (flake8, black, isort)
□ Type checking (mypy)
□ Unit tests

PR/MERGE:
□ All unit tests pass
□ Integration tests pass
□ dbt tests pass
□ Code coverage > 80%
□ Documentation updated

PRE-DEPLOY (Staging):
□ Full pipeline test run
□ Data quality checks pass
□ Performance benchmarks met
□ No regressions

PRE-DEPLOY (Production):
□ Staging validation passed
□ Quality gates passed
□ Rollback plan documented
□ Stakeholder approval
```

### 6.2 Test Organization

```
project/
├── src/
│   ├── pipelines/
│   ├── transforms/
│   └── utils/
├── tests/
│   ├── unit/              # Fast, isolated tests
│   │   ├── test_transforms.py
│   │   └── test_utils.py
│   ├── integration/       # Tests with dependencies
│   │   ├── test_database.py
│   │   └── test_pipeline.py
│   ├── smoke/            # Quick sanity checks
│   │   └── test_endpoints.py
│   ├── e2e/              # Full pipeline tests
│   │   └── test_full_pipeline.py
│   └── fixtures/         # Shared test data
│       ├── sample_data.py
│       └── conftest.py
├── dbt_project/
│   └── tests/            # dbt tests
└── pytest.ini
```

### 6.3 Continuous Improvement

```
METRICS TO TRACK:
- Test coverage percentage
- Test execution time
- Test failure rate
- Time to fix broken tests
- Quality gate pass rate

REVIEW REGULARLY:
- Remove flaky tests
- Add tests for bugs found in production
- Update tests when requirements change
- Review test execution time
- Assess coverage gaps
```

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Coverage: Unit Testing, Integration Testing, Data Quality, CI/CD, Quality Gates*
