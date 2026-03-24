#databricks/hilarious 

<mark style="background: #ABF7F7A6;">
Exam Weight: 11% — This section focuses on applying Unity Catalog objects and features to manage, organize, and govern data, as well as implementing data quality constraints and tests using Lakeflow Declarative Pipelines.</mark>

## 1. Managed vs External Tables

### Topic Overview

In Unity Catalog, tables come in two types: **Managed tables** and **External tables**. Each serves different needs depending on your data governance and storage strategy.

Managed tables are the default and recommended approach. Unity Catalog manages both the metadata (the schema, table definition) and the underlying data files. Data is stored in the managed storage location that you configure for the catalog or schema. When you DROP a managed table, both the metadata and the actual data files are deleted from cloud storage. This means Databricks owns the complete lifecycle of the table.

External tables take a different approach. Unity Catalog manages only the metadata. The actual data files live at a user specified location in cloud storage (S3, Azure Storage, GCS, etc.). When you DROP an external table, only the metadata is removed from Unity Catalog. The data files stay behind in cloud storage. This is useful when data is shared with systems outside Databricks or when the data lifecycle is controlled by external processes.

The choice between managed and external tables often comes down to this: use managed tables when Databricks is the primary owner and operator. Use external tables when the data lives elsewhere or needs independence from Databricks lifecycle management.

---

### Key Concepts

- **Managed Tables**
    
    Unity Catalog controls the entire table lifecycle. Data files are stored in the managed location (default storage path for the catalog or schema). Metadata and data are in sync and deleted together. Eligible for automatic optimization by Databricks (file compaction, clustering, etc.). Easier to manage because you don't have to worry about storage paths or data cleanup.
    
- **External Tables**
    
    Unity Catalog manages only the metadata. Data files live at a specific cloud storage path that you specify. Dropping the table removes metadata but leaves data in place. Requires an External Location and Storage Credential to be configured in Unity Catalog for governance. Useful for data shared with external systems, federated analytics, or when data lifecycle is managed outside Databricks.
    
- **When to Use Each**
    
    Use Managed tables by default. They are simpler to operate, benefit from Databricks optimizations, and provide complete governance. Use External tables when: data is shared with non-Databricks systems, you need explicit control over storage location, data is managed by an external ETL pipeline, or you want to decouple the table lifecycle from storage.
    
- **Managed Storage Locations**
    
    Each catalog and schema can have a default storage location configured. When you create a managed table without specifying a LOCATION, it automatically stores data in the catalog or schema's managed location. Managed locations are cloud storage paths (like s3://my-bucket/uc/catalogs/) that Databricks uses to store data for managed tables. You configure these at the catalog and schema level for organizational purposes.
    
- **External Locations and Storage Credentials**
    
    External tables require two Unity Catalog objects: an External Location (a reference to a cloud storage path) and a Storage Credential (credentials to access that path). Together they provide governance and access control. You create these once and then reference them when creating external tables.
    
- **Volumes vs Tables**
    
    Don't confuse tables with Volumes. Volumes are for storing unstructured or semi structured data (images, PDFs, raw files). Tables are for structured data with schemas. Both managed and external tables store structured data. Volumes provide lower level file storage access but without table semantics.
    

---

### Code Examples

Creating a Managed Table (default behavior):

```sql
CREATE TABLE my_catalog.my_schema.sales (
    order_id INT,
    customer_id INT,
    amount DECIMAL(10, 2),
    order_date DATE
);
```

Creating an External Table with a specific location:

```sql
CREATE TABLE my_catalog.my_schema.raw_events
LOCATION 's3://my-data-bucket/events/'
AS SELECT * FROM parquet.`s3://my-data-bucket/events/`;
```

Inspecting table details to see if it's managed or external:

```sql
DESCRIBE DETAIL my_catalog.my_schema.sales;
-- Look for: table_type (MANAGED or EXTERNAL), location, etc.
```

Checking the properties of a table:

```sql
SHOW TBLPROPERTIES my_catalog.my_schema.sales;
-- Shows metadata including table type and storage details
```

Comparing DROP behavior:

```sql
-- Managed table: DROP removes metadata AND data files
DROP TABLE my_catalog.my_schema.sales;

