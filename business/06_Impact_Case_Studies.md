# Impact Case Studies

> Ví dụ thực tế DE tạo impact, từ nhỏ đến lớn

---

## Case Study 1: $4,300/month Cloud Savings (Week 1)

### Context
- Company: Series B startup, 50 employees
- DE team: Just me (new hire)
- Cloud bill: ~$15,000/month (BigQuery + GCS)

### Discovery
Tuần đầu tiên, tôi chạy query phân tích chi phí:

```sql
SELECT
    user_email,
    DATE_TRUNC(creation_time, MONTH) as month,
    SUM(total_bytes_processed) / POW(10,12) as tb_scanned,
    SUM(total_bytes_processed) / POW(10,12) * 5 as cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY 1, 2
ORDER BY cost_usd DESC;
```

**Phát hiện:**
- 1 scheduled report chạy `SELECT *` từ 500GB table mỗi ngày
- Report này không ai dùng nữa (team đã chuyển sang dashboard khác)
- Chi phí: ~$2,500/month cho 1 query!

### Action
1. Confirm với stakeholder: Report không cần nữa → Disable
2. Tìm thêm 5 queries tương tự: Optimize với partition pruning
3. Add lifecycle policy cho GCS: Move to Nearline sau 30 ngày

### Result
- **Savings:** $4,300/month (28.7% reduction)
- **Effort:** 3 ngày phân tích + optimize
- **ROI:** ~$4,000/month / 3 days work = Very high

### Learning
> Đừng build gì cả tuần đầu. Analyze spending trước.

---

## Case Study 2: Marketing Self-Service (Month 1-2)

### Context
- Marketing team (8 người) mất 15 giờ/tuần làm báo cáo thủ công
- Export CSV từ Google Ads, Facebook Ads → Paste vào Excel → Send Slack
- Data delay 1 ngày → Họ tối ưu campaign chậm

### Pain discovered
Interview Marketing lead:
> "Mỗi sáng tôi mất 30 phút download data. 
> Rồi còn phải reconcile với Finance số liệu nữa.
> Thường thường data sai vì copy-paste."

### Solution
1. **Ingestion:** Airbyte sync từ Google/Facebook Ads → BigQuery (mỗi giờ)
2. **Transform:** dbt model chuẩn hóa metrics, calculate derived
3. **Dashboard:** Metabase connected to BigQuery
4. **Alert:** Slack notification nếu CAC > threshold

```sql
-- dbt model: mart_marketing_performance.sql
WITH daily_ads AS (
    SELECT 
        date,
        channel,
        campaign_name,
        SUM(spend) as spend,
        SUM(impressions) as impressions,
        SUM(clicks) as clicks,
        SUM(conversions) as conversions
    FROM {{ ref('stg_ads_union') }}
    GROUP BY 1, 2, 3
)

SELECT
    *,
    clicks / NULLIF(impressions, 0) as ctr,
    spend / NULLIF(clicks, 0) as cpc,
    spend / NULLIF(conversions, 0) as cpa,
    conversions / NULLIF(clicks, 0) as conversion_rate
FROM daily_ads
```

### Result
- **Time saved:** 15 hrs/week × 4 weeks = 60 hours/month
- **Data freshness:** 1 day → 1 hour
- **Data accuracy:** 100% (no manual copy-paste)
- **Bonus impact:** Marketing caught overspending campaign 6 hours earlier, saved $3K

### Learning
> Tự động 1 việc nhỏ cho nhiều người = Impact lớn hơn 1 feature to cho ít người.

---

## Case Study 3: Prevent Churn with Health Score (Month 3-4)

### Context
- SaaS company, $5M ARR, 200 customers
- Churn rate: 8% monthly (painful)
- Customer Success team: Reactive, only knows customer unhappy khi họ cancel

### Pain discovered
CS Lead:
> "Chúng tôi biết customer muốn cancel khi họ email nói cancel.
> Lúc đó đã quá muộn."

### Solution
Build Customer Health Score dashboard:

