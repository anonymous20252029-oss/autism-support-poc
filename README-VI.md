# Nền Tảng Số Tích Hợp Hỗ Trợ Giáo Dục Hòa Nhập Học Sinh Rối Loạn Phổ Tự Kỷ (Digital Inclusion Platform for ASD)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://autism-support-poc-brorrc4ear763c2wwdsqid.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Trải nghiệm ứng dụng trực tuyến:** [https://autism-support-poc-brorrc4ear763c2wwdsqid.streamlit.app/](https://autism-support-poc-brorrc4ear763c2wwdsqid.streamlit.app/)

Dự án nghiên cứu thử nghiệm (Proof of Concept - PoC) xây dựng hệ thống phần mềm hỗ trợ quy trình phát hiện sớm, quản lý hồ sơ giáo dục cá nhân và theo dõi can thiệp học sinh rối loạn phổ tự kỷ (RLPTK) trong môi trường học đường hòa nhập.

---

## 🌟 Điểm Nhấn Tính Năng Bản Demo (Key Features & Visualizations)

Bản demo trực quan hóa toàn diện chuỗi can thiệp và phân quyền trách nhiệm trong nhà trường:

* **Kiểm soát Truy cập Dựa trên Vai trò (RBAC System):** Mô phỏng 4 tài khoản định danh tương thích theo Thông tư 11/2024 & Thông tư 21/2023 (Giáo viên chủ nhiệm, Cán bộ Tư vấn học sinh, Nhân viên Hỗ trợ GDHN, Phụ huynh).
* **Tam giác Tích hợp & Ma trận Trách nhiệm RACI:** Trực quan hóa quy trình phối hợp khép kín giữa các lực lượng với học sinh làm trung tâm.
* **Hồ sơ Năng lực Trực quan (Student Profile Card):** Tách bạch rõ điểm mạnh, sở thích đặc biệt và các kích hoạt quá tải giác quan của từng trẻ.
* **Công cụ Can thiệp Tại lớp (Visual Support Toolbox):** Mô phỏng lịch trình bằng hình ảnh (Visual Schedule), đồng hồ đếm ngược chuyển môn và bảng tích điểm thưởng hành vi.
* **Phân tích Chuỗi Thời gian (Time-series Behavioral Tracking):** Vẽ đồ thị đa màu theo dõi mức độ độc lập của từng kỹ năng mục tiêu theo tuần kèm đường ngưỡng tự chủ.
* **Biểu đồ Radar Sẵn sàng Chuyển cấp (Transition Radar Chart):** Đo lường 5 trục kỹ năng (Giác quan, Giao tiếp, Tương tác, Tự phục vụ, Kỷ luật) trước và sau can thiệp.
* **Hộ chiếu Hòa nhập Số (Digital Inclusion Passport):** Thẻ bàn giao nhanh cho giáo viên năm học sau, nêu rõ những điều *NÊN LÀM* và *CẦN TRÁNH* để tránh sốc môi trường.

---

## 👥 Đội Ngũ & Bản Quyền Nghiên Cứu

* **Đơn vị Nghiên cứu & Phát triển Kỹ thuật (Technical Design & Implementation):**
  * **Chủ nhiệm nhóm kỹ thuật:** ThS. Võ Thị Kim Anh
  * Giảng viên Khoa Công nghệ Thông tin, Trường Đại học Tôn Đức Thắng (TDTU), Việt Nam.
  * Nghiên cứu sinh (PhD Candidate), Khoa Kỹ thuật Điện và Khoa học Máy tính (FEI), Đại học Kỹ thuật Ostrava (VSB - Technical University of Ostrava), Cộng hòa Séc.
* **Khung Nền Tảng Lý Luận (Theoretical Framework Foundation):**
  * Dựa trên mô hình tích hợp được đề xuất bởi **PGS. TS. Nguyễn Văn Tường** (Trường ĐH KHXH&NV, ĐHQG-HCM) và **TS. Lê Thị Thanh Huyền** (Trường ĐH Sư phạm TP.HCM).

---

## 📌 Cơ Sở Lý Luận & Khung Tham Chiếu

Mô hình hệ thống được số hóa bám sát khung tích hợp học đường kết hợp các văn bản pháp quy:
* **Thông tư 11/2024/TT-BGDĐT:** Vị trí việc làm Tư vấn học sinh (Điều phối & Quản lý trường hợp).
* **Thông tư 21/2023/TT-BGDĐT:** Vị trí việc làm Nhân viên Hỗ trợ giáo dục người khuyết tật (Triển khai kỹ thuật & hỗ trợ lớp học).
* **Khung hướng dẫn NICE & NHS England:** Quy trình phát hiện sớm, đánh giá và can thiệp đa ngành, liên tục.

---

## 🔄 Chuỗi Quy Trình 6 Bước Liên Tục

1. **Bước 1: Tiếp nhận & Nhận diện nguy cơ:** Sàng lọc quan sát hành vi có cấu trúc (Tuyệt đối không đưa ra chẩn đoán thay bác sĩ lâm sàng).
2. **Bước 2: Họp nhóm & Đánh giá nhu cầu đa nguồn:** Kết nối Nhà trường, Gia đình và Cơ sở y tế để xác định rào cản và thế mạnh.
3. **Bước 3: Lập kế hoạch cá nhân hóa (Digital IEP):** Thiết lập mục tiêu SMART, phân công trách nhiệm và cấu trúc điều chỉnh môi trường lớp.
4. **Bước 4: Can thiệp trong lớp:** Sử dụng công cụ trực quan, visual timer, thẻ giao tiếp AAC/PECS.
5. **Bước 5: Ghi nhận dữ liệu & Theo dõi tiến triển:** Đồ thị hóa mức độ độc lập theo chuỗi thời gian thực (Time-series chart).
6. **Bước 6: Rà soát & Chuyển tiếp:** Duy trì liên tục hồ sơ hỗ trợ, bàn giao không đứt đoạn khi chuyển lớp hoặc chuyển cấp học.

---

## 📊 Bộ Dữ Liệu Thực Nghiệm Đi Kèm (Benchmark Cases)

Hệ thống được tích hợp sẵn 6 ca lâm sàng học đường giả định chuẩn (HS-01 đến HS-06) phản ánh đầy đủ các dạng khó khăn giác quan, giao tiếp và lo âu chuyển cấp phổ biến ở bậc tiểu học.

---

## 🛠 Kiến Trúc Kỹ Thuật

* **Giao diện (Frontend/UI):** `Streamlit` (Python reactive framework).
* **Trực quan hóa dữ liệu (Visualization):** `Plotly Express` & `Plotly Graph Objects`.
* **Cơ sở dữ liệu (Database):** `SQLite` (tích hợp sẵn phục vụ PoC/mô phỏng, cấu trúc bảng chuẩn quan hệ sẵn sàng kết nối `PostgreSQL / Supabase`).
* **Xử lý dữ liệu:** `Pandas`.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Thử Nghiệm Cục Bộ

```bash
# 1. Clone repository
git clone [https://github.com/](https://github.com/)<your-username>/autism-inclusion-poc.git
cd autism-inclusion-poc

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Khởi chạy ứng dụng
streamlit run app.py
