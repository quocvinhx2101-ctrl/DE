# SQL Mastery Guide - Complete Reference

## Advanced SQL, Query Optimization, và Performance Tuning

---

## PHẦN 1: SQL FUNDAMENTALS RECAP

### 1.1 SQL Là Gì?

SQL (Structured Query Language) là ngôn ngữ tiêu chuẩn để tương tác với relational databases. Mọi Data Engineer phải master SQL vì đây là core skill.

**SQL Categories:**
- **DDL (Data Definition Language)** - CREATE, ALTER, DROP, TRUNCATE
- **DML (Data Manipulation Language)** - SELECT, INSERT, UPDATE, DELETE
- **DCL (Data Control Language)** - GRANT, REVOKE
- **TCL (Transaction Control Language)** - COMMIT, ROLLBACK, SAVEPOINT

### 1.2 Query Execution Order

Hiểu thứ tự thực thi SQL rất quan trọng để viết queries hiệu quả:

```
Logical Execution Order:
1. FROM        - Xác định source tables
2. JOIN        - Combine tables
3. WHERE       - Filter rows BEFORE grouping
4. GROUP BY    - Group rows
5. HAVING      - Filter groups AFTER grouping
6. SELECT      - Select columns
7. DISTINCT    - Remove duplicates
8. ORDER BY    - Sort results
9. LIMIT       - Limit output rows

Written Order:
SELECT ... FROM ... JOIN ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT
```

**Ví dụ minh họa:**

```sql
SELECT 
    department,                    -- Step 6
    COUNT(*) as emp_count          -- Step 6
FROM employees                     -- Step 1
JOIN departments                   -- Step 2
    ON employees.dept_id = departments.id
WHERE hire_date >= '2020-01-01'   -- Step 3
GROUP BY department                -- Step 4
HAVING COUNT(*) > 5               -- Step 5
ORDER BY emp_count DESC           -- Step 7
LIMIT 10;                         -- Step 8
```

---

## PHẦN 2: ADVANCED JOINS

### 2.1 Join Types

**INNER JOIN:**
- Chỉ trả về rows match cả hai tables

```sql
SELECT 
    o.order_id,
    c.customer_name,
    o.total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id;

-- Venn diagram:
--     A       B
--   (   [###]   )
--       ^^^
--    Only matching rows
```

**LEFT JOIN (LEFT OUTER JOIN):**
- Tất cả rows từ left table
- Matching rows từ right table
- NULL nếu không match

```sql
SELECT 
    c.customer_name,
    o.order_id,
    COALESCE(o.total_amount, 0) as total_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- Venn diagram:
--     A       B
--   (###[###]   )
--    ^^^^^^^^
--    All A + matching B
```

**RIGHT JOIN (RIGHT OUTER JOIN):**
- Ngược lại với LEFT JOIN
- Tất cả rows từ right table

```sql
SELECT 
    o.order_id,
    c.customer_name
FROM orders o
RIGHT JOIN customers c ON o.customer_id = c.customer_id;
```

**FULL OUTER JOIN:**
- Tất cả rows từ cả hai tables

```sql
SELECT 
    c.customer_name,
    o.order_id
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;

-- Venn diagram:
--     A       B
--   (###[###]###)
--    ^^^^^^^^^^^
--    All from both
```

**CROSS JOIN:**
- Cartesian product
- Mỗi row của A kết hợp với mỗi row của B

```sql
SELECT 
    p.product_name,
    c.color_name
FROM products p
CROSS JOIN colors c;

-- 3 products x 4 colors = 12 rows
```

### 2.2 Self Join

Join table với chính nó:

```sql
-- Find employees and their managers
SELECT 
    e.employee_name,
    m.employee_name as manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id;

-- Find pairs of customers in same city
SELECT 
    c1.customer_name as customer1,
    c2.customer_name as customer2,
    c1.city
FROM customers c1
JOIN customers c2 
    ON c1.city = c2.city 
    AND c1.customer_id < c2.customer_id;  -- Avoid duplicates
```

### 2.3 Anti Join và Semi Join

**Anti Join - Rows in A but NOT in B:**

```sql
-- Method 1: LEFT JOIN + IS NULL
SELECT c.*
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- Method 2: NOT EXISTS (often faster)
SELECT c.*
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.customer_id
);

-- Method 3: NOT IN (be careful with NULLs!)
SELECT c.*
FROM customers c
WHERE c.customer_id NOT IN (
    SELECT customer_id FROM orders WHERE customer_id IS NOT NULL
);
```

**Semi Join - Rows in A that have match in B (no duplicates):**