-- External table: DROP removes metadata ONLY
DROP TABLE my_catalog.my_schema.raw_events;
-- Data files at s3://my-data-bucket/events/ still exist
```

---

### Common Exam Scenarios

**Scenario 1: Data Cleanup After Table Drop**

You have a production table storing customer orders in Unity Catalog. A colleague accidentally creates an external table pointing to a shared S3 bucket containing data from multiple systems. They drop the external table, but the data in the S3 bucket is still needed by another analytics platform. What happened? The external table metadata was deleted, but the underlying data files remained in S3. If this had been a managed table, both the metadata and files would be gone, breaking the other system. This demonstrates why external tables are preferable when data has external dependencies.

**Scenario 2: Choosing Table Type for a Data Lake**

You're building a medallion architecture (Bronze/Silver/Gold) in Unity Catalog. Bronze tables ingest raw data from APIs. Silver tables contain cleaned, deduplicated data. Gold tables serve business analytics. Which table type should you use? For all three layers, use managed tables. Databricks will handle storage, optimization, and lifecycle management. You only need external tables if data needs to live outside Databricks or be accessed by non-Databricks systems. Since you control the entire pipeline, managed is the right choice.

**Scenario 3: External Location Governance**

Your organization needs to grant team members permission to query data in an external S3 location, but you don't want them to access the raw S3 bucket directly. You create an External Location and Storage Credential in Unity Catalog, then create an external table pointing to that location. Team members get permission only on the external table, not the S3 bucket. This centralizes governance and ensures access is tracked through Unity Catalog audit logs, not raw cloud storage logs.

---

### Key Takeaways

- Managed tables are the default and recommended choice. Unity Catalog manages both metadata and data. Use them unless you have a specific reason to use external tables.
- External tables store metadata in Unity Catalog but data lives in cloud storage. Dropping an external table only removes metadata, not the underlying data files.
- Use `CREATE TABLE` for managed tables. Use `CREATE TABLE ... LOCATION 'path'` for external tables.
- External tables require External Locations and Storage Credentials configured in Unity Catalog for governance and access control.
- Use `DESCRIBE DETAIL table_name` to check whether a table is managed or external and see its storage location.

---

### Gotchas and Tips

<aside> ⚠️ Dropping an external table does NOT delete the underlying data. If you DROP an external table and then need to recreate it, the data is still there. You can point a new external table to the same location and recover the schema by re reading the data. With managed tables, data is gone forever after DROP.

</aside>

<aside> ⚠️ Don't confuse managed storage locations with External Locations. Managed storage locations are where Databricks stores managed table data automatically. External Locations are user defined references to cloud storage paths for external tables. You need both concepts to understand the full picture.

</aside>

<aside> ⚠️ External tables require explicit configuration of External Locations and Storage Credentials. If these are not set up, you cannot create external tables. Managed tables have zero external setup because Databricks provides the storage automatically. This is one reason managed tables are easier to use.

</aside>

---

### Links and Resources

- [**Unity Catalog managed tables**](https://docs.databricks.com/aws/en/tables/managed) — Benefits of managed tables including automatic optimization and governance.
- [**Work with external tables**](https://docs.databricks.com/aws/en/tables/external) — Creating and managing external tables with Unity Catalog governance.
- [**Convert an external table to a managed table**](https://docs.databricks.com/aws/en/tables/convert-external-managed) — How to migrate from external to managed using SET MANAGED.

---

## 2. Unity Catalog Permissions and Roles

### Topic Overview

**Unity Catalog (UC)** is the centralized governance layer in Databricks that provides fine grained access control for all data assets. It enforces a three level namespace (`catalog.schema.table`) and allows administrators to manage who can access what data using standard SQL GRANT and REVOKE statements.

Permissions in UC follow a hierarchy. Users need USE CATALOG on the catalog and USE SCHEMA on the schema before they can SELECT from a table. This layered approach means you can control access at different levels of granularity. The system also supports ownership, where object owners can manage permissions on the objects they own.

For the exam, know the permission model inside out: what each privilege does, how inheritance works, the difference between admin roles, and the best practice of using groups with least privilege.

---

### Key Concepts

- **Three level namespace**
    
    Unity Catalog organizes data as catalog.schema.table_or_object. A metastore sits above catalogs as the top level container. Within a schema, you can have tables, views, volumes, functions, and models. This hierarchy gives you clear organizational boundaries and maps naturally to environments (dev_catalog, prod_catalog) or business domains (finance_catalog, marketing_catalog).
    
- **Securable objects hierarchy**
    
    The hierarchy from top to bottom: Metastore → Catalog → Schema → Table / View / Volume / Function / Model. Each level is a securable object that can have permissions granted on it. Permissions flow downward through inheritance but access requires explicit privileges at each namespace level (USE CATALOG + USE SCHEMA + SELECT).
    
- **Privileges**
    
    Key privileges include: USE CATALOG (access a catalog), USE SCHEMA (access a schema), SELECT (read from tables/views), MODIFY (insert/update/delete), CREATE TABLE, CREATE SCHEMA, CREATE CATALOG, EXECUTE (run functions), READ VOLUME, WRITE VOLUME, and ALL PRIVILEGES. The USE privileges are namespace access gates. Without USE CATALOG on a catalog, you cannot access anything inside it, even if you have SELECT on a table within.
    
- **GRANT and REVOKE**
    
    Access is managed through SQL statements: GRANT privilege ON securable TO principal and REVOKE privilege ON securable FROM principal. Principals can be users (individual accounts), groups (recommended), or service principals (for automated processes). You can also use SHOW GRANTS ON securable to see current permissions and SHOW GRANTS TO principal to see what a user or group can access.
    
- **Permission inheritance**
    
    Granting a privilege on a parent applies it to all current and future children. For example, GRANT SELECT ON CATALOG my_catalog TO analysts gives the analysts group SELECT on every table in every schema within that catalog, including tables created later. However, users still need USE CATALOG and USE SCHEMA to navigate to the tables. Inheritance saves you from granting permissions table by table.
    
- **Ownership and admin roles**
    
    Every securable object has an owner. The creator of an object becomes its owner by default. Owners have full control over their objects, including granting permissions to others. Ownership can be transferred with ALTER securable OWNER TO principal. Admin roles include: Account admin (manages the Databricks account), Workspace admin (manages workspace settings), and Metastore admin (top level UC admin with full control over all data objects in the metastore).
    

---

### Code Examples

#### Granting permissions

```sql
-- Grant access to a catalog
GRANT USE CATALOG ON CATALOG prod_catalog TO data_engineers;

-- Grant access to a schema
GRANT USE SCHEMA ON SCHEMA prod_catalog.sales TO data_engineers;

-- Grant read access to all tables in a schema
GRANT SELECT ON SCHEMA prod_catalog.sales TO data_analysts;

-- Grant write access to a specific table
GRANT MODIFY ON TABLE prod_catalog.sales.orders TO etl_service_principal;

