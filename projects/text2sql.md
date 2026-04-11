# Text-to-SQL V4.1 Blueprint (Governance + Admin UX + Vibe Code)

**Ngày cập nhật:** 2026-04-01

**Mục tiêu:** Biến kiến trúc V4 thành blueprint có thể code ngay, ưu tiên 2 trục bạn nhấn mạnh: **Governance** và **Admin UX**.

  

---

  

## 1) Outcome cần đạt

  

Sau khi triển khai blueprint này, hệ thống phải đạt:

- Governance có thể vận hành thực tế: policy lifecycle, approval flow, audit trail, rollback.

- Admin UX dùng được cho đội Data/Platform/Security mà không cần chỉnh code thủ công.

- End-user UX kiểu conversational analytics (web app) để người dùng hỏi dữ liệu, refine, export, share mà không cần Streamlit/CLI.

- Có đủ backend contract (API + schema + events) để bắt đầu vibe code theo sprint.

  

---

  

## 2) Scope V4.1 (phần mở rộng từ V4)

  

## Kiến trúc chốt (lock)

- **Metadata backbone:** OpenMetadata (single source of metadata truth).

- **Semantic source-of-truth:** dbt Semantic Layer (MetricFlow + dbt artifacts).

- **Policy engine:** OPA/Rego (single PDP).

- **Orchestration:** LangGraph (agent loop) + Temporal (durability).

- **Warehouse execution:** native connector trước, Trino federation là tùy chọn có guard.

  

## In-scope

- Governance Control Plane (Policy, Access, Compliance, Change Management).

- Admin Console UX (Settings, Policies, Semantic Assets, Incident, Cost, Audit).

- End-user Product UX (Genie-like chat + result experience + sharing).

- API contract + data model + event model cho 2 phần trên.

- Roadmap code-first 6 sprint.

- OpenMetadata ingestion/lineage/usage pipeline + health management.

- dbt semantic release flow (dev -> canary -> prod) và drift handling.

  

## Out-of-scope

- Fine-tuning model mới.

- Tối ưu benchmark score theo từng paper cụ thể.

- Multi-cloud geo-distributed control plane full production (chỉ để phase sau).

  

## Các điểm đã chỉnh để hợp lý hơn

- Bỏ hoàn toàn lựa chọn kép `OpenMetadata hoặc DataHub` -> chỉ OpenMetadata.

- Bỏ hoàn toàn lựa chọn kép `dbt hoặc Cube` -> chỉ dbt Semantic Layer.

- Thêm rõ ownership: metadata owner, semantic owner, policy owner, release owner.

- Thêm connector governance: connector health, freshness SLA, backfill/retry.

- Thêm semantic release gates thay vì sửa YAML/manual trực tiếp trên production.

  

---

  

## 3) Governance Blueprint (đầy đủ để build)

  

## 3.1 Governance domains

  

1. **Identity & Access Governance**

- RBAC + ABAC: user/role/team/tenant + data sensitivity + purpose.

- Scoped permissions: Workspace, Semantic Space, Data Source, Policy Set.

- Break-glass role (khẩn cấp) có TTL + bắt buộc lý do.

  

2. **Policy Governance**

- Policy-as-code với versioning: `draft -> review -> approved -> active -> deprecated`.

- 4 nhóm policy:

- Input policy (prompt/safety intent)

- SQL policy (AST pattern/risk score)

- Runtime policy (cost/time/scan/row)

- Egress policy (masking/export/sensitive fields)

  

3. **Data Governance**

- Data classification: Public/Internal/Confidential/Restricted.

- Tag-based controls (PII, PCI, PHI).

- Dynamic masking + row-level filters theo role/purpose.

- Mapping bắt buộc từ OpenMetadata tags -> policy attributes (ABAC input).

  

4. **Operational Governance**

- Change approval flow (2-man rule cho policy critical).

- Audit immutable (append-only events).

- Compliance pack (retention, legal hold, access evidence export).

  

5. **Model & Agent Governance**

- Model routing policy theo task/risk/cost budget.

- Prompt template registry + signed releases.

- Tool allowlist/denylist theo tenant.

  

6. **Metadata & Semantic Governance**

