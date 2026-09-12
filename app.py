import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    
    # Bảng người dùng hệ thống (RBAC)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        full_name TEXT,
        role TEXT,
        assigned_scope TEXT
    )''')
    
    # Bảng học sinh
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        alias_name TEXT,
        grade TEXT,
        strengths TEXT,
        challenges TEXT,
        accommodations TEXT
    )''')
    
    # Bảng tiếp nhận & sàng lọc (Bước 1)
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
    
    # Bảng kế hoạch IEP (Bước 2 & 3)
    c.execute('''CREATE TABLE IF NOT EXISTS iep_plans (
        plan_id TEXT PRIMARY KEY,
        student_id TEXT,
        target_skill TEXT,
        strategy TEXT,
        lead_role TEXT,
        approved_by TEXT,
        status TEXT
    )''')
    
    # Bảng nhật ký tiến triển (Bước 4 & 5)
    c.execute('''CREATE TABLE IF NOT EXISTS progress_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id TEXT,
        student_id TEXT,
        logged_by TEXT,
        record_date DATE,
        score INTEGER,
        notes TEXT
    )''')
    
    # Bảng chuyển tiếp (Bước 6)
    c.execute('''CREATE TABLE IF NOT EXISTS transition_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        reviewer_username TEXT,
        review_date DATE,
        summary TEXT,
        transition_plan TEXT
    )''')
    
    # Nạp tài khoản mẫu đại diện cho 4 nhóm tác nhân
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        mock_users = [
            ("gv_lan", "Cô Hoàng Lan", "Giáo viên chủ nhiệm / Bộ môn", "Khối 1, 2, 3, 4, 5"),
            ("tv_nam", "Thầy Trần Nam", "Cán bộ Tư vấn học sinh (Điều phối)", "Toàn trường (Điều phối ca)"),
            ("ht_minh", "Thầy Lê Minh", "Nhân viên Hỗ trợ GD Người khuyết tật", "Chuyên trách can thiệp chuyên biệt"),
            ("ph_huong", "Mẹ bé M.K (Chị Hương)", "Phụ huynh học sinh", "Chỉ xem HS-01")
        ]
        c.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", mock_users)
    
    # Nạp 6 ca lâm sàng học đường chuẩn
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

        # Dữ liệu chuỗi thời gian 4 tuần
        today = date.today()
        mock_logs = []
        for week in range(4):
            d = today - timedelta(days=(3 - week) * 7)
            mock_logs.append(("IEP-01", "HS-01", "ht_minh", d, 1 + week, f"Tuần {week+1}: Bé giảm dần thời lượng khóc khi chuông reo"))
            mock_logs.append(("IEP-02", "HS-02", "gv_lan", d, 2 + (1 if week >= 2 else 0), f"Tuần {week+1}: Đã bắt đầu đứng gần nhóm bạn"))
            mock_logs.append(("IEP-03", "HS-03", "tv_nam", d, min(5, 2 + week), f"Tuần {week+1}: Tự giác đi về góc yên tĩnh mà không tự cào tay"))
        c.executemany("INSERT INTO progress_logs (plan_id, student_id, logged_by, record_date, score, notes) VALUES (?, ?, ?, ?, ?, ?)", mock_logs)

        # Sàng lọc ban đầu
        mock_screenings = [
            ("HS-01", "gv_lan", "Giáo viên chủ nhiệm / Bộ môn", "Lúc chuyển tiết", 3, "Bé thường bịt tai và hét lớn khi chuông reo đổi môn", "Cần đánh giá chuyên sâu", today - timedelta(days=35)),
            ("HS-02", "ph_huong", "Phụ huynh học sinh", "Giờ ra chơi", 2, "Ở nhà bé cũng ít chơi với anh em họ, chỉ thích xếp thú bông", "Cần theo dõi thêm", today - timedelta(days=40))
        ]
        c.executemany("INSERT INTO screenings (student_id, reporter_username, reporter_role, context, indicators_count, concern_note, risk_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", mock_screenings)

        # Biên bản chuyển tiếp
        c.execute("""INSERT INTO transition_reviews (student_id, reviewer_username, review_date, summary, transition_plan) 
                     VALUES ('HS-06', 'tv_nam', ?, 'Đạt mục tiêu tiểu học, kỹ năng máy tính xuất sắc', 'Gửi hồ sơ IEP tóm tắt cho BGH trường THCS tiếp nhận')""", (str(today),))
        
    conn.commit()
    conn.close()

