---
title: "Manage data quality with pipeline expectations | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/ldp/expectations"
author:
published: 2026-02-04
created: 2026-03-31
description: "Learn how to manage data quality with Databricks Lakeflow Spark Declarative Pipelines expectations."
tags:
  - "clippings"
---
Use expectations to apply quality constraints that validate data as it flows through ETL pipelines. Expectations provide greater insight into data quality metrics and allow you to fail updates or drop records when detecting invalid records.

This article has an overview of expectations, including syntax examples and behavior options. For more advanced use cases and recommended best practices, see [Expectation recommendations and advanced patterns](https://docs.databricks.com/aws/en/ldp/expectation-patterns).

![Pipeline expectations flow graph](https://docs.databricks.com/aws/en/assets/images/expectations-flow-graph-02ab5dd2011b18ad791c67c0e8449af6.png)

## What are expectations?

Expectations are optional clauses in pipeline materialized view, streaming table, or view creation statements that apply data quality checks on each record passing through a query. Expectations use standard SQL Boolean statements to specify constraints. You can combine multiple expectations for a single dataset and set expectations across all dataset declarations in a pipeline.

The following sections introduce the three components of an expectation and provide syntax examples.

### Expectation name

Each expectation must have a name, which is used as an identifier to track and monitor the expectation. Choose a name that communicates the metrics being validated. The following example defines the expectation `valid_customer_age` to confirm that age is between 0 and 120 years:

> [!-info] -info
> important
> 
> An expectation name must be unique for a given dataset. You can reuse expectations across multiple datasets in a pipeline. See [Portable and reusable expectations](https://docs.databricks.com/aws/en/ldp/expectation-patterns#reusable-expectations).

- Python
- SQL

```sql
SQLCREATE OR REFRESH STREAMING TABLE customers(
  CONSTRAINT valid_customer_age EXPECT (age BETWEEN 0 AND 120)
) AS SELECT * FROM STREAM(datasets.samples.raw_customers);
```

### Constraint to evaluate

The constraint clause is a SQL conditional statement that must evaluate to true or false for each record. The constraint contains the actual logic for what is being validated. When a record fails this condition, the expectation is triggered.

Constraints must use valid SQL syntax and cannot contain the following:

- Custom Python functions
- External service calls
- Subqueries referencing other tables

The following are examples of constraints that could be added to dataset creation statements:

- Python
- SQL

The syntax for a constraint in SQL is:

```sql
SQLCONSTRAINT <constraint-name> EXPECT ( <constraint-clause> )
```

Multiple constraints must be separated by a comma:

```sql
SQLCONSTRAINT <constraint-name> EXPECT ( <constraint-clause> ),
CONSTRAINT <constraint2-name> EXPECT ( <constraint2-clause> )
```

Examples:

```sql
SQL-- Simple constraint
CONSTRAINT non_negative_price EXPECT (price >= 0)

-- SQL functions
CONSTRAINT valid_date EXPECT (year(transaction_date) >= 2020)

-- CASE statements
CONSTRAINT valid_order_status EXPECT (
  CASE
    WHEN type = 'ORDER' THEN status IN ('PENDING', 'COMPLETED', 'CANCELLED')
    WHEN type = 'REFUND' THEN status IN ('PENDING', 'APPROVED', 'REJECTED')
    ELSE false
  END
)

-- Multiple constraints
CONSTRAINT non_negative_price EXPECT (price >= 0),
CONSTRAINT valid_purchase_date EXPECT (date <= current_date())

-- Complex business logic
CONSTRAINT valid_subscription_dates EXPECT (
  start_date <= end_date
  AND end_date <= current_date()
  AND start_date >= '2020-01-01'
)

-- Complex boolean logic
CONSTRAINT valid_order_state EXPECT (
  (status = 'ACTIVE' AND balance > 0)
  OR (status = 'PENDING' AND created_date > current_date() - INTERVAL 7 DAYS)
)
```

### Action on invalid record

You must specify an action to determine what happens when a record fails the validation check. The following table describes the available actions:

| Action | SQL syntax | Python syntax | Result |
| --- | --- | --- | --- |
| [warn](https://docs.databricks.com/aws/en/ldp/expectations#retain) (default) | `EXPECT` | `dp.expect` | Invalid records are written to the target. |
| [drop](https://docs.databricks.com/aws/en/ldp/expectations#drop) | `EXPECT ... ON VIOLATION DROP ROW` | `dp.expect_or_drop` | Invalid records are dropped before data is written to the target. The count of dropped records is logged alongside other dataset metrics. |
| [fail](https://docs.databricks.com/aws/en/ldp/expectations#fail) | `EXPECT ... ON VIOLATION FAIL UPDATE` | `dp.expect_or_fail` | Invalid records prevent the update from succeeding. Manual intervention is required before reprocessing. This expectation causes a failure of a single flow and does not cause other flows in your pipeline to fail. |

You can also implement advanced logic to quarantine invalid records without failing or dropping data. See [Quarantine invalid records](https://docs.databricks.com/aws/en/ldp/expectation-patterns#quarantine-invalid-data).

## Expectation tracking metrics

You can see tracking metrics for `warn` or `drop` actions from the pipeline UI. Because `fail` causes the update to fail when an invalid record is detected, metrics are not recorded.

To view expectation metrics, complete the following steps:

1. In your Databricks workspace's sidebar, click **Jobs & Pipelines**.
2. Click the **Name** of your pipeline.
3. Click a dataset with an expectation defined.
4. Select the **Data quality** tab in the right sidebar.

You can view data quality metrics by querying the Lakeflow Spark Declarative Pipelines event log. See [Query data quality or expectations metrics](https://docs.databricks.com/aws/en/ldp/monitor-event-logs#data-quality-metrics).

## Retain invalid records

Retaining invalid records is the default behavior for expectations. Use the `expect` operator when you want to keep records that violate the expectation but collect metrics on how many records pass or fail a constraint. Records that violate the expectation are added to the target dataset along with valid records:

- Python
- SQL

```sql
SQLCONSTRAINT valid_timestamp EXPECT (timestamp > '2012-01-01')
```

## Drop invalid records

Use the `expect_or_drop` operator to prevent further processing of invalid records. Records that violate the expectation are dropped from the target dataset:

- Python
- SQL

```sql
SQLCONSTRAINT valid_current_page EXPECT (current_page_id IS NOT NULL and current_page_title IS NOT NULL) ON VIOLATION DROP ROW
```

## Fail on invalid records

When invalid records are unacceptable, use the `expect_or_fail` operator to stop execution immediately when a record fails validation. If the operation is a table update, the system atomically rolls back the transaction:

- Python
- SQL

```sql
SQLCONSTRAINT valid_count EXPECT (count > 0) ON VIOLATION FAIL UPDATE
```

> [!-info] -info
> important
> 
> If you have multiple parallel flows defined in a pipeline, failure of a single flow does not cause other flows to fail.

![LDP flow failure explanation graph](https://docs.databricks.com/aws/en/assets/images/flow-failure-explained-3e48f828a3e48a4ad0930d00f5a6ec41.png)

### Troubleshooting failed updates from expectations

When a pipeline fails because of an expectation violation, you must fix the pipeline code to handle the invalid data correctly before re-running the pipeline.

Expectations configured to fail pipelines modify the Spark query plan of your transformations to track information required to detect and report violations. You can use this information to identify which input record resulted in the violation for many queries. Lakeflow Spark Declarative Pipelines provides a dedicated error message to report such violations. Here's an example of an expectation violation error message:

```markdown
Console[EXPECTATION_VIOLATION.VERBOSITY_ALL] Flow 'sensor-pipeline' failed to meet the expectation. Violated expectations: 'temperature_in_valid_range'. Input data: '{"id":"TEMP_001","temperature":-500,"timestamp_ms":"1710498600"}'. Output record: '{"sensor_id":"TEMP_001","temperature":-500,"change_time":"2024-03-15 10:30:00"}'. Missing input data: false
```

## Multiple expectations management

> [!-secondary] -secondary
> note
> 
> While both SQL and Python support multiple expectations in a single dataset, only Python allows you to group multiple expectations and specify collective actions.

![LDP with multiple expectations fLow graph](https://docs.databricks.com/aws/en/assets/images/multiple-expectations-flow-graph-754e3b280dabb82589a2d1c1f55d137f.png)

You can group multiple expectations together and specify collective actions using the functions `expect_all`, `expect_all_or_drop`, and `expect_all_or_fail`.

These decorators accept a Python dictionary as an argument, where the key is the expectation name and the value is the expectation constraint. You can reuse the same set of expectations in multiple datasets in your pipeline. The following shows examples of each of the `expect_all` Python operators:

```python
Pythonvalid_pages = {"valid_count": "count > 0", "valid_current_page": "current_page_id IS NOT NULL AND current_page_title IS NOT NULL"}

@dp.table
@dp.expect_all(valid_pages)
def raw_data():
  # Create a raw dataset

@dp.table
@dp.expect_all_or_drop(valid_pages)
def prepared_data():
  # Create a cleaned and prepared dataset

@dp.table
@dp.expect_all_or_fail(valid_pages)
def customer_facing_data():
  # Create cleaned and prepared to share the dataset
```

## Limitations

- Because only streaming tables, materialized views, and temporary views support expectations, data quality metrics are supported only for these object types.
- Data quality metrics are not available when:
	- No expectations are defined on a query.
		- A flow uses an operator that does not support expectations.
		- The flow type, such as [sinks](https://docs.databricks.com/aws/en/ldp/sinks), does not support expectations.
		- There are no updates to the associated streaming table or materialized view for a given flow run.
		- The pipeline configuration does not include the necessary settings for capturing metrics, such as `pipelines.metrics.flowTimeReporter.enabled`.
- For some cases, a `COMPLETED` flow might not contain metrics. Instead, metrics are reported in each micro-batch in a `flow_progress` event with the status `RUNNING`.
- Because views are only calculated when queried, data quality metrics might not be available for a defined view. Alternatively, a view that is queried in multiple downstream datasets might have multiple sets of data quality metrics.