```sql
-- Method 1: EXISTS (preferred)
SELECT c.*
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.customer_id
);

-- Method 2: IN
SELECT c.*
FROM customers c
WHERE c.customer_id IN (
    SELECT customer_id FROM orders
);

-- Method 3: JOIN + DISTINCT (less efficient)
SELECT DISTINCT c.*
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;
```

### 2.4 Lateral Join

Cho phép subquery reference outer query columns:

```sql
-- Get top 3 orders for each customer
SELECT 
    c.customer_name,
    top_orders.order_id,
    top_orders.total_amount
FROM customers c
CROSS JOIN LATERAL (
    SELECT order_id, total_amount
    FROM orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY total_amount DESC
    LIMIT 3
) top_orders;

-- Alternative using ROW_NUMBER (more portable)
WITH ranked_orders AS (
    SELECT 
        customer_id,
        order_id,
        total_amount,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id 
            ORDER BY total_amount DESC
        ) as rn
    FROM orders
)
SELECT 
    c.customer_name,
    ro.order_id,
    ro.total_amount
FROM customers c
JOIN ranked_orders ro 
    ON c.customer_id = ro.customer_id 
    AND ro.rn <= 3;
```

---

## PHẦN 3: COMMON TABLE EXPRESSIONS (CTEs)

### 3.1 Basic CTE

```sql
WITH active_customers AS (
    SELECT 
        customer_id,
        customer_name,
        email
    FROM customers
    WHERE status = 'active'
        AND last_purchase_date >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT 
    ac.customer_name,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent
FROM active_customers ac
JOIN orders o ON ac.customer_id = o.customer_id
GROUP BY ac.customer_name;
```

### 3.2 Multiple CTEs

```sql
WITH 
monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        SUM(total_amount) as revenue
    FROM orders
    WHERE order_date >= '2024-01-01'
    GROUP BY DATE_TRUNC('month', order_date)
),
monthly_growth AS (
    SELECT 
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) as prev_revenue,
        revenue - LAG(revenue) OVER (ORDER BY month) as growth,
        ROUND(
            (revenue - LAG(revenue) OVER (ORDER BY month)) 
            / LAG(revenue) OVER (ORDER BY month) * 100, 
            2
        ) as growth_pct
    FROM monthly_sales
)
SELECT 
    month,
    revenue,
    growth,
    growth_pct,
    CASE 
        WHEN growth_pct > 10 THEN 'Strong Growth'
        WHEN growth_pct > 0 THEN 'Moderate Growth'
        WHEN growth_pct < 0 THEN 'Decline'
        ELSE 'No Change'
    END as trend
FROM monthly_growth
ORDER BY month;
```

### 3.3 Recursive CTE

**Hierarchy traversal:**

```sql
-- Employee hierarchy
WITH RECURSIVE emp_hierarchy AS (
    -- Base case: top-level managers (no manager)
    SELECT 
        employee_id,
        employee_name,
        manager_id,
        1 as level,
        employee_name::TEXT as path
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: employees with managers
    SELECT 
        e.employee_id,
        e.employee_name,
        e.manager_id,
        h.level + 1,
        h.path || ' > ' || e.employee_name
    FROM employees e
    JOIN emp_hierarchy h ON e.manager_id = h.employee_id
)
SELECT * FROM emp_hierarchy
ORDER BY path;
```

**Number sequences:**

```sql
-- Generate date series
WITH RECURSIVE date_series AS (
    SELECT DATE '2024-01-01' as date
    
    UNION ALL
    
    SELECT date + INTERVAL '1 day'
    FROM date_series
    WHERE date < '2024-12-31'
)
SELECT date FROM date_series;

-- Better alternative (PostgreSQL):
SELECT generate_series(
    '2024-01-01'::DATE,
    '2024-12-31'::DATE,
    '1 day'::INTERVAL
) as date;
```

**Graph traversal:**

```sql
-- Find all connected nodes (friends of friends)
WITH RECURSIVE connections AS (
    -- Direct friends of user 1
    SELECT 
        user_id,
        friend_id,
        1 as degree
    FROM friendships
    WHERE user_id = 1
    
    UNION
    
    -- Friends of friends (up to 3 degrees)
    SELECT 
        c.user_id,
        f.friend_id,
        c.degree + 1
    FROM connections c
    JOIN friendships f ON c.friend_id = f.user_id
    WHERE c.degree < 3
        AND f.friend_id != 1  -- Avoid cycles back to start
)
SELECT DISTINCT friend_id, MIN(degree) as closest_degree
FROM connections
GROUP BY friend_id
ORDER BY closest_degree;
```