- OpenMetadata ingestion policy: schedule, SLA, ownership, alert routing.

- dbt semantic contract policy: metric definition review, breaking-change checks.

- Semantic release lifecycle: `draft -> validated -> approved -> canary -> active`.

  

---

  

## 3.2 Governance lifecycle

  

## Lifecycle chung

1) Draft

2) Validation (syntax + simulation)

3) Review (owner + security approver)

4) Approve

5) Canary activate (10%)

6) Full activate

7) Monitor violations

8) Rollback nếu breach

  

## Bắt buộc kỹ thuật

- Mọi policy change phải tạo `change_request` + `approval_record`.

- Mọi quyết định runtime phải tạo `policy_decision_log`.

- Policy engine fail => default deny hoặc verified-query-only mode.

  

---

  

## 3.3 Governance SLO/KPI

  

- Policy decision p95 < 30ms (cache hit), < 120ms (cache miss).

- 100% query qua policy checkpoints.

- 100% change có approver traceable.

- Mean time to rollback policy lỗi < 5 phút.

- False-positive policy block rate < 3% sau tuning.

  

---

  

## 4) Admin UX Blueprint (chi tiết màn hình)

  

## 4.1 IA (Information Architecture)

  

Sidebar chính:

1. Overview

2. Workspaces

3. Semantic Assets

4. Policies

5. Access & Roles

6. Executions

7. Incidents

8. Cost & Budgets

9. Audit & Compliance

10. Release Gates

11. Settings

12. Metadata Ops

13. Semantic Releases

  

---

  

## 4.2 Màn hình cốt lõi

  

## A. Overview

- KPI cards: success rate, blocked queries, p95 latency, cost/day, incidents open.

- Health timeline: policy changes, release events, anomaly spikes.

- Top risky intents + top failing assets.

  

## B. Policies

- Policy list với trạng thái: draft/review/active/deprecated.

- Policy diff viewer (so sánh version).

- Simulation tab: test policy trên sample requests.

- Approvals tab: pending/approved/rejected.

  

## C. Access & Roles

- Role matrix: action x resource.

- ABAC builder: điều kiện theo tag/purpose/tenant.

- Break-glass requests: approve/deny + TTL.

  

## D. Semantic Assets

- Metrics/dimensions/joins registry.

- Verified query library: owner, verified_at, expiry, confidence impact.

- Drift alert center: broken mapping, stale definitions.

- dbt artifact status: manifest version, semantic manifest hash, last successful parse.

- Semantic impact preview: metric thay đổi ảnh hưởng dashboard/query nào.

  

## D2. Metadata Ops

- Connector inventory: trạng thái, lần sync cuối, độ trễ metadata, lỗi gần nhất.

- Ingestion runs: success/fail trend, retry queue, dead-letter jobs.

- Lineage coverage heatmap: bảng nào chưa có lineage/usage signal.

  

## D3. Semantic Releases

- Release candidates: danh sách thay đổi metric/dimension/join.

- Compatibility checks: breaking/non-breaking.

- Gate checks: benchmark subset + policy simulation + rollout plan.

- Promote/Rollback controls theo workspace/tenant.

  

## E. Executions

- Real-time query runs: plan, generated SQL, dry-run cost, execution result.

- Guard actions timeline: blocked/masked/cancelled.

- Retry/fallback action history.

  

## F. Incidents

- Incident detail: trigger, impacted tenants, violated policy IDs.

- Suggested playbooks: rollback policy, force verified mode, disable connector.

- Postmortem template auto-fill từ telemetry.

  

## G. Cost & Budgets

- Budget per tenant/workspace/model.

- Burn rate + forecast.

- Top expensive intents/models/tables.

  

## H. Audit & Compliance

- Search theo user/tenant/policy/date.

- Immutable event feed.

- Export evidence bundle (CSV/JSON + signature hash).

  

## I. Release Gates

- Benchmark trend (offline/online).

- Canary results with guard breaches.

- “Promote to active” gated by thresholds.

  

---

  

## 4.3 UX guardrails

  

- Mọi thao tác destructive phải có confirm + reason.

- Mọi thay đổi policy/role hiển thị impact preview.

- Mọi bảng có filter theo tenant + time range + severity.

- Không cho activate policy khi simulation fail.

  

