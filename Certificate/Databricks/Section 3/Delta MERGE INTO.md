---
title: "MERGE INTO | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into"
author:
published: 2026-03-16
created: 2026-03-31
description: "Learn how to use the MERGE INTO syntax of the Delta Lake SQL language in Databricks SQL and Databricks Runtime."
tags:
  - "clippings"
---
**Applies to:** Databricks SQL Databricks Runtime

Merges a set of updates, insertions, and deletions based on a source table into a target Delta table.

This statement is supported only for Delta Lake tables.

This page contains details for using the correct syntax with the `MERGE` command. See [Upsert into a Delta Lake table using merge](https://docs.databricks.com/aws/en/delta/merge) for more guidance on how to use `MERGE` operations to manage your data.

## Syntax

```markdown
[ common_table_expression ]
  MERGE [ WITH SCHEMA EVOLUTION ] INTO target_table_name [target_alias]
     USING source_table_reference [source_alias]
     ON merge_condition
     { WHEN MATCHED [ AND matched_condition ] THEN matched_action |
       WHEN NOT MATCHED [BY TARGET] [ AND not_matched_condition ] THEN not_matched_action |
       WHEN NOT MATCHED BY SOURCE [ AND not_matched_by_source_condition ] THEN not_matched_by_source_action } [...]

matched_action
 { DELETE |
   UPDATE SET * |
   UPDATE SET { column = { expr | DEFAULT } } [, ...] }

not_matched_action
 { INSERT * |
   INSERT (column1 [, ...] ) VALUES ( expr | DEFAULT ] [, ...] )

not_matched_by_source_action
 { DELETE |
   UPDATE SET { column = { expr | DEFAULT } } [, ...] }
```

## Parameters

- **[common table expression](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-cte)**
	Common table expressions (CTE) are one or more named queries which can be reused multiple times within the main query block to avoid repeated computations or to improve readability of complex, nested queries.
- **`WITH SCHEMA EVOLUTION`**
	**Applies to:** Databricks Runtime 15.2 and above
	Enables [automatic schema evolution](https://docs.databricks.com/aws/en/delta/update-schema#merge-schema-evolution) for this `MERGE` operation. When enabled, the schema of the target Delta table is automatically updated to match the schema of the source table.
- **[target\_table\_name](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names#table-name)**
	A [Table name](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names#table-name) identifying the table being modified. The table referenced must be a Delta table.
	The name must not include an [options specification](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names#table-name).
	The table must not be a foreign table.
- **[target\_alias](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names#table-alias)**
	A [Table alias](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names#table-alias) for the target table. The alias must not include a column list.
- **[source\_table\_reference](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names#table-name)**
	A [Table name](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names#table-name) identifying the source table to be merged into the target table.
- **[source\_alias](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names#table-alias)**
	A [Table alias](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names#table-alias) for the source table. The alias must not include a column list.
- **ON [merge\_condition](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-expression)**
	How the rows from one relation are combined with the rows of another relation. An expression with a return type of BOOLEAN.
- **`WHEN MATCHED [ AND ` [matched\_condition](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-expression) `]`**
	`WHEN MATCHED` clauses are executed when a source row matches a target table row based on the `merge_condition` and the optional `match_condition`.
- **matched\_action**
	- **`DELETE`**
		Deletes the matching target table row.
		Multiple matches are allowed when matches are unconditionally deleted. An unconditional delete is not ambiguous, even if there are multiple matches.
		- **`UPDATE`**
		Updates the matched target table row.
		To update all the columns of the target Delta table with the corresponding columns of the source dataset, use `UPDATE SET *`. This is equivalent to `UPDATE SET col1 = source.col1 [, col2 = source.col2 ...]` for all the columns of the target Delta table. Therefore, this action assumes that the source table has the same columns as those in the target table, otherwise the query will throw an analysis error.
		> [!-secondary] -secondary
		> note
		> 
		> This behavior changes when automatic schema evolution is enabled. See [Automatic schema evolution for merge](https://docs.databricks.com/aws/en/delta/update-schema#merge-schema-evolution) for details.
		**Applies to:** Databricks SQL Databricks Runtime 11.3 LTS and above
		You can specify `DEFAULT` as `expr` to explicitly update the column to its default value.
	If there are multiple `WHEN MATCHED` clauses, then they are evaluated in the order they are specified. Each `WHEN MATCHED` clause, except the last one, must have a `matched_condition`. Otherwise, the query returns a [NON\_LAST\_MATCHED\_CLAUSE\_OMIT\_CONDITION](https://docs.databricks.com/aws/en/error-messages/error-classes#non_last_matched_clause_omit_condition) error.
	If none of the `WHEN MATCHED` conditions evaluate to true for a source and target row pair that matches the `merge_condition`, then the target row is left unchanged.
- **`WHEN NOT MATCHED [BY TARGET] [ AND ` [not\_matched\_condition](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-expression) `]`**
	`WHEN NOT MATCHED` clauses insert a row when a source row does not match any target row based on the `merge_condition` and the optional `not_matched_condition`.
	**Applies to:** Databricks SQL Databricks Runtime 12.2 LTS and above
	`WHEN NOT MATCHED BY TARGET` can be used as an alias for `WHEN NOT MATCHED`.
	`not_matched_condition` must be a Boolean expression.
	- `INSERT *`
		Inserts all the columns of the target Delta table with the corresponding columns of the source dataset. This is equivalent to `INSERT (col1 [, col2 ...]) VALUES (source.col1 [, source.col2 ...])` for all the columns of the target Delta table. This action requires that the source table has the same columns as those in the target table.
		> [!-secondary] -secondary
		> note
		> 
		> This behavior changes when automatic schema evolution is enabled. See [Automatic schema evolution for merge](https://docs.databricks.com/aws/en/delta/update-schema#merge-schema-evolution) for details.
		- `INSERT ( ... ) VALUES ( ... )`
		The new row is generated based on the specified column and corresponding expressions. All the columns in the target table do not need to be specified. For unspecified target columns, the column default is inserted, or `NULL` if none exists.
		**Applies to:** Databricks SQL Databricks Runtime 11.3 LTS and above
		You can specify `DEFAULT` as an expression to explicitly insert the column default for a target column.
	If there are multiple `WHEN NOT MATCHED` clauses, then they are evaluated in the order they are specified. All `WHEN NOT MATCHED` clauses, except the last one, must have `not_matched_condition` s. Otherwise, the query returns a [NON\_LAST\_NOT\_MATCHED\_CLAUSE\_OMIT\_CONDITION](https://docs.databricks.com/aws/en/error-messages/error-classes#delta_non_last_not_matched_clause_omit_condition) error.
- **`WHEN NOT MATCHED BY SOURCE [ AND ` [not\_matched\_by\_source\_condition](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-expression) `]`**
	**Applies to:** Databricks SQL Databricks Runtime 12.2 LTS and above
	`WHEN NOT MATCHED BY SOURCE` clauses are executed when a target row does not match any rows in the source table based on the `merge_condition` and the optional `not_match_by_source_condition` evaluates to true.
	`not_matched_by_source_condition` must be a Boolean expression that only references columns from the target table.
- **not\_matched\_by\_source\_action**
	- **`DELETE`**
		Deletes the target table row.
		- **`UPDATE`**
		Updates the target table row. `expr` may only reference columns from the target table, otherwise the query will throw an analysis error.
		**Applies to:** Databricks SQL Databricks Runtime 11.3 LTS and above
		You can specify `DEFAULT` as `expr` to explicitly update the column to its default value.
	> [!-info] -info
	> important
	> 
	> Adding a `WHEN NOT MATCHED BY SOURCE` clause to update or delete target rows when the `merge_condition` evaluates to false can lead to a large number of target rows being modified. For best performance, apply `not_matched_by_source_condition` s to limit the number of target rows updated or deleted.
	If there are multiple `WHEN NOT MATCHED BY SOURCE clauses`, then they are evaluated in the order they are specified. Each `WHEN NOT MATCHED BY SOURCE` clause, except the last one, must have a `not_matched_by_source_condition`. Otherwise, the query returns a [NON\_LAST\_NOT\_MATCHED\_BY\_SOURCE\_CLAUSE\_OMIT\_CONDITION](https://docs.databricks.com/aws/en/error-messages/error-classes#non_last_not_matched_by_source_clause_omit_condition) error.
	If none of the `WHEN NOT MATCHED BY SOURCE` conditions evaluate to true for a target row that doesn't match any rows in the source table based on the `merge_condition`, then the target row is left unchanged.

> [!-info] -info
> important
> 
> `MERGE` operations fail with a [DELTA\_MULTIPLE\_SOURCE\_ROW\_MATCHING\_TARGET\_ROW\_IN\_MERGE](https://docs.databricks.com/aws/en/error-messages/error-classes#delta_multiple_source_row_matching_target_row_in_merge) error if more than one row in the source table matches the same row in the target table based on the conditions specified in the `ON` and `WHEN MATCHED` clauses. According to the SQL semantics of merge, this type of update operation is ambiguous because it is unclear which source row should be used to update the matched target row. You can preprocess the source table to eliminate the possibility of multiple matches. See the [change data capture example](https://docs.databricks.com/aws/en/delta/merge#merge-in-cdc). This example preprocesses the change dataset (the source dataset) to retain only the latest change for each key before applying that change into the target Delta table. In Databricks Runtime 15.4 LTS and below, `MERGE` only considers conditions in the `ON` clause before evaluating multiple matches.

## Examples

You can use `MERGE INTO` for complex operations like deduplicating data, upserting change data, applying SCD Type 2 operations, etc. See [Upsert into a Delta Lake table using merge](https://docs.databricks.com/aws/en/delta/merge) for a few examples.

### WHEN MATCHED

```sql
SQL-- Delete all target rows that have a match in the source table.
> MERGE INTO target USING source
  ON target.key = source.key
  WHEN MATCHED THEN DELETE

-- Conditionally update target rows that have a match in the source table using the source value.
> MERGE INTO target USING source
  ON target.key = source.key
  WHEN MATCHED AND target.updated_at < source.updated_at THEN UPDATE SET *

-- Multiple MATCHED clauses conditionally deleting matched target rows and updating two columns for all other matched rows.
> MERGE INTO target USING source
  ON target.key = source.key
  WHEN MATCHED AND target.marked_for_deletion THEN DELETE
  WHEN MATCHED THEN UPDATE SET target.updated_at = source.updated_at, target.value = DEFAULT
```

### WHEN NOT MATCHED \[BY TARGET\]

```sql
SQL-- Insert all rows from the source that are not already in the target table.
> MERGE INTO target USING source
  ON target.key = source.key
  WHEN NOT MATCHED THEN INSERT *

-- Conditionally insert new rows in the target table using unmatched rows from the source table.
> MERGE INTO target USING source
  ON target.key = source.key
  WHEN NOT MATCHED BY TARGET AND source.created_at > now() - INTERVAL “1” DAY THEN INSERT (created_at, value) VALUES (source.created_at, DEFAULT)
```

### WHEN NOT MATCHED BY SOURCE

```sql
SQL-- Delete all target rows that have no matches in the source table.
> MERGE INTO target USING source
  ON target.key = source.key
  WHEN NOT MATCHED BY SOURCE THEN DELETE

-- Multiple NOT MATCHED BY SOURCE clauses conditionally deleting unmatched target rows and updating two columns for all other matched rows.
> MERGE INTO target USING source
  ON target.key = source.key
  WHEN NOT MATCHED BY SOURCE AND target.marked_for_deletion THEN DELETE
  WHEN NOT MATCHED BY SOURCE THEN UPDATE SET target.value = DEFAULT
```

### WITH SCHEMA EVOLUTION

```sql
SQL-- Multiple MATCHED and NOT MATCHED clauses with schema evolution enabled.
> MERGE WITH SCHEMA EVOLUTION INTO target USING source
  ON source.key = target.key
  WHEN MATCHED THEN UPDATE SET *
  WHEN NOT MATCHED THEN INSERT *
  WHEN NOT MATCHED BY SOURCE THEN DELETE
```