-- Grant ability to create tables
GRANT CREATE TABLE ON SCHEMA prod_catalog.sales TO data_engineers;
```

#### Viewing and revoking permissions

```sql
-- Show grants on a table
SHOW GRANTS ON TABLE prod_catalog.sales.orders;

-- Show all grants for a principal
SHOW GRANTS TO `data_engineers`;

-- Revoke access
REVOKE SELECT ON SCHEMA prod_catalog.sales FROM former_team;

-- Transfer ownership
ALTER SCHEMA prod_catalog.sales OWNER TO `platform_team`;
```

---

### Common Exam Scenarios

**Scenario 1: User cannot access a table despite having SELECT**

An analyst has been granted SELECT on a specific table but gets an access denied error when querying it. The most likely cause is missing USE CATALOG or USE SCHEMA privileges. In Unity Catalog, you need all three: USE CATALOG on the catalog, USE SCHEMA on the schema, and SELECT on the table. Granting SELECT alone is not enough.

**Scenario 2: Granting access to all current and future tables**

A team lead wants analysts to be able to read all tables in a schema, including any new tables added later. The correct approach is to GRANT SELECT ON SCHEMA, which applies to all current and future tables within that schema via inheritance. Granting SELECT on individual tables would not cover future tables.

**Scenario 3: Least privilege for a service principal**

An ETL pipeline runs as a service principal and needs to read from bronze tables and write to silver tables. The minimum privileges are: USE CATALOG, USE SCHEMA on both schemas, SELECT on the bronze schema, and MODIFY plus CREATE TABLE on the silver schema. Granting ALL PRIVILEGES would work but violates the principle of least privilege.

---

### Key Takeaways

- Unity Catalog uses a three level namespace (catalog.schema.table) with permissions at each level.
- Users need USE CATALOG + USE SCHEMA + SELECT (or MODIFY) to access tables. Missing any one of these blocks access.
- Permissions inherit downward. Granting SELECT on a schema applies to all current and future tables in it.
- Use groups for access management, not individual users. Follow the principle of least privilege.
- Object owners have full control and can grant permissions to others. Ownership is transferable with ALTER ... OWNER TO.

---

### Gotchas and Tips

<aside> ⚠️ **USE CATALOG and USE SCHEMA are not optional.** This is the most common exam trap for UC permissions. Even with SELECT granted on a table, the user will get access denied without USE CATALOG and USE SCHEMA. Always check all three levels.

</aside>

<aside> ⚠️ **ALL PRIVILEGES is rarely the right answer.** On the exam, if an option uses ALL PRIVILEGES, it is usually a distractor unless the question specifically asks for full administrative access. Prefer specific, minimal grants.

</aside>

<aside> ⚠️ **Metastore admin vs Catalog owner.** The metastore admin has control over everything in the metastore. A catalog owner only has control within their catalog. Know the scope of each role. Metastore admins can also transfer ownership of any object.

</aside>

---

### Links and Resources

- [**Unity Catalog Access Control**](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control) — Managing privileges on securable objects in Unity Catalog.
- [**Unity Catalog Overview**](https://docs.databricks.com/aws/en/data-governance/unity-catalog/) — Comprehensive guide to Unity Catalog governance model, roles, and architecture.

---

## 3. Audit Logs

### Topic Overview

Databricks **audit logs** track all user activity and data access events within your workspace. Every action a user takes, from logging in to reading or writing data, gets recorded. These logs are stored in system tables and provide a complete audit trail for compliance, security monitoring, and troubleshooting.

The primary system table for audit data is `system.access.audit` which contains detailed information about who accessed what, when they accessed it, and from where. This becomes critical when you need to demonstrate compliance with data governance policies, investigate unauthorized access attempts, or understand data lineage and usage patterns.

On the exam, you'll encounter questions about querying audit logs, understanding what events are tracked, configuring audit log delivery, and using audit data for compliance monitoring. Knowing how to extract meaningful insights from audit logs using SQL is a key skill for data engineers working with Unity Catalog and governed environments.

---

### Key Concepts

- What Audit Logs Capture
    
    Audit logs capture virtually every action in your Databricks workspace. This includes user authentication events (logins, logouts), cluster operations (creation, deletion, resizing), workspace object access (reading or modifying notebooks, dashboards), table and view access, permission grants and revokes, and Unity Catalog operations. Each event records the timestamp, the identity of the user or service principal who performed the action, the action name, request parameters, response status, and metadata about the request source (IP address, user agent).
    
- system.access.audit Table Structure
    
    The `system.access.audit` table is a system managed table available in every Databricks workspace. Key columns include: `event_time` (timestamp of the event), `event_id` (unique identifier), `workspace_id` (workspace identifier), `identity` (user principal or service principal), `action_name` (the action performed), `request_params` (JSON containing request details), and `response` (HTTP status code and error messages if applicable).
    
- Common Audit Events
    
    Events commonly tracked and tested on the exam include: `login` (user authentication), `logout`, `createCluster`, `deleteCluster`, `readTable`, `writeTable`, `grantPermission`, `revokePermission`, and `modifyPermission`. Unity Catalog specific events track `createTable`, `deleteTable`, `updateTableTag`, and more.
    
- Querying Audit Data
    
    You query audit logs like any other table using SQL or PySpark. Since `system.access.audit` is a system table, you must have appropriate permissions to query it. The `request_params` column often contains nested JSON, so you'll use JSON functions like `get_json_object` or `from_json` to extract nested fields. Filtering by `event_time` is crucial for performance, especially on large audit logs that span weeks or months.
    
- Retention and Delivery
    
    Audit logs are retained for 90 days by default in the system table. For longer term retention and compliance, Databricks allows you to configure audit log delivery to cloud storage (S3, Azure Blob Storage, GCS) where they are archived in Parquet format. This is done through workspace settings. Once delivered to cloud storage, you can integrate with SIEM tools (Splunk, Datadog, Sentinel) for centralized monitoring and alerting. Some organizations use this capability to meet regulatory requirements like GDPR, HIPAA, and SOC 2.
    

---

### Code Examples

Query audit logs for table access events:

```sql
SELECT
  event_time,
  identity,
  action_name,
  request_params,
  response