---

  

## 4.4 End-user UX Blueprint (Genie-like, web-first)

  

## Product IA cho end-user

1. Home

2. Spaces (theo domain: Sales, Finance, Ops...)

3. Conversation

4. Query History

5. Saved Insights

6. Alerts & Subscriptions

7. Shared with me

8. Profile & Preferences

  

## Màn hình E1: Home

- Danh sách Space được cấp quyền + usage gần đây.

- Suggested questions theo Space.

- Banner quality trạng thái semantic release hiện tại (Stable/Canary).

  

## Màn hình E2: Space Overview

- Description, trusted assets coverage, semantic freshness score.

- Bộ "starter questions" do owner curate.

- Nút `Start Conversation` và `Browse Saved Insights`.

  

## Màn hình E3: Conversation (trọng tâm)

- Chat panel trái + Result panel phải (split layout).

- Mỗi answer có:

- Direct answer summary.

- Generated SQL (expand/collapse).

- Confidence + signal "used verified query".

- Explain card: metric/dimension/join path đã dùng.

- Suggested follow-up questions.

- User actions:

- Clarify intent (quick chips).

- Re-run with filters/date-range.

- Switch output mode: table/chart/summary.

- Save insight / share / pin to dashboard.

- Feedback thumbs up/down + comment.

  

## Màn hình E4: Query History

- Lọc theo Space/time/status/owner.

- Xem lại câu hỏi, SQL, execution stats, kết quả.

- Duplicate as new conversation.

  

## Màn hình E5: Saved Insights

- Insight cards: title, last refresh, owner, permissions.

- Export CSV/XLSX + share link có quyền.

- Subscribe gửi định kỳ (daily/weekly) cho recipients.

  

## Màn hình E6: Alerts & Subscriptions

- Tạo rule khi metric vượt ngưỡng.

- Delivery channel: email/webhook (phase đầu).

- Alert history + acknowledge.

  

## Màn hình E7: Shared with me

- Danh sách chat/insight/dashboard được chia sẻ.

- Permission badge: view/comment/edit.

  

## UX behaviors bắt buộc (để có "cảm giác như Genie")

- Streaming answer theo từng phase: `understanding -> planning -> executing -> summarizing`.

- Nếu mơ hồ: bot hỏi clarification thay vì đoán bừa.

- Khi blocked bởi policy: hiển thị reason thân thiện + hướng dẫn chỉnh câu hỏi.

- Khi confidence thấp: tự gợi ý verified questions liên quan.

- Mọi kết quả có provenance: "nguồn dữ liệu nào, semantic version nào".

  

## UX phi chức năng

- p95 first-token < 2.0s (không gồm full query completion).

- p95 interactive update < 500ms cho thao tác UI local (filter/sort client state).

- WCAG AA cho màu chữ/contrast/keyboard navigation.

  

---

  

## 4.5 Design system & frontend architecture

  

## Design system

- Token hóa spacing/typography/radius/shadow nhất quán.

- Component cốt lõi: `AppShell`, `SplitPane`, `ChatThread`, `ResultCard`, `SQLViewer`, `PolicyBanner`, `ConfidenceBadge`, `InsightCard`, `ApprovalDrawer`.

- Pattern library cho empty/loading/error/permission states.

  

## Frontend architecture

- SPA/SSR hybrid (Next.js app router) cho SEO nhẹ + auth tốt.

- State strategy:

- Server state: React Query.

- UI state: Zustand/Redux Toolkit (tùy team).

- Real-time events: WebSocket/SSE channel cho execution status.

- Feature flags cho rollout: chat features, chart modes, subscription features.

  

---

  

## 5) Backend contract để code ngay

  

## 5.1 API groups

  

## Governance APIs

- `POST /api/v1/policies` create draft

- `POST /api/v1/policies/{id}/validate`

- `POST /api/v1/policies/{id}/submit-review`

- `POST /api/v1/policies/{id}/approve`

- `POST /api/v1/policies/{id}/activate`

- `POST /api/v1/policies/{id}/rollback`

- `GET /api/v1/policies/{id}/versions`

  

## Access APIs

- `GET /api/v1/roles`

- `POST /api/v1/roles`

