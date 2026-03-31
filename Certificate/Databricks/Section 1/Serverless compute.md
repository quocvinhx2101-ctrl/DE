---
title: "Connect to serverless compute | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/compute/serverless"
author:
published: 2026-03-19
created: 2026-03-31
description: "Learn about serverless compute for notebooks, workflows, and Lakeflow Declarative Pipelines in Databricks."
tags:
  - "clippings"
---
This page explains how to connect to and use serverless compute for notebooks, workflows, and Lakeflow Spark Declarative Pipelines in Databricks.

## What is serverless compute?

Serverless compute is a Databricks-managed service that allows users to quickly connect to on-demand computing resources for notebooks, workflows, and Lakeflow Spark Declarative Pipelines.

When you choose to use serverless compute, you can run workloads without provisioning any compute resources in your cloud account. Instead, Databricks automatically allocates and manages the necessary compute resources. This speeds up start-up and scaling times, minimizes idle time, and reduces the need to manage compute resources.

Serverless workloads are protected by multiple layers of security and are designed to be enterprise-ready. For more information, see [Databricks serverless security](https://www.databricks.com/trust/security-features/serverless-security).

> [!-secondary] -secondary
> note
> 
> Serverless compute is available by default in most workspaces and does not require enablement. Workspaces that have Unity Catalog enabled automatically have access to serverless compute.
> 
> Other Databricks features, such as serverless SQL warehouses, model serving, and AI features, use serverless infrastructure independently and have their own configuration paths. This page covers serverless compute for notebooks, workflows, and Lakeflow Spark Declarative Pipelines only.

Use the following pages to learn how to configure workloads to use serverless compute:

- [Serverless notebooks](https://docs.databricks.com/aws/en/compute/serverless/notebooks)
- [Serverless jobs](https://docs.databricks.com/aws/en/jobs/run-serverless-jobs)
- [Serverless Lakeflow Spark Declarative Pipelines](https://docs.databricks.com/aws/en/ldp/serverless)
- [AI Runtime](https://docs.databricks.com/aws/en/machine-learning/ai-runtime/) (Preview)
- [Guides for AI Runtime](https://docs.databricks.com/aws/en/machine-learning/ai-runtime/guides)

## Other features that use serverless infrastructure

Many Databricks features run on serverless infrastructure but are configured and managed separately from serverless compute for notebooks, jobs, and Lakeflow Spark Declarative Pipelines. For example:

- [Serverless SQL warehouses](https://docs.databricks.com/aws/en/compute/sql-warehouse/#what-is-serverless-sql)
- [Mosaic AI Model Training - forecasting](https://docs.databricks.com/aws/en/machine-learning/train-model/serverless-forecasting)
- [Data quality monitoring](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring/)
- [Predictive optimization](https://docs.databricks.com/aws/en/optimizations/predictive-optimization)

## Serverless compute requirements

Serverless compute is available by default in most workspaces. No manual enablement steps are required.

Legacy workspaces that are not enabled for Unity Catalog do not have access to serverless compute. To access serverless compute, you must upgrade to Unity Catalog. See [Upgrade a Databricks workspaces to Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/upgrade/).

## Serverless compute limitations

For a list of limitations, see [Serverless compute limitations](https://docs.databricks.com/aws/en/compute/serverless/limitations).

## Frequently asked questions (FAQ)

- [How are releases rolled out?](https://docs.databricks.com/aws/en/compute/serverless#how-are-releases-rolled-out)
- [How do I determine which serverless version I am running?](https://docs.databricks.com/aws/en/compute/serverless#how-do-i-determine-which-serverless-version-i-am-running)
- [How do I estimate costs for serverless?](https://docs.databricks.com/aws/en/compute/serverless#how-do-i-estimate-costs-for-serverless)
- [How do I analyze DBU usage for a specific workload?](https://docs.databricks.com/aws/en/compute/serverless#how-do-i-analyze-dbu-usage-for-a-specific-workload)
- [Is there a delay between when you run a job or query and the appearance of charges on the billable usage system table?](https://docs.databricks.com/aws/en/compute/serverless#is-there-a-delay-between-when-you-run-a-job-or-query-and-the-appearance-of-charges-on-the-billable-usage-system-table)
- [Why do I see billing records for serverless jobs even though I haven't run serverless workloads?](https://docs.databricks.com/aws/en/compute/serverless#why-do-i-see-billing-records-for-serverless-jobs-even-though-i-havent-run-serverless-workloads)
- [Does serverless compute support private repos?](https://docs.databricks.com/aws/en/compute/serverless#does-serverless-compute-support-private-repos)
- [How do I install libraries for my job tasks?](https://docs.databricks.com/aws/en/compute/serverless#how-do-i-install-libraries-for-my-job-tasks)
- [Can I connect to custom data sources?](https://docs.databricks.com/aws/en/compute/serverless#can-i-connect-to-custom-data-sources)
- [How does the serverless compute plane networking work?](https://docs.databricks.com/aws/en/compute/serverless#how-does-the-serverless-compute-plane-networking-work)
- [Can I configure serverless compute for jobs with Declarative Automation Bundles?](https://docs.databricks.com/aws/en/compute/serverless#can-i-configure-serverless-compute-for-jobs-with-declarative-automation-bundles)
- [How do I run my serverless workload from my local development machine or from my data application?](https://docs.databricks.com/aws/en/compute/serverless#how-do-i-run-my-serverless-workload-from-my-local-development-machine-or-from-my-data-application)

### How are releases rolled out?

Serverless compute is a *versionless* product, which means that Databricks automatically upgrades the serverless compute runtime to support enhancements and upgrades to the platform. All users get the same updates, rolled out over a short period of time.

### How do I determine which serverless version I am running?

Serverless workloads always run on the latest runtime version. See [Release notes](https://docs.databricks.com/aws/en/release-notes/serverless/#release-notes) for the most recent version.

### How do I estimate costs for serverless?

Databricks recommends running and benchmarking a representative or specific workload and then analyzing the billing system table. See [Billable usage system table reference](https://docs.databricks.com/aws/en/admin/system-tables/billing).

### How do I analyze DBU usage for a specific workload?

To see the cost for a specific workload, query the `system.billing.usage` system table. See [Monitor the cost of serverless compute](https://docs.databricks.com/aws/en/admin/system-tables/serverless-billing) for sample queries and to download our cost observability dashboard.

### Is there a delay between when you run a job or query and the appearance of charges on the billable usage system table?

Yes, there could be up to a 24-hour delay between when you run a workload and its usage being reflected in the billable usage system table.

### Why do I see billing records for serverless jobs even though I haven't run serverless workloads?

[Data quality monitoring](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring/) and [predictive optimization](https://docs.databricks.com/aws/en/optimizations/predictive-optimization) run on serverless infrastructure and are billed under the serverless jobs SKU. These features are managed separately from serverless compute for notebooks, workflows, and Lakeflow Spark Declarative Pipelines.

### Does serverless compute support private repos?

Repositories can be private or require authentication. For security reasons, a pre-signed URL is required when accessing authenticated repositories.

### How do I install libraries for my job tasks?

Databricks recommends using environments to install and manage libraries for your jobs. See [Configure environment for job tasks](https://docs.databricks.com/aws/en/compute/serverless/dependencies#libraries).

### Can I connect to custom data sources?

No, only sources that use Lakehouse Federation are supported. See [Supported data sources](https://docs.databricks.com/aws/en/query-federation/database-federation#connection-types).

### How does the serverless compute plane networking work?

Serverless compute resources run in the serverless compute plane, which is managed by Databricks. For more details on the network and architecture, see [Serverless compute plane networking](https://docs.databricks.com/aws/en/security/network/serverless-network-security/).

### Can I configure serverless compute for jobs with Declarative Automation Bundles?

Yes, Declarative Automation Bundles can be used to configure jobs that use serverless compute. See [Job that uses serverless compute](https://docs.databricks.com/aws/en/dev-tools/bundles/examples#job-serverless).

### How do I run my serverless workload from my local development machine or from my data application?

Databricks Connect allows you to connect to Databricks from your local machine and run workloads on serverless. See [What is Databricks Connect?](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/).