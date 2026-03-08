# High-Signal Findings

## Batch 2: Business, mindset, roadmap anchors

Batch này review các file có giá trị tín hiệu cao nhất cho câu hỏi quan trọng nhất:

> Repo này có thật sự suy nghĩ như một Senior/Staff+ Data Engineer không, hay chỉ đang nói giọng Senior/Staff?

---

## 1) [business/08_Anti_Patterns_Value_Destruction.md](../business/08_Anti_Patterns_Value_Destruction.md)
- **Score:** 8.6/10
- **Verdict:** Keep
- **Priority:** P1

### Strengths
- Một trong những file mạnh nhất repo.
- Giọng điệu thẳng, rõ, không academic vô ích.
- Các anti-pattern chọn đúng: resume-driven development, silent failures, hero culture, documentation afterthought.
- Rất gần đời sống data/platform thực tế hơn nhiều file “learn tool X”.

### Weaknesses
- Rule-of-thumb tables có ích nhưng hơi dễ bị đọc thành universal truth.
- Một số ví dụ cost/stack khá deterministic, trong khi thực tế còn phụ thuộc compliance, concurrency, latency, team shape.
- Cần thêm anti-pattern về governance theater, dashboard vanity, và platform over-centralization.

### Staff-level judgment
Đây là file hiếm hoi thực sự phát ra signal senior/staff mạnh vì nó ưu tiên **judgment under constraints** thay vì tool worship.

### Recommendation
Giữ nguyên tinh thần. Bổ sung disclaimer rằng các thresholds chỉ là heuristics, không phải policy.

---

## 2) [business/01_ROI_Cost_Optimization.md](../business/01_ROI_Cost_Optimization.md)
- **Score:** 7.7/10
- **Verdict:** Keep
- **Priority:** P2

### Strengths
- Rất thực dụng.
- Tập trung vào một trong những cách nhanh nhất để chứng minh value.
- Có examples cụ thể, dễ hành động.
- Leadership communication template là điểm cộng lớn.

### Weaknesses
- Một số con số tiết kiệm đọc hơi quá gọn và có thể tạo kỳ vọng ảo.
- Tối ưu cost được mô tả như “quick win” gần như universal, nhưng đôi khi governance/process mới là bottleneck lớn hơn.
- Chưa nói đủ về trade-off giữa cost optimization và reliability/performance.

### Staff-level judgment
Tốt hơn mức tutorial bình thường vì đã nói đến communication upward. Tuy nhiên vẫn cần explicit hơn về việc **đừng tối ưu bill bằng cách tạo rủi ro vận hành**.

### Recommendation
Giữ. Thêm một section “when not to optimize yet” và “cost vs reliability trade-off”.

---

## 3) [mindset/06_Tech_Leadership.md](../mindset/06_Tech_Leadership.md)
- **Score:** 8.2/10
- **Verdict:** Keep
- **Priority:** P1

### Strengths
- Có substance thật, không chỉ motivational prose.
- Phần archetypes, strategy template, influence playbook, RFC framing đều rất usable.
- Tập trung đúng vào shift từ individual output sang org leverage.
- Có nhiều mô típ đúng chất Staff: phased roadmap, success gates, alternatives considered, adoption strategy.

### Weaknesses
- Một số examples hơi “clean” và linear hơn đời thật.
- Có nguy cơ over-template hóa staff work, khiến người đọc tưởng chỉ cần điền form là thành Staff.
- Nên thêm phần về political capital, sequencing, and knowing when **not** to standardize.

### Staff-level judgment
Đây là một trong các file tốt nhất repo hiện tại. Nó không hoàn hảo, nhưng đã chạm đúng operating mechanisms thay vì chỉ nói về “leadership mindset” chung chung.

### Recommendation
Giữ và dùng file này làm chuẩn chất lượng cho các file mindset/roadmap khác.

---

## 4) [mindset/05_Day2_Operations.md](../mindset/05_Day2_Operations.md)
- **Score:** 8.4/10
- **Verdict:** Keep
- **Priority:** P1

### Strengths
- Rất thực chiến.
- Day-1 vs Day-2 framing đúng và quan trọng.
- On-call, runbook, postmortem, SLA/SLO là những thứ phân biệt engineer “ship feature” với engineer “own production”.
- Tone đủ thẳng mà vẫn hữu ích.