FROM system.access.audit
WHERE action_name IN ('readTable', 'writeTable')
  AND event_time >= CURRENT_DATE() - INTERVAL 7 DAYS
ORDER BY event_time DESC;
```

Find who accessed a specific table:

```sql
SELECT
  DISTINCT identity,
  action_name,
  COUNT(*) as access_count,
  MIN(event_time) as first_access,
  MAX(event_time) as last_access
FROM system.access.audit
WHERE request_params LIKE '%my_table%'
  AND event_time >= CURRENT_DATE() - INTERVAL 30 DAYS
GROUP BY identity, action_name
ORDER BY access_count DESC;
```

Track permission changes (grants and revokes):

```sql
SELECT
  event_time,
  identity,
  action_name,
  get_json_object(request_params, '$.principal_name') as principal_name,
  get_json_object(request_params, '$.permission') as permission,
  response
FROM system.access.audit
WHERE action_name IN ('grantPermission', 'revokePermission')
  AND event_time >= CURRENT_DATE() - INTERVAL 14 DAYS
ORDER BY event_time DESC;
```

Monitor failed login attempts:

```sql
SELECT
  event_time,
  identity,
  get_json_object(request_params, '$.remote_address') as ip_address,
  COUNT(*) as failed_attempts
FROM system.access.audit
WHERE action_name = 'login'
  AND response LIKE '%401%'
  AND event_time >= CURRENT_DATE() - INTERVAL 1 DAYS
GROUP BY event_time, identity, ip_address
HAVING COUNT(*) > 3
ORDER BY failed_attempts DESC;
```

---

### Common Exam Scenarios

**Scenario 1: Compliance Audit** Your organization needs to prove that only authorized users accessed sensitive customer data in the past 30 days. You need to query `system.access.audit` for all table access events, filter by `action_name IN ('readTable', 'writeTable')` and a specific table name in the `request_params` column, and group by user to show access patterns. The exam tests your ability to filter correctly by date range (CURRENT_DATE() - INTERVAL) and understand what fields contain the information you need.

**Scenario 2: Security Investigation** You suspect unauthorized access attempts. You need to find failed login attempts by querying audit logs where `action_name = 'login'` and the `response` field contains an error code (e.g., 401, 403). The test asks you to identify which column shows failed status and how to extract the IP address from `request_params` using JSON functions like `get_json_object`.

**Scenario 3: Permission Change Tracking** Your organization needs to audit who granted permissions and to whom. You query audit logs for `action_name IN ('grantPermission', 'revokePermission')` and extract principal names and permission types from the nested JSON in `request_params`. The exam tests whether you know that permission events are tracked and how to extract nested data from request parameters.

---

### Key Takeaways

- Audit logs are stored in the `system.access.audit` system table and track every action in your workspace, including logins, cluster operations, and data access events.
- Key columns include `event_time`, `identity`, `action_name`, `request_params` (JSON), and `response` (status codes). Use `get_json_object` to extract nested fields from request_params.
- Audit logs are retained for 90 days in the system table by default. For longer term retention, configure audit log delivery to cloud storage in workspace settings.
- Common examined actions include `login`, `readTable`, `writeTable`, `grantPermission`, and `revokePermission`. Always filter queries by event_time for performance on large datasets.
- Audit logs can be delivered to SIEM tools (Splunk, Datadog, Sentinel) for centralized monitoring and are critical for demonstrating compliance with regulations like GDPR and HIPAA.

---

### Gotchas and Tips

<aside> 💡 Only 90 day retention by default. If an audit log event happened more than 90 days ago, it will not be in `system.access.audit`. Always configure audit log delivery to cloud storage immediately if you need longer term compliance records. This is a common test point.

</aside>

<aside> 💡 request_params contains nested JSON. Use `get_json_object` or parse the JSON properly. Simply using LIKE patterns (e.g., LIKE '%table_name%') works for quick searches but is not reliable for structured queries. Know how to extract nested fields for the exam.

</aside>

<aside> 💡 Always filter by `event_time` in your queries. Scanning months of audit logs without a date filter will be slow. The exam may test your understanding of query performance on large system tables.

</aside>

---

### Links and Resources

- [**Audit Log System Tables**](https://docs.databricks.com/aws/en/admin/system-tables/audit-logs) — Reference for audit log system table schema and querying audit events.
- [**System Tables Overview**](https://docs.databricks.com/aws/en/admin/system-tables/) — Overview of all available system tables for monitoring and observability.

---

## 4. Lineage in Unity Catalog

### Topic Overview

Unity Catalog automatically captures data lineage whenever queries run through the system. This means you get a complete record of how data flows between tables, notebooks, and jobs without writing any code to enable it. Lineage operates at two levels: table level tracking shows which tables feed into which other tables, while column level lineage zooms in to show how individual columns are transformed and move between tables. Think of it as a map of your entire data pipeline.

The lineage graph displays both upstream dependencies (where the data originates) and downstream consumers (what depends on this data). This bidirectional view is crucial for impact analysis and root cause troubleshooting. When you need to investigate where bad data came from or predict what will break if you change a table, lineage gives you those answers instantly.

Lineage data is stored in Unity Catalog system tables and accessible via REST APIs, making it programmatic and auditable. The system captures lineage from notebooks, jobs, Lakeflow pipelines, and SQL queries automatically. This is especially valuable for compliance scenarios where you need to prove data provenance and track regulatory requirements.

---

### Key Concepts

- What is data lineage?
    
    Data lineage is the complete record of how data moves and transforms through your pipelines. Unity Catalog captures this automatically whenever data is read from or written to a managed table. The system tracks the source tables, target tables, transformations applied, and the code that performed those transformations. This creates a queryable audit trail of your data's journey through the organization.
    
- Table level vs column level lineage
    
    Table level lineage shows relationships between entire tables: which tables as a whole are inputs and which are outputs. Column level lineage goes deeper and tracks individual columns. For example, if you have a source table with customer_id, email, and name, and you create a transformed table that renames customer_id to cust_id and masks the email, column level lineage tracks those specific column transformations. Column lineage is more granular and useful for compliance tracking and understanding field-level dependencies.
    
- Upstream and downstream
    
    Upstream means the source or origin of data. If you select the gold_customers table and view its upstream lineage, you see all the tables that feed into it. Downstream means the consumers or destinations of data. If you view gold_customers downstream lineage, you see all the dashboards, reports, and tables that depend on it. The Catalog Explorer UI displays both directions, allowing you to answer "where does this data come from?" and "what will break if I change this table?"
    
- Impact analysis
    
    Impact analysis uses lineage to predict what will be affected by a change. Before modifying or deleting a table, you can view its downstream lineage to see which jobs, dashboards, or downstream tables depend on it. This prevents breaking changes and allows you to coordinate updates across multiple teams. For example, if you want to rename a column, impact analysis shows you every table and job that references that column.
    
- How lineage is captured
    
    Lineage is captured automatically whenever a query executes that reads from or writes to a Unity Catalog managed table. No configuration is needed. The system extracts lineage from the SQL execution plan, notebook cells, job definitions, and Lakeflow pipeline DAGs. This includes both explicit reads (SELECT FROM) and implicit reads (joins, unions). Lineage is captured whether the query succeeds or fails, giving you complete traceability.
    
- Lineage in Catalog Explorer
    
    Open any table in Catalog Explorer and click the Lineage tab to see a visual graph of upstream and downstream dependencies. The graph is interactive: you can click nodes to drill into related tables, collapse/expand branches, and toggle between table and column level views. The UI shows creation timestamps for lineage records and allows filtering by time range. This visual representation makes it easy to understand complex data relationships at a glance.
    

---

### Code Examples

Lineage is captured automatically without code, but you can query lineage data programmatically using system tables.

#### Viewing lineage via system tables

```sql
-- Query the system.access.table_lineage view to see upstream dependencies
SELECT 
  downstream_table_catalog,
  downstream_table_schema,
  downstream_table_name,
  upstream_table_catalog,
  upstream_table_schema,
  upstream_table_name,
  created_timestamp
