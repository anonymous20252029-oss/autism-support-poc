import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import date, timedelta

# ==========================================
# CƠ SỞ DỮ LIỆU & NẠP DỮ LIỆU GIẢ ĐỊNH (SEED DATA)
# ==========================================
def get_db():
    conn = sqlite3.connect("autism_inclusion_poc.db", check_same_thread=False)
    return conn

def init_and_seed_db():
    conn = get_db()
    c = conn.cursor()
    
    # 1. Bảng người dùng hệ thống (RBAC)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        full_name TEXT,
        role TEXT,
        assigned_scope TEXT
    )''')
    
    # 2. Bảng học sinh
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        alias_name TEXT,
        grade TEXT,
        strengths TEXT,
        challenges TEXT,
        accommodations TEXT
    )''')
    
    # 3. Bảng tiếp nhận & sàng lọc (Bước 1)
    c.execute('''CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        reporter_username TEXT,
        reporter_role TEXT,
        context TEXT,
        indicators_count INTEGER,
        concern_note TEXT,
        risk_level TEXT,
        created_at DATE
    )''')
    
    # 4. Bảng kế hoạch IEP (Bước 2 & 3)
    c.execute('''CREATE TABLE IF NOT EXISTS iep_plans (
        plan_id TEXT PRIMARY KEY,
        student_id TEXT,
        target_skill TEXT,
        strategy TEXT,
        lead_role TEXT,
        approved_by TEXT,
        status TEXT
    )''')
    
    # 5. Bảng nhật ký tiến triển (Bước 4 & 5)
    c.execute('''CREATE TABLE IF NOT EXISTS progress_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id TEXT,
        student_id TEXT,
        logged_by TEXT,
        record_date DATE,
        target_skill TEXT,
        score INTEGER,
        notes TEXT
    )''')
    
    # 6. Bảng chuyển tiếp (Bước 6)
    c.execute('''CREATE TABLE IF NOT EXISTS transition_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        reviewer_username TEXT,
        review_date DATE,
        summary TEXT,
        transition_plan TEXT
    )''')
    
    # Nạp người dùng mẫu
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        mock_users = [
            ("gv_lan", "Cô Hoàng Lan", "Giáo viên chủ nhiệm / Bộ môn", "Khối 1, 2, 3, 4, 5"),
            ("tv_nam", "Thầy Trần Nam", "Cán bộ Tư vấn học sinh (Điều phối)", "Toàn trường (Điều phối ca)"),
            ("ht_minh", "Thầy Lê Minh", "Nhân viên Hỗ trợ GD Người khuyết tật", "Chuyên trách can thiệp chuyên biệt"),
            ("ph_huong", "Mẹ bé M.K (Chị Hương)", "Phụ huynh học sinh", "Theo dõi HS-01")
        ]
        c.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", mock_users)
    
    # Nạp 6 ca học sinh chuẩn
    c.execute("SELECT COUNT(*) FROM students")
    if c.fetchone()[0] == 0:
        mock_students = [
            ("HS-01", "Bé M.K", "Lớp 1", "Nhớ mặt chữ/số rất nhanh, thích xếp hình", "Nhạy cảm âm thanh lớn (tiếng chuông), bùng nổ khi đổi tiết", "Tai nghe chống ồn, đồng hồ đếm ngược báo trước 5 phút"),
            ("HS-02", "Bé T.A", "Lớp 2", "Rất yêu thích động vật, nhớ quy tắc lớp học", "Khó khăn tương tác bạn bè, thường thu mình trong giờ chơi", "Sắp xếp bạn ghép đôi hòa nhã (peer buddy) giờ ra chơi"),
            ("HS-03", "Bé H.N", "Lớp 3", "Tập trung chi tiết cao, tính toán nhẩm nhanh", "Quá tải giác quan khi ồn ào, tự cào tay khi bối rối", "Thẻ xin nghỉ 3 phút, góc thư giãn giác quan ở cuối lớp"),
            ("HS-04", "Bé Đ.P", "Lớp 1", "Vận động tinh khéo léo, xếp lego giỏi", "Ngôn ngữ nói hạn chế, dễ cáu gắt khi không diễn đạt được", "Bảng giao tiếp biểu tượng PECS dán tại góc bàn"),
            ("HS-05", "Bé Q.L", "Lớp 4", "Hiểu ngôn ngữ viết tốt, tính kỷ luật cao", "Không hiểu hàm ý, lúng túng khi làm việc nhóm không rõ thứ tự", "Chia nhỏ nhiệm vụ thành checklist văn bản cụ thể"),
            ("HS-06", "Bé V.H", "Lớp 5", "Trí nhớ không gian tốt, biết lập trình Scratch", "Lo âu cao độ về chuyển tiếp lên cấp 2 (thay đổi giáo viên)", "Tập dượt trước lịch trình lớp 6, làm bảng tự giới thiệu điểm mạnh")
        ]
        c.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", mock_students)
        
        # Kế hoạch IEP
        mock_ieps = [
            ("IEP-01", "HS-01", "Chuyển tiết học mà không la hét", "Dùng thẻ hình trực quan trước 5 phút", "Nhân viên Hỗ trợ GD Người khuyết tật", "tv_nam", "Đã phê duyệt"),
            ("IEP-02", "HS-02", "Chủ động mời bạn cùng chơi 1 lần/ngày", "Tập dượt mẫu câu xin chơi cùng với bạn buddy", "Giáo viên chủ nhiệm / Bộ môn", "tv_nam", "Đã phê duyệt"),
            ("IEP-03", "HS-03", "Chủ động giơ thẻ 'Xin nghỉ' khi căng thẳng", "Nhắc nhở kín đáo khi thấy học sinh bắt đầu gõ bàn", "Cán bộ Tư vấn học sinh (Điều phối)", "tv_nam", "Đang thực hiện"),
            ("IEP-04", "HS-04", "Dùng thẻ PECS yêu cầu đồ dùng học tập", "Khen thưởng tức thì khi bé chỉ vào biểu tượng", "Nhân viên Hỗ trợ GD Người khuyết tật", "tv_nam", "Đã phê duyệt"),
            ("IEP-05", "HS-05", "Hoàn thành nhiệm vụ nhóm theo checklist", "Giao vai trò cụ thể: người ghi chép kết quả", "Giáo viên chủ nhiệm / Bộ môn", "tv_nam", "Đang thực hiện"),
            ("IEP-06", "HS-06", "Giảm thang điểm lo âu chuyển cấp", "Tham quan trường THCS trước kỳ nghỉ hè", "Cán bộ Tư vấn học sinh (Điều phối)", "tv_nam", "Chờ họp duyệt")
        ]
        c.executemany("INSERT INTO iep_plans VALUES (?, ?, ?, ?, ?, ?, ?)", mock_ieps)

        # Dữ liệu tiến triển 4 tuần
        today = date.today()
        mock_logs = []
        for week in range(4):
            d = today - timedelta(days=(3 - week) * 7)
            mock_logs.append(("IEP-01", "HS-01", "ht_minh", d, "Chuyển tiết học mà không la hét", 1 + week, f"Tuần {week+1}: Giảm đáng kể thời lượng khóc khi đổi tiết"))
            mock_logs.append(("IEP-02", "HS-02", "gv_lan", d, "Chủ động mời bạn cùng chơi 1 lần/ngày", 2 + (1 if week >= 2 else 0), f"Tuần {week+1}: Đã bắt đầu đứng gần nhóm bạn"))
            mock_logs.append(("IEP-03", "HS-03", "tv_nam", d, "Chủ động giơ thẻ 'Xin nghỉ' khi căng thẳng", min(5, 2 + week), f"Tuần {week+1}: Tự giác đi về góc yên tĩnh"))
        c.executemany("INSERT INTO progress_logs (plan_id, student_id, logged_by, record_date, target_skill, score, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", mock_logs)

        # Sàng lọc
        mock_screenings = [
            ("HS-01", "gv_lan", "Giáo viên chủ nhiệm / Bộ môn", "Lúc chuyển tiết", 3, "Bé thường bịt tai và hét lớn khi chuông reo đổi môn", "Cần đánh giá chuyên sâu", today - timedelta(days=35)),
            ("HS-02", "ph_huong", "Phụ huynh học sinh", "Giờ ra chơi", 2, "Ở nhà bé ít chơi với anh em họ, chỉ xếp thú bông thẳng hàng", "Cần theo dõi thêm", today - timedelta(days=40))
        ]
        c.executemany("INSERT INTO screenings (student_id, reporter_username, reporter_role, context, indicators_count, concern_note, risk_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", mock_screenings)

        # Chuyển tiếp
        c.execute("""INSERT INTO transition_reviews (student_id, reviewer_username, review_date, summary, transition_plan) 
                     VALUES ('HS-06', 'tv_nam', ?, 'Đạt mục tiêu tiểu học, kỹ năng CNTT xuất sắc', 'Gửi hồ sơ IEP tóm tắt cho BGH trường THCS tiếp nhận')""", (str(today),))
        
    conn.commit()
    conn.close()

