# Full Audit Scorecard

## Scope completed

Audit đã phủ toàn bộ nội dung chính trong [Fun](../):
- root framing docs
- folder READMEs
- all markdown files trong business, fundamentals, tools, usecases, interview, roadmap, platforms, mindset, papers, projects
- helper scripts chính

---

## Overall verdict

### Vietnamese
Repo này **có nhiều file tốt hơn mức trung bình rất nhiều**, đặc biệt ở các chủ đề production reality, debugging, schema evolution, data contracts, Staff+ leadership, và paper synthesis. Nhưng chất lượng **không đồng đều**.

Điểm mạnh nhất:
- breadth rất rộng
- nhiều file có platform instinct thật
- vài file thật sự phát tín hiệu Senior/Staff+
- papers folder mạnh hơn kỳ vọng

Điểm yếu lớn nhất:
- framing drift và overclaiming
- quá nhiều file “complete guide / SOTA / production-ready” nhưng thiếu guardrails
- một số roadmap/career content generic
- tools/usecases/platforms có drift risk rất cao vì nhiều claim theo năm, giá, version, market trend
- projects folder có một số file rất mạnh, nhưng cũng có file định nghĩa MVP không đáng tin

### Brutal one-line summary
**Đây là một knowledge base mạnh, nhưng chưa phải một source of truth đáng tin tuyệt đối. Khi repo nói về failure, operations, migration, contracts, debugging thì rất tốt. Khi repo cố dự đoán market hoặc đóng vai buyer’s guide tuyệt đối thì chất lượng giảm rõ.**

---

## Root + framing + scripts

- [README.md](../README.md) — **6.3/10** | Revise | P1 | Master index tốt nhưng credibility bị kéo xuống vì count drift và packaging mismatch.
- [MY_LEARNING_ROADMAP.md](ROADMAP.md) — **5.8/10** | Rewrite | P1 | Tone mentoring tốt nhưng drift nặng, quá dài, và trùng vai trò với repo index.
- [business/README.md](../business/README.md) — **8.0/10** | Keep | P2 | Framing business-first là đúng; cần file con giữ được depth đó.
- [fundamentals/README.md](../fundamentals/README.md) — **7.5/10** | Keep | P2 | Map tốt, hơi oversell linear curriculum.
- [projects/README.md](../projects/README.md) — **5.4/10** | Rewrite | P0 | Hứa project repo/runnable structure trong khi thực tế chủ yếu là project specs/docs.
- [tools/README.md](../tools/README.md) — **6.4/10** | Revise | P1 | Index hữu ích nhưng “SOTA 2025” làm hại shelf life.
- [usecases/README.md](../usecases/README.md) — **6.8/10** | Revise | P2 | WHAT/HOW/WHY tốt nhưng dễ bị đọc thành default prescription.
- [mindset/README.md](../mindset/README.md) — **6.9/10** | Revise | P2 | Map ổn nhưng chưa chứng minh được độ sâu Staff+ toàn folder.
- [roadmap/README.md](../roadmap/README.md) — **6.1/10** | Revise | P2 | Navigation ổn, framing Staff+ còn yếu.
- [platforms/README.md](../platforms/README.md) — **6.0/10** | Revise | P2 | Chỉ nên coi là orientation, chưa đủ để ra quyết định platform.
- [interview/README.md](../interview/README.md) — **6.7/10** | Keep | P3 | Hữu ích, ít khác biệt.
- [papers/README.md](../papers/README.md) — **7.2/10** | Good map | P2 | Nên nói rõ đây là synthesis, không phải pure paper notes.
- [convert_ascii.py](../convert_ascii.py) — **4.9/10** | Revise | P1 | Hardcoded path + rewrite in place + không có dry-run.
- [fix_mermaid.py](../fix_mermaid.py) — **5.0/10** | Revise | P1 | Hữu ích nhưng vẫn là personal maintenance script hơn shared repo tooling.
- [scripts/setup_lab1.py](../scripts/setup_lab1.py) — **6.2/10** | Keep | P3 | Ổn như lab helper, không hơn.

---

## Folder summaries

