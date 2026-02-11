# 🔥 Project 07: Debug & Fix Production Pipeline

> Real scenario: Pipeline is broken, stakeholders are waiting, you must fix it NOW.

(Pipeline đang broken, stakeholders đang chờ, bạn phải fix ngay)

---

## 📋 Project Overview

**Difficulty:** Intermediate → Advanced
**Time Estimate:** 1-2 weeks
**Skills Learned:** Debugging, incident response, root cause analysis, postmortem

### What Makes This Project Different

This project gives you **actual buggy code** — a complete e-commerce data pipeline with 6 realistic bugs embedded. Your job:

1. Read the broken code below
2. Set up the environment (Docker Compose)
3. Run the pipeline — watch it fail
4. Find all 6 bugs using debugging techniques
5. Fix each bug
6. Add monitoring to prevent recurrence
7. Write a postmortem

> **This is skill #1 in DE.** 65% of the job is debug + maintain, not build new.

---

## 🎯 Scenario

### The Morning From Hell

You just joined a startup's Data Engineering team. Today is your first day:

```
9:00 AM — Slack from CFO:
"Revenue dashboard shows $0 for today. Fix immediately."

9:05 AM — Slack from Marketing:
"User count dropped 90% vs yesterday on the dashboard. Bug?"

9:10 AM — Airflow alert:
"DAG 'ecommerce_pipeline' failed. Task 'transform_orders' FAILED."
```

---

## 🏗️ Infrastructure Setup

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
    volumes:
      - ./sql/init.sql:/docker-entrypoint-initdb.d/01_init.sql
      - ./sql/seed_data.sql:/docker-entrypoint-initdb.d/02_seed.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d ecommerce"]
      interval: 5s
      timeout: 5s
      retries: 5
```

### Database Schema & Seed Data

```sql
-- sql/init.sql
-- Source tables (simulating operational database)

CREATE TABLE raw_orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TIMESTAMP NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) NOT NULL
);

