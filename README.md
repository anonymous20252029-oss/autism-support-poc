# Nền Tảng Số Tích Hợp Hỗ Trợ Giáo Dục Hòa Nhập Học Sinh Rối Loạn Phổ Tự Kỷ (Digital Inclusion Platform for ASD)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Dự án nghiên cứu thử nghiệm (Proof of Concept - PoC) xây dựng hệ thống phần mềm hỗ trợ quy trình phát hiện sớm, quản lý hồ sơ giáo dục cá nhân và theo dõi can thiệp học sinh rối loạn phổ tự kỷ (RLPTK) trong môi trường học đường hòa nhập.

---

## 📌 Cơ Sở Lý Luận & Khung Tham Chiếu

Mô hình hệ thống được số hóa dựa trên khung nghiên cứu tích hợp của **PGS. TS. Nguyễn Văn Tường** (Trường ĐH KHXH&NV, ĐHQG-HCM) và **TS. Lê Thị Thanh Huyền** (Trường ĐH Sư phạm TP.HCM), kết hợp các văn bản pháp quy:
- **Thông tư 11/2024/TT-BGDĐT:** Quy định vị trí việc làm Tư vấn học sinh (Đóng vai trò Điều phối & Quản lý trường hợp).
- **Thông tư 21/2023/TT-BGDĐT:** Quy định vị trí việc làm Nhân viên Hỗ trợ giáo dục người khuyết tật.
- **Khung hướng dẫn NICE (NICE Guidelines) & NHS England:** Quy trình phát hiện sớm và can thiệp đa ngành.

---

## 🔄 Chuỗi Quy Trình 6 Bước Liên Tục

Hệ thống hiện thực hóa chuỗi can thiệp khép kín:
1. **Bước 1: Tiếp nhận & Nhận diện nguy cơ:** Sàng lọc quan sát hành vi có cấu trúc (Tuyệt đối không chẩn đoán thay bác sĩ lâm sàng).
2. **Bước 2: Họp nhóm & Đánh giá nhu cầu đa nguồn:** Kết nối Nhà trường, Gia đình và Chuyên gia y tế/tâm lý.
3. **Bước 3: Lập kế hoạch cá nhân hóa (Digital IEP):** Xác lập mục tiêu SMART và các phương án điều chỉnh môi trường lớp học.
4. **Bước 4: Can thiệp trong lớp:** Sử dụng học liệu trực quan, thẻ visual timer, hỗ trợ giao tiếp AAC/PECS.
5. **Bước 5: Ghi nhận dữ liệu & Theo dõi tiến triển:** Trực quan hóa mức độ tự chủ theo thời gian thực (Time-series chart).
6. **Bước 6: Rà soát & Chuyển tiếp:** Duy trì liên tục hồ sơ hỗ trợ khi chuyển lớp hoặc chuyển cấp học.

---

## 🛠 Kiến Trúc Kỹ Thuật

- **Giao diện (Frontend/UI):** `Streamlit` (Python-based reactive web application).
- **Trực quan hóa dữ liệu (Visualization):** `Plotly Express`.
- **Cơ sở dữ liệu (Database):** `SQLite` (tích hợp sẵn phục vụ PoC/mô phỏng, sẵn sàng mở rộng sang `PostgreSQL`/`Supabase`).
- **Xử lý dữ liệu:** `Pandas`.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Demo

### 1. Chạy trên máy cục bộ (Localhost)

```bash
# Bước 1: Clone repository
git clone [https://github.com/](https://github.com/)<your-username>/autism-inclusion-poc.git
cd autism-inclusion-poc

# Bước 2: Tạo môi trường ảo (khuyến nghị)
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate

# Bước 3: Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# Bước 4: Chạy ứng dụng Streamlit
streamlit run app.py
