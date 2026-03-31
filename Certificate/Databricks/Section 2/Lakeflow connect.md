---
title: "Managed connectors in Lakeflow Connect | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/ingestion/lakeflow-connect"
author:
published: 2026-03-10
created: 2026-03-31
description: "Learn about how Databricks Lakeflow Connect managed connectors enable you to ingest data from SaaS applications and databases."
tags:
  - "clippings"
---
> [!-secondary] -secondary
> note
> 
> Managed connectors in Lakeflow Connect are in various [release states](https://docs.databricks.com/aws/en/release-notes/release-types).

This page provides an overview of managed connectors in Databricks Lakeflow Connect for ingesting data from SaaS applications and databases. The resulting ingestion pipeline is governed by Unity Catalog and is powered by serverless compute and Lakeflow Spark Declarative Pipelines. Managed connectors leverage efficient incremental reads and writes to make data ingestion faster, scalable, and more cost-efficient, while your data remains fresh for downstream consumption.

## SaaS connector components

A SaaS connector has the following components:

| Component | Description |
| --- | --- |
| Connection | A Unity Catalog securable object that stores authentication details for the application. |
| Ingestion pipeline | A pipeline that copies the data from the application into the destination tables. The ingestion pipeline runs on serverless compute. |
| Destination tables | The tables where the ingestion pipeline writes the data. These are [streaming tables](https://docs.databricks.com/aws/en/ldp/streaming-tables), which are Delta tables with extra support for incremental data processing. |

![SaaS connector components diagram](https://docs.databricks.com/aws/en/assets/images/saas-connector-components-d16c7f885e5432812153a79f58637927.png)

## Database connector components

A database connector has the following components:

| Component | Description |
| --- | --- |
| Connection | A Unity Catalog securable object that stores authentication details for the database. |
| Ingestion gateway | A pipeline that extracts snapshots, change logs, and metadata from the source database. The gateway runs on classic compute, and it runs continuously to capture changes before change logs can be truncated in the source. |
| Staging storage | A Unity Catalog volume that temporarily stores extracted data before it's applied to the destination table. This allows you to run your ingestion pipeline at whatever schedule you'd like, even as the gateway continuously captures changes. It also helps with failure recovery. You automatically create a staging storage volume when you deploy the gateway, and you can customize the catalog and schema where it lives. Data is automatically purged from staging after 30 days. |
| Ingestion pipeline | A pipeline that moves the data from staging storage into the destination tables. The pipeline runs on serverless compute. |
| Destination tables | The tables where the ingestion pipeline writes the data. These are [streaming tables](https://docs.databricks.com/aws/en/ldp/streaming-tables), which are Delta tables with extra support for incremental data processing. |

![Database connector components diagram](https://docs.databricks.com/aws/en/assets/images/database-connector-components-8a5d628eebf7e373c8cd56b1e1ddbe50.png)

## Orchestration

You can run your ingestion pipeline on one or more custom schedules. For each schedule that you add to a pipeline, Lakeflow Connect automatically creates a [job](https://docs.databricks.com/aws/en/jobs/) for it. The ingestion pipeline is a task within the job. You can optionally add more tasks to the job.

![Pipeline orchestration diagram for SaaS connectors](https://docs.databricks.com/aws/en/assets/images/saas-connector-orchestration-18ab6ef96dab616bb8d5bfb122f33bd9.png)

For database connectors, the ingestion gateway runs in its own job as a continuous task.

![Pipeline orchestration diagram for database connectors](https://docs.databricks.com/aws/en/assets/images/database-connector-orchestration-d6d9fba6b1a6b61da413e0d800334d40.png)

## Incremental ingestion

Lakeflow Connect uses incremental ingestion to improve pipeline efficiency. On the first run of your pipeline, it ingests all of the selected data from the source. In parallel, it tracks changes to the source data. On each subsequent run of the pipeline, it uses that change tracking to ingest only the data that's changed from the prior run, when possible.

The exact approach depends on what's available in your data source. For example, you can use both change tracking and change data capture (CDC) with SQL Server. In contrast, the Salesforce connector selects a cursor column from a set list of options.

Some sources or specific tables don't support incremental ingestion at this time. Databricks plans to expand coverage for incremental support.

## Networking

There are several options for connecting to a SaaS application or database.

- Connectors for SaaS applications reach out to the source's APIs. They're also automatically compatible with serverless egress controls.
- Connectors for cloud databases can connect to the source via Private Link. Alternatively, if your workspace has a Virtual Network (VNet) or Virtual Private Cloud (VPC) that's peered with the VNet or VPC hosting your database, then you can deploy the gateway inside of it.
- Connectors for on-premises databases can connect using services like AWS Direct Connect and Azure ExpressRoute.

## Deployment

You can deploy ingestion pipelines using [Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/), which enable best practices like source control, code review, testing, and continuous integration and delivery (CI/CD). Bundles are managed using the Databricks CLI and can be run in different target workspaces, such as development, staging, and production.

## Failure recovery

As a fully-managed service, Lakeflow Connect aims to automatically recover from issues when possible. For example, when a connector fails, it automatically retries with exponential backoff.

However, it's possible that an error requires your intervention (for example, when credentials expire). In these cases, the connector tries to avoid missing data by storing the last position of the cursor. It can then pick back up from that position on the next run of the pipeline when possible.

## Monitoring

Lakeflow Connect provides robust alerting and monitoring to help you maintain your pipelines. This includes event logs, cluster logs, pipeline health metrics, and data quality metrics. You can also use the `system.billing.usage` table to track costs and monitor pipeline usage. See [Monitor managed ingestion pipeline cost](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/monitor-costs).

For database connectors, you can monitor gateway progress in real time using event logs. See [Monitor ingestion gateway progress with event logs](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/gateway-event-logs).

## Release statuses

| Connector | Release status |
| --- | --- |
| Confluence | Beta |
| Dynamics 365 | Public Preview |
| Google Ads | Beta |
| Google Analytics | Generally Available |
| HubSpot | Beta |
| Jira | Beta |
| Meta Ads | Beta |
| MySQL | Public Preview |
| NetSuite | Public Preview |
| PostgreSQL | Public Preview |
| Salesforce | Generally Available |
| ServiceNow | Generally Available |
| SharePoint | Beta |
| SQL Server | Generally Available |
| TikTok Ads | Beta |
| Workday HCM | Beta |
| Workday Reports | Generally Available |
| Zendesk Support | Beta |

## Feature availability

The following tables summarize feature availability for each managed ingestion connector. For additional features and limitations, see the documentation for your specific connector.

Confluence

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | Supported  If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 250 |

Dynamics 365

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | N/A |
| Maximum number of tables per pipeline | 250 |

Google Ads

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Not supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Partially supported  Report tables support incremental ingestion. Resource tables are fully refreshed on each update. |
| Unity Catalog governance | Supported |
| Lakeflow Jobs | Supported |
| SCD type 2 | Not supported |
| Column selection and deselection | Supported  You can select specific tables. |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Not supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Not supported |
| Automated schema evolution: New tables | N/A |
| Maximum number of tables per pipeline | 250 |

Google Analytics

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | Supported  If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 250 |

HubSpot

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Not supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Partially supported  Some tables support incremental ingestion. Other tables require a full refresh. See [HubSpot connector reference](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/hubspot-reference). |
| Unity Catalog governance | Supported |
| Lakeflow Jobs | Supported |
| SCD type 2 | Supported |
| Column selection and deselection | Supported |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Not supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Not supported |
| Automated schema evolution: New tables | Supported |
| Maximum number of tables per pipeline | 250 |

Jira

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | N/A |
| Maximum number of tables per pipeline | 250 |

Meta Ads

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Not supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Partially supported  Report tables support incremental ingestion. Resource tables are fully refreshed on each update. |
| Unity Catalog governance | Supported |
| Lakeflow Jobs | Supported |
| SCD type 2 | Not supported |
| Column selection and deselection | Supported  You can select specific tables. |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Not supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Not supported |
| Automated schema evolution: New tables | N/A |
| Maximum number of tables per pipeline | 250 |

MySQL

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | Supported  If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 250 |

NetSuite

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | Supported  If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 200 |

PostgreSQL

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Not supported  Requires a full refresh. |
| Automated schema evolution: New tables | Supported  If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 250 |

Salesforce

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported  By default, formula fields require full snapshots. To enable incremental ingestion for formula fields, see [Ingest Salesforce formula fields incrementally](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/salesforce-formula-fields). |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | N/A |
| Maximum number of tables per pipeline | 250 |

ServiceNow

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported  With exceptions when your table lacks a cursor field |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | Supported  If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 250 |

SharePoint

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Yes |
| Declarative Automation Bundles | Yes |
| Incremental ingestion | Yes |
| Unity Catalog governance | Yes |
| Orchestration using Databricks Workflows | Yes |
| SCD type 2 | Yes |
| API-based column selection and deselection | Yes |
| API-based row filtering | No |
| Automated schema evolution: New and deleted columns | Yes |
| Automated schema evolution: Data type changes | No |
| Automated schema evolution: Column renames | No - Requires full refresh. |
| Automated schema evolution: New tables | Yes - If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 250 |

SQL Server

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Yes |
| API-based pipeline authoring | Yes |
| Declarative Automation Bundles | Yes |
| Incremental ingestion | Yes |
| Unity Catalog governance | Yes |
| Orchestration using Databricks Workflows | Yes |
| SCD type 2 | Yes |
| API-based column selection and deselection | Yes |
| API-based row filtering | No |
| Automated schema evolution: New and deleted columns | Yes |
| Automated schema evolution: Data type changes | No |
| Automated schema evolution: Column renames | No - Requires full refresh. |
| Automated schema evolution: New tables | Yes - If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 250 |

TikTok Ads

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Not supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported  With exceptions when your table doesn't support incremental ingestion. See [Tables that support incremental updates](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/tiktok-ads-reference#incremental-tables). |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Not supported  Requires a full refresh. |
| Automated schema evolution: New tables | Supported  If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 250 |

Workday HCM

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Not supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported (selected tables only) |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Not supported |
| API-based column selection and deselection | Not supported |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Not supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Not supported |
| Automated schema evolution: New tables | Not supported |
| Maximum number of tables per pipeline | N/A |

Workday Reports

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | N/A |
| Maximum number of tables per pipeline | 250 |

Zendesk Support

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Supported  Treated as a new column (new name) and deleted column (old name). |
| Automated schema evolution: New tables | N/A |
| Maximum number of tables per pipeline | 250 |

## Authentication methods

The following table lists the supported authentication methods for each managed ingestion connector. Databricks recommends using OAuth U2M or OAuth M2M when possible. If your connector supports OAuth, basic authentication is considered a legacy method.

Confluence

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

Dynamics 365

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

Google Ads

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

Google Analytics

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Supported (API-only) |
| Basic authentication (service account JSON key) | Not supported |

HubSpot

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

Jira

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

Meta Ads

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

MySQL

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Not supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

NetSuite

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Not supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Supported |

PostgreSQL

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Not supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

Salesforce

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

ServiceNow

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Supported (API-only) |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

SharePoint

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Supported (Public Preview) |
| OAuth (manual refresh token) | Supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

SQL Server

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

TikTok Ads

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

Workday HCM

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Not supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

Workday Reports

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Not supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Supported |
| Basic authentication (username/password) | Supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

Zendesk Support

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

## Dependence on external services

Databricks SaaS, database, and other fully-managed connectors depend on the accessibility, compatibility, and stability of the application, database, or external service they connect to. Databricks does not control these external services and, therefore, has limited (if any) influence over their changes, updates, and maintenance.

If changes, disruptions, or circumstances related to an external service impede or render impractical the operation of a connector, Databricks may discontinue or cease maintaining that connector. Databricks will make reasonable efforts to notify customers of discontinuation or cessation of maintenance, including updates to the applicable documentation.