FROM system.access.table_lineage
WHERE downstream_table_name = 'gold_customers'
ORDER BY created_timestamp DESC;
```

#### Example: Creating lineage through a simple pipeline

```sql
-- Bronze table (raw data)
CREATE OR REPLACE TABLE my_catalog.bronze.customers AS
SELECT * FROM external_system.raw_customers;

-- Silver table (cleaned data)
CREATE OR REPLACE TABLE my_catalog.silver.customers_cleaned AS
SELECT 
  customer_id,
  LOWER(TRIM(email)) as email,
  UPPER(TRIM(name)) as name
FROM my_catalog.bronze.customers
WHERE email IS NOT NULL;

-- Gold table (business ready)
CREATE OR REPLACE TABLE my_catalog.gold.customers_analytics AS
SELECT 
  customer_id,
  email,
  name,
  CURRENT_TIMESTAMP as loaded_at
FROM my_catalog.silver.customers_cleaned;

-- Lineage now shows: 
-- external_system.raw_customers -> bronze.customers -> silver.customers_cleaned -> gold.customers_analytics
```

---

### Common Exam Scenarios

#### Scenario 1: Root cause analysis after data quality issue

Your finance team reports incorrect customer revenue totals in a downstream analytics table. You need to trace back to find where the bad data originated. Using Unity Catalog lineage, you view the upstream dependencies of the analytics table and follow the chain backwards through silver and bronze layers. Column level lineage helps you identify that the customer_id column was incorrectly joined in the silver transformation. Without lineage, this investigation would take hours. With it, you pinpoint the issue in minutes. The exam tests your understanding that lineage is automatic and bidirectional, letting you navigate both upstream (to find sources) and downstream (to find impact).

#### Scenario 2: Impact analysis before schema change

You want to rename a column in a silver table from old_customer_id to new_customer_id. Before making the change, you check the downstream lineage to see which tables depend on this column. You discover that three gold tables and two Lakeflow pipelines reference this column. Instead of renaming it blindly and breaking everything, you now know you need to coordinate the update across those five downstream assets. The exam expects you to recognize that lineage is the tool for this impact assessment and that it works across notebooks, jobs, and pipelines. Lineage prevents breaking changes by making dependencies visible.


#### Scenario 3: Compliance and data provenance

A compliance officer asks you to prove the data lineage for customer PII stored in the gold_customers_pii table as part of a regulatory audit. Using Catalog Explorer, you open the table and generate a lineage report showing the complete chain from raw source data through transformations to the final table. Column level lineage shows which specific columns contain PII and how they were masked or encrypted. You export this lineage graph as evidence of data governance. The exam tests that you know lineage is: automatically captured, visible in the UI, queryable via APIs, and suitable for compliance reporting.

---

### Key Takeaways

- Lineage is automatic. Unity Catalog captures it whenever queries run against managed tables. No configuration needed.
- Lineage works at two levels: table level (high level dependencies) and column level (individual field transformations).
- Use lineage for impact analysis (downstream) and root cause analysis (upstream) when troubleshooting.
- Lineage is visible in Catalog Explorer UI and queryable via system.access.table_lineage system table for programmatic access.
- Lineage is essential for compliance and data governance because it proves data provenance and creates an audit trail.

---

### Gotchas and Tips

<aside> ⚠️ Lineage only works with managed tables. External tables and non UC locations are not included in lineage graphs. If your source data sits in external tables or cloud storage without UC registration, lineage will start from the first managed table in your pipeline.

</aside>

<aside> ⚠️ Lineage has retention limits. Unity Catalog keeps lineage data for a limited time (typically 90 days for recent data). If you need to analyze lineage from months ago, plan accordingly. Use system tables to export and archive lineage records if needed for compliance.

</aside>

<aside> ⚠️ Column level lineage may not capture all transformations, especially complex ones involving UDFs, case expressions, or nested operations. Use it for simple column mappings and joins, but for intricate logic, supplement it with code comments and documentation.

</aside>

---

### Links and Resources

- [**Data Lineage in Unity Catalog**](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-lineage) — Capturing and viewing column-level and table-level lineage across workloads.
- [**Lineage System Tables**](https://docs.databricks.com/aws/en/admin/system-tables/lineage) — Querying lineage data programmatically via system tables.

---

## 5. Delta Sharing

### Topic Overview

Delta Sharing is an open protocol that lets you securely share live data between organizations without ever copying it. Instead of ETL pipelines that duplicate data and cost money, the provider keeps the data in their own storage and the recipient queries it directly in real time. There are two flavors: Databricks to Databricks (D2D) sharing, which works natively through Unity Catalog, and Databricks to Open (D2O) sharing, which uses the open Delta Sharing protocol so recipients don't need Databricks. You share data via a Share object, which is basically a named collection of tables or views. You define who can receive it with a Recipient object, and the organization sharing the data is the Provider.

The key benefit is that data stays in the provider's storage and recipients always get live, up to date data. For D2D sharing, Unity Catalog handles governance directly. For D2O sharing, the recipient uses a bearer token to authenticate and can access data with Spark, pandas, Power BI, Tableau, or other tools that understand the Delta Sharing protocol. Recipients always get read only access—they can query the data but cannot modify it.

---

### Key Concepts

- What is Delta Sharing
    
    An open protocol developed by Databricks that allows secure data sharing between organizations without moving or copying data. The recipient accesses live data directly from the provider's storage and pays only for compute to query it. The provider retains full control and can revoke access instantly.
    
- D2D vs D2O Sharing
    
    D2D (Databricks to Databricks): Both provider and recipient use Databricks. Sharing is managed through Unity Catalog with native integration. Governance controls, permissions, and audit logs are handled automatically. D2O (Databricks to Open): The recipient does not need Databricks. They authenticate with a bearer token and access data using the open Delta Sharing protocol via Spark connectors, pandas, Power BI, Tableau, or other tools. D2O is useful for partners, customers, or teams using different analytics platforms.
    
- Shares, Providers, and Recipients
    
    A Share is a named container of tables, views, and schemas you want to share. You create it on the provider side and grant SELECT permissions on specific objects. A Recipient is an identity you create to represent who gets the share. For D2D, a recipient is a Databricks workspace ID or account. For D2O, a recipient is an external user with an email and generated bearer token. The Provider is your organization or workspace that owns the data and creates the share.
    
- Advantages of Delta Sharing
    
    - No ETL needed. No extract, transform, load pipeline required. Recipients access data directly.
    - No data duplication. Data stays in the provider's storage. No copying means no extra storage costs for the provider.
    - Real time access. Recipients always get the latest data. No stale snapshots.
    - Cross platform compatibility. D2O works with Spark, pandas, Power BI, Tableau, and any tool that supports Delta Sharing.
    - Instant revocation. Provider can disable access immediately without managing separate copies.
- Limitations and Cost Model
    
    Limitations: Recipients cannot modify shared data. Shares are read only. You cannot grant UPDATE, DELETE, or INSERT permissions. Shared data cannot be used to create new shares downstream (no multi level sharing). Cost model: The provider pays for the storage that holds the shared data. The recipient pays for the compute they use to query it. So if you are the provider sharing a 100 GB table, you pay storage costs. The recipient's Databricks cluster or compute service incurs charges when they run queries against it. For D2O recipients, they pay their own tool's compute costs, not Databricks.
    

---

### Code Examples

Provider side: creating and configuring shares

```sql
-- Create a share
CREATE SHARE customer_data;