- **Business — avg ~7.6/10**: thực dụng, value-oriented, nhưng đôi lúc dùng ROI math quá gọn và evidence hơi “sạch”.
- **Mindset — avg ~7.7/10**: có vài file Staff+ rất mạnh; file yếu thì generic career advice.
- **Roadmap — avg ~6.4/10**: hữu ích cho người mới, yếu nhất về differentiation.
- **Interview — avg ~7.7/10**: practical, usable, nhưng đôi lúc hơi scripted/tool-defaulted.
- **Papers — avg ~8.6/10**: mạnh nhất toàn repo; rủi ro chính là trộn papers + docs + ecosystem synthesis.
- **Fundamentals — avg ~7.4/10**: nền tảng tốt; advanced production topics mạnh hơn mấy file primer.
- **Projects — avg ~7.0/10**: rất uneven; scenario-based files mạnh, greenfield stack-assembly files yếu hơn.
- **Tools — avg ~6.4/10**: breadth tốt, drift risk cao, market/promo tone thỉnh thoảng lộ.
- **Platforms — avg ~5.8/10**: useful orientation, yếu hơn cho strategic platform decisions.
- **Usecases — avg ~6.1/10**: tốt cho pattern recognition, rủi ro cargo-cult cao.

---

## Business

- [business/01_ROI_Cost_Optimization.md](../business/01_ROI_Cost_Optimization.md) — **7.6/10** | Keep | P1 | ROI/savings math quá tự tin so với cloud economics thực tế.
- [business/02_Data_Quality_Trust.md](../business/02_Data_Quality_Trust.md) — **8.1/10** | Keep | P1 | Gần production nhất, nhưng còn thiếu ownership models và operating cost.
- [business/03_Automation_Business_Value.md](../business/03_Automation_Business_Value.md) — **7.4/10** | Keep | P1 | Business case thuyết phục, nhưng ít nói về failure modes và change management.
- [business/04_Stakeholder_Communication.md](../business/04_Stakeholder_Communication.md) — **7.5/10** | Keep | P2 | Template tốt nhưng hơi quá clean so với friction thật.
- [business/05_Prioritization_Framework.md](../business/05_Prioritization_Framework.md) — **7.3/10** | Keep | P2 | Hơi generic PM framing, chưa đủ platform economics.
- [business/06_Impact_Case_Studies.md](../business/06_Impact_Case_Studies.md) — **7.1/10** | Revise | P1 | Số liệu đẹp nhưng khó falsify, làm yếu tín nhiệm case-study.
- [business/07_Metrics_That_Matter.md](../business/07_Metrics_That_Matter.md) — **8.0/10** | Keep | P1 | Tốt, nhưng một số metric dễ trượt thành vanity/proxy metric.
- [business/08_Anti_Patterns_Value_Destruction.md](../business/08_Anti_Patterns_Value_Destruction.md) — **8.5/10** | Keep | P2 | Rất mạnh, chỉ cần bớt absolute ở vài rule-of-thumb.

## Mindset

- [mindset/01_Design_Patterns.md](../mindset/01_Design_Patterns.md) — **8.8/10** | Keep | P1 | Pattern catalog rất mạnh; vài recipe nén trade-off hơi gọn quá.
- [mindset/02_Architectural_Thinking.md](../mindset/02_Architectural_Thinking.md) — **7.4/10** | Keep | P2 | Tốt nhưng hơi generic software advice.
- [mindset/03_Problem_Solving.md](../mindset/03_Problem_Solving.md) — **7.6/10** | Keep | P2 | Hữu ích nhưng lặp framework nhiều hơn đào sâu debugging judgment.
- [mindset/04_Career_Growth.md](../mindset/04_Career_Growth.md) — **5.9/10** | Rewrite | P0 | File generic nhất của whole audit, Staff+/platform specificity yếu.
- [mindset/05_Day2_Operations.md](../mindset/05_Day2_Operations.md) — **8.6/10** | Keep | P1 | Rất tốt, nhưng còn có thể sâu hơn về error budgets, ownership boundaries.
- [mindset/06_Tech_Leadership.md](../mindset/06_Tech_Leadership.md) — **8.7/10** | Keep | P1 | Best Staff+ file; rủi ro là reader cargo-cult template quá máy móc.

## Roadmap

