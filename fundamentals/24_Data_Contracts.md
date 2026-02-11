# 📝 Data Contracts

> Thoả thuận giữa producer và consumer: "Đây là data tôi sẽ gửi, đây là format, đây là SLA"

---

## 📋 Mục Lục

1. [Tại Sao Cần Data Contracts?](#tại-sao-cần-data-contracts)
2. [Anatomy of a Data Contract](#anatomy-of-a-data-contract)
3. [Schema Definitions](#schema-definitions)
4. [SLA & Quality Guarantees](#sla--quality-guarantees)
5. [Breaking Changes Policy](#breaking-changes-policy)
6. [Implementation Tools](#implementation-tools)
7. [Real-World Examples](#real-world-examples)

---

## Tại Sao Cần Data Contracts?

### Không Có Data Contract

```
Monday: Backend team thêm field "middle_name"
Tuesday: Pipeline breaks vì unexpected column
Wednesday: Data team fix pipeline
Thursday: Backend team rename "user_email" → "email"
Friday: Pipeline breaks AGAIN

Kết quả:
- Data team = firefighters
- Backend team = "tại sao data team không handle được?"
- Stakeholders = "tại sao dashboard luôn sai?"
```

### Có Data Contract

```
Backend team muốn thay đổi schema:
1. PR to update data contract
2. Data team reviews impact
3. Agree on timeline + backward compatibility
4. Change deployed with confidence
5. No surprises, no broken pipelines

Kết quả:
- Clear ownership
- Breaking changes planned
- Trust between teams
```

---

## Anatomy of a Data Contract

### Data Contract Specification

```yaml
# contracts/orders/order_events.yaml

apiVersion: v1
kind: DataContract
metadata:
  name: order-events
  version: "2.1.0"
  domain: orders
  owner: orders-team
  contact:
    slack: "#team-orders"
    email: orders@company.com
  
description: |
  Real-time order events published when order state changes.
  Used by analytics, finance, and recommendation teams.

schema:
  type: avro
  fields:
    - name: order_id
      type: string
      format: uuid
      required: true
      description: "Unique order identifier"
      pii: false
      
    - name: customer_id
      type: string
      required: true
      description: "Customer who placed the order"
      pii: true
      classification: confidential
      
    - name: total_amount
      type: decimal
      precision: 10
      scale: 2
      required: true
      description: "Order total in USD"
      
    - name: status
      type: string
      enum: [pending, confirmed, shipped, delivered, cancelled]
      required: true
      
    - name: created_at
      type: timestamp
      format: "ISO 8601 UTC"
      required: true
      
    - name: items
      type: array
      items:
        type: record
        fields:
          - name: product_id
            type: string
            required: true
          - name: quantity
            type: integer
            required: true
          - name: unit_price
            type: decimal
            required: true

delivery:
  mode: streaming
  channel: kafka
  topic: orders.events.v2
  format: avro
  
  sla:
    freshness: "< 5 minutes"
    availability: "99.9%"
    throughput: "10,000 events/minute"
    
  quality:
    completeness: "> 99.9%"
    uniqueness: "order_id is unique"
    validity: "total_amount >= 0"
    
consumers:
  - name: analytics-team
    usage: "Daily order aggregations"
    sla_dependency: "Dashboard by 8 AM"
    
  - name: finance-team
    usage: "Revenue reconciliation"
    sla_dependency: "Monthly close"
    
  - name: recommendation-engine
    usage: "Real-time recommendations"
    sla_dependency: "< 1 min latency"

breaking_changes:
  notification: "2 weeks advance notice"
  channels: ["#data-contracts", "email"]
  migration_support: true
  deprecation_period: "30 days"

terms:
  retention: "3 years"
  usage_restrictions: "PII fields require approval"
  licensing: "internal use only"
```

---

## Schema Definitions

### Schema Evolution Rules

```python
# Trong contract: define rõ rule evolution

class SchemaEvolutionRules:
    compatible_changes = [
        "Add optional field (with default)",
        "Add new enum value at END",
        "Widen numeric type (INT → BIGINT)",
        "Increase string length limit",
    ]
    
    breaking_changes = [
        "Remove field",
        "Rename field",
        "Change field type (incompatible)",
        "Make optional field required",
        "Remove enum value",
        "Change field semantics",
    ]
    
    def validate_change(self, old_schema, new_schema) -> dict:
        """Check if schema change is breaking"""
        issues = []
        
        # Check removed fields
        removed = set(old_schema.keys()) - set(new_schema.keys())
        if removed:
            issues.append(f"BREAKING: Fields removed: {removed}")
        
        # Check type changes
        for field in set(old_schema.keys()) & set(new_schema.keys()):
            if old_schema[field]['type'] != new_schema[field]['type']:
                issues.append(f"BREAKING: {field} type changed")
        
        # Check new required fields
        new_fields = set(new_schema.keys()) - set(old_schema.keys())
        for field in new_fields:
            if new_schema[field].get('required', False):
                if 'default' not in new_schema[field]:
                    issues.append(f"BREAKING: New required field without default: {field}")
        
        return {
            "is_breaking": len(issues) > 0,
            "issues": issues,
            "recommendation": "Follow deprecation timeline" if issues else "Safe to deploy"
        }
```

### Versioning Strategy

```
Semantic Versioning for Data Contracts:

MAJOR.MINOR.PATCH

MAJOR (breaking):
  - Remove field
  - Change field type
  - Rename field
  → Requires consumer migration
  → 2 weeks notice + migration support

MINOR (backward compatible):
  - Add optional field
  - Add new enum value (at end)
  → Consumers should update but won't break

PATCH (non-functional):
  - Update description
  - Fix documentation
  → No consumer impact

Example: orders.events.v2 → v3 (MAJOR)
  kafka topic: orders.events.v2 (keep for 30 days)
  kafka topic: orders.events.v3 (new)
  Consumers migrate within deprecation period
```

---

## SLA & Quality Guarantees

### SLA Template

```yaml
sla:
  # Freshness: How recent is the data?
  freshness:
    target: "< 1 hour"
    measurement: "Time since last record vs current time"
    alert_threshold: "2 hours"
    
  # Completeness: Is all expected data present?
  completeness: 
    target: "> 99.9%"
    measurement: "row_count vs expected_based_on_history"
    alert_threshold: "< 95%"
    
  # Availability: Is the data accessible?
  availability:
    target: "99.9% (43 min downtime/month)"
    measurement: "Query success rate"
    
  # Accuracy: Is the data correct?
  accuracy:
    target: "> 99.99% for financial fields"
    measurement: "Monthly reconciliation with source"
    
  # Latency: How fast is data delivered?
  latency:
    target: "P99 < 5 minutes"
    measurement: "Event time to availability time"
```

### Quality Checks as Contract

```python
# Quality checks are part of the contract, not optional

class ContractQualityChecks:
    def __init__(self, contract: dict):
        self.quality_rules = contract['delivery']['quality']
    
    def validate(self, df) -> dict:
        results = {}
        
        # Completeness
        if 'completeness' in self.quality_rules:
            total = df.count()
            non_null = df.dropna(how='all').count()
            results['completeness'] = non_null / total if total > 0 else 0
            
        # Uniqueness
        if 'uniqueness' in self.quality_rules:
            field = self.quality_rules['uniqueness'].split(' ')[0]
            total = df.count()
            unique = df.select(field).distinct().count()
            results['uniqueness'] = unique / total if total > 0 else 0
            
        # Validity
        if 'validity' in self.quality_rules:
            rule = self.quality_rules['validity']
            valid_count = df.filter(rule).count()
            results['validity'] = valid_count / df.count()
        
        # Check against targets
        violations = []
        for metric, value in results.items():
            target = float(self.quality_rules[metric].strip('> %')) / 100
            if value < target:
                violations.append(f"{metric}: {value:.4f} < target {target}")
        
        return {
            "passed": len(violations) == 0,
            "results": results,
            "violations": violations
        }
```

---

## Breaking Changes Policy

### Communication Flow

```
When producer needs breaking change:

Week -2: Announce in #data-contracts
         File "Breaking Change Request" (BCR)
         
Week -1: Consumer teams review impact
         Agree on migration plan
         
Week 0:  Deploy new version alongside old
         Start consumer migration

Week +2: Check all consumers migrated
         (Platform dashboard: "Who still uses v2?")
         
Week +4: Deprecate old version
         Remove old topic/table
```

### Breaking Change Request Template

```markdown
# Breaking Change Request: BCR-2026-001

## Change Description
Rename field `user_email` → `email` in order events

## Reason
Standardizing field names across all domains

## Impact Assessment
- 3 consumer teams affected
- No data loss
- Requires consumer code change

## Migration Plan
1. v2.1: Add `email` field (copy of `user_email`)
2. Consumers switch to read `email`
3. v3.0: Remove `user_email`

## Timeline
- Feb 1: v2.1 deployed (both fields present)
- Feb 15: Deadline for consumers to update
- Mar 1: v3.0 deployed (old field removed)

## Consumer Sign-off
- [ ] analytics-team (@minh)
- [ ] finance-team (@lan)
- [ ] recommendation-team (@duc)
```

---

## Implementation Tools

### Tool Landscape

| Tool | Type | Best For |
|------|------|----------|
| **Confluent Schema Registry** | Schema validation | Kafka-based contracts |
| **Soda** | Quality checks | SQL-based validation |
| **Great Expectations** | Quality + docs | Python-based validation |
| **DataHub** | Catalog + lineage | Discovery + governance |
| **dbt** | Transform contracts | Schema tests + docs |
| **Protobuf** | Schema definition | gRPC, strict typing |
| **JSON Schema** | Schema definition | REST APIs, flexible |

### dbt as Contract Enforcement

```yaml
# dbt models/staging/schema.yml
# This IS a data contract

version: 2
models:
  - name: stg_orders
    description: "Staging orders — contract version 2.1"
    config:
      contract:
        enforced: true  # dbt 1.5+ contract enforcement
    
    columns:
      - name: order_id
        data_type: varchar
        constraints:
          - type: not_null
          - type: unique
        tests:
          - not_null
          - unique
      
      - name: total_amount
        data_type: numeric(10,2)
        constraints:
          - type: not_null
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
      
      - name: status
        data_type: varchar
        tests:
          - accepted_values:
              values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
```

---

## Real-World Examples

### Example: Uber's Data Contract

```
Uber's Approach:
├── Protobuf schemas for ALL events
├── Schema registry (centralized)
├── Backward compatibility enforced by CI/CD
├── Breaking changes require VP-level approval
├── Consumer registry: who uses what
└── Automated impact analysis

Result:
- 10,000+ data consumers
- <0.01% breakage rate
- Cross-team trust established
```

### Example: Startup (Simple Contract)

```yaml
# Cho startup 10-50 người, đơn giản hoá

# contracts/README.md
## Data Contracts (Simple Version)

### Rule 1: Schema Changes = PR
Any schema change to production tables/topics requires:
- PR with description of change
- Tag @data-team for review
- 1 week notice for breaking changes

### Rule 2: Required Fields
These fields MUST always be present:
- id (unique identifier)
- created_at (UTC timestamp)
- updated_at (UTC timestamp)

### Rule 3: Naming Convention
- snake_case for all fields
- No abbreviations (use customer_id, not cust_id)
- Timestamps always UTC, suffix _at

### Rule 4: Versioning
- Add fields: OK (non-breaking)
- Remove/rename: Announce in #data channel, 1 week wait
```

---

## Checklist

- [ ] Hiểu tại sao cần Data Contracts
- [ ] Biết viết Data Contract specification
- [ ] Có schema evolution rules
- [ ] Có breaking changes policy
- [ ] Có quality guarantees trong contract
- [ ] Biết dùng ít nhất 1 tool enforce contracts
- [ ] Có versioning strategy

---

## Liên Kết

- [22_Schema_Evolution_Migration](22_Schema_Evolution_Migration.md) - Schema changes
- [23_Data_Mesh_Data_Products](23_Data_Mesh_Data_Products.md) - Data products need contracts
- [business/02_Data_Quality_Trust](../business/02_Data_Quality_Trust.md) - Building trust through quality

---

*Data Contract = API contract for data. Nếu backend team cần API spec, data team cần Data Contract.*
