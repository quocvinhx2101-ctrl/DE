
#databricks/hilarious 

<mark style="background: #BBFABBA6;">Exam Weight: 18% — This section covers deploying workloads to meet production requirements using Lakeflow Jobs, developing and troubleshooting Lakeflow Declarative Pipelines, and working with Lakeflow Connect ingestion pipelines</mark>

## 1. Databricks Asset Bundles (DAB) vs Traditional Deployment

### Topic Overview

Databricks Asset Bundles (DABs) represent a modern infrastructure as code approach for deploying and managing Databricks resources. Instead of manually creating jobs, pipelines, notebooks, and other resources through the UI, you define everything in YAML configuration files and deploy them programmatically. This shift transforms Databricks workspace management from a manual, error prone process into a repeatable, version controlled workflow.

Traditional deployment approaches rely on manual UI interactions or custom REST API/CLI scripts to create and manage resources. These methods lack version control for deployment configurations, making it difficult to reproduce environments across different stages (development, staging, production) and nearly impossible to implement proper CI/CD workflows. DABs solve these problems by providing a declarative, file based approach that integrates seamlessly with Git and standard DevOps tools.

A DAB project centers around a databricks.yml file that declares all resources you want to deploy. You use the Databricks CLI to validate, deploy, and run your resources. The targets feature allows you to parameterize configurations per environment, enabling the same DAB definition to work across development, staging, and production workspaces with different settings.

---

### Key Concepts

- What are Databricks Asset Bundles (DABs)?
    
    DABs are a declarative infrastructure as code framework for Databricks. You define your workspace resources (jobs, pipelines, notebooks, clusters, schemas) in YAML files and deploy them using the Databricks CLI. Each DAB is a directory containing a databricks.yml file and supporting resource files. DABs integrate with Git for version control and support environment based configurations through targets.
    
- Traditional Deployment Issues
    
    Manual UI based deployments lack version control, making it impossible to track who changed what and when. REST API/CLI scripts are custom one offs without standardization. Promoting environments (dev to staging to prod) requires manual duplication and adjustment of configurations. No built in parameterization means hardcoding values or maintaining separate scripts per environment. Reproducing production setups in new workspaces is error prone and time consuming.
    
- DAB Workflow and Commands
    
    A typical DAB workflow involves: (1) Define resources in databricks.yml and supporting files, (2) Run databricks bundle validate to check for syntax errors and missing resources, (3) Run databricks bundle deploy to create or update resources in the workspace, (4) Run databricks bundle run to trigger job or pipeline execution. Each command respects the target configuration, allowing the same DAB to deploy to different workspaces.
    
- Targets and Environment Management
    
    Targets allow you to define environment specific configurations within a single DAB. A target specifies the workspace URL, paths, variable values, and resource settings for a particular environment (dev, staging, prod). You specify which target to use when running bundle commands with the --target flag. This eliminates the need for separate DAB projects per environment and ensures consistency across deployments.
    
- DABs vs REST API and CLI Scripts
    
    REST API and custom CLI scripts offer fine grained control but require you to build and maintain the entire deployment logic. DABs provide a standardized, opinionated framework that handles validation, deployment, and targeting automatically. DABs are optimized for common use cases (deploying jobs, pipelines, notebooks) whereas REST APIs require more boilerplate. DABs integrate natively with Databricks CLI and Git based workflows, while custom scripts need additional integration work.    

---

### Code Examples

#### Basic databricks.yml Example

```yaml
bundle:
  name: my_data_pipeline
  version: "1.0.0"

resources:
  jobs:
    daily_ingest:
      name: Daily Data Ingestion
      tasks:
        - task_key: load_raw_data
          notebook_task:
            notebook_path: ./notebooks/ingest.py
          existing_cluster_id: cluster-12345
    
    daily_transform:
      name: Daily Data Transform
      tasks:
        - task_key: transform_data
          notebook_task:
            notebook_path: ./notebooks/transform.py
          existing_cluster_id: cluster-12345
      depends_on:
        - job_key: daily_ingest

  pipelines:
    production_pipeline:
      name: Production Data Pipeline
      target: "${var.catalog}.${var.schema}.gold"
      clusters:
        - label: default
          num_workers: 2
      libraries:
        - package: pyspark
      configuration:
        "spark.conf.spark.sql.shuffle.partitions": "200"
```

#### Multi Target Configuration

```yaml
bundle:
  name: my_pipeline

variables:
  catalog:
    description: Unity Catalog name
    default: main

resources:
  jobs:
    process_data:
      name: Process Data
      tasks:
        - task_key: process
          notebook_task:
            notebook_path: ./notebooks/process.py
          existing_cluster_id: "${resources.clusters.compute.id}"

targets:
  dev:
    workspace:
      host: <https://dev-workspace.cloud.databricks.com>
      token: ${DBX_DEV_TOKEN}
    variables:
      catalog: dev_catalog
      cluster_id: dev-cluster-123
  
  staging:
    workspace:
      host: <https://staging-workspace.cloud.databricks.com>
      token: ${DBX_STAGING_TOKEN}
    variables:
      catalog: staging_catalog
      cluster_id: staging-cluster-456
  
  prod:
    workspace:
      host: <https://prod-workspace.cloud.databricks.com>
      token: ${DBX_PROD_TOKEN}
    variables:
      catalog: prod_catalog
      cluster_id: prod-cluster-789
```

#### DAB Deployment Commands

```bash
# Validate the bundle configuration
databricks bundle validate

# Validate for a specific target
databricks bundle validate --target dev

# Deploy to development
databricks bundle deploy --target dev

# Deploy to staging
databricks bundle deploy --target staging

# Deploy to production
databricks bundle deploy --target prod

# Run a specific job in the dev environment
databricks bundle run daily_ingest --target dev

# View the plan of what will be deployed (dry run)
databricks bundle deploy --target prod --dry-run

# List all resources in the bundle
databricks bundle list
```

#### Traditional REST API Comparison