```sql
-- Composite health score

SELECT
    customer_id,
    
    -- Usage component (40 points max)
    CASE 
        WHEN dau_last_30d >= 20 THEN 40
        WHEN dau_last_30d >= 10 THEN 30
        WHEN dau_last_30d >= 5 THEN 20
        ELSE 10
    END as usage_score,
    
    -- Feature adoption (20 points max)
    CASE
        WHEN features_used >= 10 THEN 20
        WHEN features_used >= 5 THEN 15
        ELSE 5
    END as adoption_score,
    
    -- Support sentiment (20 points max)
    CASE
        WHEN negative_tickets_30d = 0 THEN 20
        WHEN negative_tickets_30d <= 2 THEN 10
        ELSE 0
    END as support_score,
    
    -- Engagement trend (20 points max)
    CASE
        WHEN events_this_week > events_last_week THEN 20  -- Growing
        WHEN events_this_week >= events_last_week * 0.8 THEN 15  -- Stable
        ELSE 5  -- Declining
    END as trend_score

FROM customer_metrics
```

### Result (After 6 months)
- **Churn rate:** 8% → 5% (-37.5%)
- **Revenue saved:** ~$150K/year (3% of 5M ARR)
- **CS efficiency:** Focused on 20 at-risk customers instead of guessing

### Learning
> DE không chỉ là move data. DE là cung cấp insights để business hành động.

---

## Case Study 4: Real-time Fraud Detection (Advanced)

### Context
- Fintech, $50M transactions/month
- Fraud rate: 0.5% = $250K/month losses
- Current detection: Batch daily → Fraud detected 24 hours late

### Pain
> "Chúng tôi biết giao dịch fraud vào ngày hôm sau.
> Lúc đó tiền đã mất rồi."

### Solution
Real-time fraud scoring pipeline:

```
Events → Kafka → Flink (ML scoring) → Druid → Alert
              ↓
         Feature Store (real-time features)
```

**Flink job (simplified):**
```java
// Real-time fraud scoring
stream
    .keyBy(Transaction::getUserId)
    .process(new FraudScoringFunction())
    .filter(t -> t.getFraudScore() > 0.8)
    .addSink(new AlertSink());
```

**Features calculated real-time:**
- Transaction velocity (5 transactions in 1 minute = risky)
- Geo-anomaly (transaction from Vietnam then US in 30 min = flag)
- Amount deviation (10x average = suspicious)

### Result
- **Fraud detection latency:** 24 hours → 30 seconds
- **Fraud losses:** $250K → $100K/month (-60%)
- **ROI:** $150K saved/month vs $30K infrastructure cost

### Learning
> Real-time có ROI cao với financial use cases.
> Nhưng bắt đầu đơn giản, chứng minh value trước khi build phức tạp.

---

## Case Study 5: Enable Data Mesh (Staff-level)

### Context
- Enterprise, 500+ employees, 5 data teams
- Central data team bottleneck: Every request goes through 3-person team
- Backlog: 6 months wait time

### Pain
Business teams:
> "Chúng tôi có data nhưng không tự dùng được.
> Phải chờ DE team 6 tháng."

### Solution
Data Mesh architecture:
1. **Platform:** Provide self-service tools (Airflow, dbt, query engine)
2. **Standards:** Define schema standards, quality requirements
3. **Training:** Teach domain teams basic DE skills
4. **Federation:** Each domain owns their data products

**What DE team provides:**
- Infrastructure (Kubernetes, Airflow, Spark cluster)
- Data platform (ingestion tools, catalog, quality framework)
- Consulting (help domains build first pipelines)

**What domains own:**
- Their data models
- Their transformations
- Their quality tests
- Their documentation

### Result (After 1 year)
- **Backlog:** 6 months → 2 weeks
- **Data products:** 5 → 50 (10x)
- **Central DE team:** 3 → still 3 (didn't grow, scaled through platform)

### Learning
> Staff DE impact = Enable others, not do everything yourself.

---

## Pattern: How Impact Scales

| Level | Type of Impact | Example |
|-------|----------------|---------|
| **Junior** | Complete assigned tasks | Build 1 pipeline |
| **Mid** | Improve efficiency | Optimize queries, save hours |
| **Senior** | Enable others | Self-service dashboards, automation |
| **Staff** | Org-wide change | Data mesh, standards, culture |

---

## Your Turn: Find Your Impact

### Week 1
- [ ] Analyze cloud spending
- [ ] Interview 2 stakeholders about pain points
- [ ] Find 1 quick win

### Month 1
- [ ] Deliver 1 automation
- [ ] Document impact ($, hours, etc.)
- [ ] Share win with manager

### Quarter 1
- [ ] Establish reputation as "problem solver"
- [ ] Build 1 self-service capability
- [ ] Measure cumulative impact

---

*Impact is about solving real problems, not just writing code*