- [roadmap/01_Career_Levels.md](../roadmap/01_Career_Levels.md) — **6.5/10** | Revise | P1 | Year bands universalized quá mức.
- [roadmap/02_Skills_Matrix.md](../roadmap/02_Skills_Matrix.md) — **6.8/10** | Revise | P1 | Numeric scores tạo ảo giác objectivity.
- [roadmap/03_Learning_Resources.md](../roadmap/03_Learning_Resources.md) — **6.7/10** | Revise | P2 | Curation ổn nhưng ít judgment theo context.
- [roadmap/04_Certification_Guide.md](../roadmap/04_Certification_Guide.md) — **5.8/10** | Rewrite | P0 | Commodity content, decay nhanh, Staff+ value thấp.
- [roadmap/05_Job_Search_Strategy.md](../roadmap/05_Job_Search_Strategy.md) — **6.6/10** | Revise | P1 | Tỷ lệ, salary bands, timelines false-precision.

## Interview

- [interview/01_Common_Interview_Questions.md](../interview/01_Common_Interview_Questions.md) — **7.2/10** | Keep | P1 | Nhiều answer hơi canned và tool-opinionated.
- [interview/02_SQL_Deep_Dive.md](../interview/02_SQL_Deep_Dive.md) — **8.0/10** | Keep | P1 | Tốt nhưng vẫn textbook hơn engine-specific optimizer behavior.
- [interview/03_System_Design.md](../interview/03_System_Design.md) — **8.4/10** | Keep | P1 | File interview mạnh nhất; vẫn default stack hơi nhanh.
- [interview/04_Behavioral_Questions.md](../interview/04_Behavioral_Questions.md) — **7.7/10** | Keep | P2 | STAR scaffolding tốt, dễ bị biến thành interview-robot script.
- [interview/04B_Behavioral_Questions_Intern.md](../interview/04B_Behavioral_Questions_Intern.md) — **7.9/10** | Keep | P2 | Hữu ích, hơi verbose.
- [interview/05_Coding_Test_DE.md](../interview/05_Coding_Test_DE.md) — **8.1/10** | Keep | P1 | Practical, nhưng nhiều solution ở happy-path.

## Papers

- [papers/01_Distributed_Systems_Papers.md](../papers/01_Distributed_Systems_Papers.md) — **8.7/10** | Keep | P2 | Mạnh, nhưng có lúc blur paper với later product interpretation.
- [papers/02_Stream_Processing_Papers.md](../papers/02_Stream_Processing_Papers.md) — **8.8/10** | Keep | P2 | Conceptual spine rất tốt; vài phần là ecosystem summary hơn paper analysis.
- [papers/03_Data_Warehouse_Papers.md](../papers/03_Data_Warehouse_Papers.md) — **8.2/10** | Keep | P2 | Hữu ích nhưng books/docs/papers hơi bị trộn ngang nhau.
- [papers/04_Table_Format_Papers.md](../papers/04_Table_Format_Papers.md) — **9.0/10** | Keep | P1 | Một trong các file tốt nhất repo.
- [papers/05_Consensus_Papers.md](../papers/05_Consensus_Papers.md) — **9.1/10** | Keep | P1 | Kỹ thuật rất tốt, nhưng everyday DE relevance hẹp hơn độ sâu.
- [papers/06_Database_Internals_Papers.md](../papers/06_Database_Internals_Papers.md) — **9.0/10** | Keep | P1 | Rất mạnh, cần bridge rõ hơn tới decisions hằng ngày.
- [papers/07_Data_Quality_Governance_Papers.md](../papers/07_Data_Quality_Governance_Papers.md) — **8.7/10** | Keep | P2 | Tốt, nhưng governance dễ trượt sang framework cataloging.
- [papers/08_ML_Data_Papers.md](../papers/08_ML_Data_Papers.md) — **8.5/10** | Keep | P2 | Bridge tốt sang ML platform, nhưng không phải lúc nào cũng là seminal research.
- [papers/09_Query_Optimization_Papers.md](../papers/09_Query_Optimization_Papers.md) — **8.9/10** | Keep | P1 | Hiếm có file optimizer depth tốt như vậy.
- [papers/10_Serialization_Format_Papers.md](../papers/10_Serialization_Format_Papers.md) — **8.8/10** | Keep | P2 | Concrete, useful, vẫn là synthesis hơn pure papers.

## Fundamentals

