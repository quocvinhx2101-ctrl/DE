---
title: "Configure Structured Streaming trigger intervals | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/structured-streaming/triggers"
author:
published: 2026-02-10
created: 2026-03-31
description: "Learn how to configure Structured Streaming trigger intervals on Databricks."
tags:
  - "clippings"
---
This article explains how to configure trigger intervals for Structured Streaming on Databricks.

Apache Spark Structured Streaming processes data incrementally. Trigger intervals control how frequently Structured Streaming checks for new data. You can configure trigger intervals for near-real-time processing, for scheduled database refreshes, or batch processing all new data for a day or a week.

Because [What is Auto Loader?](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/) uses Structured Streaming to load data, understanding how triggers work provides you with the greatest flexibility to control costs while ingesting data with the desired frequency.

## Trigger modes overview

The following table summarizes the trigger modes available in Structured Streaming:

| Trigger Mode | Syntax Example (Python) | Best For |
| --- | --- | --- |
| Unspecified (Default) | N/A | General-purpose streaming with 3-5 second latency. Equivalent to processingTime trigger with 0 ms intervals. Stream processing runs continuously as long as new data arrives. |
| Processing Time | `.trigger(processingTime='10 seconds')` | Balancing cost and performance. Reduces overhead by preventing the system from checking for data too frequently. |
| Available Now | `.trigger(availableNow=True)` | Scheduled incremental batch processing. Processes as much data as is available at the time the streaming job is triggered. |
| Real-time mode | `.trigger(realTime='5 minutes')` | Ultra-low latency operational workloads requiring sub-second processing, such as fraud detection or real-time personalization. Public Preview. '5 minutes' indicates the length of a micro-batch. Use 5 minutes to minimize per-batch overhead such as query compilation. |
| Continuous | `.trigger(continuous='1 second')` | Not supported. This is an experimental feature included in Spark OSS. Use real-time mode instead. |

## processingTime: Time-based trigger intervals

Structured Streaming refers to time-based trigger intervals as "fixed interval micro-batches". Using the `processingTime` keyword, specify a time duration as a string, such as `.trigger(processingTime='10 seconds')`.

The configuration of this interval determines how often the system performs checks to see if new data has arrived. Configure your processing time to balance latency requirements and the rate that data arrives in the source.

## AvailableNow: Incremental batch processing

> [!-info] -info
> important
> 
> In Databricks Runtime 11.3 LTS and later, `Trigger.Once` is deprecated. Use `Trigger.AvailableNow` for all incremental batch processing workloads.

The `AvailableNow` trigger option consumes all available records as an incremental batch with the ability to configure batch size with options such as `maxBytesPerTrigger`. Sizing options vary by data source.

### Supported data sources

Databricks supports using `Trigger.AvailableNow` for incremental batch processing from many Structured Streaming sources. The following table includes the minimum supported Databricks Runtime version required for each data source:

| Source | Minimum Databricks Runtime version |
| --- | --- |
| File sources (JSON, Parquet, etc.) | 9.1 LTS |
| Delta Lake | 10.4 LTS |
| Auto Loader | 10.4 LTS |
| Apache Kafka | 10.4 LTS |
| Kinesis | 13.1 |

## realTime: Ultra-low-latency operational workloads

> [!-info] -info
> Preview
> 
> This feature is in [Public Preview](https://docs.databricks.com/aws/en/release-notes/release-types).

Real-time mode for Structured Streaming achieves end-to-end latency under 1 second at the tail, and in common cases around 300 ms. For more details on how to effectively configure and use real-time mode, see [Real-time mode in Structured Streaming](https://docs.databricks.com/aws/en/structured-streaming/real-time).

Apache Spark has an additional trigger interval known as [Continuous Processing](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#continuous-processing). This mode has been classified as experimental since Spark 2.3. Databricks doesn't support or recommend this mode. Use real-time mode instead for low-latency use cases.

> [!-secondary] -secondary
> note
> 
> The continuous processing mode on this page is unrelated to continuous processing in [Lakeflow Spark Declarative Pipelines](https://docs.databricks.com/aws/en/ldp/).

## Change trigger intervals between runs

You can change the trigger interval between runs while using the same checkpoint.

### Behavior when changing intervals

If a Structured Streaming job stops while a micro-batch is being processed, that micro-batch must complete before the new trigger interval applies. As a result, you might observe a micro-batch processing with the previously specified settings after changing the trigger interval. The following describes the expected behavior when transitioning:

- **Transitioning from time-based interval to `AvailableNow`:** A micro-batch might process ahead of processing all available records as an incremental batch.
- **Transitioning from `AvailableNow` to time-based interval:** Processing might continue for all records that were available when the last `AvailableNow` job triggered. This is expected behavior.

### Recovering from query failures

> [!-secondary] -secondary
> note
> 
> If you're trying to recover from query failure associated with an incremental batch, changing the trigger interval doesn't solve this problem because the batch must still be completed. Scale up the compute capacity used to process the batch to try to resolve the issue. In rare cases, you might need to restart the stream with a new checkpoint.