init_and_seed_db()

# ==========================================
# THIẾT LẬP GIAO DIỆN & PHÂN QUYỀN
# ==========================================
st.set_page_config(page_title="Nền tảng Hỗ trợ Hòa nhập Học sinh RLPTK", layout="wide", page_icon="🏫")
conn = get_db()

# Cấu hình phân quyền (RBAC)
ROLE_PERMISSIONS = {
    "Giáo viên chủ nhiệm / Bộ môn": {
        "can_edit_student": False,
        "can_create_iep": False,
        "can_approve": False,
        "can_trans": False,
        "desc": "Theo dõi hàng ngày, phát hiện sớm dấu hiệu nguy cơ, thực hiện can thiệp và chấm điểm tiến triển trong giờ học."
    },
    "Cán bộ Tư vấn học sinh (Điều phối)": {
        "can_edit_student": True,
        "can_create_iep": True,
        "can_approve": True,
        "can_trans": True,
        "desc": "Đầu mối điều phối ca, tạo/sửa hồ sơ học sinh, kích hoạt họp nhóm, phê duyệt IEP và chủ trì bàn giao chuyển tiếp."
    },
    "Nhân viên Hỗ trợ GD Người khuyết tật": {
        "can_edit_student": True,
        "can_create_iep": True,
        "can_approve": False,
        "can_trans": False,
        "desc": "Chuyên trách thiết lập mục tiêu kỹ thuật, tài liệu học tập trực quan và cùng giáo viên ghi nhận tiến triển."
    },
    "Phụ huynh học sinh": {
        "can_edit_student": False,
        "can_create_iep": False,
        "can_approve": False,
        "can_trans": False,
        "desc": "Cung cấp thông tin quan sát tại nhà, đồng thuận kế hoạch và theo dõi đồ thị tiến bộ của con."
    }
}