- `PUT /api/v1/roles/{id}`

- `POST /api/v1/access/simulate`

- `POST /api/v1/breakglass/request`

- `POST /api/v1/breakglass/{id}/approve`

  

## Semantic/Verified APIs

- `GET /api/v1/semantic/assets`

- `POST /api/v1/verified-queries`

- `PUT /api/v1/verified-queries/{id}`

- `POST /api/v1/verified-queries/{id}/verify`

  

## OpenMetadata APIs

- `POST /api/v1/metadata/connectors`

- `GET /api/v1/metadata/connectors`

- `POST /api/v1/metadata/connectors/{id}/sync`

- `GET /api/v1/metadata/ingestion-runs`

- `GET /api/v1/metadata/lineage/coverage`

  

## dbt Semantic APIs

- `POST /api/v1/semantic/dbt/artifacts/upload`

- `GET /api/v1/semantic/dbt/releases`

- `POST /api/v1/semantic/dbt/releases/{id}/validate`

- `POST /api/v1/semantic/dbt/releases/{id}/approve`

- `POST /api/v1/semantic/dbt/releases/{id}/promote`

- `POST /api/v1/semantic/dbt/releases/{id}/rollback`

  

## Execution/Observability APIs

- `GET /api/v1/executions`

- `GET /api/v1/executions/{id}`

- `POST /api/v1/executions/{id}/cancel`

- `GET /api/v1/incidents`

- `POST /api/v1/incidents/{id}/resolve`

  

## Audit/Compliance APIs

- `GET /api/v1/audit/events`

- `POST /api/v1/compliance/evidence-export`

  

## End-user Product APIs

- `GET /api/v1/spaces`

- `GET /api/v1/spaces/{id}`

- `GET /api/v1/spaces/{id}/starter-questions`

- `POST /api/v1/conversations`

- `GET /api/v1/conversations/{id}`

- `POST /api/v1/conversations/{id}/messages`

- `GET /api/v1/conversations/{id}/stream` (SSE/WebSocket)

- `POST /api/v1/messages/{id}/feedback`

- `POST /api/v1/messages/{id}/save-insight`

- `GET /api/v1/insights`

- `POST /api/v1/insights/{id}/share`

- `POST /api/v1/insights/{id}/subscribe`

- `GET /api/v1/history/queries`

- `POST /api/v1/alerts`

- `GET /api/v1/alerts`

  

---

  

## 5.2 Data model (minimum tables)

  

## Identity & Access

- `users(id, tenant_id, email, status, created_at)`

- `roles(id, tenant_id, name, scope, created_at)`

- `role_bindings(id, user_id, role_id, workspace_id, expires_at)`

- `abac_rules(id, tenant_id, subject_expr, resource_expr, action, effect)`

  

## Policy

- `policies(id, tenant_id, name, type, status, current_version)`

- `policy_versions(id, policy_id, version, content, checksum, created_by)`

- `policy_approvals(id, policy_version_id, reviewer_id, decision, reason, at)`

- `policy_decisions(id, request_id, policy_id, version, decision, reason, latency_ms)`

  

## Semantic / Verified

- `semantic_assets(id, tenant_id, type, name, owner, status, updated_at)`

- `verified_queries(id, tenant_id, asset_id, nl_question, sql_text, verified_by, verified_at, expiry_at)`

- `semantic_drifts(id, tenant_id, asset_id, drift_type, severity, detected_at, status)`

- `dbt_artifacts(id, tenant_id, artifact_type, version, checksum, uploaded_by, uploaded_at)`

- `semantic_releases(id, tenant_id, release_name, status, manifest_checksum, approved_by, promoted_at)`

- `semantic_release_checks(id, release_id, check_type, status, report_uri, created_at)`

  

## Metadata Ops

- `metadata_connectors(id, tenant_id, source_type, config_ref, owner, status, created_at)`

- `metadata_ingestion_runs(id, connector_id, run_state, started_at, ended_at, error_summary)`

- `metadata_freshness(id, tenant_id, entity_fqn, freshness_minutes, sla_minutes, status, updated_at)`

  

## Execution / Incident

- `executions(id, tenant_id, request_id, state, model, est_cost, actual_cost, started_at, ended_at)`