CREATE TABLE raw_order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES raw_orders(order_id),
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE raw_customers (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analytics tables (the pipeline writes here)
CREATE TABLE analytics_daily_revenue (
    report_date DATE NOT NULL,
    total_revenue DECIMAL(15,2),
    order_count INTEGER,
    avg_order_value DECIMAL(10,2),
    processed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE analytics_daily_users (
    report_date DATE NOT NULL,
    active_users INTEGER,
    new_users INTEGER,
    processed_at TIMESTAMP DEFAULT NOW()
);
```

```sql
-- sql/seed_data.sql
-- Realistic seed data WITH intentional data quality issues

-- Normal orders (correct data)
INSERT INTO raw_orders (customer_id, order_date, amount, currency, status) VALUES
(1, NOW() - INTERVAL '1 hour', 150.00, 'USD', 'completed'),
(2, NOW() - INTERVAL '2 hours', 89.99, 'USD', 'completed'),
(3, NOW() - INTERVAL '3 hours', 250.00, 'USD', 'completed'),
(4, NOW() - INTERVAL '5 hours', 45.00, 'USD', 'completed'),
(5, NOW() - INTERVAL '8 hours', 320.00, 'USD', 'completed'),
(6, NOW() - INTERVAL '10 hours', 175.50, 'USD', 'completed'),
(7, NOW() - INTERVAL '14 hours', 99.00, 'USD', 'completed'),
(8, NOW() - INTERVAL '18 hours', 420.00, 'USD', 'completed'),
(9, NOW() - INTERVAL '20 hours', 65.00, 'USD', 'completed'),
(10, NOW() - INTERVAL '22 hours', 180.00, 'USD', 'completed');

-- 🐛 BUG 1: Future-dated test records that leaked into production
INSERT INTO raw_orders (customer_id, order_date, amount, currency, status) VALUES
(999, NOW() + INTERVAL '5 days', 99999.99, 'USD', 'completed'),
(998, NOW() + INTERVAL '10 days', 50000.00, 'USD', 'completed');

-- 🐛 BUG 3: New currency field — some orders are in VND, not USD
INSERT INTO raw_orders (customer_id, order_date, amount, currency, status) VALUES
(11, NOW() - INTERVAL '4 hours', 3750000, 'VND', 'completed'),  -- ~$150 USD
(12, NOW() - INTERVAL '6 hours', 2250000, 'VND', 'completed');  -- ~$90 USD

-- Order items (for join/cartesian product bug)
-- 🐛 BUG 2: Order 1 has 3 items → will cause 3x revenue count on bad JOIN
INSERT INTO raw_order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 101, 1, 80.00),
(1, 102, 1, 40.00),
(1, 103, 1, 30.00),
(2, 201, 2, 44.99),
(3, 301, 1, 250.00),
(4, 101, 1, 45.00),
(5, 401, 1, 320.00);

-- Customers
INSERT INTO raw_customers (customer_id, email, country, created_at) VALUES
(1, 'alice@example.com', 'US', NOW() - INTERVAL '90 days'),
(2, 'bob@example.com', 'UK', NOW() - INTERVAL '60 days'),
(3, 'chi@example.com', 'VN', NOW() - INTERVAL '30 days'),
(4, 'dave@example.com', 'US', NOW() - INTERVAL '15 days'),
(5, 'eve@example.com', 'VN', NOW() - INTERVAL '7 days'),
(6, 'frank@example.com', 'SG', NOW() - INTERVAL '3 days'),
(7, 'grace@example.com', 'VN', NOW() - INTERVAL '2 days'),
(8, 'hank@example.com', 'US', NOW() - INTERVAL '1 day'),
(9, 'iris@example.com', 'VN', NOW() - INTERVAL '12 hours'),
(10, 'jack@example.com', 'UK', NOW() - INTERVAL '6 hours'),
(11, 'khanh@example.com', 'VN', NOW() - INTERVAL '4 hours'),
(12, 'lam@example.com', 'VN', NOW() - INTERVAL '2 hours');
```

---

## 🐛 THE BUGGY PIPELINE CODE

### File 1: `scripts/extract.py` — The Data Extractor

This script extracts data from the source database. **It contains 2 bugs.**

```python
# scripts/extract.py — BUGGY VERSION
# Your job: find and fix the bugs

import psycopg2
import json
import os
from datetime import datetime

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": "ecommerce",
    "user": "admin",
    "password": "admin123",
}


def extract_orders(target_date: str) -> list:
    """Extract orders for a specific date."""
    
    # ═══════════════════════════════════════════════════
    # 🐛 BUG 5: CONNECTION LEAK
    # This function opens a connection but never closes it.
    # After ~100 runs, PostgreSQL runs out of connections:
    #   "FATAL: too many clients already"
    # 
    # The developer forgot to use a context manager or 
    # explicit conn.close() in the finally block.
    # ═══════════════════════════════════════════════════
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # ═══════════════════════════════════════════════════
    # 🐛 BUG 4: TIMEZONE BUG
    # CURRENT_DATE is PostgreSQL server time (UTC).
    # Business operates in Vietnam (UTC+7).
    # Orders between midnight-7AM UTC show as "tomorrow"
    # because Vietnam is already the next day.
    # 
    # Result: Dashboard shows $0 revenue until 7 AM UTC
    # because "today" in UTC misses Vietnam morning orders.
    # ═══════════════════════════════════════════════════
    
    query = """
        SELECT 
            order_id, customer_id, order_date, 
            amount, currency, status
        FROM raw_orders
        WHERE DATE(order_date) = CURRENT_DATE
          AND status = 'completed'
    """
    
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        record = dict(zip(columns, row))
        # Convert datetime to string for JSON serialization
        record["order_date"] = record["order_date"].isoformat()
        results.append(record)
    
    print(f"Extracted {len(results)} orders for {target_date}")
    
    # 🐛 Connection is NEVER closed here!
    # conn.close() ← This line is missing
    
    return results