```bash
# Traditional approach: manual REST API calls
# This requires custom scripting and error handling

# Create a job using REST API
curl -X POST <https://your-workspace.databricks.com/api/2.1/jobs/create> \\
  -H "Authorization: Bearer <token>" \\
  -d '{
    "name": "Daily Ingest",
    "tasks": [
      {
        "task_key": "load_data",
        "notebook_task": {
          "notebook_path": "/Users/user/notebooks/ingest"
        },
        "existing_cluster_id": "cluster-123"
      }
    ]
  }'

# Update the same job for staging (manual duplication with different IDs)
curl -X POST <https://staging-workspace.databricks.com/api/2.1/jobs/create> \\
  -H "Authorization: Bearer <staging-token>" \\
  -d '{
    "name": "Daily Ingest",
    "tasks": [
      {
        "task_key": "load_data",
        "notebook_task": {
          "notebook_path": "/Users/user/notebooks/ingest"
        },
        "existing_cluster_id": "cluster-456"
      }
    ]
  }'

# With DABs, a single command handles both:
databricks bundle deploy --target dev
databricks bundle deploy --target staging
```

---

### Common Exam Scenarios

#### Scenario 1: Deploying the Same Pipeline to Multiple Environments

A team needs to deploy a data pipeline to development, staging, and production workspaces with different cluster sizes and catalog names. Using a traditional approach, they would need to create three separate job definitions with hardcoded workspace URLs and cluster IDs. With DABs, they define the pipeline once in databricks.yml and use targets to specify environment specific values. A single databricks bundle deploy --target prod command deploys to production with the correct workspace URL, cluster size, and catalog name. This eliminates copy paste errors and ensures consistency across all environments.

#### Scenario 2: Version Controlling Deployment Configurations

A team manually creates jobs through the Databricks UI and loses track of what changed and when. An engineer modifies a job, causing a production outage, but no one can see who made the change or revert it. With DABs, the databricks.yml file lives in Git, so every change has a commit message, author, and timestamp. The team can see exactly what changed in a pull request before deployment. If a change causes issues, they can quickly revert to the previous version. This provides audit trails and enables code review for infrastructure changes.

#### Scenario 3: Implementing CI/CD for Data Pipelines

A team wants to run automated tests and deploy pipelines through a CI/CD system (GitHub Actions, GitLab CI). Traditional approaches require custom scripting to call REST APIs. DABs integrate seamlessly with CI/CD: the pipeline runs databricks bundle validate to check configurations, then databricks bundle deploy --target staging to deploy to staging for testing, and finally databricks bundle deploy --target prod upon approval. The same DAB definition is used throughout the entire workflow, reducing opportunities for configuration drift.

---

### Key Takeaways

- DABs provide infrastructure as code for Databricks, replacing manual UI interactions with declarative YAML configuration files that integrate with Git and standard DevOps tools.
- Key commands are: databricks bundle validate (check config), databricks bundle deploy (create/update resources), and databricks bundle run (execute jobs/pipelines).
- Targets enable environment based parameterization, allowing a single DAB to deploy to dev, staging, and prod with different configurations.
- DABs solve traditional deployment issues: lack of version control, manual duplication, configuration drift, and difficulty promoting environments.
- DABs support deploying jobs, pipelines, notebooks, clusters, schemas, and other Databricks resources with a single, standardized framework.

---

### Gotchas and Tips

<aside> ⚠️ Secrets and Environment Variables

</aside>

Never hardcode tokens, passwords, or API keys directly in databricks.yml. Use environment variables (referenced with ${VARIABLE_NAME}) or Databricks secrets. Store sensitive values in CI/CD system secrets or local environment configuration files that are .gitignored.

<aside> ⚠️ Path References in Resources

</aside>

When referencing notebook paths in databricks.yml, use relative paths (e.g., ./notebooks/my_notebook.py) from the bundle root directory. The Databricks CLI automatically resolves these relative paths and uploads the notebooks to the workspace during deployment. Absolute paths or workspace URLs can cause path resolution issues.

<aside> ⚠️ Dry Run Before Production Deployment

</aside>

Always run databricks bundle deploy --target prod --dry-run before actually deploying to production. This shows you exactly what resources will be created, updated, or deleted without actually making changes. It catches configuration errors and unintended side effects before they impact production.

---

### Links and Resources

