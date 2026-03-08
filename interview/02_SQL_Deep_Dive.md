# 💾 SQL Deep Dive - Interview Questions

> Câu hỏi SQL nâng cao thường gặp trong phỏng vấn Data Engineer

---

## 📚 Mục Lục

1. [Window Functions](#-window-functions)
2. [CTEs & Recursive Queries](#-ctes--recursive-queries)
3. [Performance & Optimization](#-performance--optimization)
4. [Complex Joins](#-complex-joins)
5. [Data Manipulation](#-data-manipulation)
6. [Real-world Problems](#-real-world-problems)

---

## 🪟 Window Functions

### Q1: Running Total và Moving Average

**Question:** Tính running total và 7-day moving average của sales

```sql
SELECT 
    date,
    sales,
    -- Running total
    SUM(sales) OVER (
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    
    -- 7-day moving average
    AVG(sales) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d,
    
    -- Year-to-date
    SUM(sales) OVER (
        PARTITION BY EXTRACT(YEAR FROM date)
        ORDER BY date
    ) AS ytd_sales
FROM daily_sales;
```

### Q2: RANK vs DENSE_RANK vs ROW_NUMBER

**Question:** Giải thích sự khác biệt với ví dụ

```sql
SELECT 
    name,
    score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS row_num,
    RANK() OVER (ORDER BY score DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank
FROM students;

-- Result:
-- name    | score | row_num | rank | dense_rank
-- Alice   | 100   | 1       | 1    | 1
-- Bob     | 100   | 2       | 1    | 1          ← Same score
-- Charlie | 95    | 3       | 3    | 2          ← rank=3, dense_rank=2
-- David   | 90    | 4       | 4    | 3
```

**Differences:**
- **ROW_NUMBER:** Unique number, no ties
- **RANK:** Same rank for ties, skips numbers
- **DENSE_RANK:** Same rank for ties, no skips

### Q3: LEAD và LAG

**Question:** Tính percentage change so với ngày trước

```sql
SELECT 
    date,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY date) AS prev_day,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) AS change,
    ROUND(
        (revenue - LAG(revenue, 1) OVER (ORDER BY date)) 
        / NULLIF(LAG(revenue, 1) OVER (ORDER BY date), 0) * 100, 
        2
    ) AS pct_change,
    -- Next day preview
    LEAD(revenue, 1) OVER (ORDER BY date) AS next_day
FROM daily_revenue;
```

### Q4: FIRST_VALUE và LAST_VALUE

**Question:** So sánh mỗi giá trị với min/max trong partition

```sql
SELECT 
    department,
    employee,
    salary,
    FIRST_VALUE(salary) OVER (
        PARTITION BY department 
        ORDER BY salary
    ) AS min_salary,
    LAST_VALUE(salary) OVER (
        PARTITION BY department 
        ORDER BY salary
        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS max_salary,
    salary - FIRST_VALUE(salary) OVER (
        PARTITION BY department 
        ORDER BY salary
    ) AS diff_from_min
FROM employees;
```

### Q5: NTILE - Phân chia thành buckets

**Question:** Chia customers thành 4 quartiles theo spending

```sql
SELECT 
    customer_id,
    total_spending,
    NTILE(4) OVER (ORDER BY total_spending DESC) AS quartile,
    CASE NTILE(4) OVER (ORDER BY total_spending DESC)
        WHEN 1 THEN 'Top 25%'
        WHEN 2 THEN '25-50%'
        WHEN 3 THEN '50-75%'
        WHEN 4 THEN 'Bottom 25%'
    END AS segment
FROM customer_summary;
```

---

## 🔄 CTEs & Recursive Queries

### Q6: Basic CTE

**Question:** Tìm customers có orders > average

```sql
WITH order_summary AS (
    SELECT 
        customer_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_amount
    FROM orders
    GROUP BY customer_id
),
average_stats AS (
    SELECT 
        AVG(order_count) AS avg_orders,
        AVG(total_amount) AS avg_amount
    FROM order_summary
)
SELECT 
    os.customer_id,
    os.order_count,
    os.total_amount
FROM order_summary os
CROSS JOIN average_stats a
WHERE os.order_count > a.avg_orders
   OR os.total_amount > a.avg_amount;
```

### Q7: Recursive CTE - Employee Hierarchy

**Question:** Lấy org chart với all levels từ CEO xuống

```sql
WITH RECURSIVE employee_hierarchy AS (
    -- Base case: CEO (no manager)
    SELECT 
        id,
        name,
        manager_id,
        1 AS level,
        name AS path
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case
    SELECT 
        e.id,
        e.name,
        e.manager_id,
        eh.level + 1,
        eh.path || ' > ' || e.name
    FROM employees e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy
ORDER BY level, name;
```

### Q8: Recursive CTE - Date Series

**Question:** Generate date series cho missing dates

```sql
WITH RECURSIVE date_series AS (
    SELECT DATE '2024-01-01' AS date
    UNION ALL
    SELECT date + INTERVAL '1 day'
    FROM date_series
    WHERE date < DATE '2024-12-31'
)
SELECT 
    ds.date,
    COALESCE(s.sales, 0) AS sales
FROM date_series ds
LEFT JOIN sales s ON ds.date = s.date
ORDER BY ds.date;
```

---

## ⚡ Performance & Optimization

### Q9: Explain Query Execution Plan

**Question:** Giải thích EXPLAIN output và cách optimize

```sql
EXPLAIN ANALYZE
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE c.created_at > '2024-01-01'
GROUP BY c.id, c.name
HAVING COUNT(o.id) > 5;
```

**Key things to look for:**
```
1. Seq Scan vs Index Scan
   - Seq Scan on large tables = bad
   - Add index on frequently filtered columns

2. Nested Loop vs Hash Join vs Merge Join
   - Nested Loop: Good for small tables
   - Hash Join: Good for equality joins
   - Merge Join: Good for sorted data

3. Rows estimated vs actual
   - Big difference = statistics outdated
   - Run ANALYZE table

4. Sort operations
   - Expensive for large datasets
   - Consider index for ORDER BY columns
```

### Q10: Index Optimization

**Question:** Khi nào nên và không nên dùng index?

**When to use:**
```sql
-- Columns in WHERE clause
CREATE INDEX idx_customer_email ON customers(email);

-- Columns in JOIN
CREATE INDEX idx_order_customer ON orders(customer_id);

-- Columns in ORDER BY
CREATE INDEX idx_order_date ON orders(created_at DESC);

-- Composite index for multiple columns
CREATE INDEX idx_composite ON orders(customer_id, status, created_at);
```

**When NOT to use:**
- Small tables (< 1000 rows)
- Columns with low cardinality
- Tables with heavy write operations
- Columns rarely used in queries

**Partial Index:**
```sql
-- Index only for active records
CREATE INDEX idx_active_users 
ON users(email) 
WHERE status = 'active';
```

### Q11: Query Optimization Techniques

**Question:** Optimize slow query này

```sql
-- Before (slow)
SELECT *
FROM orders o
WHERE o.customer_id IN (
    SELECT id FROM customers WHERE country = 'US'
);

-- After (optimized)
SELECT o.*
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
WHERE c.country = 'US';

-- Or with EXISTS (often faster for correlated)
SELECT o.*
FROM orders o
WHERE EXISTS (
    SELECT 1 FROM customers c 
    WHERE c.id = o.customer_id AND c.country = 'US'
);
```

**General tips:**
```
1. SELECT only needed columns, not *
2. Use LIMIT for testing
3. Avoid functions on indexed columns in WHERE
   Bad:  WHERE YEAR(date) = 2024
   Good: WHERE date >= '2024-01-01' AND date < '2025-01-01'
4. Use EXISTS instead of COUNT(*) > 0
5. Batch large updates/deletes
```

---

## 🔗 Complex Joins

### Q12: Self Join - Find Duplicates

**Question:** Tìm duplicate records với cùng email nhưng khác ID

```sql
SELECT 
    a.id AS id1,
    b.id AS id2,
    a.email
FROM users a
INNER JOIN users b ON a.email = b.email
WHERE a.id < b.id;
```

### Q13: Anti Join - Records without Match

**Question:** Tìm customers chưa có orders

```sql
-- Method 1: LEFT JOIN + NULL
SELECT c.*
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL;

-- Method 2: NOT EXISTS (often faster)
SELECT c.*
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- Method 3: NOT IN (careful with NULLs!)
SELECT c.*
FROM customers c
WHERE c.id NOT IN (
    SELECT customer_id FROM orders WHERE customer_id IS NOT NULL
);
```

### Q14: Multiple Aggregations

**Question:** Sales summary by multiple dimensions

```sql
SELECT 
    COALESCE(region, 'ALL') AS region,
    COALESCE(product_category, 'ALL') AS category,
    COALESCE(CAST(EXTRACT(YEAR FROM date) AS VARCHAR), 'ALL') AS year,
    SUM(amount) AS total_sales,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM sales
GROUP BY GROUPING SETS (
    (region, product_category, EXTRACT(YEAR FROM date)),
    (region, product_category),
    (region),
    ()
)
ORDER BY region NULLS LAST, category NULLS LAST;
```

---

## ✏️ Data Manipulation

### Q15: UPSERT/MERGE

**Question:** Insert or update record

```sql
-- PostgreSQL
INSERT INTO inventory (product_id, quantity, updated_at)
VALUES (101, 50, NOW())
ON CONFLICT (product_id) 
DO UPDATE SET 
    quantity = inventory.quantity + EXCLUDED.quantity,
    updated_at = EXCLUDED.updated_at;

-- Standard SQL MERGE
MERGE INTO inventory t
USING (SELECT 101 AS product_id, 50 AS quantity) s
ON t.product_id = s.product_id
WHEN MATCHED THEN 
    UPDATE SET quantity = t.quantity + s.quantity
WHEN NOT MATCHED THEN 
    INSERT (product_id, quantity) VALUES (s.product_id, s.quantity);
```

### Q16: Pivot Table

**Question:** Chuyển rows thành columns

```sql
-- Raw data
-- month   | product | sales
-- Jan     | A       | 100
-- Jan     | B       | 200
-- Feb     | A       | 150

-- Pivot
SELECT 
    month,
    SUM(CASE WHEN product = 'A' THEN sales ELSE 0 END) AS product_a,
    SUM(CASE WHEN product = 'B' THEN sales ELSE 0 END) AS product_b,
    SUM(CASE WHEN product = 'C' THEN sales ELSE 0 END) AS product_c
FROM sales
GROUP BY month;
```

### Q17: Unpivot Table

**Question:** Chuyển columns thành rows

```sql
-- Pivoted data
-- month | product_a | product_b
-- Jan   | 100       | 200

-- Unpivot
SELECT month, 'A' AS product, product_a AS sales FROM monthly_sales
UNION ALL
SELECT month, 'B' AS product, product_b AS sales FROM monthly_sales
UNION ALL
SELECT month, 'C' AS product, product_c AS sales FROM monthly_sales;
```

---

## 🌍 Real-world Problems

### Q18: Consecutive Login Days

**Question:** Tìm users có streak login 7 ngày liên tiếp

```sql
WITH login_dates AS (
    SELECT DISTINCT user_id, DATE(login_time) AS login_date
    FROM logins
),
date_groups AS (
    SELECT 
        user_id,
        login_date,
        login_date - INTERVAL '1 day' * ROW_NUMBER() OVER (
            PARTITION BY user_id ORDER BY login_date
        ) AS grp
    FROM login_dates
),
streaks AS (
    SELECT 
        user_id,
        grp,
        COUNT(*) AS streak_length,
        MIN(login_date) AS streak_start,
        MAX(login_date) AS streak_end
    FROM date_groups
    GROUP BY user_id, grp
)
SELECT * FROM streaks WHERE streak_length >= 7;
```

### Q19: Sessionization

**Question:** Group events into sessions (30 min gap = new session)

```sql
WITH events_with_prev AS (
    SELECT 
        user_id,
        event_time,
        LAG(event_time) OVER (
            PARTITION BY user_id ORDER BY event_time
        ) AS prev_event_time
    FROM user_events
),
session_starts AS (
    SELECT 
        user_id,
        event_time,
        CASE 
            WHEN prev_event_time IS NULL THEN 1
            WHEN event_time - prev_event_time > INTERVAL '30 minutes' THEN 1
            ELSE 0
        END AS is_session_start
    FROM events_with_prev
),
sessions AS (
    SELECT 
        user_id,
        event_time,
        SUM(is_session_start) OVER (
            PARTITION BY user_id ORDER BY event_time
        ) AS session_id
    FROM session_starts
)
SELECT 
    user_id,
    session_id,
    MIN(event_time) AS session_start,
    MAX(event_time) AS session_end,
    COUNT(*) AS event_count
FROM sessions
GROUP BY user_id, session_id;
```

### Q20: Funnel Analysis

**Question:** Tính conversion rate qua các steps

```sql
WITH funnel AS (
    SELECT 
        user_id,
        MAX(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) AS step1,
        MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS step2,
        MAX(CASE WHEN event_type = 'checkout' THEN 1 ELSE 0 END) AS step3,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS step4
    FROM events
    WHERE date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY user_id
)
SELECT 
    'Page View' AS step,
    SUM(step1) AS users,
    100.0 AS conversion_pct
FROM funnel
UNION ALL
SELECT 
    'Add to Cart',
    SUM(step2),
    ROUND(100.0 * SUM(step2) / NULLIF(SUM(step1), 0), 2)
FROM funnel
UNION ALL
SELECT 
    'Checkout',
    SUM(step3),
    ROUND(100.0 * SUM(step3) / NULLIF(SUM(step1), 0), 2)
FROM funnel
UNION ALL
SELECT 
    'Purchase',
    SUM(step4),
    ROUND(100.0 * SUM(step4) / NULLIF(SUM(step1), 0), 2)
FROM funnel;
```

---

## 💡 SQL Interview Tips

**Practice Resources:**
- LeetCode SQL problems
- HackerRank SQL challenges
- Mode Analytics tutorials

**Common Mistakes:**
1. Forgetting NULL handling
2. Not understanding GROUP BY requirements
3. Misusing window function frames
4. Not considering index performance

**Best Practices:**
- Write readable SQL with good formatting
- Add comments for complex logic
- Test with edge cases (empty, NULL, duplicates)
- Consider performance from the start

---

## 🔗 Liên Kết

- [Common Interview Questions](01_Common_Interview_Questions.md)
- [System Design Questions](03_System_Design.md)
- [Fundamentals - SQL](../fundamentals/05_SQL_Mastery.md)

---

*Cập nhật: February 2026*