# Sidebar - Quản lý tài khoản
st.sidebar.title("HỆ THỐNG HÒA NHẬP")
st.sidebar.caption("Chuyển đổi số theo TT 11/2024 & TT 21/2023")

users_df = pd.read_sql("SELECT * FROM users", conn)
user_dict = {f"{r['full_name']} ({r['role']})": r['username'] for _, r in users_df.iterrows()}

selected_user_display = st.sidebar.selectbox("👤 Đăng nhập tài khoản:", list(user_dict.keys()))
current_username = user_dict[selected_user_display]
current_user_row = users_df[users_df['username'] == current_username].iloc[0]
current_role = current_user_row['role']

st.sidebar.markdown(f"**Vai trò:** `{current_role}`")
st.sidebar.info(f"📌 **Nhiệm vụ:** {ROLE_PERMISSIONS[current_role]['desc']}")

# Chế độ hiển thị: Luôn cho phép duyệt tất cả các bước (đầy đủ như phiên bản gốc)
show_all_menu = st.sidebar.checkbox("Hiển thị đầy đủ tất cả các bước", value=True)

all_steps = [
    "Sơ đồ Mô phỏng & Tổng quan",
    "1. Tiếp nhận & Nhận diện nguy cơ",
    "2. Hồ sơ Học sinh & Đánh giá nhu cầu",
    "3. Kế hoạch Cá nhân hóa (Digital IEP)",
    "4. Nhật ký Can thiệp & Biểu đồ tiến triển",
    "5. Rà soát & Chuyển tiếp",
    "📊 Báo cáo Dữ liệu & Mô phỏng"
]

if show_all_menu:
    menu_options = all_steps
else:
    # Lọc các bước phù hợp vai trò
    allowed = ["Sơ đồ Mô phỏng & Tổng quan", "1. Tiếp nhận & Nhận diện nguy cơ", "4. Nhật ký Can thiệp & Biểu đồ tiến triển", "📊 Báo cáo Dữ liệu & Mô phỏng"]
    if ROLE_PERMISSIONS[current_role]["can_create_iep"] or ROLE_PERMISSIONS[current_role]["can_edit_student"]:
        allowed.extend(["2. Hồ sơ Học sinh & Đánh giá nhu cầu", "3. Kế hoạch Cá nhân hóa (Digital IEP)"])
    if ROLE_PERMISSIONS[current_role]["can_trans"]:
        allowed.append("5. Rà soát & Chuyển tiếp")
    menu_options = [s for s in all_steps if s in allowed]

