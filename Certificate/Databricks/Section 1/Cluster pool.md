---
title: "Pool configuration reference | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/compute/pools"
author:
published: 2025-02-11
created: 2026-03-31
description: "Learn how to create a Databricks pool in the UI, including the available configuration options for new pools."
tags:
  - "clippings"
---
This article describes the available settings when creating a pool using the UI. To learn how to use the Databricks CLI to create a pool, see [Databricks CLI commands](https://docs.databricks.com/aws/en/dev-tools/cli/commands). To learn how to use the REST API to create a pool, see the [Instance Pools API](https://docs.databricks.com/api/workspace/instancepools).

> [!-secondary] -secondary
> note
> 
> If your workload supports serverless compute, Databricks recommends using serverless compute instead of pools to take advantage of always-on, scalable compute. See [Connect to serverless compute](https://docs.databricks.com/aws/en/compute/serverless/).

## Pool size

When you create a pool, in order to control its size, you can set three parameters: minimum idle instances, maximum capacity, and idle instance auto termination.

### Minimum Idle Instances

The minimum number of instances the pool keeps idle. These instances do not terminate, regardless of the auto termination settings. If a cluster consumes idle instances from the pool, Databricks provisions additional instances to maintain the minimum.

### Maximum Capacity

The maximum number of instances the pool can provision. If set, this value constrains *all instances* (idle + used). If a cluster using the pool requests more instances than this number during [autoscaling](https://docs.databricks.com/aws/en/compute/configure#autoscaling), the request fails with an `INSTANCE_POOL_MAX_CAPACITY_FAILURE` error.

This configuration is *optional*. Databricks recommend setting a value only in the following circumstances:

- You have an instance quota you *must* stay under.
- You want to protect one set of work from impacting another set of work. For example, suppose your instance quota is 100 and you have teams A and B that need to run jobs. You can create pool A with a max 50 and pool B with max 50 so that the two teams share the 100 quota fairly.
- You need to cap cost.

### Idle instance auto termination

The time in minutes above the value set in [Minimum Idle Instances](https://docs.databricks.com/aws/en/compute/pools#pool-min) that instances can be idle before being terminated by the pool.

## Instance types

A pool consists of both idle instances kept ready for new clusters and instances in use by running clusters. All of these instances are of the same instance provider type, selected when creating a pool.

A pool's instance type cannot be edited. Clusters attached to a pool use the same instance type for the driver and worker nodes. Different families of instance types fit different use cases, such as memory-intensive or compute-intensive workloads.

Databricks always provides one year's deprecation notice before ceasing support for an instance type.

## Preloaded Databricks Runtime version

You can speed up cluster launches by selecting a Databricks Runtime version to be loaded on idle instances in the pool. If a user selects that runtime when they create a cluster backed by the pool, that cluster will launch even more quickly than a pool-backed cluster that doesn't use a preloaded Databricks Runtime version.

Setting this option to **None** slows down cluster launches, as it causes the Databricks Runtime version to download on demand to idle instances in the pool. When the cluster releases the instances in the pool, the Databricks Runtime version remains cached on those instances. The next cluster creation operation that uses the same Databricks Runtime version might benefit from this caching behavior, but it is not guaranteed.

## Preloaded Docker image

Docker images are supported with pools if you use the [Instance Pools API](https://docs.databricks.com/api/workspace/instancepools) to create the pool.

## Pool tags

Pool tags allow you to easily monitor the cost of cloud resources used by various groups in your organization. You can specify tags as key-value pairs when you create a pool, and Databricks applies these tags to cloud resources like VMs and disk volumes, as well as [DBU usage reports](https://docs.databricks.com/aws/en/admin/account-settings/usage).

For convenience, Databricks applies three default tags to each pool: `Vendor`, `DatabricksInstancePoolId`, and `DatabricksInstancePoolCreatorId`. You can also add custom tags when you create a pool. You can add up to 43 custom tags.

### Custom tags

To add additional tags to the pool, navigate to the **Tabs** tab at the bottom of the **Create Pool** page. Click the **\+ Add** button, then enter the key-value pair.

Pool-backed clusters inherit default and custom tags from the pool configuration. For detailed information about how pool tags and cluster tags work together, see [Use tags to attribute and track usage](https://docs.databricks.com/aws/en/admin/account-settings/usage-detail-tags).

## AWS configurations

When you configure a pool's AWS instances you can choose the availability zone (AZ), whether to use spot instances and the max spot price, and the EBS volume type and size. All clusters attached to the pool inherit these configurations.

### Availability zones

Choosing a specific AZ for a pool is useful primarily if your organization has purchased reserved instances in specific availability zones. For more information on AZs, see [AWS availability zones](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html).

#### Auto-AZ with pools

If you use a fleet instance type with your pool, you can select **auto** as the availability zone. When you use auto-AZ, the availability zone is automatically selected based on available cloud provider capacity. The pool will be moved to the best AZ right before every scale-up-from-zero event, and will remain fixed to a single AZ while the pool is non-empty. For more information, see [AWS Fleet instance types](https://docs.databricks.com/aws/en/compute/configure#fleet).

Clusters that you attach to a pool inherit the pool's availability zone. You cannot specify the availability zone for individual clusters in pools.

### Spot instances

You can specify whether you want the pool to use spot instances. A pool can either be all spot instances or all on-demand instances.

You can also set the max spot price to use when launching spot instances. This is set as a percentage of the corresponding on-demand price. By default, Databricks sets the max spot price at 100% of the on-demand price. See [AWS spot pricing](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html).

### EBS volumes

Databricks provisions EBS volumes for every instance as follows:

- A 30 GB unencrypted EBS instance root volume used only by the host operating system and Databricks internal services.
- A 150 GB encrypted EBS container root volume used by the Spark worker. This hosts Spark services and logs.
- (HIPAA only) a 75 GB encrypted EBS worker log volume that stores logs for Databricks internal services.

#### Add EBS shuffle volumes

To add shuffle volumes, select **General Purpose SSD** in the **EBS Volume Type** dropdown list.

By default, Spark shuffle outputs go to the instance local disk. For instance types that do not have a local disk, or if you want to increase your Spark shuffle storage space, you can specify additional EBS volumes. This is particularly useful to prevent out of disk space errors when you run Spark jobs that produce large shuffle outputs.

Databricks encrypts these EBS volumes for both on-demand and spot instances. Read more about [AWS EBS volumes](https://aws.amazon.com/ebs/features/).

#### AWS EBS limits

Ensure that your AWS EBS limits are high enough to satisfy the runtime requirements for all instances in all pools. For information on the default EBS limits and how to change them, see [Amazon Elastic Block Store (EBS) Limits](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html#limits_ebs).

### Autoscaling local storage

If you don't want to allocate a fixed number of EBS volumes at pool creation time, use autoscaling local storage. With autoscaling local storage, Databricks monitors the amount of free disk space available on your pool's Spark workers. If a worker begins to run too low on disk, Databricks automatically attaches a new EBS volume to the worker before it runs out of disk space. EBS volumes are attached up to a limit of 5 TB of total disk space per instance (including the instance's local storage).

To configure autoscaling storage, select **Enable autoscaling local storage**.

The EBS volumes attached to an instance are detached only when the instance is returned to AWS. That is, EBS volumes are never detached from an instance as long as it is in the pool. To scale down EBS usage, Databricks recommends configuring the [Pool size](https://docs.databricks.com/aws/en/compute/pools#instance-pool-sizing).

> [!-secondary] -secondary
> note
> 
> - Databricks uses Amazon EBS GP3 volumes to extend the local storage of an instance. The [default AWS capacity limit](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html#limits_ebs) for these volumes is 50 TiB. To avoid hitting this limit, administrators should request an increase in this limit based on their usage requirements.
> - If you want to use autoscaling local storage, the IAM role or keys used to create your account must include the permissions `ec2:AttachVolume`, `ec2:CreateVolume`, `ec2:DeleteVolume`, and `ec2:DescribeVolumes`. For the complete list of permissions and instructions on how to update your existing IAM role or keys, see [Create a credential configuration](https://docs.databricks.com/aws/en/admin/workspace/create-uc-workspace#credential).