---

## PHẦN 4: WINDOW FUNCTIONS

### 4.1 Window Function Anatomy

```sql
function_name(expression) OVER (
    [PARTITION BY partition_expression]
    [ORDER BY sort_expression [ASC|DESC]]
    [frame_clause]
)

Frame clause options:
- ROWS BETWEEN ... AND ...
- RANGE BETWEEN ... AND ...
- GROUPS BETWEEN ... AND ... (PostgreSQL 11+)

Frame boundaries:
- UNBOUNDED PRECEDING
- n PRECEDING
- CURRENT ROW
- n FOLLOWING
- UNBOUNDED FOLLOWING
```

### 4.2 Ranking Functions

**ROW_NUMBER - Unique sequential numbers:**

```sql
SELECT 
    product_name,
    category,
    price,
    ROW_NUMBER() OVER (
        PARTITION BY category 
        ORDER BY price DESC
    ) as price_rank
FROM products;

-- Results:
-- Electronics: Laptop (1), Phone (2), Tablet (3)
-- Clothing: Jacket (1), Shirt (2), Pants (3)
```

**RANK - Same rank for ties, gaps after:**

```sql
SELECT 
    student_name,
    score,
    RANK() OVER (ORDER BY score DESC) as rank
FROM exam_results;

-- Scores: 100, 95, 95, 90
-- Ranks:  1,   2,  2,  4  (gap at 3)
```

**DENSE_RANK - Same rank for ties, no gaps:**

```sql
SELECT 
    student_name,
    score,
    DENSE_RANK() OVER (ORDER BY score DESC) as dense_rank
FROM exam_results;

-- Scores: 100, 95, 95, 90
-- Ranks:  1,   2,  2,  3  (no gap)
```

**NTILE - Divide into buckets:**

```sql
SELECT 
    customer_name,
    total_purchases,
    NTILE(4) OVER (ORDER BY total_purchases DESC) as quartile
FROM customer_summary;

-- Quartile 1: Top 25% spenders
-- Quartile 4: Bottom 25% spenders
```

**PERCENT_RANK và CUME_DIST:**

```sql
SELECT 
    product_name,
    price,
    PERCENT_RANK() OVER (ORDER BY price) as pct_rank,
    CUME_DIST() OVER (ORDER BY price) as cume_dist
FROM products;

-- PERCENT_RANK: (rank - 1) / (total rows - 1), range 0-1
-- CUME_DIST: rank / total rows, range > 0 to 1
```

### 4.3 Aggregate Window Functions

```sql
SELECT 
    order_date,
    daily_sales,
    
    -- Running total
    SUM(daily_sales) OVER (
        ORDER BY order_date
    ) as running_total,
    
    -- 7-day moving average
    AVG(daily_sales) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7d,
    
    -- Year-to-date total
    SUM(daily_sales) OVER (
        PARTITION BY EXTRACT(YEAR FROM order_date)
        ORDER BY order_date
    ) as ytd_sales,
    
    -- Percentage of total
    daily_sales / SUM(daily_sales) OVER () * 100 as pct_of_total,
    
    -- Percentage of category
    daily_sales / SUM(daily_sales) OVER (
        PARTITION BY category
    ) * 100 as pct_of_category

FROM daily_sales_summary;
```

### 4.4 Value Functions

**LAG và LEAD:**

```sql
SELECT 
    month,
    revenue,
    
    -- Previous month
    LAG(revenue, 1) OVER (ORDER BY month) as prev_month,
    
    -- 12 months ago (YoY comparison)
    LAG(revenue, 12) OVER (ORDER BY month) as same_month_last_year,
    
    -- Next month forecast comparison
    LEAD(revenue, 1) OVER (ORDER BY month) as next_month,
    
    -- Month-over-month growth
    revenue - LAG(revenue, 1) OVER (ORDER BY month) as mom_growth,
    
    -- Year-over-year growth
    revenue - LAG(revenue, 12) OVER (ORDER BY month) as yoy_growth

FROM monthly_revenue;

-- With default value for NULLs
LAG(revenue, 1, 0) OVER (ORDER BY month) as prev_month_or_zero
```

**FIRST_VALUE và LAST_VALUE:**

```sql
SELECT 
    employee_name,
    department,
    salary,
    
    -- Highest salary in department
    FIRST_VALUE(salary) OVER (
        PARTITION BY department 
        ORDER BY salary DESC
    ) as highest_in_dept,
    
    -- Lowest salary in department
    LAST_VALUE(salary) OVER (
        PARTITION BY department 
        ORDER BY salary DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as lowest_in_dept,
    
    -- Salary gap from highest
    FIRST_VALUE(salary) OVER (
        PARTITION BY department 
        ORDER BY salary DESC
    ) - salary as gap_from_highest

FROM employees;
```