-- Add tables to the share
ALTER SHARE customer_data ADD TABLE catalog.schema.customers;
ALTER SHARE customer_data ADD TABLE catalog.schema.orders;

-- You can also add views
ALTER SHARE customer_data ADD VIEW catalog.schema.customer_summary;
```

Provider side: creating recipients and granting shares

```sql
-- Create a D2D recipient (Databricks workspace)
CREATE RECIPIENT partner_workspace USING ID '1234567890-abcdef';

-- Create a D2O recipient (external user or organization)
CREATE RECIPIENT external_partner USING BEARER_TOKEN;
-- This generates a token automatically that you share with the recipient

-- Grant the share to a recipient
GRANT SELECT ON SHARE customer_data TO RECIPIENT partner_workspace;
GRANT SELECT ON SHARE customer_data TO RECIPIENT external_partner;

-- View recipients and shares
SHOW RECIPIENTS;
SHOW SHARES;
```

Recipient side: accessing shared data (D2D with Databricks)

```sql
-- View available shares
SHOW SHARES;

-- Mount a shared table into your workspace
CREATE TABLE my_catalog.my_schema.customers
  USING DELTADB
  LOCATION 'share/provider_workspace/customer_data/customers';

-- Query the shared data
SELECT * FROM my_catalog.my_schema.customers LIMIT 10;
```

Recipient side: accessing shared data (D2O with Spark connector)

```python
# D2O recipient using Spark
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("DeltaSharingReader").getOrCreate()