- [fundamentals/01_Data_Modeling_Fundamentals.md](../fundamentals/01_Data_Modeling_Fundamentals.md) — **8.0/10** | Keep | P2 | Tốt, nhưng hơi textbook hơn decision guide.
- [fundamentals/02_SQL_Mastery_Guide.md](../fundamentals/02_SQL_Mastery_Guide.md) — **8.0/10** | Keep | P2 | Dày và hữu ích, cần warehouse-specific trade-off rõ hơn.
- [fundamentals/03_Data_Warehousing_Concepts.md](../fundamentals/03_Data_Warehousing_Concepts.md) — **8.0/10** | Keep | P2 | Solid, có thể sắc hơn về operating constraints.
- [fundamentals/04_Data_Lakes_Lakehouses.md](../fundamentals/04_Data_Lakes_Lakehouses.md) — **8.0/10** | Keep | P2 | Comprehensive nhưng hơi vendor-format tour.
- [fundamentals/05_Distributed_Systems_Fundamentals.md](../fundamentals/05_Distributed_Systems_Fundamentals.md) — **7.0/10** | Revise | P2 | Tốt nhưng CS-generic quá cho Staff+ DE curriculum.
- [fundamentals/06_Data_Formats_Storage.md](../fundamentals/06_Data_Formats_Storage.md) — **8.0/10** | Keep | P2 | Practical, cần nói hơn về blast radius của layout tệ.
- [fundamentals/07_Batch_vs_Streaming.md](../fundamentals/07_Batch_vs_Streaming.md) — **7.0/10** | Revise | P2 | Dựa nhiều vào diagram hơn trade-offs reliability hiện đại.
- [fundamentals/08_Data_Integration_APIs.md](../fundamentals/08_Data_Integration_APIs.md) — **5.0/10** | Revise | P0 | Kitchen-sink + markdown/rendering issues làm giảm trust ngay.
- [fundamentals/09_Security_Governance.md](../fundamentals/09_Security_Governance.md) — **7.0/10** | Revise | P2 | Surface coverage ổn, opinionated controls còn yếu.
- [fundamentals/10_Cloud_Platforms.md](../fundamentals/10_Cloud_Platforms.md) — **5.0/10** | Rewrite | P1 | Vendor catalog nhiều hơn decision framework.
- [fundamentals/11_Testing_CICD.md](../fundamentals/11_Testing_CICD.md) — **8.0/10** | Keep | P2 | Mạnh, chỉ cần trim.
- [fundamentals/12_Monitoring_Observability.md](../fundamentals/12_Monitoring_Observability.md) — **8.0/10** | Keep | P2 | Tốt, cần tách rõ pipeline health với data observability.
- [fundamentals/13_Python_Data_Engineering.md](../fundamentals/13_Python_Data_Engineering.md) — **6.0/10** | Revise | P2 | Python-101 kéo tốc độ file xuống.
- [fundamentals/14_Git_Version_Control.md](../fundamentals/14_Git_Version_Control.md) — **6.0/10** | Revise | P2 | Competent nhưng off-curriculum quá nhiều.
- [fundamentals/15_Clean_Code_Data_Engineering.md](../fundamentals/15_Clean_Code_Data_Engineering.md) — **9.0/10** | Keep | P1 | Excellent nhưng quá dài để teach tốt.
- [fundamentals/16_DE_Environment_Setup.md](../fundamentals/16_DE_Environment_Setup.md) — **4.0/10** | Rewrite | P1 | Scope collapse, thiếu curation.
- [fundamentals/17_Cost_Optimization.md](../fundamentals/17_Cost_Optimization.md) — **8.0/10** | Keep | P2 | Useful; ROI neatness hơi sạch.
- [fundamentals/18_OOP_Design_Patterns.md](../fundamentals/18_OOP_Design_Patterns.md) — **7.0/10** | Keep | P2 | Practical nhưng có nguy cơ đẩy DE sang overengineering.
- [fundamentals/19_DSA_For_Data_Engineering.md](../fundamentals/19_DSA_For_Data_Engineering.md) — **7.0/10** | Keep | P2 | Pragmatic, hơi interview-tinged.
- [fundamentals/20_Networking_Protocols.md](../fundamentals/20_Networking_Protocols.md) — **7.0/10** | Keep | P2 | Hữu ích hơn kỳ vọng, vẫn broad.
- [fundamentals/21_Debugging_Troubleshooting.md](../fundamentals/21_Debugging_Troubleshooting.md) — **9.0/10** | Keep | P1 | Một trong file tốt nhất repo.
- [fundamentals/22_Schema_Evolution_Migration.md](../fundamentals/22_Schema_Evolution_Migration.md) — **9.0/10** | Keep | P1 | Signal production rất mạnh.
- [fundamentals/23_Data_Mesh_Data_Products.md](../fundamentals/23_Data_Mesh_Data_Products.md) — **9.0/10** | Keep | P1 | Mature và grounded, chỉ cần mạnh tay hơn ở “when mesh is overkill”.
- [fundamentals/24_Data_Contracts.md](../fundamentals/24_Data_Contracts.md) — **9.0/10** | Keep | P1 | Highly actionable; nên có enforcement examples sâu hơn.
- [fundamentals/25_Reverse_ETL.md](../fundamentals/25_Reverse_ETL.md) — **9.0/10** | Keep | P1 | Rất tốt, hơi centered vào Salesforce-style examples.

