
1. Kiến trúc của databrick chia thành 2 group là Control Plane và Data Plane (Storage & Compute). Ở lớp Data còn chia thành 2 dạng và dùng severless workspace (databricks) hoặc sử dụng classic workspace (Cloud).

2. Severlesss cũng có những lưu ý nhất định là mặc dù active rất nhanh và linh hoạt thời gian không sử dụng là nó tắt nhưng
	- Severless cho Job/Notebook . Nó hoàn toàn **Zero-config (Không cấu hình)**. Bạn **KHÔNG THỂ** chọn Size (Small/Medium), cũng **KHÔNG THỂ** cấu hình số lượng Worker (`min_workers` / `max_workers`) hay Scaling Range.
	- Serverless SQL Warehouse. Nó sinh ra để cắm vào BI tool để viết query nên để tránh viết những câu sai tốn quá nhiều tài nguyên
		- **"Size áo" (Cluster Size - Small, Medium, Large):** Đây là sức mạnh của **MỘT CỤM MÁY**. Nhưng Databricks giấu nhẹm đi việc bên trong cụm Small đó có bao nhiêu Worker Nodes hay bao nhiêu RAM. Bạn chỉ biết Small là yếu, Large là mạnh.
		- **Scaling Range (Min/Max):** Đây là **SỐ LƯỢNG CỤM MÁY**, chứ KHÔNG PHẢI số lượng Worker Nodes trong một máy.