def extract_customers() -> list:
    """Extract all customers."""
    conn = psycopg2.connect(**DB_CONFIG)  # 🐛 Another leaked connection
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM raw_customers")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        record = dict(zip(columns, row))
        if record.get("created_at"):
            record["created_at"] = record["created_at"].isoformat()
        results.append(record)
    
    print(f"Extracted {len(results)} customers")
    # 🐛 Connection is NEVER closed here either!
    return results


if __name__ == "__main__":
    orders = extract_orders(datetime.now().strftime("%Y-%m-%d"))
    customers = extract_customers()
    print(f"Total: {len(orders)} orders, {len(customers)} customers")
```

### File 2: `sql/transform_orders.sql` — The Transform Query

This SQL transforms raw orders into the analytics table. **It contains 3 bugs.**

```sql
-- sql/transform_orders.sql — BUGGY VERSION
-- Your job: find and fix the bugs

-- ═══════════════════════════════════════════════════════════
-- 🐛 BUG 6: NOT IDEMPOTENT
-- This INSERT has no ON CONFLICT or DELETE-before-INSERT.
-- If the pipeline fails and retries, this INSERT runs AGAIN,
-- creating DUPLICATE rows in analytics_daily_revenue.
-- 
-- Run 1: INSERT → 1 row for today
-- Pipeline fails at next step → Airflow retries
-- Run 2: INSERT → ANOTHER row for today
-- Result: Revenue appears DOUBLED on dashboard
-- ═══════════════════════════════════════════════════════════

INSERT INTO analytics_daily_revenue (report_date, total_revenue, order_count, avg_order_value)
SELECT
    -- ═══════════════════════════════════════════════════════
    -- 🐛 BUG 4 (same timezone bug, SQL side):
    -- CURRENT_DATE is UTC. Business is UTC+7.
    -- ═══════════════════════════════════════════════════════
    CURRENT_DATE AS report_date,
    
    -- ═══════════════════════════════════════════════════════
    -- 🐛 BUG 2: CARTESIAN PRODUCT ON JOIN
    -- This JOIN with raw_order_items creates a cartesian product!
    -- 
    -- Order 1 has 3 items. The JOIN produces:
    --   order_id=1, amount=150  (matched with item 1)
    --   order_id=1, amount=150  (matched with item 2)
    --   order_id=1, amount=150  (matched with item 3)
    -- 
    -- SUM(o.amount) counts $150 THREE times = $450
    -- Actual revenue should be $150.
    -- 
    -- The developer probably added the JOIN to "enrich with item
    -- data" but forgot that it MULTIPLIES the order row.
    -- ═══════════════════════════════════════════════════════
    SUM(o.amount) AS total_revenue,
    COUNT(*) AS order_count,
    AVG(o.amount) AS avg_order_value

FROM raw_orders o
JOIN raw_order_items oi ON o.order_id = oi.order_id

WHERE DATE(o.order_date) = CURRENT_DATE
  AND o.status = 'completed';
  
  -- ═══════════════════════════════════════════════════════
  -- 🐛 BUG 1 (IMPLICIT): NO FILTER FOR FUTURE DATES
  -- The seed data has orders with future dates (test data).
  -- If query used '>= CURRENT_DATE' instead of '= CURRENT_DATE',
  -- it would include test records with amounts of $99,999.
  -- Currently masked by the '= CURRENT_DATE' filter, but
  -- the test data still pollutes other queries.
  -- 
  -- 🐛 BUG 3 (IMPLICIT): NO CURRENCY CONVERSION
  -- SUM(o.amount) mixes USD and VND amounts!
  -- Order 11: 3,750,000 VND treated as $3,750,000 USD
  -- This inflates revenue by ~$3.75M
  -- ═══════════════════════════════════════════════════════