## Projects

- [projects/01_ETL_Pipeline.md](../projects/01_ETL_Pipeline.md) — **5.0/10** | Revise | P1 | Quá nhiều tool cho quá ít problem.
- [projects/02_Realtime_Dashboard.md](../projects/02_Realtime_Dashboard.md) — **6.0/10** | Revise | P1 | Thiếu reality về late data, replay, schema evolution.
- [projects/03_Data_Warehouse.md](../projects/03_Data_Warehouse.md) — **8.0/10** | Keep | P2 | Solid starter warehouse project.
- [projects/04_Data_Platform.md](../projects/04_Data_Platform.md) — **4.0/10** | Rewrite | P0 | “MVP” nhưng stack phình quá mức, không credible.
- [projects/05_ML_Pipeline.md](../projects/05_ML_Pipeline.md) — **7.0/10** | Revise | P2 | Good concepts, architecture hơi tutorial-simple.
- [projects/06_CDC_Pipeline.md](../projects/06_CDC_Pipeline.md) — **8.0/10** | Keep | P1 | Strong, chỉ là local complexity có thể làm learner đuối.
- [projects/07_Debug_Production_Pipeline.md](../projects/07_Debug_Production_Pipeline.md) — **9.0/10** | Keep | P1 | Standout project; nên có automated validation harness chặt hơn.
- [projects/08_Legacy_Migration.md](../projects/08_Legacy_Migration.md) — **9.0/10** | Keep | P1 | Rất realistic; rollback/cutover drill có thể sâu hơn.

## Tools

