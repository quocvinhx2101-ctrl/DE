---
title: "Compute | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/compute"
author:
published: 2026-03-17
created: 2026-03-31
description: "Learn about the types of Databricks compute available in your workspace."
tags:
  - "clippings"
---
Databricks compute refers to the selection of computing resources available on Databricks to run your data engineering, data science, and analytics workloads. Choose from serverless compute for on-demand scaling, classic compute for customizable resources, or SQL warehouses for optimized analytics.

You can view and manage compute resources in the **Compute** section of your workspace:

## Serverless compute

On-demand, automatically managed compute that scales based on your workload requirements.

| Topic | Description |
| --- | --- |
| [Serverless compute for notebooks](https://docs.databricks.com/aws/en/compute/serverless/notebooks) | Interactive Python and SQL execution in notebooks with automatic scaling and no infrastructure management. |
| [Serverless compute for jobs](https://docs.databricks.com/aws/en/jobs/run-serverless-jobs) | Run Lakeflow Jobs without configuring or deploying infrastructure. Automatically provisions and scales compute resources. |
| [Serverless pipelines](https://docs.databricks.com/aws/en/ldp/serverless) | Run Lakeflow Spark Declarative Pipelines without configuring or deploying infrastructure. Automatically provisions and scales compute resources. |
| [Serverless compute limitations](https://docs.databricks.com/aws/en/compute/serverless/limitations) | Understanding limitations and requirements for serverless workloads and supported configurations. |

## Classic compute

Provisioned compute resources that you create, configure, and manage for your workloads.

| Topic | Description |
| --- | --- |
| [Classic compute overview](https://docs.databricks.com/aws/en/compute/use-compute) | Overview of who can access and create classic compute resources. |
| [Configure compute](https://docs.databricks.com/aws/en/compute/configure) | Create and configure compute for interactive data analysis in notebooks or automated workflows with Lakeflow Jobs. |
| [Standard compute](https://docs.databricks.com/aws/en/compute/standard-overview) | Multi-user compute with shared resources for cost-effective collaboration. [Lakeguard](https://docs.databricks.com/aws/en/compute/lakeguard) provides secure user isolation. |
| [Dedicated compute](https://docs.databricks.com/aws/en/compute/dedicated-overview) | Compute resource assigned to a single user or group. |
| [Instance pools](https://docs.databricks.com/aws/en/compute/pool-index) | Pre-configured instances that reduce compute startup time and provide cost savings for frequent workloads. |

## SQL warehouses

Optimized compute resources for specific use cases and advanced functionality. SQL warehouses can be configured as serverless or classic.

| Topic | Description |
| --- | --- |
| [SQL warehouses](https://docs.databricks.com/aws/en/compute/sql-warehouse/) | Optimized compute for **SQL** queries, analytics, and business intelligence workloads with **serverless** or **classic** options. |
| [SQL warehouse types](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-types) | Understanding the differences between serverless and classic SQL warehouse options to choose the right type for your workloads. |

## Additional topics

| Topic | Description |
| --- | --- |
| [What is Photon?](https://docs.databricks.com/aws/en/compute/photon) | High-performance query engine that accelerates **SQL** workloads and provides faster data processing. |
| [What is Lakeguard?](https://docs.databricks.com/aws/en/compute/lakeguard) | Security framework that provides data governance and access control for compute resources. |

For information about working with compute using the command line or APIs, see [What is the Databricks CLI?](https://docs.databricks.com/aws/en/dev-tools/cli/) and the [Databricks REST API reference](https://docs.databricks.com/api/workspace).

## Reserved ports

Certain ports are reserved on the driver node for internal Databricks services. To avoid conflicts, do not bind services to the following ports:

- 1023
- 6059
- 6060
- 6061
- 6062: Occupied by ipywidgets by default. You can change the port if needed. See [ipywidgets](https://docs.databricks.com/aws/en/notebooks/ipywidgets#requirements).
- 7071
- 7077
- 10000
- 15001
- 15002
- 36423
- 38841
- 39909
- 40000
- 40001
- 41063