init_and_seed_db()

# ==========================================
# GIAO DIỆN & QUẢN LÝ PHÂN QUYỀN (RBAC)
# ==========================================
st.set_page_config(page_title="Nền tảng Hỗ trợ Hòa nhập Học sinh RLPTK", layout="wide", page_icon="🏫")
conn = get_db()

# BẢNG MA TRẬN PHÂN QUYỀN (RACI Matrix cho chuỗi 6 bước)
ROLE_PERMISSIONS = {
    "Giáo viên chủ nhiệm / Bộ môn": {
        "allowed_steps": ["Sơ đồ Mô phỏng & Tổng quan", "Bước 1: Tiếp nhận & Nhận diện nguy cơ", "Bước 4 & 5: Can thiệp & Theo dõi tiến triển", "📊 Báo cáo Dữ liệu"],
        "can_create_iep": False,
        "can_approve": False,
        "desc": "Theo dõi hàng ngày, phát hiện sớm dấu hiệu nguy cơ, thực hiện can thiệp và chấm điểm tiến triển trong giờ học."
    },
    "Cán bộ Tư vấn học sinh (Điều phối)": {
        "allowed_steps": ["Sơ đồ Mô phỏng & Tổng quan", "Bước 1: Tiếp nhận & Nhận diện nguy cơ", "Bước 2: Họp nhóm & Đánh giá nhu cầu", "Bước 3: Lập kế hoạch cá nhân (IEP)", "Bước 4 & 5: Can thiệp & Theo dõi tiến triển", "Bước 6: Rà soát & Chuyển tiếp", "📊 Báo cáo Dữ liệu"],
        "can_create_iep": True,
        "can_approve": True,
        "desc": "Đầu mối tiếp nhận, kích hoạt họp nhóm, phê duyệt kế hoạch IEP, điều phối chuyển gửi chuyên khoa và tổ chức bàn giao chuyển cấp."
    },
    "Nhân viên Hỗ trợ GD Người khuyết tật": {
        "allowed_steps": ["Sơ đồ Mô phỏng & Tổng quan", "Bước 2: Họp nhóm & Đánh giá nhu cầu", "Bước 3: Lập kế hoạch cá nhân (IEP)", "Bước 4 & 5: Can thiệp & Theo dõi tiến triển", "📊 Báo cáo Dữ liệu"],
        "can_create_iep": True,
        "can_approve": False,
        "desc": "Chuyên trách thiết lập kỹ thuật can thiệp, chuẩn bị học liệu visual/AAC, hướng dẫn giáo viên và ghi nhật ký tiến triển."
    },
    "Phụ huynh học sinh": {
        "allowed_steps": ["Sơ đồ Mô phỏng & Tổng quan", "Bước 1: Tiếp nhận & Nhận diện nguy cơ", "Bước 4 & 5: Can thiệp & Theo dõi tiến triển"],
        "can_create_iep": False,
        "can_approve": False,
        "desc": "Cung cấp phản ánh lo ngại tại gia đình, đồng thuận kế hoạch can thiệp và theo dõi biểu đồ tiến bộ của con."
    }
}

# Sidebar - Quản lý tài khoản đăng nhập
st.sidebar.title("HỆ THỐNG HÒA NHẬP")
st.sidebar.caption("Chuyển đổi số theo TT 11/2024 & TT 21/2023")

users_df = pd.read_sql("SELECT * FROM users", conn)
user_dict = {f"{r['full_name']} ({r['role']})": r['username'] for _, r in users_df.iterrows()}

selected_user_display = st.sidebar.selectbox("👤 Đăng nhập tài khoản:", list(user_dict.keys()))
current_username = user_dict[selected_user_display]
current_user_row = users_df[users_df['username'] == current_username].iloc[0]
current_role = current_user_row['role']

st.sidebar.markdown(f"**Vai trò:** `{current_role}`")
st.sidebar.info(f"📌 **Trách nhiệm:** {ROLE_PERMISSIONS[current_role]['desc']}")

st.sidebar.divider()

# Menu điều hướng theo phân quyền
all_steps = [
    "Sơ đồ Mô phỏng & Tổng quan",
    "Bước 1: Tiếp nhận & Nhận diện nguy cơ",
    "Bước 2: Họp nhóm & Đánh giá nhu cầu",
    "Bước 3: Lập kế hoạch cá nhân (IEP)",
    "Bước 4 & 5: Can thiệp & Theo dõi tiến triển",
    "Bước 6: Rà soát & Chuyển tiếp",
    "📊 Báo cáo Dữ liệu"
]