-- Transform for user metrics (this one has the data quality bug)
INSERT INTO analytics_daily_users (report_date, active_users, new_users)
SELECT
    CURRENT_DATE AS report_date,
    
    -- 🐛 BUG 1: FUTURE-DATED RECORDS
    -- COUNT(*) includes test customer records linked to future orders.
    -- This inflates user counts... then when test records are filtered
    -- differently in another query, the 90% drop appears.
    COUNT(DISTINCT c.customer_id) AS active_users,
    
    COUNT(DISTINCT CASE 
        WHEN c.created_at >= CURRENT_DATE THEN c.customer_id 
    END) AS new_users

FROM raw_customers c
JOIN raw_orders o ON c.customer_id = o.customer_id
WHERE o.status = 'completed';
-- 🐛 No date filter! Counts ALL-TIME users as "today's active users"
-- Yesterday's dashboard showed all historical users.
-- Today's dashboard only shows today's... hence the "90% drop".
```

### File 3: `dags/ecommerce_pipeline.py` — The Airflow DAG

```python
# dags/ecommerce_pipeline.py — The orchestration layer
# This file ties together extraction and transformation

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, "/opt/airflow/scripts")

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["data-team@company.com"],
    "retries": 3,                    # 🐛 Retries + non-idempotent SQL = duplicates!
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "ecommerce_pipeline",
    default_args=default_args,
    description="Daily e-commerce data pipeline",
    schedule_interval="0 1 * * *",   # Runs at 1 AM UTC daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

def run_extraction(**context):
    """Extract data from source database."""
    from extract import extract_orders, extract_customers
    
    target_date = context["ds"]  # Airflow execution date
    orders = extract_orders(target_date)
    customers = extract_customers()
    
    # Push to XCom for downstream tasks
    context["ti"].xcom_push(key="order_count", value=len(orders))
    context["ti"].xcom_push(key="customer_count", value=len(customers))

extract_task = PythonOperator(
    task_id="extract_data",
    python_callable=run_extraction,
    dag=dag,
)

transform_task = PostgresOperator(
    task_id="transform_orders",
    postgres_conn_id="ecommerce_db",
    sql="sql/transform_orders.sql",
    dag=dag,
)

extract_task >> transform_task
```

---

## ✅ THE SOLUTIONS

> **DO NOT read below until you've tried finding and fixing all 6 bugs yourself.**

<details>
<summary>🔧 Solution — Bug 1: Future-Dated Test Records</summary>

**Root cause:** Test records with future dates leaked into production data.

**Fix:** Add date filter AND a data quality check.

```sql
-- Add this WHERE clause to ALL queries touching raw_orders:
WHERE o.order_date <= NOW()  -- Exclude future dates
  AND o.order_date >= CURRENT_DATE  -- Only today
  AND o.status = 'completed'

-- PREVENTION: Add a data quality check in the pipeline
-- Run this BEFORE the transform step:
DO $$
DECLARE
    future_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO future_count
    FROM raw_orders WHERE order_date > NOW();
    
    IF future_count > 0 THEN
        RAISE WARNING 'Found % records with future dates!', future_count;
        -- Log to monitoring, but don't fail — quarantine instead
        INSERT INTO dq_issues (check_name, issue_count, detected_at)
        VALUES ('future_dates', future_count, NOW());
    END IF;
END $$;
```
</details>

<details>
<summary>🔧 Solution — Bug 2: Cartesian Product JOIN</summary>

**Root cause:** `JOIN raw_order_items` multiplies rows. Order 1 has 3 items → revenue counted 3x.

**Fix:** Either don't join, or aggregate items first.

```sql
-- OPTION A: Don't join items (preferred — you don't need item data for revenue)
SELECT
    CURRENT_DATE AT TIME ZONE 'Asia/Ho_Chi_Minh' AS report_date,
    SUM(amount) AS total_revenue,
    COUNT(DISTINCT order_id) AS order_count,  -- Also fix: COUNT(*) → COUNT(DISTINCT)
    AVG(amount) AS avg_order_value