**NTH_VALUE:**

```sql
SELECT 
    product_name,
    category,
    sales,
    
    -- Second highest sales in category
    NTH_VALUE(sales, 2) OVER (
        PARTITION BY category 
        ORDER BY sales DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as second_highest

FROM product_sales;
```

### 4.5 Frame Specifications

```sql
-- Default frame when ORDER BY present:
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW

-- Common frame specifications:

-- All rows in partition
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING

-- Current row only
ROWS BETWEEN CURRENT ROW AND CURRENT ROW

-- Trailing 7-day window
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW

-- Centered 7-day window
ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING

-- From start to current
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW

-- From current to end
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
```

**ROWS vs RANGE vs GROUPS:**

```sql
-- ROWS: Physical rows
SUM(amount) OVER (
    ORDER BY date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
)  -- Exactly 3 rows

-- RANGE: Logical range (same values grouped)
SUM(amount) OVER (
    ORDER BY date
    RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
)  -- All rows within 7 days

-- GROUPS: Groups of peers
SUM(amount) OVER (
    ORDER BY date
    GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW
)  -- Current group + 1 preceding group
```

---

## PHẦN 5: SUBQUERIES VÀ CORRELATED SUBQUERIES

### 5.1 Scalar Subquery

Returns single value:

```sql
SELECT 
    employee_name,
    salary,
    salary - (SELECT AVG(salary) FROM employees) as diff_from_avg,
    salary / (SELECT MAX(salary) FROM employees) * 100 as pct_of_max
FROM employees;
```

### 5.2 Table Subquery

Returns multiple rows/columns:

```sql
-- In FROM clause
SELECT 
    category,
    avg_price,
    product_count
FROM (
    SELECT 
        category,
        AVG(price) as avg_price,
        COUNT(*) as product_count
    FROM products
    GROUP BY category
) category_stats
WHERE product_count >= 10;
```

### 5.3 Correlated Subquery

References outer query - executes once per outer row:

```sql
-- Find employees earning more than department average
SELECT 
    e.employee_name,
    e.department,
    e.salary
FROM employees e
WHERE e.salary > (
    SELECT AVG(salary)
    FROM employees
    WHERE department = e.department  -- References outer query
);

-- Alternative with window function (often faster)
SELECT 
    employee_name,
    department,
    salary
FROM (
    SELECT 
        employee_name,
        department,
        salary,
        AVG(salary) OVER (PARTITION BY department) as dept_avg
    FROM employees
) with_avg
WHERE salary > dept_avg;
```

### 5.4 EXISTS vs IN

```sql
-- EXISTS: Stops at first match, handles NULLs well
SELECT c.*
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.customer_id
    AND o.total_amount > 1000
);

-- IN: Compares against full list
SELECT c.*
FROM customers c
WHERE c.customer_id IN (
    SELECT customer_id 
    FROM orders
    WHERE total_amount > 1000
);

-- Performance:
-- EXISTS often faster for large inner tables
-- IN often faster for small inner tables
-- EXISTS handles NULLs correctly; IN may give unexpected results
```

---

## PHẦN 6: SET OPERATIONS

### 6.1 UNION và UNION ALL

```sql
-- UNION: Combines and removes duplicates (slower)
SELECT product_name FROM products_us
UNION
SELECT product_name FROM products_eu;

-- UNION ALL: Keeps all rows including duplicates (faster)
SELECT product_name FROM products_us
UNION ALL
SELECT product_name FROM products_eu;

-- Use case: Combining data from multiple sources
SELECT 
    'Sales' as source,
    customer_id,
    amount,
    transaction_date
FROM sales
UNION ALL
SELECT 
    'Refunds' as source,
    customer_id,
    -amount,  -- Negative for refunds
    transaction_date
FROM refunds;
```

### 6.2 INTERSECT

Rows that appear in both queries:

```sql
-- Customers who bought both Product A and Product B
SELECT customer_id
FROM orders
WHERE product_id = 'A'
INTERSECT
SELECT customer_id
FROM orders
WHERE product_id = 'B';
```

### 6.3 EXCEPT (MINUS in Oracle)

Rows in first query but not in second:

```sql
-- Customers who bought A but never bought B
SELECT customer_id
FROM orders
WHERE product_id = 'A'
EXCEPT
SELECT customer_id
FROM orders
WHERE product_id = 'B';
```

---