menu_options = [s for s in all_steps if s in ROLE_PERMISSIONS[current_role]['allowed_steps']]
step = st.sidebar.radio("Quy trình khả dụng cho bạn:", menu_options)

st.sidebar.divider()
st.sidebar.markdown("""
<div style='font-size:12px; color:gray;'>
<b>Nhóm Nghiên cứu Kỹ thuật:</b><br>
ThS. Võ Thị Kim Anh (TDTU & FEI/VSB)<br>
<b>Cơ sở Lý luận:</b><br>
PGS.TS. Nguyễn Văn Tường & TS. Lê Thị Thanh Huyền
</div>
""", unsafe_allow_html=True)

# ==========================================
# SƠ ĐỒ MÔ PHỎNG HÌNH ẢNH TRỰC QUAN (VISUAL PIPELINE)
# ==========================================
if step == "Sơ đồ Mô phỏng & Tổng quan":
    st.header("Sơ Đồ Mô Phỏng Quy Trình 6 Bước & Phân Bổ Trách Nhiệm")
    st.markdown("Quy trình khép kín, liên tục kết nối **Dữ liệu – Con người – Trách nhiệm** trong môi trường trường học:")
    
    # 1. Bảng trực quan hóa dòng quy trình 6 bước
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
    
    # 2. Sơ đồ ma trận trách nhiệm (RACI Chart trực quan)
    st.subheader("Ma trận Phân quyền & Vai trò Tham gia (RACI Matrix)")
    raci_data = pd.DataFrame([
        {"Bước nghiệp vụ": "Bước 1: Sàng lọc & Tiếp nhận lo ngại", "GV Chủ nhiệm": "Chủ trì (R)", "Tư vấn HS": "Phối hợp (C)", "NV Hỗ trợ GDHN": "Tham vấn (I)", "Phụ huynh": "Đồng thuận (A)"},
        {"Bước nghiệp vụ": "Bước 2: Họp nhóm & Đánh giá nhu cầu", "GV Chủ nhiệm": "Tham gia (C)", "Tư vấn HS": "Chủ trì (R)", "NV Hỗ trợ GDHN": "Phối hợp (C)", "Phụ huynh": "Tham gia (C)"},
        {"Bước nghiệp vụ": "Bước 3: Lập kế hoạch cá nhân (IEP)", "GV Chủ nhiệm": "Phối hợp (C)", "Tư vấn HS": "Phê duyệt (A)", "NV Hỗ trợ GDHN": "Xây dựng (R)", "Phụ huynh": "Ký duyệt (A)"},
        {"Bước nghiệp vụ": "Bước 4: Can thiệp ngay tại lớp", "GV Chủ nhiệm": "Thực hiện (R)", "Tư vấn HS": "Giám sát (A)", "NV Hỗ trợ GDHN": "Trợ giảng (R)", "Phụ huynh": "Hỗ trợ nhà (C)"},
        {"Bước nghiệp vụ": "Bước 5: Ghi nhận & Theo dõi tiến triển", "GV Chủ nhiệm": "Chấm điểm (R)", "Tư vấn HS": "Theo dõi (A)", "NV Hỗ trợ GDHN": "Ghi chép (R)", "Phụ huynh": "Theo dõi (I)"},
        {"Bước nghiệp vụ": "Bước 6: Rà soát & Chuyển tiếp cấp học", "GV Chủ nhiệm": "Bàn giao (C)", "Tư vấn HS": "Chủ trì (R)", "NV Hỗ trợ GDHN": "Tổng kết (C)", "Phụ huynh": "Đồng hành (C)"}
    ])
    st.dataframe(raci_data, use_container_width=True, hide_index=True)
    st.caption("*(R: Responsible - Người làm | A: Accountable - Người duyệt/chịu trách nhiệm | C: Consulted - Tham vấn | I: Informed - Nhận thông tin)*")