- [tools/00_SOTA_Overview_2025.md](../tools/00_SOTA_Overview_2025.md) — **4.0/10** | Revise | P1 | Maximal drift risk, maximal hype surface.
- [tools/01_Apache_Iceberg_Complete_Guide.md](../tools/01_Apache_Iceberg_Complete_Guide.md) — **7.0/10** | Keep | P2 | “Universal adoption” language overreaches.
- [tools/02_Delta_Lake_Complete_Guide.md](../tools/02_Delta_Lake_Complete_Guide.md) — **6.0/10** | Revise | P2 | Interop story sạch hơn reality.
- [tools/03_Apache_Hudi_Complete_Guide.md](../tools/03_Apache_Hudi_Complete_Guide.md) — **6.0/10** | Revise | P2 | Chưa nói rõ khi nào Hudi là wrong choice.
- [tools/04_Apache_Flink_Complete_Guide.md](../tools/04_Apache_Flink_Complete_Guide.md) — **7.0/10** | Keep | P2 | Latest-version claims dễ age badly.
- [tools/05_Apache_Kafka_Complete_Guide.md](../tools/05_Apache_Kafka_Complete_Guide.md) — **7.0/10** | Keep | P2 | “Kafka wins” hơi quá absolute.
- [tools/06_Apache_Spark_Complete_Guide.md](../tools/06_Apache_Spark_Complete_Guide.md) — **6.0/10** | Revise | P2 | Chạy theo feature chronology hơn practical boundaries.
- [tools/07_dbt_Complete_Guide.md](../tools/07_dbt_Complete_Guide.md) — **6.0/10** | Revise | P2 | Hơi product-roadmap narration.
- [tools/08_Apache_Airflow_Complete_Guide.md](../tools/08_Apache_Airflow_Complete_Guide.md) — **7.0/10** | Keep | P2 | Practical, vẫn hơi version-led.
- [tools/09_Prefect_Dagster_Complete_Guide.md](../tools/09_Prefect_Dagster_Complete_Guide.md) — **7.0/10** | Keep | P2 | Comparison hơi gọn và pricing/lifecycle claims sẽ rot nhanh.
- [tools/10_Data_Quality_Tools_Guide.md](../tools/10_Data_Quality_Tools_Guide.md) — **6.0/10** | Revise | P2 | Blur testing, observability, governance.
- [tools/11_Data_Catalogs_Guide.md](../tools/11_Data_Catalogs_Guide.md) — **4.0/10** | Rewrite | P1 | Quá rộng + exact-version/timeline claims = trust thấp.
- [tools/12_Polars_Complete_Guide.md](../tools/12_Polars_Complete_Guide.md) — **8.0/10** | Keep | P2 | Strong and grounded.
- [tools/13_DuckDB_Complete_Guide.md](../tools/13_DuckDB_Complete_Guide.md) — **8.0/10** | Keep | P2 | Excellent mental model, hơi dài.
- [tools/14_Trino_Presto_Complete_Guide.md](../tools/14_Trino_Presto_Complete_Guide.md) — **8.0/10** | Keep | P2 | Deep and useful, trim được 30%.
- [tools/15_Fivetran_Airbyte_Guide.md](../tools/15_Fivetran_Airbyte_Guide.md) — **7.0/10** | Keep | P2 | Connector counts/pricing rot nhanh.
- [tools/16_Observability_Monitoring_Tools.md](../tools/16_Observability_Monitoring_Tools.md) — **6.0/10** | Revise | P2 | Buzzword comfort hơi cao.
- [tools/17_Modern_Alternatives.md](../tools/17_Modern_Alternatives.md) — **6.0/10** | Revise | P2 | Trendy comparison, fit analysis chưa đủ rigor.
- [tools/18_Terraform_IaC_for_DE.md](../tools/18_Terraform_IaC_for_DE.md) — **8.0/10** | Keep | P2 | Practical nhất folder; AWS bias nên nói rõ.
- [tools/19_GenAI_for_DE.md](../tools/19_GenAI_for_DE.md) — **5.0/10** | Revise | P1 | Optimism outruns guardrails.

## Platforms

- [platforms/01_Databricks.md](../platforms/01_Databricks.md) — **6.0/10** | Revise | P2 | Vendor-marketing tone lộ rõ nhất.
- [platforms/02_Snowflake.md](../platforms/02_Snowflake.md) — **6.0/10** | Revise | P2 | Pricing/preview/features drift nhanh.
- [platforms/03_BigQuery.md](../platforms/03_BigQuery.md) — **8.0/10** | Keep | P2 | Strongest platform file.
- [platforms/04_Redshift.md](../platforms/04_Redshift.md) — **5.0/10** | Rewrite | P1 | Quá thin và hơi stale.
- [platforms/05_Azure_Synapse.md](../platforms/05_Azure_Synapse.md) — **4.0/10** | Rewrite | P1 | 2026 mà không đối diện Fabric thì file này lỗi chiến lược.

## Usecases