## PHẦN 7: ADVANCED AGGREGATIONS

### 7.1 GROUPING SETS

```sql
-- Multiple grouping levels in one query
SELECT 
    COALESCE(region, 'All Regions') as region,
    COALESCE(category, 'All Categories') as category,
    SUM(sales) as total_sales
FROM sales
GROUP BY GROUPING SETS (
    (region, category),  -- By region and category
    (region),            -- By region only
    (category),          -- By category only
    ()                   -- Grand total
);

-- Equivalent to:
SELECT region, category, SUM(sales) FROM sales GROUP BY region, category
UNION ALL
SELECT region, NULL, SUM(sales) FROM sales GROUP BY region
UNION ALL
SELECT NULL, category, SUM(sales) FROM sales GROUP BY category
UNION ALL
SELECT NULL, NULL, SUM(sales) FROM sales;
```

### 7.2 ROLLUP

Hierarchical subtotals:

```sql
SELECT 
    region,
    country,
    city,
    SUM(sales) as total_sales
FROM sales
GROUP BY ROLLUP (region, country, city);

-- Generates:
-- (region, country, city)  - Detail rows
-- (region, country, NULL)  - Subtotal by region+country
-- (region, NULL, NULL)     - Subtotal by region
-- (NULL, NULL, NULL)       - Grand total
```

### 7.3 CUBE

All possible combinations:

```sql
SELECT 
    region,
    product,
    SUM(sales) as total_sales
FROM sales
GROUP BY CUBE (region, product);

-- Generates:
-- (region, product)   - By both
-- (region, NULL)      - By region only
-- (NULL, product)     - By product only
-- (NULL, NULL)        - Grand total
```

### 7.4 GROUPING Function

Identify which columns are aggregated:

```sql
SELECT 
    region,
    product,
    SUM(sales) as total_sales,
    GROUPING(region) as is_region_total,
    GROUPING(product) as is_product_total,
    CASE 
        WHEN GROUPING(region) = 1 AND GROUPING(product) = 1 THEN 'Grand Total'
        WHEN GROUPING(region) = 1 THEN 'Product Total'
        WHEN GROUPING(product) = 1 THEN 'Region Total'
        ELSE 'Detail'
    END as row_type
FROM sales
GROUP BY CUBE (region, product);
```

---

## PHẦN 8: ADVANCED TECHNIQUES

### 8.1 Pivoting Data

**Manual Pivot:**

```sql
-- From rows to columns
SELECT 
    product,
    SUM(CASE WHEN month = 'Jan' THEN sales ELSE 0 END) as jan_sales,
    SUM(CASE WHEN month = 'Feb' THEN sales ELSE 0 END) as feb_sales,
    SUM(CASE WHEN month = 'Mar' THEN sales ELSE 0 END) as mar_sales
FROM monthly_sales
GROUP BY product;

-- Dynamic pivot (PostgreSQL with crosstab)
SELECT * FROM crosstab(
    'SELECT product, month, sales FROM monthly_sales ORDER BY 1,2',
    'SELECT DISTINCT month FROM monthly_sales ORDER BY 1'
) AS ct(product TEXT, jan NUMERIC, feb NUMERIC, mar NUMERIC);
```

**Unpivot:**

```sql
-- From columns to rows
SELECT 
    product,
    'Jan' as month,
    jan_sales as sales
FROM pivot_table
UNION ALL
SELECT 
    product,
    'Feb' as month,
    feb_sales as sales
FROM pivot_table
UNION ALL
SELECT 
    product,
    'Mar' as month,
    mar_sales as sales
FROM pivot_table;

-- Using LATERAL (PostgreSQL)
SELECT 
    product,
    month,
    sales
FROM pivot_table
CROSS JOIN LATERAL (
    VALUES 
        ('Jan', jan_sales),
        ('Feb', feb_sales),
        ('Mar', mar_sales)
) AS unpivoted(month, sales);
```

### 8.2 Gap and Island Problems

**Find gaps in sequences:**

```sql
-- Find missing order IDs
WITH order_range AS (
    SELECT 
        order_id,
        LEAD(order_id) OVER (ORDER BY order_id) as next_id
    FROM orders
)
SELECT 
    order_id + 1 as gap_start,
    next_id - 1 as gap_end
FROM order_range
WHERE next_id - order_id > 1;
```

**Find islands (consecutive groups):**