### Weaknesses
- Còn hơi generic ở phần alerting taxonomy và ops tooling; có thể sâu hơn về false positives, dependency contracts, and escalation economics.
- Chưa nói rõ enough về data-specific operational pain như backfill blast radius, replay strategy, idempotency, and consumer communication.

### Staff-level judgment
File này tăng uy tín repo mạnh. Nó kéo repo gần hơn với platform engineering thật.

### Recommendation
Giữ. Sau này nên nối trực tiếp với [fundamentals/21_Debugging_Troubleshooting.md](../fundamentals/21_Debugging_Troubleshooting.md) và [projects/07_Debug_Production_Pipeline.md](../projects/07_Debug_Production_Pipeline.md).

---

## 5) [roadmap/01_Career_Levels.md](../roadmap/01_Career_Levels.md)
- **Score:** 6.6/10
- **Verdict:** Revise
- **Priority:** P2

### Strengths
- Dễ đọc.
- Hữu ích cho người mới cần mental model ban đầu.
- Chia level theo scope/impact là hướng đi đúng.

### Weaknesses
- Years-of-experience mapping quá cứng và dễ gây hiểu nhầm.
- Career growth trong data/platform rarely linear như bảng mô tả.
- Một số phần vẫn thiên về checklist học tool hơn là capability model.
- Principal được gắn với “industry leadership” hơi hẹp và không phải chuẩn phổ quát.

### Staff-level judgment
Có giá trị orientation, nhưng chưa đủ sắc để làm khung đánh giá career trưởng thành. Staff+ growth phụ thuộc scope, ambiguity, influence, business context, không chỉ tenure.

### Recommendation
Đổi từ “years-based ladder” sang “capability + scope + ambiguity + influence” ladder.

---

## 6) [roadmap/02_Skills_Matrix.md](../roadmap/02_Skills_Matrix.md)
- **Score:** 6.0/10
- **Verdict:** Revise
- **Priority:** P1

### Strengths
- Có tổ chức.
- Tốt cho self-assessment sơ bộ.
- Bao phủ kỹ thuật + architecture + soft skills khá rộng.

### Weaknesses
- Numeric matrix nhìn có vẻ precise hơn thực tế.
- Staff column nhiều chỗ đơn giản là “Senior nhưng giỏi hơn”, chưa phản ánh shift về leverage và decision quality.
- Một số kỹ năng bị mô hình hóa như độc lập, trong khi thực tế competence phụ thuộc domain/context.
- Có nguy cơ khiến người đọc tối ưu “score completion” thay vì capability building.

### Staff-level judgment
Đây là file có ý tốt nhưng hơi spreadsheet-driven. Với Staff+, matrix kiểu này dễ biến thành ảo giác đo lường.

### Recommendation
Giữ matrix như appendix, nhưng phần chính nên chuyển thành observable behaviors và examples theo scope.

---

## Batch 2 synthesis

### What genuinely looks senior/staff
- [business/08_Anti_Patterns_Value_Destruction.md](../business/08_Anti_Patterns_Value_Destruction.md)
- [mindset/06_Tech_Leadership.md](../mindset/06_Tech_Leadership.md)
- [mindset/05_Day2_Operations.md](../mindset/05_Day2_Operations.md)

### What still looks more "career-content" than platform rigor
- [roadmap/01_Career_Levels.md](../roadmap/01_Career_Levels.md)
- [roadmap/02_Skills_Matrix.md](../roadmap/02_Skills_Matrix.md)

### Honest take
Repo này **không phải toàn bộ đều ở level staff**, nhưng nó **đã có vài file thật sự phát tín hiệu staff/platform tốt**. Vấn đề hiện tại không phải thiếu ambition; vấn đề là chất lượng chưa đồng đều. Những file mạnh kéo repo lên, nhưng các file framing và roadmap hơi generic lại kéo perception xuống.

---

## Recommended next files

Batch 3 nên đọc các file sau để kiểm tra execution realism:
- [fundamentals/21_Debugging_Troubleshooting.md](../fundamentals/21_Debugging_Troubleshooting.md)
- [fundamentals/24_Data_Contracts.md](../fundamentals/24_Data_Contracts.md)
- [fundamentals/22_Schema_Evolution_Migration.md](../fundamentals/22_Schema_Evolution_Migration.md)
- [projects/07_Debug_Production_Pipeline.md](../projects/07_Debug_Production_Pipeline.md)
- [projects/08_Legacy_Migration.md](../projects/08_Legacy_Migration.md)
