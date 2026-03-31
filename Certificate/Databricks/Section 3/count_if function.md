---
title: "count_if aggregate function | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/sql/language-manual/functions/count_if"
author:
published: 2024-01-12
created: 2026-03-31
description: "Learn the syntax of the count\_if aggregate function of the SQL language in Databricks SQL and Databricks Runtime."
tags:
  - "clippings"
---
**Applies to:** Databricks SQL Databricks Runtime

Returns the number of true values for the group in `expr`.

## Syntax

```markdown
count_if ( [ALL | DISTINCT] expr ) [ FILTER ( WHERE cond ) ]
```

This function can also be invoked as a [window function](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-window-functions) using the `OVER` clause.

## Arguments

- `expr`: A BOOLEAN expression.
- `cond`: An optional boolean expression filtering the rows used for aggregation.

## Returns

A `BIGINT`.

`count_if(expr) FILTER(WHERE cond)` is equivalent to `count_if(expr AND cond)`.

If `DISTINCT` is specified only unique rows are counted.

## Examples

```sql
SQL> SELECT count_if(col % 2 = 0) FROM VALUES (NULL), (0), (1), (2), (2), (3) AS tab(col);
 3

> SELECT count_if(DISTINCT col % 2 = 0) FROM VALUES (NULL), (0), (1), (2), (2), (3) AS tab(col);
 2

> SELECT count_if(col IS NULL) FROM VALUES (NULL), (0), (1), (2), (3) AS tab(col);
 1
```