# Read shared data using Delta Sharing URL
share_url = "<https://sharing.databricks.com/api/2.0/shares/customer_data/objects>"
token = "<bearer_token_from_provider>"

df = spark.read.format("deltaSharing") \\
    .option("bearerToken", token) \\
    .option("shareUrl", share_url) \\
    .load("customers")

df.show()
```

---

### Common Exam Scenarios

#### Scenario 1: Choosing Between D2D and D2O

Your organization has a data lake on Databricks and needs to share customer analytics data with an external partner who uses Tableau. Which sharing model should you use? D2O. The partner does not have Databricks, but they can authenticate with a bearer token and use the Delta Sharing protocol with Tableau. D2D would not work here because the recipient is not on Databricks. This scenario tests understanding of when each sharing model applies.

#### Scenario 2: Cost and Storage Responsibility

Your company shares a 500 GB fact table with five partner organizations via Delta Sharing. Who pays for the storage? Your company (the provider). One of the partners runs a query that scans the entire table. Who pays for that compute? The partner. This tests understanding of the cost model. The provider always pays for storage. Recipients pay for compute.

#### Scenario 3: Read Only Constraints in Production

You receive a request from a partner to update a few rows in a shared table for data correction. Is this possible with Delta Sharing? No. Shares are read only. If the partner needs to modify data, you would have to use an alternative approach like a custom API or ETL pipeline that allows write access. This tests understanding that Delta Sharing provides read only access and that recipient data quality requirements must be met by the provider, not the recipient.

---

### Key Takeaways

- Delta Sharing is an open protocol for sharing live data without copying. Providers retain ownership and recipients always access current data.
- D2D (Databricks to Databricks) uses Unity Catalog natively. D2O (Databricks to Open) supports non Databricks recipients via bearer tokens and is cross platform.
- Provider pays for storage. Recipients pay for compute. This makes sharing cost efficient for the provider.
- Shares are read only. Recipients cannot modify shared data. Access can be revoked instantly.
- Use CREATE SHARE to define shares, ALTER SHARE to add objects, CREATE RECIPIENT to define recipients, and GRANT SELECT ON SHARE to enable sharing.

---

### Gotchas and Tips

<aside> ⚠️ Shares are always read only. You cannot grant write permissions to recipients. This is fundamental to Delta Sharing and applies to D2D and D2O alike. If a recipient needs to modify data, use a different sharing mechanism.

</aside>

<aside> ⚠️ Bearer tokens for D2O are generated once when you create a recipient. If you lose the token, you cannot retrieve it. Store tokens securely and rotate them periodically for security.

</aside>

<aside> ⚠️ D2O recipients can access data with non Databricks tools, but those tools must support the Delta Sharing protocol. Always verify tool compatibility before sharing.

</aside>

---

### Links and Resources

- [**Delta Sharing Overview**](https://docs.databricks.com/aws/en/delta-sharing/) — Introduction to the open protocol for secure data sharing.
- [**Share Data with Databricks Recipients**](https://docs.databricks.com/aws/en/delta-sharing/share-data-databricks) — Databricks-to-Databricks sharing setup and management.
- [**Share Data with Open Recipients**](https://docs.databricks.com/aws/en/delta-sharing/share-data-open) — Sharing data with non-Databricks consumers using the open protocol.

---

## 6. Lakehouse Federation

### Topic Overview

Lakehouse Federation is a feature that lets you query external databases directly from Databricks without copying the data over. Think of it as creating a bridge to databases like MySQL, PostgreSQL, SQL Server, Snowflake, BigQuery, or Redshift. You register these external systems using **Connections** and **Foreign Catalogs** in Unity Catalog, then query them using familiar SQL and the same `catalog.schema.table` syntax you use for local tables.

The power here is **query pushdown**. When you run a query against a federated table, Databricks sends the filtering and computation down to the source database instead of pulling raw data and processing it locally. This keeps your data where it lives while giving you a unified query experience across all your data sources.

Lakehouse Federation is read only. You can't write back to federated tables directly. It's best for scenarios where you need to join your Databricks lakehouse with live operational data, gradually migrate off legacy systems, or access reference tables stored elsewhere.

---

### Key Concepts

- What is Lakehouse Federation?
    
    Lakehouse Federation enables you to query data stored in external databases from within Databricks without moving or replicating that data. It's achieved through Foreign Catalogs registered with Unity Catalog. Your queries execute against the remote database, returning results through Databricks. This is particularly useful for accessing live operational data or reference tables while maintaining a single query interface.
    
- Connections
    
    A Connection stores the credentials and metadata needed to connect to an external database. It includes the host, port, database name, username, and password (encrypted in Databricks). Connections are the foundational object. You create them first, then reference them when creating Foreign Catalogs. Multiple Foreign Catalogs can use the same Connection if they point to different databases on the same server.
    
- Foreign Catalogs
    
    A Foreign Catalog is a Unity Catalog that maps to an external database via a Connection. It acts as the entry point for querying remote data. Under a Foreign Catalog, you see schemas and tables that mirror the structure of the external database. You control access to foreign catalogs using UC permissions (USAGE, SELECT, etc.). From the user's perspective, they query a foreign catalog the same way they query a local UC catalog.
    
- Query Pushdown
    
    Query pushdown means that filtering, aggregations, and joins are sent to the remote database to execute, rather than fetching all the raw data to Databricks. This dramatically reduces network traffic and improves performance. Not all SQL operations can be pushed down (complex functions, certain joins), so Databricks intelligently decides what to push and what to compute locally. The remote database does the heavy lifting.
    
- Benefits of Lakehouse Federation
    
    - No data movement: keep data where it lives, query it from Databricks
    - Unified governance through Unity Catalog controls
    - Single query engine across multiple data sources
    - Access live data without replication or ETL pipelines
    - Efficient joins between lakehouse and operational data
- Limitations of Lakehouse Federation
    
    - Read only: no INSERT, UPDATE, DELETE operations to federated tables
    - Performance depends on the remote database and network latency
    - Not all SQL features are supported (some functions, data types)
    - Remote system must be accessible and available

---

### Code Examples

Creating a Connection to a PostgreSQL database:

```sql
CREATE CONNECTION postgres_prod
PROVIDER = postgresql
OPTIONS (
  host = 'prod-db.example.com',
  port = 5432,
  user = 'databricks_user',
  password = 'secure_password'
);
```

Creating a Foreign Catalog from that Connection:

```sql
CREATE FOREIGN CATALOG postgres_external
USING CONNECTION postgres_prod
DATABASE production;
```

Querying a federated table (same syntax as local tables):

```sql
SELECT customer_id, order_count
FROM postgres_external.public.customers
WHERE country = 'USA'
LIMIT 1000;
```

Joining lakehouse data with federated tables:

```sql
SELECT 
  l.transaction_id,
  l.amount,
  f.customer_name,
  f.country