- `execution_steps(id, execution_id, step_type, state, latency_ms, payload_ref)`

- `incidents(id, tenant_id, severity, category, status, opened_at, closed_at)`

  

## End-user Product

- `spaces(id, tenant_id, name, description, owner, semantic_release_id, status, created_at)`

- `conversations(id, tenant_id, space_id, created_by, title, status, created_at, updated_at)`

- `messages(id, conversation_id, role, content_json, confidence_score, verified_query_id, created_at)`

- `query_runs(id, message_id, execution_id, sql_text, dry_run_cost, run_state, created_at)`

- `insights(id, tenant_id, space_id, title, payload_ref, owner, visibility, created_at)`

- `insight_shares(id, insight_id, principal_type, principal_id, permission, shared_at)`

- `subscriptions(id, insight_id, schedule_cron, channel, recipients_json, status)`

- `alerts(id, tenant_id, space_id, rule_json, severity, status, created_at)`

  

## Audit / Compliance

- `audit_events(id, tenant_id, actor, action, resource_type, resource_id, metadata, at)`

- `evidence_exports(id, tenant_id, requester, scope, file_uri, checksum, created_at)`

  

---

  

## 5.3 Event model

  

Topic tối thiểu:

- `policy.changed`

- `policy.decision_made`

- `access.breakglass_requested`

- `execution.started|finished|cancelled`

- `incident.opened|resolved`

- `semantic.drift_detected`

- `metadata.ingestion_run_finished`

- `semantic.release_promoted|rolled_back`

- `release.gate_failed|passed`

- `conversation.message_streamed`

- `conversation.clarification_requested`

- `insight.saved|shared|subscribed`

- `alert.triggered|acknowledged`

  

Schema event chuẩn:

- `event_id, tenant_id, event_type, actor, resource, ts, trace_id, payload`

  

---

  

## 6) Security blueprint (thực thi được)

  

- OIDC + short-lived tokens + refresh rotation.

- Secrets qua vault, không để trong config file.

- Signed artifacts cho policy bundle và prompt template.

- mTLS nội bộ cho service-to-service.

- Encrypt in transit + at rest.

- SQL execution sandbox + outbound network egress control.

- Audit append-only + checksum chaining (tamper-evident).

- Signed share links + TTL + scope-bound permissions.

- PII redaction layer trước khi render answer text cho end-user.

  

---

  

## 6.1 Backend enterprise runtime (module-level)

  

Service bắt buộc ngoài các service hiện có:

- `conversation-service`: quản lý state đa-turn, clarification flow, message persistence.

- `response-composer`: tổng hợp answer text + chart spec + provenance + policy hints.

- `insight-service`: save/share/subscription lifecycle.

- `alert-service`: evaluate alert rules, dispatch notifications.

- `realtime-gateway`: SSE/WebSocket fanout cho status streaming.

- `cache-service`: semantic/context cache + query result cache có TTL.

  

Patterns kỹ thuật bắt buộc:

- Idempotency key cho mọi mutation API (create message, save insight, share).

- Outbox pattern cho event publish tránh mất event.

- Retry policy có jitter + DLQ cho jobs async.

- Read/write separation cho workload query-heavy (history, audit, insights).

- Tenant-aware rate limiting ở gateway + service layer.

  

---

  

## 7) Vibe Code Plan (6 sprint)

  

## Sprint 1: Foundation

- Monorepo + auth + tenant model + base admin shell.

- CRUD roles/policies draft.

- OpenMetadata connector registry skeleton + dbt artifact store skeleton.

  

## Sprint 2: Governance core

- Policy versioning + approval workflow + simulation.

- Policy decision logging end-to-end.

- ABAC mapping từ OpenMetadata tags vào PDP input.

  

## Sprint 3: Admin UX core

- Pages: Overview, Policies, Access, Audit.

- Diff viewer + approval inbox.

- Pages: Metadata Ops + Semantic Releases (read-only trước).

- End-user pages: Home, Space Overview, Conversation (MVP).

  

## Sprint 4: Execution governance

- Execution timeline, guarded run controls, incident panel.

- Cost budget guard + alert.

- Connector health alerting + ingestion retry queue.

- Streaming pipeline (SSE/WebSocket) từ execution -> conversation UI.

  