# ==========================================
# BƯỚC 1: TIẾP NHẬN & SÀNG LỌC NGUY CƠ
# ==========================================
elif step == "Bước 1: Tiếp nhận & Nhận diện nguy cơ":
    st.header("Bước 1: Tiếp nhận lo ngại & Nhận diện có cấu trúc")
    st.warning("⚠️ **Nguyên tắc đạo đức dữ liệu:** Bảng kiểm chỉ hỗ trợ nhận diện sơ bộ dấu hiệu cần đánh giá thêm. Tuyệt đối **không kết luận chẩn đoán** thay thế bác sĩ/chuyên gia tâm lý lâm sàng.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Gửi Phiếu Ghi Nhận Lo Ngại Mới")
        with st.form("form_screening"):
            students = pd.read_sql("SELECT student_id, alias_name FROM students", conn)
            sid = st.selectbox("Chọn học sinh quan sát:", students.apply(lambda r: f"{r['student_id']} - {r['alias_name']}", axis=1))
            real_sid = sid.split(" - ")[0]
            context = st.selectbox("Bối cảnh quan sát:", ["Giờ học", "Giờ ra chơi", "Hoạt động nhóm", "Lúc chuyển tiết", "Tại nhà"])
            
            st.write("**Chỉ báo hành vi quan sát có cấu trúc:**")
            q1 = st.checkbox("Phản ứng quá mức với âm thanh lớn, ánh sáng hoặc xúc giác")
            q2 = st.checkbox("Khó khăn rõ rệt khi đổi hoạt động hoặc thay đổi thời khóa biểu")
            q3 = st.checkbox("Hạn chế tương tác mắt, ít phản hồi khi giáo viên gọi tên")
            q4 = st.checkbox("Khó khăn trong chia sẻ trò chơi hoặc bày tỏ nhu cầu với bạn")
            
            note = st.text_area("Mô tả chi tiết hành vi quan sát:")
            
            if st.form_submit_button("Lưu & Gửi tới Cán bộ Tư vấn học sinh"):
                score = sum([q1, q2, q3, q4])
                risk = "Cần đánh giá chuyên sâu" if score >= 2 else "Mức độ thông thường (theo dõi thêm)"
                c = conn.cursor()
                c.execute("""INSERT INTO screenings (student_id, reporter_username, reporter_role, context, indicators_count, concern_note, risk_level, created_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (real_sid, current_username, current_role, context, score, note, risk, str(date.today())))
                conn.commit()
                st.success(f"Đã lưu thành công! Chỉ số cảnh báo: {score}/4 ({risk}). Phiếu đã được điều phối tới Cán bộ Tư vấn học sinh.")

    with col2:
        st.subheader("Lịch sử Các Phiếu Tiếp Nhận Đã Gửi")
        scrs = pd.read_sql("SELECT id, student_id, reporter_role, context, indicators_count, risk_level, created_at FROM screenings ORDER BY id DESC", conn)
        st.dataframe(scrs, use_container_width=True)

# ==========================================
# BƯỚC 2: HỌP NHÓM & ĐÁNH GIÁ NHU CẦU
# ==========================================
elif step == "Bước 2: Họp nhóm & Đánh giá nhu cầu":
    st.header("Bước 2: Họp nhóm hỗ trợ & Đánh giá nhu cầu giáo dục đa nguồn")
    st.info("💡 **Điều phối viên:** Cán bộ Tư vấn học sinh chủ trì phiên họp, đặt các nguồn thông tin từ Gia đình, Nhà trường và Chuyên khoa cạnh nhau.")
    
    st_list = pd.read_sql("SELECT * FROM students", conn)
    sel_sid = st.selectbox("Chọn hồ sơ học sinh:", st_list['student_id'].tolist())
    s_info = st_list[st_list['student_id'] == sel_sid].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"Hồ sơ Tổng hợp: {s_info['alias_name']} ({s_info['student_id']})")
        st.markdown(f"- **Khối lớp:** {s_info['grade']}")
        st.markdown(f"- **Điểm mạnh & Sở thích:** :green[{s_info['strengths']}]")
        st.markdown(f"- **Rào cản & Khó khăn:** :red[{s_info['challenges']}]")
        st.markdown(f"- **Điều chỉnh đề xuất:** {s_info['accommodations']}")
        
    with c2:
        st.subheader("Lịch sử Sàng lọc Đa nguồn")
        hist = pd.read_sql(f"SELECT reporter_role, context, indicators_count, risk_level, concern_note, created_at FROM screenings WHERE student_id='{sel_sid}'", conn)
        if not hist.empty:
            st.dataframe(hist, use_container_width=True)
        else:
            st.caption("Chưa có bản ghi sàng lọc trước đó.")

# ==========================================
# BƯỚC 3: LẬP KẾ HOẠCH CÁ NHÂN (IEP)
# ==========================================
elif step == "Bước 3: Lập kế hoạch cá nhân (IEP)":
    st.header("Bước 3: Hồ sơ Hỗ trợ Giáo dục Cá nhân (Digital IEP)")
    
    # Kiểm tra quyền tạo/duyệt
    can_edit = ROLE_PERMISSIONS[current_role]['can_create_iep']
    can_appr = ROLE_PERMISSIONS[current_role]['can_approve']
    
    if not can_edit:
        st.warning(f"🔒 **Quyền hạn chế:** Tài khoản vai trò **{current_role}** chỉ có quyền Xem hồ sơ IEP đã phê duyệt.")
        
    iep_df = pd.read_sql("""SELECT iep.plan_id, iep.student_id, s.alias_name, iep.target_skill, 
                                   iep.strategy, iep.lead_role, iep.approved_by, iep.status 
                            FROM iep_plans iep JOIN students s ON iep.student_id = s.student_id""", conn)
    st.dataframe(iep_df, use_container_width=True)
    
    if can_edit:
        st.divider()
        st.subheader("➕ Thiết lập hoặc Điều chỉnh Mục tiêu Can thiệp (SMART)")
        with st.form("form_iep"):
            f_sid = st.selectbox("Chọn học sinh:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            f_pid = f"IEP-{f_sid[-2:]}-M{date.today().strftime('%m')}"
            f_skill = st.text_input("Mục tiêu đo lường được (SMART):", placeholder="Ví dụ: Giảm số lần bùng nổ khi đổi tiết xuống dưới 1 lần/tuần")
            f_strat = st.text_area("Chiến lược hỗ trợ và điều chỉnh môi trường:")
            f_role = st.selectbox("Vị trí chịu trách nhiệm chính:", [
                "Nhân viên Hỗ trợ GD Người khuyết tật", 
                "Giáo viên chủ nhiệm / Bộ môn", 
                "Cán bộ Tư vấn học sinh (Điều phối)"
            ])
            
            f_appr = current_username if can_appr else "Chờ Cán bộ TVHS duyệt"
            f_status = "Đã phê duyệt" if can_appr else "Chờ duyệt"
            
            if st.form_submit_button("Lưu Kế hoạch IEP"):
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO iep_plans VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (f_pid, f_sid, f_skill, f_strat, f_role, f_appr, f_status))
                conn.commit()
                st.success(f"Đã lưu kế hoạch {f_pid}! Trạng thái: **{f_status}**.")
                st.rerun()

# ==========================================
# BƯỚC 4 & 5: CAN THIỆP & THEO DÕI TIẾN TRIỂN
# ==========================================
elif step == "Bước 4 & 5: Can thiệp & Theo dõi tiến triển":
    st.header("Bước 4 & 5: Thực hiện Can thiệp & Theo dõi Dữ liệu Tiến triển")
    
    col_in, col_viz = st.columns([1, 2])
    
    with col_in:
        st.subheader("Ghi nhận Đánh giá Tiến bộ")
        with st.form("form_log"):
            sel_s = st.selectbox("Học sinh:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            plans = pd.read_sql(f"SELECT plan_id, target_skill FROM iep_plans WHERE student_id='{sel_s}'", conn)
            
            if not plans.empty:
                plan_str = st.selectbox("Mục tiêu đang theo dõi:", plans['plan_id'] + " - " + plans['target_skill'])
                real_pid = plan_str.split(" - ")[0]
            else:
                real_pid = "IEP-TEMP"
                st.caption("Chưa có kế hoạch chính thức.")
                
            log_d = st.date_input("Ngày quan sát:", date.today())
            log_score = st.slider("Mức độ độc lập / tự chủ (Thang 1 - 5):", 1, 5, 3,
                                  help="1: Cần hỗ trợ hoàn toàn | 3: Cần gợi ý hình ảnh/lời nói | 5: Độc lập hoàn toàn")
            log_note = st.text_input("Ghi chú biểu hiện cụ thể:")
            
            if st.form_submit_button("Lưu Điểm Tiến Triển"):
                c = conn.cursor()
                c.execute("INSERT INTO progress_logs (plan_id, student_id, logged_by, record_date, score, notes) VALUES (?, ?, ?, ?, ?, ?)",
                          (real_pid, sel_s, current_username, str(log_d), log_score, log_note))
                conn.commit()
                st.success("Đã ghi nhận dữ liệu tiến triển!")
                st.rerun()

    with col_viz:
        st.subheader("Biểu đồ Chuỗi Thời gian (Time-series Tracking)")
        df_logs = pd.read_sql(f"SELECT record_date, score, notes, logged_by FROM progress_logs WHERE student_id='{sel_s}' ORDER BY record_date ASC", conn)
        
        if not df_logs.empty:
            fig = px.line(
                df_logs, x="record_date", y="score", markers=True, text="score",
                title=f"Đồ thị mức độ tự chủ của học sinh {sel_s} theo thời gian",
                labels={"score": "Thang điểm độc lập (1-5)", "record_date": "Ngày đánh giá"}
            )
            fig.update_traces(textposition="top center", line=dict(width=3, color="#0284C7"))
            fig.update_yaxes(range=[0.5, 5.5], tickvals=[1, 2, 3, 4, 5])
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu tiến triển cho học sinh này.")

# ==========================================
# BƯỚC 6: RÀ SOÁT & CHUYỂN TIẾP
# ==========================================
elif step == "Bước 6: Rà soát & Chuyển tiếp":
    st.header("Bước 6: Rà soát Định kỳ & Lập Hồ sơ Chuyển tiếp")
    st.write("Đảm bảo quá trình hỗ trợ không bị gián đoạn khi học sinh chuyển lớp hoặc chuyển cấp học.")
    
    trans_records = pd.read_sql("""SELECT t.id, t.student_id, s.alias_name, s.grade, t.review_date, t.summary, t.transition_plan, u.full_name as reviewer 
                                   FROM transition_reviews t 
                                   JOIN students s ON t.student_id = s.student_id 
                                   LEFT JOIN users u ON t.reviewer_username = u.username""", conn)
    st.dataframe(trans_records, use_container_width=True)
    
    if current_role == "Cán bộ Tư vấn học sinh (Điều phối)":
        st.divider()
        st.subheader("📝 Lập Hồ sơ Chuyển tiếp Mới")
        with st.form("form_trans"):
            t_sid = st.selectbox("Chọn học sinh chuyển cấp/chuyển lớp:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            t_sum = st.text_area("Tóm tắt tiến bộ và các mục tiêu đã hoàn thành:")
            t_plan = st.text_area("Các lưu ý về giác quan và chiến lược cần chuyển giao cho thầy cô năm sau:")
            
            if st.form_submit_button("Lưu & Phê duyệt Hồ sơ Bàn giao"):
                c = conn.cursor()
                c.execute("INSERT INTO transition_reviews (student_id, reviewer_username, review_date, summary, transition_plan) VALUES (?, ?, ?, ?, ?)",
                          (t_sid, current_username, str(date.today()), t_sum, t_plan))
                conn.commit()
                st.success("Đã hoàn thành hồ sơ chuyển tiếp!")
                st.rerun()
    else:
        st.caption("🔒 *Chỉ Cán bộ Tư vấn học sinh (Điều phối ca) mới có quyền tạo biên bản chuyển tiếp chính thức.*")

# ==========================================
# BÁO CÁO DỮ LIỆU & TỔNG QUAN
# ==========================================
elif step == "📊 Báo cáo Dữ liệu":
    st.header("Báo Cáo Tổng Hợp & Quản Lý Dữ Liệu PoC")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Người dùng hệ thống", len(pd.read_sql("SELECT username FROM users", conn)))
    m2.metric("Tổng số học sinh (Ca)", len(pd.read_sql("SELECT student_id FROM students", conn)))
    m3.metric("Kế hoạch IEP đang chạy", len(pd.read_sql("SELECT plan_id FROM iep_plans", conn)))
    m4.metric("Dữ liệu theo dõi", len(pd.read_sql("SELECT id FROM progress_logs", conn)))
    
    st.subheader("Danh sách Tài khoản Người dùng & Phân vai (RBAC)")
    st.dataframe(pd.read_sql("SELECT username, full_name, role, assigned_scope FROM users", conn), use_container_width=True)
    
    st.subheader("Danh mục 6 Ca Lâm Sàng Học Đường Giả Định")
    st.dataframe(pd.read_sql("SELECT * FROM students", conn), use_container_width=True)