- [**What are Databricks Asset Bundles?**](https://docs.databricks.com/aws/en/dev-tools/bundles) — Overview of DABs for infrastructure as code deployments.
- [**Databricks Asset Bundle deployment modes**](https://docs.databricks.com/aws/en/dev-tools/bundles/deployment-modes) — Development vs production deployment mode differences.
- [**CI/CD on Databricks**](https://docs.databricks.com/aws/en/dev-tools/ci-cd/) — Overview of CI/CD approaches including DABs and Git integration.

---

## 2.  Asset Bundle Structure
### Topic Overview

A Databricks Asset Bundle (DAB) is a declarative framework for packaging, deploying, and managing Databricks resources as code. The bundle follows a strict directory and configuration structure that defines how your code, jobs, pipelines, and other assets are organized locally and then synced and deployed to a Databricks workspace.

The foundation of every DAB is the databricks.yml configuration file. This YAML file sits at the root of your bundle and contains the bundle metadata, resource definitions, variables, environment targets, and workspace configuration. Everything else your notebooks, Python scripts, test files, and library packages lives in subdirectories that are referenced by databricks.yml.

When you run databricks bundle deploy, the DAB CLI reads your configuration, builds any artifacts (like wheel files), syncs your local files to the workspace, and creates or updates all the resources defined in your bundle. This makes it easy to version control your entire data infrastructure and reproduce deployments consistently across environments.

---

## Key Concepts

- **databricks.yml Anatomy**
    
    The databricks.yml file has these main sections:
    
    - bundle: Metadata like name and version
    - variables: Parameterized values used throughout the config
    - resources: Job definitions, Lakeflow pipelines, schemas, models, experiments
    - targets: Environment specific overrides (dev, staging, prod)
    - workspace: Configuration for syncing to the remote workspace (host, auth, path)
    - artifacts: Build instructions for libraries (e.g., Python wheels)

- **Resources Block**
    
	The resources: section defines all the Databricks assets that will be created or updated on deploy. Common resource types include:
    
    - jobs: Scheduled or triggered workflows (tasks, schedule, clusters, parameters)
    - pipelines: Lakeflow Spark Declarative Pipelines (batch or streaming ingestion and transformation)
    - schemas: Unity Catalog schemas
    - models: Unity Catalog registered models
    - experiments: MLflow experiments for tracking ML runs
    
    Each resource is a named block containing configuration properties. Notebooks referenced in job tasks use relative paths from the bundle root, making it easy to move the entire bundle between workspaces.

- **Variables and Parameterization**
    
	Variables allow you to parameterize your bundle configuration. Define them in the variables: section with default values, then reference them in resources using ${var.variable_name}. Variables are particularly useful for:
    
    - Cluster sizing and configuration (per environment)
    - Data paths and schema names
    - Timeout and retry values for jobs
    - Environment specific settings (dev uses cheaper clusters, prod uses larger ones)
    
    The targets: section lets you override variable values per environment. When deploying, use databricks bundle deploy --target=prod to select which target's overrides apply.

- **Include for Modular Configs**
    
	For larger bundles, the include: directive lets you split configuration across multiple YAML files instead of one monolithic databricks.yml. This makes bundles easier to organize and maintain.
    
    Example: You could have resources/jobs.yml, resources/pipelines.yml, and resources/schemas.yml each with their own resource definitions. The main databricks.yml then includes all of them:

```yaml
include:
  - resources/jobs.yml
  - resources/pipelines.yml
  - resources/schemas.yml
```


- **Artifacts for Libraries**
    
	The artifacts: section defines how to build libraries (typically Python wheels) from source code in your bundle. The build process runs before deployment.
    
    A typical artifact entry specifies:
    
    - Type: usually whl for Python wheel
    - Path: source directory where [setup.py](http://setup.py) lives
    - Executable: path to the build script (often python [setup.py](http://setup.py) bdist_wheel)
    
	Jobs can then reference and install the built wheel, allowing you to package custom Python code and deploy it with your bundle.


- **Workspace and File Sync**
    
	The workspace: section in your bundle configuration tells the DAB CLI how to connect to and sync files to the Databricks workspace. It typically includes:
    
    - host: The Databricks workspace URL (e.g., [https://my-workspace.cloud.databricks.com](https://my-workspace.cloud.databricks.com))
    - token: Authentication token or a reference to a profile
    - root_path: The remote workspace path where files are synced (e.g., /Workspace/Users/user@company.com/my-bundle)
    
    When you deploy, the DAB CLI syncs all your notebooks, Python files, and other source code to the workspace root path. This allows job tasks to reference notebooks by relative paths.


---

### Code Examples

Complete databricks.yml with main sections:

```yaml
bundle:
  name: my-data-pipeline
  version: 1.0.0

variables:
  environment:
    default: dev
  num_workers:
    default: 2
  catalog_name:
    default: main
  schema_name:
    default: raw_data
  batch_size:
    default: 1000

resources:
  jobs:
    ingest_data:
      name: "Daily Data Ingestion - ${var.environment}"
      tasks:
        - task_key: ingest
          notebook_task:
            notebook_path: ./src/ingest
            base_parameters:
              batch_size: "${var.batch_size}"
          new_cluster:
            spark_version: "13.3.x-scala2.12"
            node_type_id: "i3.xlarge"
            num_workers: "${var.num_workers}"
          timeout_seconds: 3600

    transform_data:
      name: "Transform Data - ${var.environment}"
      tasks:
        - task_key: transform
          notebook_task:
            notebook_path: ./src/transform
          depends_on:
            - task_key: ingest
          new_cluster:
            spark_version: "13.3.x-scala2.12"
            num_workers: "${var.num_workers}"
```

Multi task job with dependencies:

```yaml
resources:
  jobs:
    multi_task_job:
      name: "Multi-Task ETL Job"
      tasks:
        - task_key: extract
          notebook_task:
            notebook_path: ./src/extract
            base_parameters:
              source_table: customer_raw
          new_cluster:
            spark_version: "13.3.x-scala2.12"
            node_type_id: "i3.xlarge"
            num_workers: 2
          timeout_seconds: 1800

        - task_key: transform
          depends_on:
            - task_key: extract
          notebook_task:
            notebook_path: ./src/transform
          new_cluster:
            spark_version: "13.3.x-scala2.12"
            num_workers: 2

        - task_key: load
          depends_on:
            - task_key: transform
          notebook_task:
            notebook_path: ./src/load

        - task_key: quality_check
          depends_on:
            - task_key: transform
          notebook_task:
            notebook_path: ./src/data_quality
```

Variables with environment specific targets:

```yaml
variables:
  cluster_size: small
  num_workers: 2
  instance_type: i3.xlarge
  notification_email: dev-team@company.com

targets:
  dev:
    variables:
      cluster_size: small
      num_workers: 2
      instance_type: i3.xlarge
      notification_email: dev-team@company.com

  staging:
    variables:
      cluster_size: medium
      num_workers: 4
      instance_type: i3.2xlarge
      notification_email: staging-team@company.com

  prod:
    variables:
      cluster_size: large
      num_workers: 8
      instance_type: i3.4xlarge
      notification_email: ops-team@company.com
```

Include pattern with modular configuration:

```yaml
bundle:
  name: modular-bundle
  version: 1.0.0

include:
  - ./resources/variables.yml
  - ./resources/jobs.yml
  - ./resources/pipelines.yml
  - ./resources/schemas.yml
  - ./targets.yml

workspace:
  host: "<https://my-workspace.cloud.databricks.com>"
  token: "${env.DATABRICKS_TOKEN}"
  root_path: "/Workspace/Users/user@company.com/modular-bundle"
```

Typical bundle directory structure:

```bash
my-data-bundle/
├── databricks.yml              # Root config file
├── src/
│   ├── ingest.py
│   ├── transform.py
│   ├── load.py
│   └── data_quality.py
├── tests/
│   ├── test_ingest.py
│   └── test_transform.py
├── resources/
│   ├── jobs.yml
│   ├── pipelines.yml
│   └── variables.yml
├── .databricks/
│   └── state/
└── my_package/
    ├── setup.py
    └── my_package/
```

---

### Common Exam Scenarios

#### Scenario 1: Environment specific configuration

A company has a data pipeline defined in a single DAB. In development, they use small clusters with 2 workers to save costs. In production, they need large clusters with 8 workers for performance. How would you structure the databricks.yml to support this?

Answer: Use the targets: section in databricks.yml with variable overrides. Define a variable num_workers with default value 2 (dev), then in the targets.prod section, override it to 8. Reference ${var.num_workers} in the cluster configuration. Deploy with databricks bundle deploy --target=prod to use the prod overrides.

#### Scenario 2: Resource dependencies and multi task jobs

Your bundle defines a job with four tasks: extract, transform, load, and quality check. The extract task should run first, then transform depends on extract, and both load and quality check depend on transform. How do you structure this in the resources section?

Answer: Each task has a task_key and an optional depends_on block. The extract task has no depends_on (runs immediately). Transform has depends_on: [task_key: extract]. Both load and quality check have depends_on: [task_key: transform]. This creates a DAG where extract runs first, then transform, then load and quality check run in parallel.

#### Scenario 3: Modularizing a large bundle

Your databricks.yml file has grown very large with 20+ jobs, 15 pipelines, and complex variable definitions. It's becoming hard to maintain. How would you restructure it?

Answer: Use the include: directive to split configuration into separate files. Create resources/jobs.yml and resources/pipelines.yml for resource definitions, and variables.yml for variable definitions. In the main databricks.yml, include all of them. Each file is now smaller and easier to manage. The CLI merges them at runtime.

---

### Key Takeaways

- The DAB is rooted in databricks.yml which defines all bundle metadata, resources, variables, and workspace configuration.
- Variables enable parameterization; targets: section allows environment specific overrides.
- Resources define jobs (with task dependencies), pipelines, schemas, models, and experiments.
- Use include: to split large bundles into modular YAML files for better maintainability.
- File sync ensures your local source code is always reflected in the workspace at the configured root path.

---

### Gotchas and Tips

<aside> ⚠️ Variable interpolation happens at deploy time. If you reference a variable in databricks.yml but don't define it as a variable, the deployment will fail. Always declare variables you plan to use.

</aside>

<aside> ⚠️ Notebook paths in job task definitions are relative to the bundle root on disk. Ensure your notebook_path points to a valid file. For example, ./src/ingest looks for a file named [ingest.py](http://ingest.py) in the src/ directory.

</aside>

<aside> ⚠️ When using include: to split configs, file paths are relative to the bundle root, not relative to the including file. Always use paths from the bundle root.

</aside>

---

### Links and Resources

- [**Databricks Asset Bundle configuration**](https://docs.databricks.com/aws/en/dev-tools/bundles/settings) — How to structure databricks.yml and configure bundle settings.
- [**Configuration reference**](https://docs.databricks.com/aws/en/dev-tools/bundles/reference) — Full reference for all bundle configuration options.
- [**Databricks Asset Bundles resources**](https://docs.databricks.com/aws/en/dev-tools/bundles/resources) — Defining jobs, pipelines, and other resources in bundle configs.

---

## 3. Workflow Deployment, Repair, and Rerun

### Topic Overview

Lakeflow Jobs (formerly called Databricks Workflows) are the central orchestration mechanism for scheduling and executing data pipelines on Databricks. When you have built your pipeline logic across multiple notebooks or scripts, you need a way to run them reliably on a schedule, handle failures gracefully, and monitor their execution. That's what jobs do.

A job is a collection of one or more tasks arranged in a directed acyclic graph (DAG). Each task can run on different clusters, use different compute resources, and depend on the success or failure of other tasks. This flexibility lets you build sophisticated multi step pipelines: ingest data, transform it, run quality checks, and load results to a warehouse all in one job with clear dependency management.

One of the most practical features is the ability to repair and rerun failed runs. If a job fails partway through, you don't have to restart from the beginning. You can fix the underlying issue (bad data, downstream API timeout, etc.) and rerun only the failed tasks and anything that depends on them. This is critical in production environments where you want to minimize wasted compute and keep pipelines responsive to issues.

---

### Key Concepts

- Lakeflow Jobs Overview
    
    Lakeflow Jobs are Databricks managed orchestration. You define a job via UI, API, or YAML (in Databricks Asset Bundles). The Databricks platform handles scheduling, retrying, monitoring, and cluster provisioning. Each job has a unique ID and can be triggered on a schedule (cron), manually, by file arrival, or continuously. Jobs are the standard way to operationalize data pipelines in production.
    
- Task Types and DAG
    
    A job consists of one or more tasks. Supported task types include: Notebook, Python, JAR, SQL, Lakeflow Pipeline, dbt, and Spark Submit. Tasks form a DAG where you define dependencies: "run task B only after task A succeeds". This allows parallel execution of independent tasks and strict sequencing of dependent ones.
    
- Scheduling Options
    
    Jobs can be triggered in multiple ways: cron schedules (e.g., "every day at 2 AM UTC"), manual trigger (user clicks Run Now), file arrival triggers (run when a file lands in a cloud location), and continuous triggers (run continuously, waiting for new runs). You can also trigger a job via REST API.
    
- Repair and Rerun
    
    When a job run fails, the Repair and Rerun feature lets you retry the failed tasks without re running the entire job from the start. A repair preserves the original run ID and executes only the tasks that failed plus any downstream tasks that depend on them. This is much more efficient than restarting the whole pipeline and is the standard production practice for handling transient failures.
    
- Task Values
    
    Task values allow one task to pass data to downstream tasks in the same job run. Use dbutils.jobs.taskValues.set(key, value) in one task to set a value, and dbutils.jobs.taskValues.get(key, default) in another task to retrieve it. This enables dynamic pipelines where one task's output determines the behavior of downstream tasks.
    
- Retries and Notifications
    
    Each task can be configured with automatic retry logic: max retries, timeout behavior, and backoff strategy. Job level notifications send alerts on job start, success, or failure via email, webhook, or PagerDuty. This keeps operators informed and can trigger downstream systems when pipelines complete.
    
- Job Clusters vs Existing Clusters
    
    A job cluster is ephemeral: provisioned when the job run starts and terminated when it finishes. This is cost efficient and isolates job runs from each other. An existing cluster is a long lived cluster you manage separately. Use existing clusters for development and testing, but job clusters for production pipelines.
    
- Concurrent Runs
    
    You can set a max concurrent runs limit on a job to prevent too many instances from running simultaneously. This is useful if your downstream systems can't handle parallel executions or if you want to control resource consumption.
    

---

### Code Examples

Job definition with multi task DAG (YAML format for Databricks Asset Bundles):

```yaml
resources:
  jobs:
    data_pipeline_job:
      name: "Multi Task Data Pipeline"
      schedule:
        quartz_cron_expression: "0 0 2 * * ?"  # 2 AM daily
        timezone_id: "UTC"
      max_concurrent_runs: 1
      tasks:
        - task_key: "extract_data"
          notebook_task:
            notebook_path: "/Workspace/extract"
            base_parameters:
              source: "s3://my-bucket/raw"
          job_cluster_key: "job_cluster"
        - task_key: "transform_data"
          notebook_task:
            notebook_path: "/Workspace/transform"
          depends_on:
            - task_key: "extract_data"
          job_cluster_key: "job_cluster"
        - task_key: "quality_check"
          sql_task:
            file_path: "/Workspace/quality_check.sql"
          depends_on:
            - task_key: "transform_data"
          job_cluster_key: "job_cluster"
      job_clusters:
        - job_cluster_key: "job_cluster"
          new_cluster:
            spark_version: "15.3.x-scala2.12"
            node_type_id: "i3.xlarge"
            num_workers: 2
```

Using task values to share data between tasks (Python):

```python
# Task 1: Extract and set a task value
import datetime
from dbutils.jobs import TaskValues

# Perform extraction logic
records_processed = 150000

# Set the task value for downstream tasks
dbutils.jobs.taskValues.set("records_count", records_processed)
dbutils.jobs.taskValues.set("extraction_date", str(datetime.date.today()))

print(f"Extracted {records_processed} records")
```

In a downstream task, retrieve the values:

```python
# Task 2: Retrieve and use task values
records_count = dbutils.jobs.taskValues.get("records_count", "0")
extraction_date = dbutils.jobs.taskValues.get("extraction_date", "unknown")

print(f"Processing {records_count} records from {extraction_date}")

# Use these values to control downstream logic
if int(records_count) > 100000:
    print("Large dataset detected, using optimized transform")
else:
    print("Small dataset, using standard transform")
```

Repairing a failed run using the Databricks CLI:

```bash
# List recent runs for a job
databricks jobs list-runs --job-id 123

# View details of a failed run
databricks runs get --run-id 456

# Repair and rerun the failed run (preserves run ID)
databricks runs repair-run --run-id 456 --jar-params "param1" "param2"

# Check the status of the repair run
databricks runs get --run-id 456
```

Scheduling a job with cron expression (JSON format for REST API):

```json
{
  "name": "Daily ETL Job",
  "tasks": [
    {
      "task_key": "main_task",
      "notebook_task": {
        "notebook_path": "/Users/user@company.com/etl_notebook"
      },
      "job_cluster_key": "auto_cluster"
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 30 3 ? * MON-FRI",
    "timezone_id": "America/New_York"
  },
  "max_concurrent_runs": 1,
  "job_clusters": [
    {
      "job_cluster_key": "auto_cluster",
      "new_cluster": {
        "spark_version": "15.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2
      }
    }
  ]
}
```

---

### Common Exam Scenarios

#### Scenario 1:  

A multi task job fails at the quality check stage. The upstream extract and transform tasks completed successfully. You want to rerun the pipeline with minimal compute waste.

The correct approach is to use the Repair and Rerun feature on the failed run. This will execute only the quality check task (and any tasks downstream from it) without re executing the extract and transform tasks that already succeeded. This preserves the run ID and minimizes wasted cluster time. Simply clicking "Run Now" on the job would restart the entire pipeline from scratch, which is inefficient.

#### Scenario 2: 

Your extract task outputs the number of records processed. You want the transform task to behave differently depending on whether the extract loaded more than 1 million rows.

You use task values: the extract task calls dbutils.jobs.taskValues.set("record_count", 1500000) to store the count. The transform task retrieves it with dbutils.jobs.taskValues.get("record_count") and adjusts its parallelism or algorithm accordingly. This enables dynamic pipeline logic without relying on external state or databases.

#### Scenario 3: 

You need to choose between using a job cluster versus an existing cluster for your production pipeline. Your company wants to minimize costs but also ensure job isolation.

For production pipelines, job clusters are the best practice. Each job run gets its own ephemeral cluster that is provisioned at start and terminated at end. This isolates job runs from each other (no resource contention between concurrent jobs), eliminates the need to manage cluster uptime, and often reduces cost compared to keeping an always on cluster. Existing clusters are useful for development and ad hoc work where you want immediate cluster availability.

---

### Key Takeaways

- Lakeflow Jobs orchestrate data pipelines as DAGs of tasks with explicit dependencies. Multiple task types (Notebook, Python, SQL, Lakeflow Pipeline, dbt, etc.) can be mixed in a single job.
- Repair and rerun is the production standard for handling job failures. It reruns only failed tasks and their downstream dependents, preserving the original run ID and saving compute.
- Task values enable dynamic pipelines where one task can pass data to downstream tasks using dbutils.jobs.taskValues methods without external coordination.
- Job clusters are ephemeral and provisioned per run, making them cost effective and isolating production pipelines. Use existing clusters for development.
- Jobs can be triggered via cron schedule, manual trigger, file arrival, continuous mode, or REST API. Notifications and retries keep operators informed and handle transient failures.

---

### Gotchas and Tips

<aside> ⚠️ Repair and Rerun Preserves Run ID: When you repair a failed run, the original run ID is preserved and new run attempts are appended to the same run's history. This is different from clicking "Run Now" which creates a brand new run. If you need to track pipeline execution, understand that repairs are part of the same logical run.

</aside>

<aside> ⚠️ Task Values Are Ephemeral: Task values exist only during a single job run and are not persisted to storage. They are ideal for passing small amounts of data between tasks in the same run, but do not use them to store permanent state. Each new job run has a clean slate.

</aside>

<aside> ⚠️ Concurrent Runs Limit Can Queue Jobs: If you set max_concurrent_runs to 1 and a job run takes longer than your schedule interval, the next scheduled run will queue and wait. This can lead to pipeline backlog. Monitor job duration and adjust the schedule or concurrency limit accordingly.

</aside>

---

### Links and Resources

- [**Lakeflow Jobs**](https://docs.databricks.com/aws/en/jobs/) — Main documentation for scheduling and orchestrating workflows.
- [**Configure and edit Lakeflow Jobs**](https://docs.databricks.com/aws/en/jobs/configure-job) — Setting up jobs with tasks, dependencies, and retry policies.
- [**Automating jobs with schedules and triggers**](https://docs.databricks.com/aws/en/jobs/triggers) — Time based and event based triggers for automated execution.

---

## 4. Serverless Compute

### Topic Overview

Serverless compute is Databricks managed infrastructure where you don't configure or manage clusters yourself. Instead, Databricks provisions and manages the compute on your behalf. This is a significant shift from traditional cluster based workflows where you manually create, configure, and tear down compute resources.

Serverless compute is available for several workloads: SQL Warehouses (the most common option for SQL queries and BI tools), Notebooks (for exploratory work and development), Jobs and Workflows (for scheduled ETL and automation), and Lakeflow Pipelines (for data pipeline orchestration).

The main advantages of serverless compute are instant startup (no waiting for cluster provisioning), automatic scaling handled by Databricks, no cluster management overhead, and pay per use billing with no idle costs. You simply define your workload and submit it. Databricks takes care of the rest.

---

### Key Concepts

- What is Serverless
    
    Serverless means Databricks provisions, configures, and scales compute resources automatically without you needing to manage the infrastructure. You focus on your code and data, Databricks handles cluster lifecycle. It's called serverless even though servers are involved behind the scenes because you never interact with server configuration directly.
    
- Serverless SQL Warehouses
    
    The most common serverless option on Databricks. Used for SQL queries, dashboards, BI tool connections, and analytics workloads. Serverless SQL Warehouses run Photon by default, which provides GPU acceleration for SQL operations. No cluster configuration needed. You simply execute SQL and the warehouse scales up or down automatically based on query load. Billing is based on compute usage.
    
- Serverless for Jobs and Notebooks
    
    You can run notebook tasks and Python tasks within jobs using serverless compute. Benefits include faster job startup (no cluster provisioning delay), automatic scaling based on task requirements, and simpler job configuration since you don't specify instance types or cluster sizes. This is ideal for production workflows where you want hands off execution and predictable startup times.
    
- Serverless vs Classic Compute
    
    Classic (self managed) compute gives you full control over instance types, cluster size, auto scaling policies, and runtime configuration. You manage cluster lifecycle, which adds operational overhead but provides fine grained control. Serverless abstracts these details. Serverless has faster startup times but may have higher per unit cost since you're paying for Databricks managed infrastructure. Classic gives you cost predictability if you have steady state workloads but requires hands on management.
    
- Cost Considerations
    
    Serverless billing is based on DBU consumption, measured while your workload runs. You don't pay for idle time since resources are released when not in use. This is advantageous for variable workloads with unpredictable demand. There are no costs for provisioning or cluster management. However, per DBU costs may be higher than classic compute. For sustained, steady state workloads, classic compute might be cheaper. Always compare your expected usage patterns.
    
- Unity Catalog Requirement
    
    Serverless compute requires Unity Catalog for data governance and access control. You cannot use the legacy Hive Metastore with serverless compute. All data accessed by serverless workloads must be registered in Unity Catalog. This is actually a benefit because Unity Catalog provides fine grained access control, audit logs, and data lineage tracking.
    
- Region Availability
    
    Serverless compute is not available in all regions. Check Databricks documentation for your region's availability. Common regions like US East, US West, and EU have serverless support, but some regional availability gaps exist. If serverless is not available in your required region, you must fall back to classic compute.
    

---

### Code Examples

#### Example 1: Querying via Serverless SQL Warehouse

```sql
-- Execute SQL against a serverless SQL warehouse
-- No cluster provisioning needed, Databricks handles scaling
SELECT 
  customer_id,
  COUNT(*) as order_count,
  SUM(total_amount) as total_spent
FROM main.ecommerce.orders
WHERE order_date >= CURRENT_DATE - INTERVAL 30 DAY
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 100;

-- Serverless SQL warehouse automatically:
-- - Provisions compute when query arrives
-- - Scales up if needed for large result sets
-- - Scales down when query completes
-- - Applies Photon acceleration by default
```

#### Example 2: Job Configuration Using Serverless Compute

```yaml
# Databricks Asset Bundle job configuration using serverless compute
resources:
  jobs:
    daily_etl_pipeline:
      name: Daily ETL Pipeline
      tasks:
        - task_key: ingest_data
          notebook_task:
            notebook_path: /pipelines/ingest_raw_data
          # No cluster configuration needed for serverless
          # Databricks automatically handles compute provisioning
          max_concurrent_runs: 1
          
        - task_key: transform_data
          depends_on:
            - task_key: ingest_data
          notebook_task:
            notebook_path: /pipelines/transform_bronze_to_silver
          # Serverless automatically scales for this task
          
      schedule:
        quartz_cron_expression: "0 0 * * *"
        timezone_id: America/New_York

# With serverless:
# - Job starts immediately (no cluster wait time)
# - Databricks provisions smallest compute needed
# - Scales if tasks require more resources
# - Releases resources when done
# - No idle compute costs
```

#### Example 3: Classic Cluster Configuration (For Comparison)

```yaml
# Classic cluster configuration (more configuration overhead)
resources:
  jobs:
    daily_etl_pipeline:
      name: Daily ETL Pipeline
      clusters:
        - cluster_key: main_cluster
          num_workers: 2
          spark_version: "14.3.x-scala2.12"
          node_type_id: "i3.xlarge"
          aws_attributes:
            availability: SPOT
          spark_conf:
            spark.databricks.optimizer.dynamicFilePruning: "true"
      tasks:
        - task_key: ingest_data
          notebook_task:
            notebook_path: /pipelines/ingest_raw_data
          cluster_key: main_cluster
        - task_key: transform_data
          depends_on:
            - task_key: ingest_data
          notebook_task:
            notebook_path: /pipelines/transform_bronze_to_silver
          cluster_key: main_cluster

# With classic cluster:
# - You specify instance types and worker count
# - Longer startup (cluster provision + initialization)
# - Fixed cost structure based on configured cluster
# - You manage scaling policies
# - Idle costs if cluster sits unused
# - More control, more complexity
```

---

### Common Exam Scenarios

#### Scenario 1: Choosing Compute Type for a Dashboard

An organization needs to publish an interactive dashboard that runs ad hoc SQL queries from business users throughout the day. Query patterns are unpredictable and the dashboard may sit unused for hours. Which compute should they use?

Answer: Serverless SQL Warehouse. The unpredictable usage pattern means you don't want to pay for idle time. Serverless automatically scales based on query demand and releases resources when not in use, eliminating idle costs. Classic compute would be wasteful here since the cluster would sit provisioned even when no queries run.

#### Scenario 2: Minimizing Job Startup Time

A data team has a critical job that must complete within a tight SLA. Currently using classic compute, job startup takes 5 minutes just for cluster provisioning. The actual job runs for 3 minutes. They need to minimize total runtime. What should they change?

Answer: Switch to serverless compute for the job tasks. Serverless has near instant startup (seconds instead of minutes) since Databricks provision compute on demand. This reduces total job time from 8 minutes to approximately 3 plus few seconds, meeting the SLA much more reliably.

#### Scenario 3: Governance Requirement Impact on Compute Choice

A company wants to use serverless compute for their new ETL pipelines but still uses Hive Metastore for data governance. Can they use serverless?

Answer: No. Serverless compute requires Unity Catalog for governance. They cannot use Hive Metastore with serverless. They must either migrate to Unity Catalog (which is the recommended path) or stay with classic compute if they're not ready to migrate yet.

---

### Key Takeaways

- Serverless compute is Databricks managed infrastructure with no cluster configuration needed. Available for SQL Warehouses, Jobs, Notebooks, and Lakeflow Pipelines.
- Instant startup and automatic scaling are major benefits. No idle costs since resources are released when not in use. Billing is based on DBU consumption only during active execution.
- Serverless SQL Warehouses run Photon by default, providing automatic SQL acceleration without any additional configuration.
- Unity Catalog is mandatory for serverless compute. Hive Metastore is not compatible, so you must migrate or use classic compute.
- Choose serverless for variable or unpredictable workloads, choose classic if you need fine grained control over instance types and configuration.

---

### Gotchas and Tips

<aside> ⚠️ Unity Catalog is not optional. If your workspace still uses Hive Metastore, you cannot use serverless compute at all. This is a hard requirement, not a nice to have. You must migrate to UC first.

</aside>

<aside> ⚠️ Not all regions support serverless. Before architecting a solution with serverless, verify your target region supports it. Exam questions may test this by asking what to do if serverless is unavailable in a specific region.

</aside>

<aside> ⚠️ Per DBU cost for serverless is higher than classic compute. For high volume, always on workloads, classic compute may be more cost effective. Don't assume serverless is always cheaper. Calculate based on your actual usage pattern.

</aside>

---

### Links and Resources

- [**Run jobs with serverless compute for workflows**](https://docs.databricks.com/aws/en/jobs/run-serverless-jobs) — Running jobs without managing infrastructure using serverless compute.
- [**Serverless compute for notebooks**](https://docs.databricks.com/aws/en/compute/serverless/notebooks) — Using serverless compute for interactive development.
- [**Connect to serverless compute**](https://docs.databricks.com/aws/en/admin/workspace-settings/serverless) — Admin settings for enabling serverless in your workspace.

---

## 5. Spark UI Optimization

### Topic Overview

The **Spark UI** is the primary diagnostic tool for understanding and optimizing Spark job execution. When a Spark job runs on your Databricks cluster, the UI shows real time metrics about job progress, stage breakdown, task execution, memory usage, and data movement. This information is essential for identifying performance bottlenecks and making targeted optimizations.

You can access the Spark UI from the cluster detail page (in the Compute section) or directly from a job run page in Databricks. The UI is organized into several tabs: Jobs, Stages, Tasks, Storage, Environment, Executors, and SQL/DataFrame. Each tab reveals different aspects of execution. Most exam scenarios involve reading the Spark UI to diagnose performance issues and recommend fixes.

Understanding the Spark UI is critical for optimization. A single slow query might appear fine in isolation, but the UI reveals whether the slowness comes from data skew, excessive shuffling, poor partitioning, or missing broadcast joins. For the exam, you need to recognize these patterns and know the techniques to fix them.

---

### Key Concepts

- Navigating the Spark UI
    
    The Jobs tab shows all Spark jobs submitted. Each job is a high level action like a collect() or write() call. Clicking into a job shows its stages. The Stages tab displays stage level details: shuffle read/write bytes, number of tasks, task durations, and data distribution across partitions. Uneven task durations in this tab often indicate data skew. The SQL/DataFrame tab shows the physical execution plan as a Directed Acyclic Graph (DAG). This is where you see whether Spark is using BroadcastHashJoin (efficient) or SortMergeJoin (requires shuffle), how many Exchange (shuffle) nodes are present, and partition counts.
    
- Identifying Data Skew
    
    Data skew occurs when some partitions contain much more data than others, causing some tasks to be significantly slower than the rest. In the Spark UI Stages tab, you see this as a few tasks taking much longer than others while most finish quickly. For example, if 200 tasks complete in 5 seconds but one task takes 45 seconds, that's a classic skew symptom. You can fix skew by salting the join key (adding random values to distribute data more evenly), repartitioning with a better key, or using broadcast joins to avoid the shuffle entirely. Adaptive Query Execution (AQE) has built in skew detection and can automatically adjust.
    
- Shuffle Operations
    
    A shuffle happens when Spark needs to move data across executors. This is expensive because it requires network I/O, disk I/O, and serialization. Common shuffle operations include joins, groupBy, distinct, and repartition. In the Spark UI SQL/DataFrame tab, shuffles appear as Exchange nodes. To minimize shuffle: use broadcast joins for small tables instead of sort merge joins, avoid unnecessary groupBy operations, coalesce partitions instead of repartitioning when possible, and use Adaptive Query Execution to let Spark optimize automatically. The Stages tab shows Shuffle Read and Shuffle Write metrics in bytes. High shuffle amounts mean expensive operations.
    
- Broadcast Joins
    
    A broadcast join is an optimization where a small table is copied to all executors in memory, eliminating the need for a shuffle. Instead of moving data across the network, each executor joins against its local copy of the small table. This is much faster for small table joins. Spark automatically broadcasts tables smaller than `spark.sql.autoBroadcastJoinThreshold` (default 10MB). You can explicitly hint Spark to broadcast a table using the `broadcast()` function. Be cautious with broadcast threshold: broadcasting a 100MB table sends 100MB to every executor, which can consume memory quickly. For the Associate exam, knowing when to use broadcast joins and how to enable them is important.
    
- Partition Tuning
    
    The number of partitions affects parallelism and shuffle size. Too few partitions means fewer tasks and lower parallelism. Too many partitions means more task overhead and smaller data chunks. `spark.sql.shuffle.partitions` controls the number of partitions after a shuffle (default 200). Use `coalesce()` to reduce partitions without reshuffling (data from multiple partitions moves to fewer executors). Use `repartition()` to increase partitions or redistribute by a column (both trigger a shuffle). For exam questions, remember coalesce is cheaper than repartition.
    
- Adaptive Query Execution (AQE)
    
    Adaptive Query Execution is enabled by default in Databricks. AQE automatically optimizes a query plan during execution based on runtime statistics. It does three main things: (1) dynamically adjusts shuffle partition count based on actual data size, (2) converts sort merge joins to broadcast joins if one side turns out to be small, and (3) detects and handles data skew in join keys by splitting large partitions. AQE reduces the need for manual tuning and catches optimization opportunities that the optimizer couldn't predict at plan time. For the exam, understand that AQE is active by default and you don't need to enable it.
    
- Caching Strategies
    
    Caching a DataFrame stores its data in memory (or disk) so subsequent actions don't recompute it. Use `df.cache()` (or `df.persist()` with a storage level) for DataFrames accessed multiple times. The Spark UI Storage tab shows cached DataFrames, their size, and how much memory is used. Cache large DataFrames that are reused often, but avoid caching one off transformations. Also remember that cache doesn't persist across job runs; it's per session.
    
- Photon Acceleration
    
    Photon is a high performance vectorized query execution engine available on Databricks. It accelerates certain SQL and DataFrame operations by using native code instead of Java. Photon is enabled on certain cluster types and handles filtering, aggregations, and joins more efficiently. You don't need to change code to use Photon; it kicks in automatically for supported operations. For the exam, just know that Photon accelerates query execution through vectorization.
    

---

### Code Examples

**Broadcast Join Hint (SQL and PySpark)**

```sql
-- SQL: use BROADCAST hint
SELECT *
FROM large_table l
JOIN /*+ BROADCAST(s) */ small_table s
  ON l.id = s.id
```

```python
# PySpark: use broadcast() function
from pyspark.sql.functions import broadcast

large_df = spark.read.table("large_table")
small_df = spark.read.table("small_table")

result = large_df.join(broadcast(small_df), "id")
```

**Repartitioning and Coalescing (PySpark)**

```python
# Increase partitions and redistribute by a column (triggers shuffle)
df_repartitioned = df.repartition(100, "user_id")

# Reduce partitions without shuffle (for final write)
df_coalesced = df.coalesce(4)

# You would use coalesce before writing to reduce output file count
df_coalesced.write.mode("overwrite").parquet("/output/path")
```

**Setting Shuffle Partitions (PySpark)**

```python
# Set default shuffle partitions for the session
spark.conf.set("spark.sql.shuffle.partitions", "400")

# Now all shuffle operations use 400 partitions
df_grouped = df.groupBy("category").count()

# Reset to default
spark.conf.set("spark.sql.shuffle.partitions", "200")
```

**Caching a DataFrame (PySpark)**

```python
from pyspark import StorageLevel

# Cache in memory
df.cache()

# Or explicitly specify storage level
df.persist(StorageLevel.MEMORY_ONLY)

# Cache with disk spillover (if memory is full, spill to disk)
df.persist(StorageLevel.MEMORY_AND_DISK)

# Trigger materialization and check Storage tab in Spark UI
df.count()

# Unpersist when done
df.unpersist()
```

---

### Common Exam Scenarios

**Scenario 1: High Task Duration Variance**

You check the Spark UI Stages tab for a join operation. You see 200 tasks, and most complete in 8 seconds, but one task takes 2 minutes. The Shuffle Read metric shows most tasks read 5MB but the slow task read 500MB. This is a classic data skew problem. The join key has skewed distribution—one key value appears in many more rows. To fix this, you could salt the join key (add a random suffix to split the skewed key across multiple tasks) or use Adaptive Query Execution to detect and handle the skew automatically. In this case, since AQE is enabled by default, it should already be trying to handle it, but explicit salting gives you more control.

**Scenario 2: Excessive Shuffle Operations**

Your Spark UI SQL tab shows a chain of Exchange (shuffle) nodes in the DAG. Your query joins a large table with a small lookup table. The Shuffle Write metric is 2GB. You could optimize by using a broadcast join on the small table to eliminate that shuffle entirely. Check the size of the small table; if it's under 10MB (or whatever your threshold is set to), you could explicitly use `broadcast(small_df)`. This avoids the shuffle and often reduces execution time by an order of magnitude.

**Scenario 3: Poor Partition Count Choice**

You have a 100GB DataFrame that you need to write to Parquet. The default `spark.sql.shuffle.partitions` is 200, so Spark creates 200 output files. Each file is ~500MB. You want fewer, larger files for downstream consumption. Use `coalesce(50)` to merge 200 partitions into 50 without reshuffling. This creates 50 output files (~2GB each) and is faster than repartition because it doesn't trigger a shuffle.

---

### Key Takeaways

- The Spark UI is your window into job execution. Use it to spot slow stages, data skew, excessive shuffling, and memory issues.
- Data skew (uneven task durations) is a common performance issue. Fix it with salting, better partitioning, or broadcast joins.
- Shuffles are expensive. Use broadcast joins for small tables, avoid unnecessary groupBy operations, and let Adaptive Query Execution optimize automatically.
- Use `coalesce()` to reduce partitions without shuffle, and `repartition()` to increase or redistribute partitions (both have trade offs).
- Cache frequently accessed DataFrames to avoid recomputation. Check the Storage tab in Spark UI to verify cache usage.

---

### Gotchas and Tips

<aside> ⚠️ Broadcast threshold is per executor. If you set `spark.sql.autoBroadcastJoinThreshold` to 100MB and broadcast a 100MB table to 10 executors, you use 1GB of memory total. Broadcasting massive tables can exhaust memory quickly.

</aside>

<aside> ⚠️ Coalesce does not trigger a shuffle but may cause uneven data distribution and slower writes. Repartition triggers a shuffle but redistributes data evenly. Use coalesce only when you don't care about data distribution (e.g., final write where file count is the main concern).

</aside>

<aside> ⚠️ Cache is session specific and not persistent across cluster restarts or job runs. If you cache a DataFrame and then submit a new job, that cache is gone. Use Delta tables or external storage for persistent caching.

</aside>

---

### Links and Resources

- [**Diagnose cost and performance issues using the Spark UI**](https://docs.databricks.com/aws/en/optimizations/spark-ui-guide/) — Complete guide to reading and interpreting the Spark UI for optimization.
- [**Debugging with the Spark UI**](https://docs.databricks.com/aws/en/compute/troubleshooting/debugging-spark-ui) — Step by step debugging using the Spark UI for skew, spill, and shuffle issues.