```sql
-- Find consecutive login days
WITH numbered AS (
    SELECT 
        user_id,
        login_date,
        login_date - (ROW_NUMBER() OVER (
            PARTITION BY user_id 
            ORDER BY login_date
        ) * INTERVAL '1 day') as grp
    FROM user_logins
)
SELECT 
    user_id,
    MIN(login_date) as streak_start,
    MAX(login_date) as streak_end,
    COUNT(*) as consecutive_days
FROM numbered
GROUP BY user_id, grp
HAVING COUNT(*) >= 7;  -- At least 7 consecutive days
```

### 8.3 Running Differences

```sql
-- Calculate session duration from events
WITH events_with_next AS (
    SELECT 
        session_id,
        event_type,
        event_time,
        LEAD(event_time) OVER (
            PARTITION BY session_id 
            ORDER BY event_time
        ) as next_event_time
    FROM events
)
SELECT 
    session_id,
    event_type,
    event_time,
    next_event_time - event_time as time_to_next_event
FROM events_with_next;
```

### 8.4 Cumulative Percentages

```sql
SELECT 
    product_name,
    revenue,
    SUM(revenue) OVER (ORDER BY revenue DESC) as cumulative_revenue,
    SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER () * 100 as cumulative_pct,
    CASE 
        WHEN SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER () <= 0.8 
        THEN 'A (Top 80%)'
        WHEN SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER () <= 0.95 
        THEN 'B (Next 15%)'
        ELSE 'C (Bottom 5%)'
    END as abc_category
FROM product_revenue
ORDER BY revenue DESC;
```

---

## PHẦN 9: QUERY OPTIMIZATION

### 9.1 Understanding Execution Plans

```sql
-- PostgreSQL
EXPLAIN ANALYZE
SELECT c.customer_name, SUM(o.total_amount)
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01'
GROUP BY c.customer_name;

-- Key things to look for in execution plan:
-- 1. Scan types: Seq Scan (bad for large tables) vs Index Scan (good)
-- 2. Join types: Nested Loop, Hash Join, Merge Join
-- 3. Estimated vs Actual rows
-- 4. Cost estimates
-- 5. Sort operations (expensive)
```

**Scan Types:**
- **Seq Scan** - Reads entire table, OK for small tables or high selectivity
- **Index Scan** - Uses index to find rows, good for selective queries
- **Index Only Scan** - All data from index, fastest
- **Bitmap Scan** - Combines multiple indexes

**Join Types:**
- **Nested Loop** - Good for small tables or indexed joins
- **Hash Join** - Good for larger tables, needs memory
- **Merge Join** - Good for pre-sorted data or large tables

### 9.2 Indexing Strategies

**B-Tree Index (Default):**

```sql
-- Single column index
CREATE INDEX idx_orders_date ON orders(order_date);

-- Composite index (order matters!)
CREATE INDEX idx_orders_customer_date 
ON orders(customer_id, order_date);

-- Query benefits from composite index:
SELECT * FROM orders 
WHERE customer_id = 123 AND order_date >= '2024-01-01';

-- This query CANNOT use the composite index efficiently:
SELECT * FROM orders 
WHERE order_date >= '2024-01-01';
-- Because customer_id is first in the index
```

**Partial Index:**

```sql
-- Only index active records
CREATE INDEX idx_active_users 
ON users(email) 
WHERE is_active = true;

-- Beneficial for queries filtering on is_active = true
```

**Expression Index:**

```sql
-- Index on expression
CREATE INDEX idx_orders_year 
ON orders(EXTRACT(YEAR FROM order_date));

-- Index on lower case for case-insensitive search
CREATE INDEX idx_customers_email_lower 
ON customers(LOWER(email));
```

**Covering Index:**

```sql
-- Include additional columns for index-only scans
CREATE INDEX idx_orders_covering 
ON orders(customer_id) 
INCLUDE (order_date, total_amount);

-- Query can be satisfied entirely from index:
SELECT order_date, total_amount
FROM orders
WHERE customer_id = 123;
```

### 9.3 Query Optimization Tips

**1. Avoid SELECT *:**

```sql
-- Bad
SELECT * FROM orders WHERE customer_id = 123;

-- Good
SELECT order_id, order_date, total_amount 
FROM orders WHERE customer_id = 123;
```

**2. Use appropriate data types:**

```sql
-- Bad: String comparison
WHERE order_date = '2024-01-15'  -- Implicit conversion

-- Good: Proper type
WHERE order_date = DATE '2024-01-15'
```

**3. Avoid functions on indexed columns:**

```sql
-- Bad: Can't use index on order_date
WHERE YEAR(order_date) = 2024

-- Good: Range query uses index
WHERE order_date >= '2024-01-01' 
  AND order_date < '2025-01-01'
```

**4. Use EXISTS instead of COUNT:**