FROM raw_orders
WHERE DATE(order_date AT TIME ZONE 'Asia/Ho_Chi_Minh') 
      = (CURRENT_DATE AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE
  AND status = 'completed'
  AND order_date <= NOW()  -- Bug 1 fix
  AND currency = 'USD';    -- Bug 3 fix (simple version)


-- OPTION B: If you DO need item data, aggregate items first with a subquery
WITH order_items_agg AS (
    SELECT 
        order_id, 
        COUNT(*) AS item_count,
        SUM(quantity * unit_price) AS items_total
    FROM raw_order_items
    GROUP BY order_id
)
SELECT
    report_date,
    SUM(o.amount) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS order_count,
    AVG(o.amount) AS avg_order_value
FROM raw_orders o
LEFT JOIN order_items_agg oi ON o.order_id = oi.order_id
WHERE ...
```
</details>

<details>
<summary>🔧 Solution — Bug 3: Currency Mixing (USD + VND)</summary>

**Root cause:** Source system added `currency` field. Pipeline assumes all amounts are USD.

**Fix:** Convert VND to USD before aggregation.

```sql
-- Fix: Normalize all amounts to USD
SELECT
    report_date,
    SUM(CASE 
        WHEN currency = 'VND' THEN amount / 25000.0  -- VND → USD conversion
        WHEN currency = 'USD' THEN amount
        ELSE amount  -- Unknown currency → log warning
    END) AS total_revenue_usd,
    COUNT(DISTINCT order_id) AS order_count
FROM raw_orders
WHERE ...

-- BETTER FIX: Add a DQ check that alerts on new currencies
-- so you don't miss EUR, GBP, etc. in the future
SELECT DISTINCT currency 
FROM raw_orders 
WHERE currency NOT IN ('USD', 'VND');
-- If this returns rows → unknown currency detected → alert on-call
```
</details>

<details>
<summary>🔧 Solution — Bug 4: Timezone Bug</summary>

**Root cause:** `CURRENT_DATE` is UTC. Business is Vietnam (UTC+7). Orders between midnight-7AM UTC appear as "tomorrow."

**Fix:** Use timezone-aware date functions.

```sql
-- WRONG (UTC):
WHERE DATE(order_date) = CURRENT_DATE

-- RIGHT (Vietnam timezone):
WHERE DATE(order_date AT TIME ZONE 'Asia/Ho_Chi_Minh') 
      = (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE

-- Or with explicit timezone variable:
SET timezone = 'Asia/Ho_Chi_Minh';
WHERE DATE(order_date) = CURRENT_DATE;  -- Now CURRENT_DATE is Vietnam time
```

```python
# In the Python extractor — also fix timezone:
from datetime import datetime
import pytz

# WRONG:
# target_date = datetime.now().strftime("%Y-%m-%d")  # Server timezone

# RIGHT:
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
target_date = datetime.now(vn_tz).strftime("%Y-%m-%d")
```
</details>

<details>
<summary>🔧 Solution — Bug 5: Connection Leak</summary>

**Root cause:** `psycopg2.connect()` opens connections that are never closed.

**Fix:** Use context manager pattern.

```python
# FIXED extract.py — proper connection handling

import psycopg2
from contextlib import contextmanager

@contextmanager
def get_connection():
    """Context manager for database connections — auto-closes."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()  # ALWAYS closes, even if exception occurs


def extract_orders(target_date: str) -> list:
    """Extract orders with proper connection handling."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            query = """
                SELECT order_id, customer_id, order_date,
                       amount, currency, status
                FROM raw_orders
                WHERE DATE(order_date AT TIME ZONE 'Asia/Ho_Chi_Minh') 
                      = %(target_date)s::DATE
                  AND status = 'completed'
                  AND order_date <= NOW()
            """
            cursor.execute(query, {"target_date": target_date})
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
    
    # Connection is already closed here
    results = []
    for row in rows:
        record = dict(zip(columns, row))
        record["order_date"] = record["order_date"].isoformat()
        results.append(record)
    
    print(f"Extracted {len(results)} orders for {target_date}")
    return results


# EVEN BETTER: Use a connection pool for production
from psycopg2 import pool

connection_pool = pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    **DB_CONFIG
)

def extract_with_pool(query: str, params: dict = None) -> list:
    """Extract using connection pool — production pattern."""
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        connection_pool.putconn(conn)  # Return to pool, don't close
```
</details>

<details>
<summary>🔧 Solution — Bug 6: Non-Idempotent INSERT</summary>

**Root cause:** `INSERT INTO analytics_daily_revenue` with no deduplication. Airflow retries = duplicate rows.

**Fix:** DELETE-then-INSERT or UPSERT pattern.

```sql
-- FIXED transform_orders.sql — Idempotent write

-- Strategy: DELETE today's data first, then INSERT
-- Run this 1x or 100x → same result

BEGIN;

-- Step 1: Delete today's data (if exists from previous run)
DELETE FROM analytics_daily_revenue
WHERE report_date = (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE;

-- Step 2: Insert fresh calculation
INSERT INTO analytics_daily_revenue (report_date, total_revenue, order_count, avg_order_value)
SELECT
    (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE AS report_date,
    
    SUM(CASE 
        WHEN currency = 'VND' THEN amount / 25000.0
        ELSE amount 
    END) AS total_revenue,
    
    COUNT(DISTINCT order_id) AS order_count,
    
    AVG(CASE 
        WHEN currency = 'VND' THEN amount / 25000.0
        ELSE amount 
    END) AS avg_order_value

FROM raw_orders
WHERE DATE(order_date AT TIME ZONE 'Asia/Ho_Chi_Minh') 
      = (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE
  AND status = 'completed'
  AND order_date <= NOW()
  AND currency IN ('USD', 'VND');

-- Step 3: Same for users table
DELETE FROM analytics_daily_users
WHERE report_date = (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE;

INSERT INTO analytics_daily_users (report_date, active_users, new_users)
SELECT
    (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE AS report_date,
    
    COUNT(DISTINCT c.customer_id) AS active_users,
    
    COUNT(DISTINCT CASE 
        WHEN DATE(c.created_at AT TIME ZONE 'Asia/Ho_Chi_Minh') 
             = (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE 
        THEN c.customer_id 
    END) AS new_users

FROM raw_customers c
JOIN raw_orders o ON c.customer_id = o.customer_id
WHERE DATE(o.order_date AT TIME ZONE 'Asia/Ho_Chi_Minh') 
      = (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE
  AND o.status = 'completed'
  AND o.order_date <= NOW();

COMMIT;
```
</details>

---

## 📝 Deliverables

### Phase 1: Triage (30 minutes)

Write a triage report before touching any code:

```markdown
# Triage Report — E-commerce Pipeline
## Date: [today]
## Reported by: CFO (revenue = $0), Marketing (users -90%), Airflow (DAG failed)

### Severity: P1 (Critical)
Revenue dashboard showing $0 affects CFO daily report to board.

### Immediate Impact:
- CFO cannot report accurate revenue
- Marketing cannot track campaign performance
- Daily metrics email shows wrong numbers

### Quick Mitigation (while debugging):
- Notify CFO: "Investigating, ETA 2 hours"
- Check yesterday's data in DB directly → if correct, dashboard likely 
  showing wrong date, not actual data loss
- Do NOT try to hot-fix in production without understanding root cause

### Initial Hypothesis:
- $0 revenue → likely a filter/date bug (data exists but query misses it)
- 90% user drop → likely a query change, not actual user loss
- DAG failure → SQL error in transform step
```

### Phase 2: Debug & Fix (2-4 hours per bug)

For each bug, document:
1. **Symptom** — what you saw
2. **Root cause** — what actually went wrong  
3. **Fix** — code change
4. **Verification** — how you confirmed the fix works

### Phase 3: Prevention (1-2 days)

Add monitoring for each failure mode:

```python
# monitoring.py — Prevent these bugs from recurring

data_quality_checks = {
    "no_future_dates": {
        "sql": "SELECT COUNT(*) FROM raw_orders WHERE order_date > NOW()",
        "threshold": 0,
        "action": "alert",
    },
    "revenue_not_zero": {
        "sql": "SELECT total_revenue FROM analytics_daily_revenue WHERE report_date = CURRENT_DATE",
        "threshold": 0,
        "action": "page_oncall",
    },
    "revenue_anomaly": {
        "sql": """
            SELECT CASE WHEN today < avg_7d * 0.5 THEN 1 ELSE 0 END
            FROM (
                SELECT 
                    (SELECT total_revenue FROM analytics_daily_revenue 
                     WHERE report_date = CURRENT_DATE) as today,
                    (SELECT AVG(total_revenue) FROM analytics_daily_revenue 
                     WHERE report_date >= CURRENT_DATE - 7) as avg_7d
            ) t
        """,
        "threshold": 0,
        "action": "alert",
    },
    "unknown_currency": {
        "sql": "SELECT COUNT(*) FROM raw_orders WHERE currency NOT IN ('USD', 'VND')",
        "threshold": 0,
        "action": "alert",
    },
    "connection_count": {
        "sql": "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'",
        "threshold": 50,
        "action": "alert",
    },
}
```

### Phase 4: Postmortem

```markdown
# Postmortem: E-commerce Pipeline Failures

## Date: [today]
## Author: [you]
## Duration of incident: [start] to [end]
## Severity: P1

## Summary
6 bugs simultaneously caused $0 revenue on dashboard and 90% user count drop.

## Impact
- CFO received incorrect board report
- Marketing paused 2 campaigns due to false "user decline"
- 4 hours of engineering time to diagnose and fix

## Root Causes
1. Test data with future dates in production database
2. Cartesian product JOIN inflating revenue by 3x
3. Mixed currencies (VND treated as USD amounts)
4. UTC timezone instead of Vietnam (UTC+7)
5. Connection leak in Python extractor
6. Non-idempotent INSERTs causing duplicates on retry

## What Went Well
- [list things]

## What Went Wrong
- No data quality checks caught any of these issues
- No monitoring for anomalous revenue values
- Pipeline had been running with bugs for days (nobody noticed until $0)

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Add DQ checks for all 6 failure modes | @you | [date] | TODO |
| Add revenue anomaly alerting | @you | [date] | TODO |
| Implement connection pooling | @you | [date] | TODO |
| Add timezone tests to CI | @you | [date] | TODO |
| Review all date filters for timezone handling | @team | [date] | TODO |
```

---

## 🎯 Learning Outcomes

| Skill | How you practice it |
|-------|-------------------|
| **Debugging** | Find 6 bugs from symptoms, not from code review |
| **Incident response** | Triage, communicate, fix under pressure |
| **SQL debugging** | Fix join logic, timezone, aggregation errors |
| **Data quality** | Add DQ checks that prevent recurrence |
| **Idempotency** | Convert INSERT to DELETE+INSERT pattern |
| **Connection management** | Context managers, connection pools |
| **Postmortem writing** | Blameless analysis with action items |

---

## 🔗 Related Files

- [21_Debugging_Troubleshooting](../fundamentals/21_Debugging_Troubleshooting.md) — debugging framework
- [22_Schema_Evolution](../fundamentals/22_Schema_Evolution_Migration.md) — handling schema drift
- [11_Testing_CICD](../fundamentals/11_Testing_CICD.md) — preventing bugs with tests
- [01_Design_Patterns](../mindset/01_Design_Patterns.md) — Idempotency, Circuit Breaker, DLQ patterns

---

*Fixing bugs teaches more than building features. This project simulates your real first week on the job.*

*Updated: February 2026*