FROM main.analytics.transactions l
INNER JOIN postgres_external.public.customers f
  ON l.customer_id = f.customer_id
WHERE l.transaction_date >= '2025-01-01';
```

---

### Common Exam Scenarios

#### Scenario 1:

You work for a fintech company with customer accounts in PostgreSQL and transaction data in Databricks. You need to join these datasets to analyze spending patterns without moving production data. You create a Connection to your PostgreSQL cluster, then a Foreign Catalog mapped to the accounts database. Queries against the foreign catalog tables use predicate pushdown to filter accounts server side, returning only matching rows to Databricks for the join. This minimizes data transfer and doesn't disrupt your operational database performance.

#### Scenario 2:

Your company is migrating from Snowflake to Databricks but has legacy reference tables still on Snowflake (SKUs, product hierarchies, pricing). Instead of copying all this data, you use Lakehouse Federation to query the Snowflake reference tables directly. Analytics teams can join your Databricks lakehouse fact tables with federated reference tables. Once migration is complete, you simply drop the foreign catalogs. This approach lets you migrate gradually without waiting for all reference data to move.

#### Scenario 3: 

An exam question asks which approach is best for querying live operational data from MySQL without moving it: (A) ETL pipeline to replicate data daily, (B) Lakehouse Federation with Foreign Catalog, (C) export to CSV and upload. The answer is (B). Federation lets you query current data without pipelines or ETL overhead, and Unity Catalog controls access. The key insight is that federation is read only, so it's perfect for reference and operational queries, not for storing your transformed data.

---

### Key Takeaways

- Lakehouse Federation lets you query external databases (PostgreSQL, Snowflake, BigQuery, etc.) directly from Databricks without copying data
- Use **Connections** to store connection credentials and **Foreign Catalogs** to map external databases into Unity Catalog
- Query pushdown sends filtering and computation to the source database, reducing network traffic and improving performance
- Federation is read only. You cannot INSERT, UPDATE, or DELETE through federated tables
- Perfect use cases: joining lakehouse data with live operational systems, gradual migration from legacy platforms, accessing reference data without replication

---

### Gotchas and Tips

<aside> ⚠️ Lakehouse Federation is read only. If a question asks about updating data in a federated table, the answer is no. You must use an ETL pipeline to move and transform the data into your lakehouse instead.

</aside>

<aside> ⚠️ Performance depends on the remote database. If your source system is slow or under heavy load, federated queries will be slow too. Federation doesn't improve the performance of bad source queries. It just lets you query them from Databricks.

</aside>

<aside> ⚠️ Not all SQL features are supported in pushdown. Complex UDFs, regex, and some window functions may not push down. Databricks will compute these locally after fetching data. Write queries with simple WHERE and JOIN conditions to maximize pushdown efficiency.

</aside>

---

### Links and Resources

- [**Lakehouse Federation Overview**](https://docs.databricks.com/aws/en/query-federation/) — Querying data in external systems without moving or copying it.
- [**Federation Connections**](https://docs.databricks.com/aws/en/query-federation/connections) — Creating and managing connections to external data sources.