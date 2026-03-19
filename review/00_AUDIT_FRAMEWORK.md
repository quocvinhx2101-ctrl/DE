# Data Engineering Audit Framework

## Mục tiêu / Objective

Tài liệu này định nghĩa cách audit toàn bộ [Fun](../) dưới góc nhìn **Senior/Staff+ Data Engineer / Data Platform engineer**.

Review này cố ý ưu tiên:
- **judgment** hơn là liệt kê tool
- **production realism** hơn là tutorial comfort
- **business impact** hơn là technical vanity
- **consistency** hơn là số lượng file

---

## Scope

### In scope
- Tất cả Markdown files trong [Fun](../)
- Root docs: [README.md](../README.md), [MY_LEARNING_ROADMAP.md](ROADMAP.md)
- Folder-level READMEs
- Python helper scripts:
  - [convert_ascii.py](../convert_ascii.py)
  - [fix_mermaid.py](../fix_mermaid.py)
  - [scripts/setup_lab1.py](../scripts/setup_lab1.py)

### Out of scope for now
- `.obsidian/`
- Git history
- External websites/resources unless a file makes a strong factual claim that needs verification later

---

## Audit rubric

Mỗi file được chấm theo thang **1-10** trên 8 tiêu chí.

| Criterion | Câu hỏi chính | Weight |
|---|---|---:|
| Technical correctness | Có claim nào dễ sai, quá broad, hoặc lỗi thời không? | 20% |
| Senior/staff judgment | Có trade-off, sequencing, ownership, org thinking không? | 20% |
| Production realism | Có nói tới SLA/SLO, on-call, rollback, observability, cost, governance không? | 15% |
| Business relevance | Nội dung có gắn với value, prioritization, adoption không? | 10% |
| Clarity & pedagogy | Dễ đọc, có structure, có path học hợp lý không? | 10% |
| Actionability | Đọc xong làm được gì, quyết định được gì? | 10% |
| Internal consistency | Có khớp với repo-level narrative và file khác không? | 10% |
| Maintainability | File có dễ stale, drift, khó update không? | 5% |

### Verdict labels
- **Keep**: tốt, chỉ cần tinh chỉnh nhỏ
- **Revise**: giữ ý chính nhưng cần chỉnh đáng kể
- **Rewrite**: giữ topic, viết lại gần như toàn bộ
- **Archive**: topic/value hiện tại không xứng đáng giữ nguyên

### Priority labels
- **P0**: làm repo mất uy tín hoặc có khả năng gây hiểu sai rõ ràng
- **P1**: quality issue lớn, làm yếu signal senior/staff
- **P2**: có ích nhưng thiếu depth/consistency
- **P3**: hygiene/cosmetic

---

## Mandatory review template

Mỗi file phải có đủ các mục sau:

### 1. Purpose / Mục đích
File này đang cố làm gì?

### 2. Strengths / Điểm mạnh
Những gì thực sự tốt, không nịnh.

### 3. Weaknesses / Điểm yếu
Những gì junior, generic, overclaimed, stale, hoặc thiếu thực chiến.

### 4. Senior/Staff signal
- Tăng tín nhiệm ở đâu
- Mất tín nhiệm ở đâu

### 5. Production gap
Những gì còn thiếu để dùng như tài liệu cho platform engineering thật.

### 6. Recommendation
Keep / Revise / Rewrite / Archive + priority.

---

## Review sequencing

Thứ tự review được cố ý sắp theo giá trị platform judgment:

1. Root framing docs
2. Folder READMEs
3. [business](../business)
4. [mindset](../mindset)
5. [roadmap](../roadmap)
6. [fundamentals](../fundamentals)
7. [projects](../projects)
8. [usecases](../usecases)
9. [tools](../tools)
10. [platforms](../platforms)
11. [interview](../interview)
12. [papers](../papers)
13. helper scripts

---

## Known risk patterns to watch

### Content risks
- count drift giữa index files
- "SOTA" framing dễ stale nhanh
- tool-heavy but judgment-light
- BigTech hero worship without right-sizing for SMEs
- project docs hứa hẹn codebase nhưng repo thực tế là docs-first
- staff-level claims nhưng thiếu org/process/decision depth

### Engineering hygiene risks
- hardcoded absolute paths
- no validation for Mermaid/link drift
- duplicated narratives across files
- stale date/version banners

---

## Initial success criteria

Audit phase 1 được xem là chạy đúng khi:
- root docs và folder READMEs đã có nhận xét chi tiết
- đã có score + verdict + priority cho batch đầu tiên
- đã có list của systemic issues lặp lại nhiều nơi
- đã tách bạch rõ: **good educational intent** vs **weak platform rigor**