## Sprint 5: Semantic & Verified

- Semantic asset registry + verified query management + drift alerts.

- dbt semantic release flow đầy đủ (validate/approve/promote/rollback).

- Saved Insights + Share + Query History hoàn chỉnh.

  

## Sprint 6: Release gates

- Offline gate runner + canary gate + promotion UI.

- Evidence export for compliance.

- Progressive rollout theo tenant/workspace cho semantic releases.

- Alerts & Subscriptions + policy-safe exports.

  

---

  

## 8) Definition of Done (để claim “vào phase production beta”)

  

- 100% requests có trace + audit + policy decisions.

- Policy workflow hoạt động đầy đủ draft->active->rollback.

- Admin có thể xử lý incident/policy/access không cần thao tác DB tay.

- End-user có thể hoàn thành full flow: hỏi -> clarify -> nhận kết quả -> lưu insight -> share -> subscribe.

- Release gate chặn được bản có regression safety/accuracy.

- Có runbook và dashboard cho on-call.

  

---

  

## 9) Reference implementation skeleton

  

```text

kest/

apps/

api/ # FastAPI control/data plane APIs

admin-web/ # Admin UX (React/Next)

worker/ # async jobs: drift, gate, exports

services/

policy-pdp/ # OPA adapter + decision service

planner-runtime/ # LangGraph orchestration

execution-gateway/ # dry-run/cost/execute/cancel

semantic-service/ # dbt semantic assets + verified queries + release mgmt

metadata-service/ # OpenMetadata ingestion, lineage, freshness, usage

conversation-service/# multi-turn state + clarification manager

response-composer/ # answer synthesis + provenance + chart spec

insight-service/ # save/share/subscription management

realtime-gateway/ # SSE/WebSocket streaming

alert-service/ # alert evaluation + dispatch

audit-service/ # immutable event writer

packages/

contracts/ # OpenAPI + event schemas

policy-bundles/ # rego bundles + tests

ui-kit/ # design primitives

infra/

temporal/

postgres/

redis/

otel/

helm/

```

  

---

  

## 10) Quyết định kiến trúc chốt cho phase code

  

- **Chốt OpenMetadata** làm metadata backbone duy nhất.

- **Chốt dbt Semantic Layer** làm semantic source-of-truth duy nhất.

- `sqlglot` chỉ là parser/normalizer, **không** là security boundary.

- PDP phải là runtime dependency bắt buộc; fail-safe mặc định deny hoặc verified-only.

- Mọi thay đổi policy/access phải đi qua admin workflow có approval và audit.

- Mọi thay đổi semantic (dbt artifacts/metrics/joins) phải đi qua semantic release workflow.

- Mọi connector metadata phải có owner + SLA + health alert + retry policy.

  

---

  

## 10.1 Kiến trúc chuẩn tham chiếu (đã tối ưu cho triển khai)

  

**Control Plane**

- Admin Web + Governance API + Policy PDP + Release Gate Service.

  

**Knowledge Plane**

- OpenMetadata (catalog, lineage, usage, glossary, tags).

- dbt artifacts + semantic manifest + verified queries.

  

**Execution Plane**

- Planner runtime (LangGraph) + workflow durability (Temporal).

- Execution gateway (dry-run/cost/guarded execute/cancel).

  

**Observability Plane**

- OTel traces, policy decision logs, audit events, cost telemetry.

  

Nguyên tắc: mọi query phải đi theo chuỗi `Intent -> Semantic Resolve -> Policy Decide -> Dry-run -> Execute -> Post-check -> Audit`.

  

---

  

## 11) Bản “thực dụng nhất” để bắt đầu tuần này

  

Nếu cần đi nhanh mà vẫn đúng hướng:

1. Build ngay 4 page admin: `Overview`, `Policies`, `Access`, `Audit`.

2. Build 6 API lõi: create/validate/approve/activate policy + simulate access + query audit.

3. Bật policy decision logging + execution timeline trước mọi optimization.

4. Chỉ cho phép execute full query khi qua dry-run + budget + policy score.

  

Đây là mức tối thiểu để từ kiến trúc chuyển sang sản phẩm có thể vận hành, không chỉ demo.