```sql
-- Bad
SELECT customer_id
FROM customers
WHERE (SELECT COUNT(*) FROM orders WHERE customer_id = customers.customer_id) > 0;

-- Good
SELECT customer_id
FROM customers
WHERE EXISTS (SELECT 1 FROM orders WHERE customer_id = customers.customer_id);
```

**5. Limit early when possible:**

```sql
-- Bad: Sorts everything first
SELECT * FROM orders
ORDER BY order_date DESC
LIMIT 10;

-- Better with index on order_date DESC:
CREATE INDEX idx_orders_date_desc ON orders(order_date DESC);
```

**6. Use UNION ALL instead of UNION when duplicates are OK:**

```sql
-- UNION removes duplicates (extra sort/distinct operation)
SELECT customer_id FROM orders_2023
UNION
SELECT customer_id FROM orders_2024;

-- UNION ALL is faster
SELECT customer_id FROM orders_2023
UNION ALL
SELECT customer_id FROM orders_2024;
```

### 9.4 Common Anti-Patterns

**1. N+1 Query Problem:**

```sql
-- Bad: One query per customer
FOR each customer:
    SELECT * FROM orders WHERE customer_id = ?

-- Good: Single query with JOIN
SELECT c.*, o.*
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;
```

**2. Cartesian Products:**

```sql
-- Bad: Missing join condition
SELECT * FROM customers, orders;  -- M x N rows!

-- Good: Proper join
SELECT * FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;
```

**3. Implicit Type Conversions:**

```sql
-- Bad: customer_id is INT, comparing to string
WHERE customer_id = '123'

-- Good: Match types
WHERE customer_id = 123
```

---

## PHẦN 10: DATABASE-SPECIFIC SQL

### 10.1 PostgreSQL Specific

```sql
-- DISTINCT ON (first row per group)
SELECT DISTINCT ON (customer_id)
    customer_id,
    order_id,
    order_date,
    total_amount
FROM orders
ORDER BY customer_id, order_date DESC;

-- FILTER clause
SELECT 
    COUNT(*) as total_orders,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    SUM(amount) FILTER (WHERE status = 'completed') as completed_revenue
FROM orders;

-- Array aggregation
SELECT 
    customer_id,
    ARRAY_AGG(product_name ORDER BY order_date) as products_ordered
FROM orders
GROUP BY customer_id;

-- JSON aggregation
SELECT 
    customer_id,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'order_id', order_id,
            'amount', total_amount,
            'date', order_date
        ) ORDER BY order_date DESC
    ) as order_history
FROM orders
GROUP BY customer_id;
```

### 10.2 MySQL Specific

```sql
-- GROUP_CONCAT
SELECT 
    customer_id,
    GROUP_CONCAT(product_name ORDER BY order_date SEPARATOR ', ') as products
FROM orders
GROUP BY customer_id;

-- JSON functions
SELECT 
    customer_id,
    JSON_ARRAYAGG(
        JSON_OBJECT(
            'order_id', order_id,
            'amount', total_amount
        )
    ) as orders_json
FROM orders
GROUP BY customer_id;

-- Variables for row numbering (before MySQL 8)
SET @row_num = 0;
SELECT 
    @row_num := @row_num + 1 as row_num,
    customer_name,
    total_purchases
FROM customers
ORDER BY total_purchases DESC;
```

### 10.3 BigQuery Specific

```sql
-- QUALIFY for window function filtering
SELECT 
    customer_id,
    order_date,
    total_amount
FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1;

-- Struct and Arrays
SELECT 
    customer_id,
    ARRAY_AGG(STRUCT(order_id, order_date, total_amount)) as orders
FROM orders
GROUP BY customer_id;

-- Unnesting arrays
SELECT 
    customer_id,
    order.order_id,
    order.total_amount
FROM customers,
UNNEST(order_history) as order;

-- Approximate aggregations (faster for large data)
SELECT 
    APPROX_COUNT_DISTINCT(customer_id) as unique_customers,
    APPROX_QUANTILES(order_amount, 100)[OFFSET(50)] as median_amount
FROM orders;
```

### 10.4 Snowflake Specific

```sql
-- QUALIFY clause
SELECT 
    customer_id,
    order_date,
    total_amount
FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1;

-- Flatten for semi-structured data
SELECT 
    raw_data:customer_id::STRING as customer_id,
    f.value:product_name::STRING as product_name,
    f.value:quantity::INT as quantity
FROM raw_orders,
LATERAL FLATTEN(input => raw_data:items) f;

-- Time travel
SELECT * FROM orders AT(TIMESTAMP => '2024-01-15 10:00:00'::TIMESTAMP);
SELECT * FROM orders BEFORE(STATEMENT => '<query_id>');

-- Clone tables
CREATE TABLE orders_backup CLONE orders;
```

