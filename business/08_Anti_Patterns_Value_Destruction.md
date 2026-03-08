# Anti-Patterns: Những Việc Phá Hủy Giá Trị

> Đọc cái này TRƯỚC khi đọc gì khác. Biết cái sai trước, tránh nó.

---

## Tại Sao File Này Quan Trọng Nhất?

```
Biết cái SAI giúp bạn:
- Không lãng phí 6 tháng build thứ không ai dùng
- Không bị đánh giá thấp dù code giỏi
- Không gây hại cho công ty dù vô tình

"Avoiding stupidity is easier than seeking brilliance" - Charlie Munger
```

---

## Anti-Pattern 1: Resume-Driven Development

### Mô tả
Build hệ thống phức tạp vì muốn có trên resume, không vì business cần.

### Ví dụ
```
Data: 5GB/ngày
Họ build: Kafka + Spark + Kubernetes + Iceberg
Thực tế cần: PostgreSQL + cron job

Cost gây ra: $5,000/month (thay vì $200)
Complexity: 10x (maintain nightmare)
Business value: Như nhau
```

### Tại sao xảy ra
- Muốn học công nghệ mới
- Sợ CV không "sexy"
- Over-engineer cho "tương lai scale"
- Không hiểu thực tế business

### Cách tránh
```
Hỏi 3 câu trước khi chọn tool:
1. Data size hiện tại bao nhiêu? (GB, not TB)
2. Team có maintain được không? (skill + headcount)
3. Chi phí có hợp lý với business size không?
```

### Rule of thumb
| Data Size | Appropriate Stack |
|-----------|-------------------|
| <10GB/day | PostgreSQL + dbt + cron |
| 10-100GB/day | DuckDB/BigQuery + Airflow |
| 100GB-1TB/day | Spark + managed Airflow |
| >1TB/day | Consider Kafka, Flink |

---

## Anti-Pattern 2: Build First, Ask Later

### Mô tả
Xây xong rồi mới hỏi stakeholder có dùng không.

### Ví dụ
```
DE: *Mất 3 tháng build pipeline phức tạp*
DE: "Done! Marketing team, here's your new dashboard!"
Marketing: "Actually, we stopped that campaign. And we use different metrics now."
DE: *3 months wasted*
```

### Tại sao xảy ra
- Sợ bị reject ý tưởng
- Thích code hơn nói chuyện
- Assume requirements không đổi
- Không có habit check-in

### Cách tránh
```
Framework: Build incrementally, validate often

Week 1: Show mockup, get feedback
Week 2: Build MVP, show to 1-2 users
Week 3: Iterate based on feedback
Week 4: Roll out if validated

Never build more than 2 weeks without stakeholder validation.
```

---

## Anti-Pattern 3: Perfect is the Enemy of Good

### Mô tả
Delay delivery vì chờ hoàn hảo.

### Ví dụ
```
Timeline:
- Week 1-2: Build 80% of value
- Week 3-6: Polish 20% edge cases
- Week 7: Add monitoring
- Week 8: Add more tests
- Week 9: Still not deployed

Meanwhile:
- Business still using Excel
- Competitor shipped faster
- Requirements changed
```

### Tại sao xảy ra
- Fear of criticism
- Perfectionism
- Not understanding "good enough"
- No clear definition of done

### Cách tránh
```
80/20 Rule:
- 80% của value đến từ 20% của effort
- Ship 80%, iterate on 20%
- Working imperfect > Perfect not working

Questions:
- What's the MINIMUM that delivers value?
- Can we add improvements in v2?
- What's the cost of waiting?
```

---

## Anti-Pattern 4: Not My Job Syndrome

### Mô tả
Chỉ làm technical, ignore business context.

### Ví dụ
```
DE: "Pipeline chạy đúng rồi, data đã load."
Business: "Nhưng dashboard vẫn sai."
DE: "Đó là vấn đề của Analyst team, không phải của tôi."

Result:
- Problem not solved
- DE seen as unhelpful
- Trust eroded
```

### Tại sao xảy ra
- Defined by job description too narrowly
- Avoiding accountability
- Not understanding end-to-end

### Cách tránh
```
Ownership Mindset:
- "My job is to solve the problem, not just run the pipeline"
- Follow through until business outcome achieved
- If blocked, escalate + propose solutions

Even if not your job to fix, it IS your job to ensure it gets fixed.
```

---

## Anti-Pattern 5: Silent Failures

### Mô tả
Pipeline fail nhưng không ai biết cho đến khi CEO hỏi "Tại sao dashboard trống?"

### Ví dụ
```
3 AM: Pipeline fails silently
6 AM: Data not refreshed
9 AM: CEO opens dashboard, sees yesterday's numbers
9:05 AM: CEO Slack: "Why is data stale?"
9:06 AM: Panic mode

Trust: Destroyed
Your weekend: Ruined
```

### Tại sao xảy ra
- No alerting configured
- Alerts go to ignored channel
- "It usually works"
- No monitoring culture

### Cách tránh
```
Alerting checklist:
- [ ] Pipeline failure → Slack/PagerDuty immediately
- [ ] Data quality issue → Alert before business hours
- [ ] SLA breach → Escalation path defined
- [ ] Test alerts regularly (fire drill)

Rule: If CEO can discover issue before you, you've failed.
```