- [usecases/01_Netflix_Data_Platform.md](../usecases/01_Netflix_Data_Platform.md) — **6.0/10** | Revise | P2 | Historical vs current architecture bị blend quá casual.
- [usecases/02_Uber_Data_Platform.md](../usecases/02_Uber_Data_Platform.md) — **6.0/10** | Revise | P2 | Real-time stack bị simplified quá đẹp.
- [usecases/03_Airbnb_Data_Platform.md](../usecases/03_Airbnb_Data_Platform.md) — **6.0/10** | Revise | P2 | Old stack details thiếu time-bound caveat.
- [usecases/04_LinkedIn_Data_Platform.md](../usecases/04_LinkedIn_Data_Platform.md) — **7.0/10** | Keep | P2 | BigTech case rõ nhất, vẫn cargo-cult prone.
- [usecases/05_Spotify_Data_Platform.md](../usecases/05_Spotify_Data_Platform.md) — **6.0/10** | Revise | P2 | Narrative arc hơi frozen.
- [usecases/06_Meta_Data_Platform.md](../usecases/06_Meta_Data_Platform.md) — **6.0/10** | Revise | P2 | Nhiều mythology hơn transferable guidance.
- [usecases/07_Startup_Data_Platform.md](../usecases/07_Startup_Data_Platform.md) — **7.0/10** | Keep | P2 | Mostly sane, nhưng vẫn hơi eager to spend startup money.
- [usecases/08_Ecommerce_SME_Platform.md](../usecases/08_Ecommerce_SME_Platform.md) — **6.0/10** | Revise | P2 | Warehouse-first quá nhanh trước khi chứng minh Postgres không đủ.
- [usecases/09_SaaS_Company_Platform.md](../usecases/09_SaaS_Company_Platform.md) — **7.0/10** | Keep | P2 | Best SME file, nhưng tooling ramps with ARR hơi máy móc.
- [usecases/10_Fintech_SME_Platform.md](../usecases/10_Fintech_SME_Platform.md) — **4.0/10** | Rewrite | P1 | Compliance/security bị đối xử như checklist.
- [usecases/11_Healthcare_SME_Platform.md](../usecases/11_Healthcare_SME_Platform.md) — **5.0/10** | Revise | P1 | HIPAA guidance checklist-driven quá mức.
- [usecases/12_Manufacturing_SME_Platform.md](../usecases/12_Manufacturing_SME_Platform.md) — **7.0/10** | Keep | P2 | Domain fit ổn hơn, vẫn hơi warehouse-happy.

---

## Strongest files in the repo

1. [papers/05_Consensus_Papers.md](../papers/05_Consensus_Papers.md)
2. [papers/04_Table_Format_Papers.md](../papers/04_Table_Format_Papers.md)
3. [papers/06_Database_Internals_Papers.md](../papers/06_Database_Internals_Papers.md)
4. [papers/09_Query_Optimization_Papers.md](../papers/09_Query_Optimization_Papers.md)
5. [mindset/01_Design_Patterns.md](../mindset/01_Design_Patterns.md)
6. [mindset/06_Tech_Leadership.md](../mindset/06_Tech_Leadership.md)
7. [mindset/05_Day2_Operations.md](../mindset/05_Day2_Operations.md)
8. [fundamentals/21_Debugging_Troubleshooting.md](../fundamentals/21_Debugging_Troubleshooting.md)
9. [fundamentals/22_Schema_Evolution_Migration.md](../fundamentals/22_Schema_Evolution_Migration.md)
10. [projects/07_Debug_Production_Pipeline.md](../projects/07_Debug_Production_Pipeline.md)

## Weakest files in the repo

1. [projects/README.md](../projects/README.md)
2. [projects/04_Data_Platform.md](../projects/04_Data_Platform.md)
3. [mindset/04_Career_Growth.md](../mindset/04_Career_Growth.md)
4. [roadmap/04_Certification_Guide.md](../roadmap/04_Certification_Guide.md)
5. [fundamentals/16_DE_Environment_Setup.md](../fundamentals/16_DE_Environment_Setup.md)
6. [fundamentals/10_Cloud_Platforms.md](../fundamentals/10_Cloud_Platforms.md)
7. [tools/00_SOTA_Overview_2025.md](../tools/00_SOTA_Overview_2025.md)
8. [tools/11_Data_Catalogs_Guide.md](../tools/11_Data_Catalogs_Guide.md)
9. [platforms/05_Azure_Synapse.md](../platforms/05_Azure_Synapse.md)
10. [usecases/10_Fintech_SME_Platform.md](../usecases/10_Fintech_SME_Platform.md)

---

## Systemic issues

### P0
- Project packaging mismatch
- A few files claim credibility they do not yet earn
- Some roadmap/certification content adds volume more than signal

### P1
- Count drift / framing drift
- Exact-number / price / version / trend claims decay too fast
- Tool and platform buyer guidance is too confident in places
- Several files are too long and insufficiently curated

### P2
- BigTech cargo-cult risk in use cases
- Genericity in career content
- Repetition of Airflow + dbt + Docker + Postgres defaults
- Mixed distinction between “paper summary”, “ecosystem summary”, and “reference guide”

### P3
- Inconsistent polish and formatting
- Some helper scripts should be parameterized/tested
