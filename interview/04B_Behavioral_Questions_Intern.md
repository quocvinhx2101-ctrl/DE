# 🎯 Behavioral Interview Questions - Intern/Fresher Edition

> Dành cho người chưa có kinh nghiệm đi làm, chỉ có project học tập

---

## 📋 Mục Lục

1. [STAR Method cho Intern](#-star-method-cho-intern)
2. [Nguồn Stories Bạn Có Thể Dùng](#-nguồn-stories-bạn-có-thể-dùng)
3. [Technical Projects & Learning](#-technical-projects--learning)
4. [Teamwork & Collaboration](#-teamwork--collaboration)
5. [Problem Solving](#-problem-solving)
6. [Handling Difficulty](#-handling-difficulty)
7. [Why Data Engineering?](#-why-data-engineering)

---

## 📖 STAR Method cho Intern

### STAR Format (Điều chỉnh cho sinh viên)

```
S - Situation
    Thay vì "tại công ty X", bạn dùng:
    - "Trong đồ án môn học..."
    - "Trong project nhóm..."
    - "Khi tự học..."
    - "Trong cuộc thi/hackathon..."

T - Task
    Trách nhiệm cụ thể của bạn:
    - Vai trò trong nhóm?
    - Mục tiêu project?
    - Deadline?

A - Action
    Bạn đã làm gì cụ thể:
    - Các bước kỹ thuật
    - Cách phân chia công việc
    - Cách giải quyết vấn đề

R - Result
    Kết quả (không cần business metrics):
    - Điểm số / đánh giá
    - Project có chạy được không
    - Bạn học được gì
```

### Tips cho Intern

```
✅ NÊN:
- Trung thực về mức độ đóng góp (interviewer biết đâu là thật)
- Focus vào những gì BẠN làm, không phải nhóm
- Thể hiện khả năng học nhanh
- Cho thấy sự tò mò và đam mê

❌ KHÔNG:
- Bịa kinh nghiệm không có
- Nói "nhóm em làm" mà không nói rõ bạn làm gì
- Nói không biết gì - luôn có thể nói về quá trình học
- So sánh với tiêu chuẩn người đi làm 3-5 năm
```

---

## 🎯 Nguồn Stories Bạn Có Thể Dùng

### Bạn CÓ kinh nghiệm từ đâu?

| Nguồn                     | Ví dụ stories                                 |
| ------------------------- | --------------------------------------------- |
| **Đồ án môn học**         | Data warehouse, ETL pipeline, database design |
| **Project cá nhân**       | Side projects, GitHub repos                   |
| **Thực tập**              | Dù chỉ 2-3 tháng cũng là kinh nghiệm quý      |
| **Hackathon/Competition** | Cuộc thi data, coding challenges              |
| **Học online**            | Coursera projects, Kaggle notebooks           |
| **Làm nhóm**              | Bất kỳ teamwork nào                           |
| **Research**              | Đề tài nghiên cứu, thesis                     |

### Story Bank - Chuẩn bị 5-7 stories

```
Story 1: Technical project lớn nhất
Story 2: Khi làm việc nhóm hiệu quả
Story 3: Khi gặp khó khăn và vượt qua
Story 4: Khi phải học thứ mới rất nhanh
Story 5: Khi có xung đột/bất đồng với ai đó
Story 6: Khi thất bại và bài học rút ra
Story 7: Khi giúp đỡ người khác
```

---

## 💻 Technical Projects & Learning

### Q1: "Tell me about a technical project you've worked on"

**Sample Answer - Đồ án môn học:**

```
Situation:
"Trong môn Data Warehouse ở năm 4, nhóm 4 người được giao 
xây dựng hệ thống phân tích bán hàng từ dữ liệu e-commerce."

Task:
"Em phụ trách phần ETL pipeline - lấy data từ CSV files, 
transform, và load vào PostgreSQL warehouse. Deadline 8 tuần."

Action:
"1. Tuần 1-2: Research về ETL patterns, học pandas và SQL
2. Tuần 3-4: Thiết kế schema star với 1 fact table, 4 dimensions
3. Tuần 5-6: Code pipeline bằng Python:
   - Extract từ 5 CSV files (~500K records)
   - Transform: làm sạch data, xử lý missing values, tính metrics
   - Load vào PostgreSQL warehouse
4. Tuần 7: Debug vấn đề duplicate records (do không có unique key)
5. Tuần 8: Thuyết trình và demo"

Result:
"- Pipeline xử lý 500K records trong 5 phút
- Điểm đồ án: 9/10
- Bản thân học được: pandas, SQL optimization, và debug data issues
- Code được push lên GitHub (link: github.com/...)"
```

### Q2: "What made you interested in Data Engineering?"

**Sample Answer:**

```
Situation:
"Em bắt đầu học data science vì thấy nó 'hot', nhưng trong quá 
trình làm project Kaggle, em nhận ra một insight quan trọng."

Realization:
"Model accuracy phụ thuộc rất nhiều vào data quality. 
Em mất 80% thời gian làm sạch data, chỉ 20% làm model.
Và em thấy phần data cleaning thú vị hơn phần model!"

Why DE specifically:
"1. Em thích solve problems có tính hệ thống
2. Em thích build infrastructure hơn one-off analysis
3. Em thấy DE là 'invisible hero' - không có DE tốt, không có AI gì cả
4. Em thích nghĩ về scale và performance"

What I've done:
"Sau khi nhận ra điều này, em đã:
- Tự học Python cho DE (không phải DS)
- Làm ETL project với Airflow
- Đọc blog của Netflix, Uber về data platform
- Xây dựng portfolio trên GitHub"
```

### Q3: "Tell me about a technology you learned on your own"

**Sample Answer:**

```
Situation:
"Sau khi học môn database, em muốn hiểu thêm về tools 
thực tế mà doanh nghiệp dùng. Em chọn học Apache Airflow."

Task:
"Tự học đủ để build 1 project hoàn chỉnh trong 1 tháng."

Action:
"1. Tuần 1: Đọc official docs, xem YouTube tutorials
2. Tuần 2: Cài local bằng Docker, follow tutorials
3. Tuần 3: Gặp vấn đề - DAG không hiện, lỗi dependency
   - Debug bằng cách đọc logs
   - Hỏi trên Stack Overflow
   - Join Airflow Slack community
4. Tuần 4: Build ETL project hoàn chỉnh
   - DAG lấy data từ API mỗi ngày
   - Transform và load vào SQLite
   - Set up error handling và alerts"

Result:
"- Có 1 project Airflow trên GitHub
- Hiểu workflow orchestration là gì
- Học được cách đọc docs và debug độc lập
- Tự tin hơn khi approach công nghệ mới"
```

---

## 🤝 Teamwork & Collaboration

### Q4: "Tell me about a time you worked effectively in a team"

**Sample Answer:**

```
Situation:
"Đồ án môn Software Engineering, nhóm 5 người xây dựng 
web app trong 10 tuần. Em chưa quen 4 người còn lại."

Task:
"Phụ trách backend API và database. Cần coordinate 
với frontend và mobile team."

Action:
"1. Tuần đầu: Tổ chức meeting định nghĩa API contract
   - Document rõ endpoints, request/response format
   - Dùng Swagger để mọi người có thể test
2. Hàng tuần: Daily standup 15 phút qua Discord
3. Khi frontend cần field mới:
   - Thay vì chỉnh sửa ngay, hỏi 'use case là gì?'
   - Đôi khi tìm ra cách tốt hơn không cần thay đổi API
4. Dùng Git branches - không push trực tiếp main
5. Code review lẫn nhau trước khi merge"

Result:
"- Không có conflict nào giữa backend và frontend
- Team mình deliver đúng hạn (nhiều nhóm khác delay)
- Được thầy khen phần documentation tốt
- Vẫn giữ liên lạc với team sau môn học"
```

### Q5: "Describe a conflict you had with a teammate"

**Sample Answer:**

```
Situation:
"Trong đồ án database design, một thành viên muốn dùng 
MongoDB vì 'flexible hơn'. Em nghĩ PostgreSQL phù hợp hơn."

Task:
"Cần quyết định database trong tuần đầu để kịp deadline."

Action:
"1. Thay vì tranh cãi, em hỏi: 'Tại sao bạn thấy MongoDB tốt hơn?'
   - Bạn ấy nói: schema sẽ thay đổi nhiều
2. Em share quan điểm của mình:
   - Use case của mình cần nhiều JOINs (relational)
   - Team quen SQL hơn NoSQL
   - Đồ án cần demo query performance
3. Đề xuất: 'Hay mình list ra requirements rồi so sánh?'
4. Cùng nhau làm bảng so sánh 10 phút
5. Kết luận: PostgreSQL fit hơn cho đồ án này"

Result:
"- Chọn PostgreSQL, project chạy tốt
- Quan trọng hơn: bạn ấy không 'thua', mà cùng đi đến kết luận
- Học được: Đừng tranh cãi, hãy so sánh dựa trên facts"
```

### Q6: "How do you handle different opinions in a team?"

```
Framework tôi dùng:

1. LISTEN FIRST
   - Hiểu tại sao họ nghĩ như vậy
   - Hỏi "Can you help me understand your perspective?"

2. ACKNOWLEDGE
   - "Đó là điểm tốt, tôi chưa nghĩ đến"
   - Người ta sẽ open hơn nếu thấy mình lắng nghe

3. SHARE PERSPECTIVE
   - "Đây là những gì tôi đang nghĩ..."
   - Không phải "bạn sai" mà là "thêm một góc nhìn"

4. DECIDE TOGETHER
   - So sánh dựa trên criteria rõ ràng
   - Nếu không thống nhất, để người có nhiều context nhất quyết định
```

---

## 🔧 Problem Solving

### Q7: "Tell me about a difficult problem you solved"

**Sample Answer - Debugging:**

```
Situation:
"Trong đồ án, pipeline ETL của em đột nhiên tạo ra 
duplicate records - 500K thành 700K rows."

Task:
"Tìm ra nguyên nhân và fix trước demo vào tuần sau."

Action:
"1. Đầu tiên: Panic 😅 - không biết bắt đầu từ đâu
2. Bình tĩnh lại, chia nhỏ vấn đề:
   - Check source data: OK, 500K records
   - Check sau mỗi transform step
3. Phát hiện: Duplicate xuất hiện sau bước JOIN
   - JOIN với bảng có duplicate keys
4. Root cause:
   - Bảng lookup 'categories' có duplicate category_id
   - Mỗi product JOIN với 2 categories → double rows
5. Fix:
   - Deduplicate bảng lookup trước khi JOIN
   - Thêm check row count sau mỗi step"

Result:
"- Fix trong 2 ngày
- Demo thành công
- Học được: Luôn validate row count sau mỗi transformation
- Thêm assertion vào code để catch sớm"
```

### Q8: "How do you approach learning something new?"

```
My Learning Framework:

1. BIG PICTURE (1-2 hours)
   - Đọc overview: tool này làm gì, dùng ở đâu
   - Xem 1 video tổng quan 30 phút
   - Hiểu TẠI SAO trước KHI LÀM SAO

2. HANDS-ON (2-3 days)
   - Follow official tutorial
   - Gõ code, KHÔNG copy-paste
   - Break things intentionally, learn from errors

3. BUILD SOMETHING (1-2 weeks)
   - Apply vào project thực tế của mình
   - Gặp vấn đề → Search → Hỏi community
   - Document những gì học được

4. TEACH/SHARE
   - Viết blog hoặc README
   - Giải thích cho bạn bè
   - Dạy để học sâu hơn

Example:
Học Docker theo framework này trong 2 tuần, từ không biết gì 
đến containerize được project đồ án.
```

---

## 💥 Handling Difficulty

### Q9: "Tell me about a time you failed"

**Sample Answer:**

```
Situation:
"Đồ án đầu tiên về data, em tự tin estimate 2 tuần. 
Thực tế mất 5 tuần và điểm bị trừ vì nộp muộn."

What Went Wrong:
"1. Underestimate cleaning data (mất 2 tuần thay vì 2 ngày)
2. Không có backup plan khi gặp vấn đề
3. Không hỏi sớm khi stuck"

Failure:
"Nộp muộn 1 tuần, bị trừ 1 điểm (từ 9 xuống 8)."

What I Learned:
"1. Data quality issues LUÔN tốn thời gian hơn dự kiến
2. Estimate xong thì nhân 2, thậm chí 3
3. Stuck quá 2 giờ → Hỏi, đừng tự mò
4. Chia nhỏ task, commit thường xuyên

Applied:
Đồ án sau, em estimate x2 và check-in với nhóm hàng ngày.
Kết quả: Deliver đúng hạn, điểm 9.5."
```

### Q10: "Tell me about a time you were under pressure"

**Sample Answer:**

```
Situation:
"Final semester, deadline 3 đồ án lớn trong cùng 1 tuần. 
Một môn là Database, một là ML, một là Software Engineering."

Task:
"Hoàn thành cả 3 với chất lượng chấp nhận được."

Action:
"1. Không panic (okay, panic 1 ngày rồi bình tĩnh lại)
2. Ưu tiên: Xếp theo deadline và trọng số điểm
3. Time blocking:
   - Sáng: Database (khó nhất, cần clarity)
   - Chiều: SE (teamwork, có thể parallel)
   - Tối: ML (familiar hơn, làm nhanh hơn)
4. Scope management:
   - Database: Làm core features, skip nice-to-have
   - ML: Dùng simpler model, focus documentation
5. Sleep: Vẫn ngủ 6 tiếng/đêm (no all-nighters)
6. Exercise: 30 phút đi bộ mỗi ngày để giữ sáng suốt"

Result:
"- Cả 3 submit đúng hạn
- Điểm: 8.5, 8, 9
- Học được: Planning > Working harder
- Không burnout, vẫn có thể học tiếp tuần sau"
```

---

## 🎯 Why Data Engineering?

### Q11: "Why do you want to be a Data Engineer?"

```
Framework:

1. HOW YOU DISCOVERED DE
   - Từ đâu biết nghề này
   - Moment "aha" khi nhận ra DE phù hợp

2. WHAT YOU LIKE ABOUT IT
   - Technical aspects
   - Problem types
   - Impact potential

3. WHAT YOU'VE DONE TO PREPARE
   - Projects
   - Learning
   - Research

4. HOW IT FITS YOUR STRENGTHS
   - Personality traits
   - Technical skills
   - Career goals
```

**Sample Answer:**

```
How I Discovered:
"Bắt đầu học Data Science, nhưng trong quá trình làm 
Kaggle, em nhận ra em thích phần data preparation hơn modeling.
Em google 'who builds data pipelines' → Data Engineer."

What I Like:
"1. Problem solving có tính hệ thống
   - Không phải ad-hoc analysis, mà build system đúng 1 lần, chạy lâu dài
2. Infrastructure mindset
   - Thà spend 1 tuần automate hơn là làm tay 5 phút mỗi ngày
3. Visible impact
   - Pipeline em build sẽ được dùng bởi cả team

What I've Done:
"- 3 projects ETL trên GitHub
- Tự học Airflow, dbt
- Đọc engineering blog của Netflix, Uber
- Học SQL nâng cao (window functions, CTEs)"

Why It Fits Me:
"Em thích optimize, thích systems thinking, và thích 
làm nền tảng cho người khác build tiếp.
DE dường như là intersection of những thứ em thích."
```

### Q12: "Where do you see yourself in 3-5 years?"

**Sample Answer:**

```
"Trong 1-2 năm đầu:
- Master các fundamentals: SQL thật tốt, Python production-ready
- Hiểu sâu 1 stack (ví dụ: Airflow + dbt + Snowflake)
- Build trust qua việc deliver reliably

Năm 2-3:
- Bắt đầu handle bigger projects độc lập
- Học distributed systems (Spark, Kafka)
- Bắt đầu mentor juniors mới vào

Năm 3-5:
- Lead technical decisions cho team
- Design systems, không chỉ implement
- Contribute to data strategy

Điều em KHÔNG muốn:
- Đừng bị stuck ở level làm task được assign mãi
- Muốn grow về cả technical depth và impact"
```

---

## 📝 Questions for INTERN to Ask Interviewer

### Câu hỏi thể hiện sự tò mò đúng mực

```
About the team:
- "Tech stack hiện tại của team là gì?"
- "Data pipeline hiện xử lý bao nhiêu data/ngày?"
- "Team dùng gì để orchestrate? (Airflow? Dagster?)"

About learning:
- "Intern sẽ được mentor như thế nào?"
- "Có code review process không?"
- "Onboarding cho intern như thế nào?"

About growth:
- "Path từ Intern → Junior như thế nào?"
- "Có conversion rate từ intern thành full-time không?"
- "Team có culture chia sẻ kiến thức không?"

About the work:
- "Project đầu tiên intern thường làm là gì?"
- "Intern có opportunity contribute vào production không?"
- "Có expectation cụ thể nào cho intern không?"
```

---

## 📋 Quick Reference - Intern Edition

### Chuẩn bị trước phỏng vấn

```
[ ] 5-7 stories sẵn sàng (STAR format)
[ ] GitHub profile clean và có projects
[ ] Biết rõ từng line code trong project của mình
[ ] Research về công ty và tech stack họ dùng
[ ] Chuẩn bị 3-5 câu hỏi cho interviewer
[ ] Practice trả lời trước gương hoặc với bạn
```

### Thể hiện ĐÚNG mindset

```
Intern không cần:
- 5 năm experience
- Biết hết mọi thứ
- Dẫn dắt team

Intern CẦN thể hiện:
- Eagerness to learn
- Ability to figure things out
- Good communication
- Self-awareness (biết cái mình chưa biết)
- Curiosity và passion

Power phrases:
- "Tôi chưa có kinh nghiệm production, nhưng tôi đã..."
- "Tôi học được điều này từ project..."
- "Khi gặp vấn đề này, tôi đã tự research và..."
- "Đây là area tôi muốn develop thêm..."
```

---

## 🔗 Liên Kết

- [Behavioral Questions - Người có kinh nghiệm](04_Behavioral_Questions.md)
- [Common Interview Questions](01_Common_Interview_Questions.md)
- [SQL Deep Dive](02_SQL_Deep_Dive.md)
- [Coding Test DE](05_Coding_Test_DE.md)

---

*Dành cho: Intern, Fresher, hoặc người chuyển ngành*
*Cập nhật: February 2026*