---

## Anti-Pattern 6: Documentation as Afterthought

### Mô tả
Code xong không document, rồi 6 tháng sau chính mình không hiểu.

### Ví dụ
```
Month 1: Build complex pipeline, no docs
Month 6: You forgot why you did X
Month 8: You leave company
Month 9: New hire takes 3 months to understand
Month 12: They rebuild from scratch

Cost: 6 months of productivity
```

### Tại sao xảy ra
- "Code is self-documenting" (lie)
- Deadline pressure
- Boring
- Will do later (never)

### Cách tránh
```
Minimum documentation:
1. README: What this does, why it exists
2. Architecture: How components connect
3. Runbook: How to operate/debug
4. Data dictionary: What each field means

Rule: If you can't explain it in README, you don't understand it.
```

---

## Anti-Pattern 7: Hero Culture

### Mô tả
Một người biết mọi thứ, không ai khác có thể maintain.

### Ví dụ
```
"Hero" DE:
- Only person who understands critical pipeline
- Always on-call (burns out)
- Takes all complex tasks (bottleneck)
- Leaves suddenly (company stuck)

Bus factor = 1 → Very bad
```

### Tại sao xảy ra
- Ego (feels good to be needed)
- Faster to do than explain
- No time for knowledge sharing
- Management doesn't prioritize

### Cách tránh
```
Increase bus factor:
- Pair programming on critical systems
- Rotate on-call
- Document ruthlessly
- Let others own pieces

Test: Can you take 2 weeks vacation without being contacted?
If no → You're the hero, fix it.
```

---

## Anti-Pattern 8: All Tech, No Talk

### Mô tả
Technical skills 10/10, communication 2/10.

### Ví dụ
```
DE does amazing work.
No one knows about it.
Less skilled but more visible colleague gets promoted.
DE complains: "Politics!"

Reality: Visibility is part of the job.
```

### Tại sao xảy ra
- Introverted (fine, but must adapt)
- "Work speaks for itself" (it doesn't)
- Don't know how to communicate
- Think it's "bragging"

### Cách tránh
```
Make impact visible:
- Weekly update to manager (even if not asked)
- Demo to stakeholders
- Document wins
- Share learnings with team

It's not bragging if you're stating facts:
"I optimized queries that save $4K/month"
```

---

## Anti-Pattern 9: Shiny Object Syndrome

### Mô tả
Jump to new tool/framework mỗi tuần, không master gì cả.

### Ví dụ
```
Month 1: "Let's use Airflow!"
Month 2: "Wait, Prefect looks better"
Month 3: "Actually Dagster is the future"
Month 4: "Maybe Mage.ai?"

Result:
- 4 months, no production system
- Half-learned 4 tools
- Mastered 0
```

### Tại sao xảy ra
- FOMO
- Twitter/Hacker News influence
- Bored with current tool
- Grass is greener

### Cách tránh
```
2-year rule:
- Pick tools that will still exist in 2 years
- Master one before adding another
- New tool = 10x better, not 2x

Questions:
- Is current tool REALLY blocking us?
- What's the switching cost?
- Will we actually use new features?
```

---

## Anti-Pattern 10: Optimizing Prematurely

### Mô tả
Optimize thứ chưa cần optimize.

### Ví dụ
```
Query runs in 5 seconds.
DE spends 2 weeks making it run in 0.5 seconds.
Query runs once a day.

Time saved: 4.5 seconds/day = 27 minutes/year
Time spent: 80 hours

ROI: -79.5 hours
```

### Tại sao xảy ra
- It's fun (engineering challenge)
- Doesn't want to do boring work
- Doesn't calculate ROI
- "Best practice"

### Cách tránh
```
Optimization checklist:
1. Is this actually slow? (measure first)
2. Does speed matter here? (batch vs real-time)
3. What's the ROI of optimizing?

Rule: Optimize only when there's real pain.
"Make it work, make it right, make it fast" - in that order.
```

---

## Summary: Red Flags Checklist

When you catch yourself doing these, STOP:

- [ ] Choosing tool because it's on HN, not because it's needed
- [ ] Building more than 2 weeks without stakeholder check-in
- [ ] Delaying ship for "polish"
- [ ] Saying "not my problem"
- [ ] Not setting up alerts
- [ ] "I'll document later"
- [ ] Being the only one who knows
- [ ] Not telling anyone about your wins
- [ ] Switching tools frequently
- [ ] Optimizing before measuring

---

## Positive Patterns (What TO Do)

| Anti-Pattern | Positive Pattern |
|--------------|------------------|
| Resume-driven | Outcome-driven |
| Build first | Validate first |
| Perfect | Good enough, then iterate |
| Not my job | End-to-end ownership |
| Silent failures | Loud failures (alerts) |
| No docs | Docs as you go |
| Hero | Team knowledge |
| All tech | Tech + communication |
| Shiny objects | Deep mastery |
| Premature optimization | Measure then optimize |

---

*Avoiding these anti-patterns = 80% of being a good DE*
