---
title: "Predictive optimization for Unity Catalog managed tables | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/optimizations/predictive-optimization"
author:
published: 2026-03-06
created: 2026-03-31
description: "Learn how predictive optimization improves data layout and query performance for Unity Catalog managed tables on Databricks."
tags:
  - "clippings"
---
This page describes predictive optimization, which automatically runs maintenance operations for Unity Catalog managed tables on Databricks.

> [!-secondary] -secondary
> note
> 
> Predictive optimization is enabled by default for accounts created on or after November 11, 2024. Databricks began enabling existing accounts on May 7, 2025. This rollout is gradual and is expected to complete by April 2026. To check whether your account is already enabled, see [Verify whether predictive optimization is enabled](https://docs.databricks.com/aws/en/optimizations/predictive-optimization#check-po-enabled).

With predictive optimization enabled, Databricks automatically does the following:

- Identifies tables that would benefit from maintenance operations and queues those operations to run.
- Collects statistics when data is written to a managed table.

This eliminates unnecessary maintenance runs and the burden of tracking and troubleshooting performance manually.

Databricks recommends predictive optimization for all Unity Catalog managed tables. For example, automatic liquid clustering uses intelligent optimization of data layout based on your data usage patterns. See [Use liquid clustering for tables](https://docs.databricks.com/aws/en/delta/clustering).

## What operations does predictive optimization run?

Predictive optimization runs the following operations on Unity Catalog managed tables:

| Operation | Description |
| --- | --- |
| `OPTIMIZE` | Triggers incremental clustering for enabled tables. See [Use liquid clustering for tables](https://docs.databricks.com/aws/en/delta/clustering). Improves query performance by optimizing file sizes. See [Optimize data file layout](https://docs.databricks.com/aws/en/delta/optimize). |
| `VACUUM` | Reduces storage costs by deleting data files no longer referenced by the table. See [Remove unused data files with vacuum](https://docs.databricks.com/aws/en/delta/vacuum). |
| `ANALYZE` | Triggers incremental update of statistics to improve query performance. See [ANALYZE TABLE … COMPUTE STATISTICS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-analyze-compute-statistics). |

> [!-secondary] -secondary
> note
> 
> `OPTIMIZE` does not run `ZORDER` when executed by predictive optimization. On tables that use Z-order, predictive optimization ignores Z-ordered files.

If automatic liquid clustering is enabled, predictive optimization might select new clustering keys before clustering data. See [Automatic liquid clustering](https://docs.databricks.com/aws/en/delta/clustering#auto-liquid).

> [!-warning] -warning
> The retention window for `VACUUM` is determined by the `delta.deletedFileRetentionDuration` table property, which defaults to 7 days. `VACUUM` removes data files no longer referenced by a Delta table version within that window. To retain data for longer durations (for example, to support extended time travel), set this property before you enable predictive optimization:
> 
> ```sql
> SQLALTER TABLE table_name SET TBLPROPERTIES ('delta.deletedFileRetentionDuration' = '30 days');
> ```

## Compute and billing

Predictive optimization runs `ANALYZE`, `OPTIMIZE`, and `VACUUM` operations using serverless compute for jobs. Your account is billed for this compute using a serverless jobs SKU.

See pricing for [Databricks managed services](https://www.databricks.com/product/pricing/managed-services). See [Track predictive optimization with system tables](https://docs.databricks.com/aws/en/optimizations/predictive-optimization#observability).

## Prerequisites

The following requirements must be met to use predictive optimization:

- Your Databricks workspace must be on the [Premium plan or above](https://databricks.com/product/pricing/platform-addons) in a [supported region](https://docs.databricks.com/aws/en/resources/feature-region-support).
- You must use SQL warehouses or Databricks Runtime 12.2 LTS or above.
- Only Unity Catalog managed tables are supported.

## Enable predictive optimization

You can enable predictive optimization for an account, a catalog, or a schema. All Unity Catalog managed tables inherit the account value by default. You can override the account default at the catalog or schema level.

You must have the following privileges to enable or disable predictive optimization:

| Unity Catalog object | Privilege |
| --- | --- |
| Account | Account admin |
| Catalog | Catalog owner |
| Schema | Schema owner |

An account admin can enable predictive optimization for all metastores in an account. Catalogs and schemas inherit this setting by default, but you can override it at either level.

1. Go to the accounts console.
2. Navigate to **Settings**, then **Feature enablement**.
3. Select the option you want (for example, **Enabled**) next to **Predictive optimization**.

> [!-secondary] -secondary
> note
> 
> - Metastores in regions that don't support predictive optimization aren't enabled.
> - Disabling predictive optimization at the account level does not disable it for catalogs or schemas that have specifically enabled it.

### Enable or disable predictive optimization for a catalog or schema

Predictive optimization uses an inheritance model. When enabled for a catalog, schemas in that catalog inherit the setting, and tables within an enabled schema inherit it as well. You can explicitly enable or disable predictive optimization for a catalog or schema to override this behavior.

> [!-secondary] -secondary
> note
> 
> You can disable predictive optimization at the catalog or schema level before enabling it at the account level. If predictive optimization is later enabled at the account level, it remains blocked for tables in those objects.

Use the following syntax to enable, disable, or reset predictive optimization to inherit from the parent object:

```sql
SQLALTER CATALOG [catalog_name] { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
ALTER { SCHEMA | DATABASE } schema_name { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
```

## Verify whether predictive optimization is enabled

The `Predictive Optimization` field is a Unity Catalog property that shows whether predictive optimization is enabled. If the setting is inherited from a parent object, the field value indicates this.

Use the following syntax to check the status:

```sql
SQLDESCRIBE (CATALOG | SCHEMA | TABLE) EXTENDED name
```

## Track predictive optimization with system tables

Databricks provides the system table `system.storage.predictive_optimization_operations_history` for observability into predictive optimization operations, costs, and impact. See [Predictive optimization system table reference](https://docs.databricks.com/aws/en/admin/system-tables/predictive-optimization).

## Limitations

Predictive optimization does not run on the following table types:

- Tables loaded to a workspace as Delta Sharing recipients
- External tables