step = st.sidebar.radio("Quy trình nghiệp vụ:", menu_options)

st.sidebar.divider()
st.sidebar.markdown("""
<div style='font-size:12px; color:gray;'>
<b>Nhóm Kỹ thuật:</b> ThS. Võ Thị Kim Anh (TDTU & FEI/VSB)<br>
<b>Cơ sở Lý luận:</b> PGS.TS. Nguyễn Văn Tường & TS. Lê Thị Thanh Huyền
</div>
""", unsafe_allow_html=True)

# ==========================================
# SƠ ĐỒ MÔ PHỎNG HÌNH ẢNH TRỰC QUAN
# ==========================================
if step == "Sơ đồ Mô phỏng & Tổng quan":
    st.header("Sơ Đồ Mô Phỏng Chuỗi 6 Bước Liên Tục & Trách Nhiệm Phối Hợp")
    st.write("Mô hình tích hợp số hóa kết nối chặt chẽ **Dữ liệu – Con người – Trách nhiệm** trong môi trường học đường:")
    
    col_steps = st.columns(6)
    step_metadata = [
        ("1. Tiếp nhận", "Giáo viên / Phụ huynh", "Ghi nhận lo ngại có cấu trúc", "#E0F2FE", "#0369A1"),
        ("2. Đánh giá", "Cán bộ TVHS & Nhóm", "Họp nhóm, đánh giá đa nguồn", "#FEF3C7", "#B45309"),
        ("3. Lập IEP", "Nhân viên GDHN & GV", "Mục tiêu SMART & điều chỉnh", "#DCFCE7", "#15803D"),
        ("4. Can thiệp", "GV bộ môn / GDHN", "Visual support, lịch trình", "#F3E8FF", "#7E22CE"),
        ("5. Theo dõi", "Đa lực lượng", "Chấm điểm độc lập định kỳ", "#FCE7F3", "#BE185D"),
        ("6. Chuyển tiếp", "Cán bộ TVHS & BGH", "Bàn giao năm học/cấp học", "#E2E8F0", "#334155")
    ]
    
    for i, (title, owner, note, bg, fg) in enumerate(step_metadata):
        with col_steps[i]:
            st.markdown(f"""
            <div style="background-color:{bg}; border-left: 4px solid {fg}; padding:10px; border-radius:6px; min-height:140px;">
                <b style="color:{fg}; font-size:14px;">{title}</b><br>
                <small style="color:#1E293B;"><b>Phụ trách:</b> {owner}</small><br>
                <p style="font-size:11px; color:#475569; margin-top:5px;">{note}</p>
            </div>
            """, unsafe_allow_html=True)
            
    st.write("")
    st.subheader("Ma Trận Trách Nhiệm Nghiệp Vụ (RACI Matrix)")
    raci_data = pd.DataFrame([
        {"Bước nghiệp vụ": "Bước 1: Sàng lọc & Tiếp nhận lo ngại", "GV Chủ nhiệm": "Chủ trì (R)", "Tư vấn HS": "Phối hợp (C)", "NV Hỗ trợ GDHN": "Tham vấn (I)", "Phụ huynh": "Đồng thuận (A)"},
        {"Bước nghiệp vụ": "Bước 2: Họp nhóm & Đánh giá nhu cầu", "GV Chủ nhiệm": "Tham gia (C)", "Tư vấn HS": "Chủ trì (R)", "NV Hỗ trợ GDHN": "Phối hợp (C)", "Phụ huynh": "Tham gia (C)"},
        {"Bước nghiệp vụ": "Bước 3: Lập kế hoạch cá nhân (IEP)", "GV Chủ nhiệm": "Phối hợp (C)", "Tư vấn HS": "Phê duyệt (A)", "NV Hỗ trợ GDHN": "Xây dựng (R)", "Phụ huynh": "Ký duyệt (A)"},
        {"Bước nghiệp vụ": "Bước 4: Can thiệp ngay tại lớp", "GV Chủ nhiệm": "Thực hiện (R)", "Tư vấn HS": "Giám sát (A)", "NV Hỗ trợ GDHN": "Trợ giảng (R)", "Phụ huynh": "Hỗ trợ nhà (C)"},
        {"Bước nghiệp vụ": "Bước 5: Ghi nhận & Theo dõi tiến triển", "GV Chủ nhiệm": "Chấm điểm (R)", "Tư vấn HS": "Theo dõi (A)", "NV Hỗ trợ GDHN": "Ghi chép (R)", "Phụ huynh": "Theo dõi (I)"},
        {"Bước nghiệp vụ": "Bước 6: Rà soát & Chuyển tiếp cấp học", "GV Chủ nhiệm": "Bàn giao (C)", "Tư vấn HS": "Chủ trì (R)", "NV Hỗ trợ GDHN": "Tổng kết (C)", "Phụ huynh": "Đồng hành (C)"}
    ])
    st.dataframe(raci_data, use_container_width=True, hide_index=True)
    st.caption("*(R: Responsible - Thực hiện | A: Accountable - Phê duyệt | C: Consulted - Tham vấn | I: Informed - Nhận thông tin)*")

