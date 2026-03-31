---
title: "Connect to a SQL warehouse | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/compute/sql-warehouse"
author:
published: 2026-01-08
created: 2026-03-31
description: "Learn about using SQL warehouses, formerly called SQL endpoints, for data warehousing on Databricks."
tags:
  - "clippings"
---
A SQL warehouse is a compute resource that lets you query and explore data on Databricks.

Most users have access to SQL warehouses configured by administrators.

For information on serverless compute plane architecture, see [Serverless compute plane](https://docs.databricks.com/aws/en/getting-started/high-level-architecture#serverless).

Databricks recommends using serverless SQL warehouses when available.

## Use SQL warehouses

The SQL warehouses you have access to appear in the compute drop-down menus of workspace UIs that support SQL warehouse compute, including the query editor, Catalog Explorer, and dashboards.

You can also view, sort, and search available SQL warehouses by clicking **SQL Warehouses** in the sidebar. By default, warehouses are sorted by state (running warehouses first), then in alphabetical order.

The UI indicates whether or not a warehouse is currently running. Running a query against a stopped warehouse starts it automatically if you have access to the warehouse. See [Start a SQL warehouse](https://docs.databricks.com/aws/en/compute/sql-warehouse#start).

> [!-secondary] -secondary
> note
> 
> To help you get started, Databricks creates a small SQL warehouse called **Starter Warehouse** automatically. You can edit or delete this SQL warehouse.

> [!-info] -info
> important
> 
> You can also attach a notebook to a pro or serverless SQL warehouse. See [Notebooks and SQL warehouses](https://docs.databricks.com/aws/en/notebooks/notebook-compute#notebook-sql-warehouse) for more information and limitations.

## What are Serverless SQL warehouses?

> [!-secondary] -secondary
> note
> 
> Before you can create a serverless SQL warehouse in a [region that supports the feature](https://docs.databricks.com/aws/en/resources/feature-region-support), there might be required steps. See [Set up serverless SQL warehouses](https://docs.databricks.com/aws/en/admin/sql/serverless).

Databricks SQL delivers optimal price and performance with serverless SQL warehouses. Key advantages of serverless warehouses over pro and classic models include:

- **Instant and elastic compute**: Eliminates waiting for infrastructure resources and avoids resource over-provisioning during usage spikes. Intelligent workload management dynamically handles scaling. See [SQL warehouse types](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-types) for more information on intelligent workload management and other serverless features.
- **Minimal management overhead**: Capacity management, patching, upgrades, and performance optimization are all handled by Databricks, simplifying operations and leading to predictable pricing.
- **Lower total cost of ownership (TCO)**: Automatic provisioning and scaling of resources as needed helps avoid over-provisioning and reduces idle times, thus lowering TCO.

## Start a SQL warehouse

To manually start a stopped SQL warehouse, click **SQL Warehouses** in the sidebar then click the start icon next to the warehouse.

> [!-secondary] -secondary
> note
> 
> You must have at least CAN MONITOR permissions on the SQL warehouse to manually restart it. See [SQL warehouse ACLs](https://docs.databricks.com/aws/en/security/auth/access-control/#sql-warehouses).

A SQL warehouse auto-restarts in the following conditions:

- A warehouse is stopped and you attempt to run a query.
- A job assigned to a stopped warehouse is scheduled to run.
- A connection is established to a stopped warehouse from a JDBC/ODBC interface.
- A dashboard associated with a dashboard-level warehouse is opened.

## Create a SQL warehouse

Configuring and launching SQL warehouses requires elevated permissions generally restricted to an administrator. See [SQL warehouse admin settings](https://docs.databricks.com/aws/en/admin/sql/) and [Create a SQL warehouse](https://docs.databricks.com/aws/en/compute/sql-warehouse/create).

Unity Catalog governs data access permissions on SQL warehouses for most assets. Administrators configure most data access permissions. SQL warehouses can have custom data access configured instead of or in addition to Unity Catalog. See [Data access configurations](https://docs.databricks.com/aws/en/admin/sql/data-access-configuration).

You should contact an administrator in the following situations:

- You cannot connect to any SQL warehouses.
- You cannot run queries because a SQL warehouse is stopped.
- You cannot access tables or data from your SQL warehouse.

> [!-secondary] -secondary
> note
> 
> Some organizations might allow users to modify privileges on either database objects or SQL warehouses. Check with your teammates and admins to understand how your organization manages data access.

## Warehouse sizing and autoscaling behavior

For information on how classic and pro SQL warehouses are sized and how autoscaling works, see [SQL warehouse sizing, scaling, and queuing behavior](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-behavior).

## SQL warehouses and third party BI tools

Databricks SQL supports many third party [BI and visualization tools](https://docs.databricks.com/aws/en/integrations/) that can connect to SQL warehouses, including the following:

- [Power BI with Databricks](https://docs.databricks.com/aws/en/partners/bi/power-bi)
- [Connect Tableau and Databricks](https://docs.databricks.com/aws/en/partners/bi/tableau)

## Developer tools for SQL warehouses

You can use the REST API, CLI, and other drivers and integrations to configure and run commands on SQL warehouses. See the following:

- [Databricks SQL REST API](https://docs.databricks.com/api/workspace/warehouses)
- [Databricks SQL Connector for Python](https://docs.databricks.com/aws/en/dev-tools/python-sql-connector)
- [Databricks SQL CLI](https://docs.databricks.com/aws/en/dev-tools/databricks-sql-cli)
- [Databricks Driver for SQLTools for Visual Studio Code](https://docs.databricks.com/aws/en/dev-tools/sqltools-driver)
- [DataGrip integration with Databricks](https://docs.databricks.com/aws/en/dev-tools/datagrip)
- [DBeaver integration with Databricks](https://docs.databricks.com/aws/en/dev-tools/dbeaver)
- [Connect to SQL Workbench/J](https://docs.databricks.com/aws/en/archive/partners/workbenchj)

## SQL warehouses vs SQL endpoints

SQL warehouses and SQL endpoints both refer to a type of SQL-optimized compute resource that powers Databricks SQL. In 2023, SQL endpoints were renamed as SQL warehouses.