---

## PHẦN 11: SQL FOR DATA ENGINEERING

### 11.1 Data Validation Queries

```sql
-- Check for duplicates
SELECT 
    customer_id,
    COUNT(*) as duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Check for orphan records
SELECT o.order_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Check for NULL values
SELECT 
    COUNT(*) as total_rows,
    COUNT(email) as non_null_emails,
    COUNT(*) - COUNT(email) as null_emails,
    ROUND((COUNT(*) - COUNT(email))::NUMERIC / COUNT(*) * 100, 2) as null_pct
FROM customers;

-- Check value distributions
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100, 2) as percentage
FROM orders
GROUP BY status
ORDER BY count DESC;
```

### 11.2 Data Profiling Queries

```sql
-- Column statistics
SELECT 
    COUNT(*) as row_count,
    COUNT(DISTINCT column_name) as distinct_values,
    COUNT(*) - COUNT(column_name) as null_count,
    MIN(column_name) as min_value,
    MAX(column_name) as max_value,
    AVG(column_name::NUMERIC) as avg_value,  -- For numeric columns
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY column_name) as median
FROM table_name;

-- Frequency distribution
WITH value_counts AS (
    SELECT 
        column_name,
        COUNT(*) as count
    FROM table_name
    GROUP BY column_name
)
SELECT 
    column_name,
    count,
    ROUND(count::NUMERIC / SUM(count) OVER () * 100, 2) as percentage,
    SUM(count) OVER (ORDER BY count DESC) as cumulative_count
FROM value_counts
ORDER BY count DESC
LIMIT 20;
```

### 11.3 Incremental Loading Patterns

```sql
-- Delta load with watermark
INSERT INTO target_table
SELECT *
FROM source_table
WHERE updated_at > (SELECT COALESCE(MAX(updated_at), '1900-01-01') FROM target_table);

-- Merge/Upsert pattern
MERGE INTO target_table t
USING source_table s
ON t.id = s.id
WHEN MATCHED AND s.updated_at > t.updated_at THEN
    UPDATE SET 
        column1 = s.column1,
        column2 = s.column2,
        updated_at = s.updated_at
WHEN NOT MATCHED THEN
    INSERT (id, column1, column2, updated_at)
    VALUES (s.id, s.column1, s.column2, s.updated_at);

-- Soft delete pattern
MERGE INTO dim_customer t
USING staging_customer s
ON t.customer_id = s.customer_id
WHEN MATCHED THEN
    UPDATE SET 
        customer_name = s.customer_name,
        is_deleted = FALSE,
        updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (customer_id, customer_name, is_deleted, updated_at)
    VALUES (s.customer_id, s.customer_name, FALSE, CURRENT_TIMESTAMP);

-- Mark deleted records
UPDATE dim_customer
SET is_deleted = TRUE, deleted_at = CURRENT_TIMESTAMP
WHERE customer_id NOT IN (SELECT customer_id FROM staging_customer)
  AND is_deleted = FALSE;
```

---

## PHẦN 12: BEST PRACTICES

### 12.1 Code Style

```sql
-- Use consistent formatting
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM customers AS c
LEFT JOIN orders AS o 
    ON c.customer_id = o.customer_id
WHERE c.created_at >= '2024-01-01'
    AND c.status = 'active'
GROUP BY 
    c.customer_id,
    c.customer_name
HAVING SUM(o.total_amount) > 1000
ORDER BY total_spent DESC
LIMIT 100;

-- Use meaningful aliases
-- Good: c for customers, o for orders
-- Bad: t1, t2, x, y
```

### 12.2 Performance Checklist

- [ ] Check execution plan for full table scans
- [ ] Ensure indexes exist for WHERE and JOIN columns
- [ ] Use appropriate data types
- [ ] Avoid SELECT * in production
- [ ] Use LIMIT during development
- [ ] Consider partitioning for large tables
- [ ] Use EXPLAIN ANALYZE to verify assumptions
- [ ] Monitor query execution times

### 12.3 Common Mistakes to Avoid

- Using DISTINCT to hide duplicates instead of fixing the root cause
- Not handling NULL values properly
- Using OR instead of IN or UNION
- Forgetting to account for timezone differences
- Not testing with production-like data volumes
- Ignoring index maintenance

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Coverage: SQL Fundamentals to Advanced Topics, Query Optimization, Database-Specific Features*