# ==========================================
# BƯỚC 1: TIẾP NHẬN & NHẬN DIỆN NGUY CƠ
# ==========================================
elif step == "1. Tiếp nhận & Nhận diện nguy cơ":
    st.header("Bước 1: Tiếp nhận lo ngại & Nhận diện có cấu trúc")
    st.warning("⚠️ **Nguyên tắc đạo đức dữ liệu:** Bảng kiểm chỉ hỗ trợ nhận diện sơ bộ dấu hiệu cần đánh giá thêm, tuyệt đối **không đưa ra kết luận chẩn đoán** thay thế chuyên gia lâm sàng.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Gửi Phiếu Ghi Nhận Lo Ngại")
        with st.form("form_screening"):
            students = pd.read_sql("SELECT student_id, alias_name FROM students", conn)
            sid = st.selectbox("Chọn học sinh quan sát:", students.apply(lambda r: f"{r['student_id']} - {r['alias_name']}", axis=1))
            real_sid = sid.split(" - ")[0]
            context = st.selectbox("Bối cảnh quan sát:", ["Giờ học", "Giờ ra chơi", "Hoạt động nhóm", "Lúc chuyển tiết", "Tại nhà"])
            
            st.write("**Bảng kiểm quan sát hành vi có cấu trúc:**")
            q1 = st.checkbox("Có phản ứng quá mức với kích thích giác quan (âm thanh chuông, ánh sáng)")
            q2 = st.checkbox("Gặp khó khăn lớn khi thay đổi lịch trình hoặc thứ tự hoạt động thường lệ")
            q3 = st.checkbox("Hạn chế tương tác mắt, ít phản hồi khi người khác gọi tên hoặc bắt chuyện")
            q4 = st.checkbox("Khó khăn trong việc hiểu ngôn ngữ cơ thể hoặc bày tỏ nhu cầu với bạn bè")
            
            note = st.text_area("Mô tả chi tiết lo ngại của người quan sát:")
            
            if st.form_submit_button("Lưu Phiếu Tiếp Nhận"):
                score = sum([q1, q2, q3, q4])
                risk = "Cần đánh giá chuyên sâu" if score >= 2 else "Mức độ thông thường (theo dõi thêm)"
                c = conn.cursor()
                c.execute("""INSERT INTO screenings (student_id, reporter_username, reporter_role, context, indicators_count, concern_note, risk_level, created_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (real_sid, current_username, current_role, context, score, note, risk, str(date.today())))
                conn.commit()
                st.success(f"Đã ghi nhận! Kết quả sàng lọc: **{risk}** (Số chỉ báo: {score}/4). Đã chuyển thông tin tới Cán bộ Tư vấn học sinh.")
                st.rerun()

    with col2:
        st.subheader("Lịch Sử Các Phiếu Sàng Lọc Đã Gửi")
        scrs = pd.read_sql("SELECT id, student_id, reporter_role, context, indicators_count, risk_level, created_at FROM screenings ORDER BY id DESC", conn)
        st.dataframe(scrs, use_container_width=True)

# ==========================================
# BƯỚC 2: HỒ SƠ HỌC SINH & ĐÁNH GIÁ NHU CẦU
# ==========================================
elif step == "2. Hồ sơ Học sinh & Đánh giá nhu cầu":
    st.header("Bước 2: Hồ Sơ Học Sinh & Đánh Giá Nhu Cầu Đa Nguồn")
    st.info("💡 Kết nối dữ liệu đa nguồn từ Nhà trường, Gia đình và Cơ sở y tế/chuyên môn để xác định rõ thế mạnh và rào cản.")
    
    # Tính năng cũ: Form thêm/cập nhật học sinh mới
    with st.expander("➕ Thêm mới / Cập nhật Hồ sơ Học sinh (Dành cho Quản trị/Điều phối)", expanded=False):
        if not ROLE_PERMISSIONS[current_role]["can_edit_student"]:
            st.warning("🔒 Vai trò của bạn chỉ có quyền xem, không có quyền sửa đổi hồ sơ học sinh gốc.")
        else:
            with st.form("form_student_add"):
                c_s1, c_s2 = st.columns(2)
                f_sid = c_s1.text_input("Mã định danh học sinh (Ví dụ: HS-07):")
                f_alias = c_s2.text_input("Tên viết tắt ẩn danh (Ví dụ: Bé T.K):")
                f_grade = c_s1.selectbox("Khối lớp:", ["Lớp 1", "Lớp 2", "Lớp 3", "Lớp 4", "Lớp 5"])
                f_strengths = st.text_area("Thế mạnh & Sở thích (Trí nhớ, hình ảnh, âm nhạc, kỷ luật...):")
                f_challenges = st.text_area("Khó khăn / Rào cản học tập (Giác quan, giao tiếp, bùng nổ...):")
                f_accom = st.text_area("Điều chỉnh môi trường lớp học đề xuất:")
                
                if st.form_submit_button("Lưu Hồ Sơ Học Sinh"):
                    if f_sid and f_alias:
                        c = conn.cursor()
                        c.execute("INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?, ?)",
                                  (f_sid, f_alias, f_grade, f_strengths, f_challenges, f_accom))
                        conn.commit()
                        st.success("Đã cập nhật hồ sơ học sinh thành công!")
                        st.rerun()
                    else:
                        st.error("Vui lòng điền mã học sinh và tên viết tắt!")

    # Chi tiết đánh giá từng học sinh
    st_list = pd.read_sql("SELECT * FROM students", conn)
    sel_sid = st.selectbox("Chọn hồ sơ học sinh cần rà soát:", st_list['student_id'].tolist())
    s_info = st_list[st_list['student_id'] == sel_sid].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"Hồ Sơ Năng Lực: {s_info['alias_name']} ({s_info['student_id']})")
        st.markdown(f"- **Khối lớp:** {s_info['grade']}")
        st.markdown(f"- **Thế mạnh & Sở thích:** :green[{s_info['strengths']}]")
        st.markdown(f"- **Rào cản & Khó khăn:** :red[{s_info['challenges']}]")
        st.markdown(f"- **Điều chỉnh lớp học:** {s_info['accommodations']}")
        
    with c2:
        st.subheader("Lịch Sử Báo Cáo Sàng Lọc Từ Giáo Viên & Phụ Huynh")
        hist = pd.read_sql(f"SELECT reporter_role, context, indicators_count, risk_level, concern_note, created_at FROM screenings WHERE student_id='{sel_sid}'", conn)
        if not hist.empty:
            st.dataframe(hist, use_container_width=True)
        else:
            st.caption("Chưa có ghi nhận sàng lọc trước đó.")

# ==========================================
# BƯỚC 3: KẾ HOẠCH CÁ NHÂN HÓA (DIGITAL IEP)
# ==========================================
elif step == "3. Kế hoạch Cá nhân hóa (Digital IEP)":
    st.header("Bước 3: Hồ Sơ Hỗ Trợ Giáo Dục Cá Nhân Hóa (Digital IEP)")
    st.write("Xây dựng mục tiêu SMART, phân công rõ người phụ trách và theo dõi trạng thái phê duyệt.")
    
    # Bảng danh sách IEP hiện tại
    iep_df = pd.read_sql("""SELECT iep.plan_id, iep.student_id, s.alias_name, s.grade, iep.target_skill, 
                                   iep.strategy, s.accommodations, iep.lead_role, iep.approved_by, iep.status 
                            FROM iep_plans iep JOIN students s ON iep.student_id = s.student_id""", conn)
    st.dataframe(iep_df, use_container_width=True)
    
    # Form tạo hoặc điều chỉnh IEP
    can_create = ROLE_PERMISSIONS[current_role]["can_create_iep"]
    can_appr = ROLE_PERMISSIONS[current_role]["can_approve"]
    
    with st.expander("➕ Thiết lập hoặc Điều chỉnh Mục tiêu IEP Mới", expanded=can_create):
        if not can_create:
            st.warning(f"🔒 Vai trò **{current_role}** chỉ có quyền xem kế hoạch đã được phê duyệt.")
        else:
            with st.form("form_new_iep"):
                f_sid = st.selectbox("Chọn học sinh:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
                f_pid = f"IEP-{f_sid[-2:]}-M{date.today().strftime('%m')}"
                f_skill = st.text_input("Mục tiêu đo lường được (SMART):", placeholder="Ví dụ: Tự hoàn thành bài tập 15 phút với thẻ visual timer")
                f_strategy = st.text_area("Chiến lược hướng dẫn & Gợi ý can thiệp:")
                f_role = st.selectbox("Người phụ trách chính:", [
                    "Nhân viên Hỗ trợ GD Người khuyết tật", 
                    "Giáo viên chủ nhiệm / Bộ môn", 
                    "Cán bộ Tư vấn học sinh (Điều phối)"
                ])
                
                f_appr = current_username if can_appr else "Chờ Cán bộ TVHS duyệt"
                f_status = "Đã phê duyệt" if can_appr else "Chờ duyệt"
                
                if st.form_submit_button("Lưu Mục Tiêu Vào Kế Hoạch IEP"):
                    c = conn.cursor()
                    c.execute("INSERT OR REPLACE INTO iep_plans VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (f_pid, f_sid, f_skill, f_strategy, f_role, f_appr, f_status))
                    conn.commit()
                    st.success(f"Đã lưu kế hoạch {f_pid}! Trạng thái: **{f_status}**.")
                    st.rerun()

# ==========================================
# BƯỚC 4 & 5: NHẬT KÝ CAN THIỆP & BIỂU ĐỒ TIẾN TRIỂN
# ==========================================
elif step == "4. Nhật ký Can thiệp & Biểu đồ tiến triển":
    st.header("Bước 4 & 5: Nhật Ký Can Thiệp Trong Lớp & Biểu Đồ Tiến Triển")
    
    col_input, col_chart = st.columns([1, 2])
    
    with col_input:
        st.subheader("Ghi Nhận Đánh Giá Hàng Tuần")
        with st.form("form_progress_entry"):
            sel_student = st.selectbox("Chọn học sinh:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            current_plans = pd.read_sql(f"SELECT plan_id, target_skill FROM iep_plans WHERE student_id='{sel_student}'", conn)
            
            if not current_plans.empty:
                plan_choice = st.selectbox("Mục tiêu đang can thiệp:", current_plans['plan_id'] + " - " + current_plans['target_skill'])
                real_pid = plan_choice.split(" - ")[0]
                real_skill = " - ".join(plan_choice.split(" - ")[1:])
            else:
                real_pid = "IEP-GEN"
                real_skill = st.text_input("Kỹ năng can thiệp tạm thời:", value="Kỹ năng thích ứng lớp học")
                
            rec_date = st.date_input("Ngày quan sát:", date.today())
            score = st.slider("Mức độ độc lập / tự chủ (Thang 1 - 5):", 1, 5, 3, 
                              help="1: Cần cầm tay chỉ việc | 3: Cần gợi ý hình ảnh/lời nói | 5: Hoàn toàn tự chủ")
            obs_note = st.text_input("Ghi chú tiến triển cụ thể:")
            
            if st.form_submit_button("Lưu Điểm Tiến Trình"):
                c = conn.cursor()
                c.execute("INSERT INTO progress_logs (plan_id, student_id, logged_by, record_date, target_skill, score, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (real_pid, sel_student, current_username, str(rec_date), real_skill, score, obs_note))
                conn.commit()
                st.success("Đã lưu chỉ số tiến triển thành công!")
                st.rerun()

    with col_chart:
        st.subheader("Biểu Đồ Xu Hướng Mức Độ Tự Chủ")
        df_logs = pd.read_sql(f"SELECT record_date, target_skill, score, notes, logged_by FROM progress_logs WHERE student_id='{sel_student}' ORDER BY record_date ASC", conn)
        
        if not df_logs.empty:
            # Biểu đồ phân tích theo từng kỹ năng mục tiêu (tính năng gốc)
            fig = px.line(
                df_logs, 
                x="record_date", 
                y="score", 
                color="target_skill",
                markers=True,
                title=f"Đồ thị theo dõi mức độ tự chủ của học sinh {sel_student}",
                labels={"score": "Điểm tự chủ (1-5)", "record_date": "Ngày đánh giá", "target_skill": "Mục tiêu kỹ năng"}
            )
            fig.update_traces(line=dict(width=3))
            fig.update_yaxes(range=[0.5, 5.5], tickvals=[1, 2, 3, 4, 5])
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info(f"Chưa có dữ liệu tiến triển cho học sinh {sel_student}. Hãy nhập phiếu bên trái để bắt đầu vẽ biểu đồ.")

# ==========================================
# BƯỚC 6: RÀ SOÁT & CHUYỂN TIẾP
# ==========================================
elif step == "5. Rà soát & Chuyển tiếp":
    st.header("Bước 6: Rà Soát Định Kỳ & Hồ Sơ Chuyển Tiếp Cấp Học")
    st.write("Đảm bảo quá trình hỗ trợ liên tục, không bị gián đoạn thông tin khi học sinh lên lớp mới hoặc chuyển trường.")
    
    trans_records = pd.read_sql("""SELECT t.id, t.student_id, s.alias_name, s.grade, t.review_date, t.summary, t.transition_plan, u.full_name as reviewer 
                                   FROM transition_reviews t 
                                   JOIN students s ON t.student_id = s.student_id 
                                   LEFT JOIN users u ON t.reviewer_username = u.username""", conn)
    st.dataframe(trans_records, use_container_width=True)
    
    if ROLE_PERMISSIONS[current_role]["can_trans"]:
        st.divider()
        st.subheader("📝 Lập Hồ Sơ Chuyển Tiếp / Bàn Giao Mới")
        with st.form("form_trans"):
            t_sid = st.selectbox("Chọn học sinh chuyển cấp/chuyển lớp:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            t_sum = st.text_area("Tóm tắt tiến bộ và các mục tiêu đã hoàn thành:")
            t_plan = st.text_area("Các lưu ý về giác quan và chiến lược cần chuyển giao cho thầy cô năm sau:")
            
            if st.form_submit_button("Lưu & Phê Duyệt Hồ Sơ Bàn Giao"):
                c = conn.cursor()
                c.execute("INSERT INTO transition_reviews (student_id, reviewer_username, review_date, summary, transition_plan) VALUES (?, ?, ?, ?, ?)",
                          (t_sid, current_username, str(date.today()), t_sum, t_plan))
                conn.commit()
                st.success("Đã lưu hồ sơ chuyển tiếp bàn giao thành công!")
                st.rerun()
    else:
        st.caption("🔒 *Chỉ Cán bộ Tư vấn học sinh (Điều phối ca) mới có quyền phê duyệt biên bản chuyển tiếp chính thức.*")

# ==========================================
# TỔNG HỢP BÁO CÁO & MÔ PHỎNG
# ==========================================
elif step == "📊 Báo cáo Dữ liệu & Mô phỏng":
    st.header("Báo Cáo Giám Sát Toàn Diện Hệ Thống PoC")
    st.markdown("Dữ liệu phục vụ nghiệm thu và đánh giá mô hình thực nghiệm:")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng số người dùng", len(pd.read_sql("SELECT username FROM users", conn)))
    c2.metric("Tổng số ca học sinh", len(pd.read_sql("SELECT student_id FROM students", conn)))
    c3.metric("Kế hoạch IEP đang chạy", len(pd.read_sql("SELECT plan_id FROM iep_plans", conn)))
    c4.metric("Bản ghi tiến triển", len(pd.read_sql("SELECT id FROM progress_logs", conn)))
    
    st.divider()
    st.subheader("1. Danh mục Toàn bộ Ca Học Sinh Mẫu (Benchmark Case Studies)")
    st.dataframe(pd.read_sql("SELECT * FROM students", conn), use_container_width=True)
    
    st.subheader("2. Danh sách Tài khoản & Phân quyền Hệ thống (RBAC)")
    st.dataframe(pd.read_sql("SELECT username, full_name, role, assigned_scope FROM users", conn), use_container_width=True)
    
    st.subheader("3. Toàn bộ Lịch sử Sàng lọc Nguy cơ Đã Ghi Nhận")
    st.dataframe(pd.read_sql("SELECT * FROM screenings ORDER BY id DESC", conn), use_container_width=True)
