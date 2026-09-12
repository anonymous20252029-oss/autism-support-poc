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
    
    # 1. Bảng học sinh
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        alias_name TEXT,
        grade TEXT,
        strengths TEXT,
        challenges TEXT,
        accommodations TEXT
    )''')
    
    # 2. Bảng tiếp nhận & sàng lọc (Bước 1)
    c.execute('''CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        reporter_role TEXT,
        context TEXT,
        indicators_count INTEGER,
        concern_note TEXT,
        risk_level TEXT,
        created_at DATE
    )''')
    
    # 3. Bảng kế hoạch IEP (Bước 2 & 3)
    c.execute('''CREATE TABLE IF NOT EXISTS iep_plans (
        plan_id TEXT PRIMARY KEY,
        student_id TEXT,
        target_skill TEXT,
        strategy TEXT,
        lead_role TEXT,
        status TEXT
    )''')
    
    # 4. Bảng nhật ký tiến triển (Bước 4 & 5)
    c.execute('''CREATE TABLE IF NOT EXISTS progress_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id TEXT,
        student_id TEXT,
        record_date DATE,
        score INTEGER,
        notes TEXT
    )''')
    
    # 5. Bảng chuyển tiếp (Bước 6)
    c.execute('''CREATE TABLE IF NOT EXISTS transition_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        review_date DATE,
        summary TEXT,
        transition_plan TEXT
    )''')
    
    # Nạp 6 ca lâm sàng chuẩn nếu CSDL còn rỗng
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
        
        # Nạp kế hoạch IEP mẫu cho từng em
        mock_ieps = [
            ("IEP-01", "HS-01", "Chuyển tiết học mà không la hét", "Dùng thẻ hình trực quan trước 5 phút", "Nhân viên hỗ trợ GDHN", "Đang thực hiện"),
            ("IEP-02", "HS-02", "Chủ động mời bạn cùng chơi 1 lần/ngày", "Tập dượt mẫu câu xin chơi cùng với bạn buddy", "Giáo viên chủ nhiệm", "Đang thực hiện"),
            ("IEP-03", "HS-03", "Chủ động giơ thẻ 'Xin nghỉ' khi căng thẳng", "Nhắc nhở kín đáo khi thấy học sinh bắt đầu gõ bàn", "Cán bộ Tư vấn HS", "Đang thực hiện"),
            ("IEP-04", "HS-04", "Dùng thẻ PECS yêu cầu đồ dùng học tập", "Khen thưởng tức thì khi bé chỉ vào biểu tượng", "Nhân viên hỗ trợ GDHN", "Đang thực hiện"),
            ("IEP-05", "HS-05", "Hoàn thành nhiệm vụ nhóm theo checklist", "Giao vai trò cụ thể: người ghi chép kết quả", "Giáo viên chủ nhiệm", "Đang thực hiện"),
            ("IEP-06", "HS-06", "Giảm thang điểm lo âu chuyển cấp", "Tham quan trường THCS trước kỳ nghỉ hè", "Cán bộ Tư vấn HS", "Đang chuẩn bị")
        ]
        c.executemany("INSERT INTO iep_plans VALUES (?, ?, ?, ?, ?, ?)", mock_ieps)

        # Nạp dữ liệu tiến triển mô phỏng (4 tuần gần nhất) để vẽ đồ thị
        today = date.today()
        mock_logs = []
        for week in range(4):
            d = today - timedelta(days=(3 - week) * 7)
            mock_logs.append(("IEP-01", "HS-01", d, 1 + week, f"Tuần {week+1}: Bé giảm dần thời lượng khóc khi đổi tiết"))
            mock_logs.append(("IEP-02", "HS-02", d, 2 + (1 if week >= 2 else 0), f"Tuần {week+1}: Đã bắt đầu đứng gần nhóm bạn"))
            mock_logs.append(("IEP-03", "HS-03", d, min(5, 2 + week), f"Tuần {week+1}: Tự giác đi về góc yên tĩnh mà không tự cào tay"))
        c.executemany("INSERT INTO progress_logs (plan_id, student_id, record_date, score, notes) VALUES (?, ?, ?, ?, ?)", mock_logs)

        # Nạp báo cáo tiếp nhận sàng lọc ban đầu
        mock_screenings = [
            ("HS-01", "Giáo viên chủ nhiệm", "Lúc chuyển tiết", 3, "Bé thường bịt tai và hét lớn khi chuông reo đổi môn", "Cần đánh giá chuyên sâu", today - timedelta(days=35)),
            ("HS-02", "Phụ huynh", "Giờ ra chơi", 2, "Ở nhà bé cũng ít chơi với anh em họ, chỉ thích xếp thú bông", "Cần theo dõi thêm", today - timedelta(days=40))
        ]
        c.executemany("INSERT INTO screenings (student_id, reporter_role, context, indicators_count, concern_note, risk_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", mock_screenings)

        # Nạp ghi chú chuyển tiếp (Bước 6)
        c.execute("""INSERT INTO transition_reviews (student_id, review_date, summary, transition_plan) 
                     VALUES ('HS-06', ?, 'Đạt mục tiêu tiểu học, kỹ năng máy tính xuất sắc', 'Gửi hồ sơ IEP tóm tắt cho ban giám hiệu trường THCS tiếp nhận')""", (str(today),))
        
    conn.commit()
    conn.close()

init_and_seed_db()

# ==========================================
# GIAO DIỆN STREAMLIT CHUỖI 6 BƯỚC LIÊN TỤC
# ==========================================
st.set_page_config(page_title="Nền tảng Hỗ trợ Hòa nhập Học sinh RLPTK", layout="wide", page_icon="🏫")

st.sidebar.title("GIÁO DỤC HÒA NHẬP")
st.sidebar.caption("Mô hình tích hợp có ứng dụng công nghệ số (PGS.TS. Nguyễn Văn Tường)")

# Lựa chọn vai trò theo Thông tư 11 & 21
user_role = st.sidebar.selectbox(
    "Vai trò người dùng:",
    [
        "Giáo viên chủ nhiệm / Bộ môn", 
        "Cán bộ Tư vấn học sinh (Điều phối)", 
        "Nhân viên Hỗ trợ GD Người khuyết tật", 
        "Phụ huynh học sinh"
    ]
)

step = st.sidebar.radio(
    "Chuỗi quy trình 6 bước:",
    [
        "Bước 1: Tiếp nhận & Nhận diện nguy cơ",
        "Bước 2: Họp nhóm & Đánh giá nhu cầu",
        "Bước 3: Lập kế hoạch cá nhân (IEP)",
        "Bước 4 & 5: Can thiệp & Theo dõi tiến triển",
        "Bước 6: Rà soát & Chuyển tiếp",
        "📊 Tổng hợp Dữ liệu & Mô phỏng"
    ]
)

conn = get_db()

# --- BƯỚC 1: TIẾP NHẬN & NHẬN DIỆN NGUY CƠ ---
if step == "Bước 1: Tiếp nhận & Nhận diện nguy cơ":
    st.header("Bước 1: Tiếp nhận lo ngại & Nhận diện có cấu trúc")
    st.warning("⚠️ **Nguyên tắc đạo đức dữ liệu:** Bảng kiểm chỉ hỗ trợ nhận diện sơ bộ dấu hiệu cần đánh giá thêm. Hệ thống tuyệt đối **không đưa ra kết luận chẩn đoán** thay thế bác sĩ/chuyên gia tâm lý lâm sàng.")
    
    with st.form("screening_form"):
        col1, col2 = st.columns(2)
        sid = col1.selectbox("Chọn mã học sinh:", pd.read_sql("SELECT student_id, alias_name FROM students", conn).apply(lambda r: f"{r['student_id']} - {r['alias_name']}", axis=1))
        real_sid = sid.split(" - ")[0]
        context = col2.selectbox("Bối cảnh quan sát chính:", ["Trong giờ học", "Giờ ra chơi", "Hoạt động nhóm", "Lúc chuyển tiết", "Tại gia đình"])
        
        st.write("---")
        st.write("**Bảng kiểm quan sát hành vi có cấu trúc:**")
        q1 = st.checkbox("Có phản ứng quá mức với kích thích giác quan (âm thanh chuông, ánh sáng, tiếng ồn)")
        q2 = st.checkbox("Gặp khó khăn lớn khi thay đổi lịch trình hoặc thứ tự hoạt động thường lệ")
        q3 = st.checkbox("Ít tương tác mắt, hạn chế đáp lại khi người khác gọi tên hoặc bắt chuyện")
        q4 = st.checkbox("Khó khăn trong việc hiểu ngôn ngữ cơ thể hoặc bày tỏ nhu cầu với bạn bè")
        
        note = st.text_area("Mô tả chi tiết lo ngại của người quan sát:")
        
        if st.form_submit_button("Gửi phiếu tiếp nhận lo ngại"):
            score = sum([q1, q2, q3, q4])
            risk = "Cần đánh giá chuyên sâu" if score >= 2 else "Mức độ thông thường (theo dõi thêm)"
            c = conn.cursor()
            c.execute("""INSERT INTO screenings (student_id, reporter_role, context, indicators_count, concern_note, risk_level, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""", (real_sid, user_role, context, score, note, risk, str(date.today())))
            conn.commit()
            st.success(f"Đã ghi nhận! Kết quả sàng lọc: **{risk}** (Số chỉ báo: {score}/4). Đã chuyển thông tin tới Cán bộ Tư vấn học sinh để kích hoạt họp nhóm.")

# --- BƯỚC 2: HỌP NHÓM & ĐÁNH GIÁ NHU CẦU ---
elif step == "Bước 2: Họp nhóm & Đánh giá nhu cầu":
    st.header("Bước 2: Đánh giá nhu cầu giáo dục đa nguồn & Họp nhóm hỗ trợ")
    st.info("Đánh giá tích hợp: Đặt dữ liệu từ Nhà trường, Gia đình và Cơ sở y tế/chuyên môn cạnh nhau để tìm ra rào cản và thế mạnh.")
    
    students_df = pd.read_sql("SELECT * FROM students", conn)
    chosen_id = st.selectbox("Chọn học sinh cần xem xét hồ sơ đánh giá:", students_df['student_id'].tolist())
    student_info = students_df[students_df['student_id'] == chosen_id].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Hồ sơ năng lực học tập")
        st.markdown(f"- **Mã HS:** {student_info['student_id']} ({student_info['alias_name']})")
        st.markdown(f"- **Khối lớp:** {student_info['grade']}")
        st.markdown(f"- **Thế mạnh & Sở thích:** :green[{student_info['strengths']}]")
        st.markdown(f"- **Rào cản/Khó khăn:** :red[{student_info['challenges']}]")
    
    with c2:
        st.subheader("Lịch sử các báo cáo lo ngại (Đa nguồn)")
        scr_history = pd.read_sql(f"SELECT reporter_role, context, indicators_count, risk_level, concern_note, created_at FROM screenings WHERE student_id='{chosen_id}'", conn)
        if not scr_history.empty:
            st.dataframe(scr_history, use_container_width=True)
        else:
            st.caption("Chưa có ghi nhận sàng lọc trước đó.")

# --- BƯỚC 3: LẬP KẾ HOẠCH HỖ TRỢ CÁ NHÂN (IEP) ---
elif step == "Bước 3: Lập kế hoạch cá nhân (IEP)":
    st.header("Bước 3: Hồ sơ Hỗ trợ Giáo dục Cá nhân hóa (Digital IEP)")
    st.write("Xây dựng mục tiêu SMART, phân định rõ trách nhiệm của từng vị trí việc làm.")
    
    iep_df = pd.read_sql("""SELECT iep.plan_id, iep.student_id, s.alias_name, s.grade, iep.target_skill, 
                                   iep.strategy, s.accommodations, iep.lead_role, iep.status 
                            FROM iep_plans iep JOIN students s ON iep.student_id = s.student_id""", conn)
    st.dataframe(iep_df, use_container_width=True)
    
    with st.expander("➕ Thiết lập hoặc điều chỉnh mục tiêu IEP mới"):
        with st.form("new_iep"):
            f_sid = st.selectbox("Chọn học sinh:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            f_plan_id = f"IEP-{f_sid[-2:]}-NEW"
            f_skill = st.text_input("Mục tiêu đo lường được (SMART):", placeholder="Ví dụ: Tự hoàn thành bài tập 15 phút với thẻ visual timer")
            f_strategy = st.text_area("Chiến lược hướng dẫn & Gợi ý hỗ trợ:")
            f_role = st.selectbox("Người phụ trách chính:", ["Giáo viên chủ nhiệm", "Nhân viên Hỗ trợ GDHN", "Cán bộ Tư vấn HS", "Phụ huynh"])
            
            if st.form_submit_button("Lưu mục tiêu vào kế hoạch"):
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO iep_plans VALUES (?, ?, ?, ?, ?, 'Đang thực hiện')",
                          (f_plan_id, f_sid, f_skill, f_strategy, f_role))
                conn.commit()
                st.success("Đã bổ sung mục tiêu IEP thành công!")

# --- BƯỚC 4 & 5: CAN THIỆP & THEO DÕI TIẾN TRIỂN ---
elif step == "Bước 4 & 5: Can thiệp & Theo dõi tiến triển":
    st.header("Bước 4 & 5: Can thiệp trong lớp học & Phân tích tiến trình thời gian thực")
    
    col_input, col_view = st.columns([1, 2])
    with col_input:
        st.subheader("Nhật ký can thiệp định kỳ")
        with st.form("log_form"):
            selected_student = st.selectbox("Học sinh:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            current_plans = pd.read_sql(f"SELECT plan_id, target_skill FROM iep_plans WHERE student_id='{selected_student}'", conn)
            
            if not current_plans.empty:
                plan_choice = st.selectbox("Mục tiêu đang theo dõi:", current_plans['plan_id'] + " - " + current_plans['target_skill'])
                real_pid = plan_choice.split(" - ")[0]
            else:
                real_pid = "IEP-TEMP"
                st.caption("Chưa có kế hoạch, ghi nhận tạm thời.")
                
            rec_date = st.date_input("Ngày quan sát:", date.today())
            score = st.slider("Mức độ tự chủ / độc lập:", 1, 5, 3, 
                              help="1: Nhắc nhở/cầm tay chỉ việc 100% | 3: Cần nhắc nhở cử chỉ/hình ảnh | 5: Hoàn toàn tự chủ")
            note_log = st.text_input("Ghi chú tiến triển cụ thể:")
            
            if st.form_submit_button("Lưu chỉ số"):
                c = conn.cursor()
                c.execute("INSERT INTO progress_logs (plan_id, student_id, record_date, score, notes) VALUES (?, ?, ?, ?, ?)",
                          (real_pid, selected_student, str(rec_date), score, note_log))
                conn.commit()
                st.success("Đã ghi nhận dữ liệu tiến triển!")
                
    with col_view:
        st.subheader("Đồ thị tiến bộ của học sinh")
        df_chart = pd.read_sql(f"SELECT record_date, score, notes FROM progress_logs WHERE student_id='{selected_student}' ORDER BY record_date ASC", conn)
        if not df_chart.empty:
            fig = px.line(df_chart, x="record_date", y="score", markers=True, title=f"Xu hướng mức độ tự chủ của {selected_student}",
                          labels={"score": "Điểm tự chủ (1-5)", "record_date": "Thời gian"})
            fig.update_yaxes(range=[0.5, 5.5])
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_chart, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu tiến triển cho học sinh này.")

# --- BƯỚC 6: RÀ SOÁT & CHUYỂN TIẾP ---
elif step == "Bước 6: Rà soát & Chuyển tiếp":
    st.header("Bước 6: Rà soát định kỳ & Chuyển tiếp cấp học / năm học")
    st.write("Đảm bảo tính liên tục, không bị đứt đoạn hỗ trợ khi học sinh lên lớp mới hoặc chuyển trường.")
    
    trans_df = pd.read_sql("""SELECT t.id, t.student_id, s.alias_name, s.grade, t.review_date, t.summary, t.transition_plan 
                              FROM transition_reviews t JOIN students s ON t.student_id = s.student_id""", conn)
    st.dataframe(trans_df, use_container_width=True)
    
    with st.form("trans_form"):
        t_sid = st.selectbox("Chọn học sinh chuẩn bị chuyển tiếp:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
        t_sum = st.text_area("Tóm tắt năng lực đạt được sau giai đoạn can thiệp:")
        t_plan = st.text_area("Khuyến nghị và điều chỉnh môi trường cần bàn giao cho giáo viên năm học sau:")
        
        if st.form_submit_button("Lưu hồ sơ chuyển tiếp"):
            c = conn.cursor()
            c.execute("INSERT INTO transition_reviews (student_id, review_date, summary, transition_plan) VALUES (?, ?, ?, ?)",
                      (t_sid, str(date.today()), t_sum, t_plan))
            conn.commit()
            st.success("Đã tạo hồ sơ chuyển tiếp bàn giao thành công!")

# --- TỔNG HỢP MÔ PHỎNG DỮ LIỆU ---
elif step == "📊 Tổng hợp Dữ liệu & Mô phỏng":
    st.header("Báo cáo Giám sát Toàn diện Hệ thống Mô phỏng")
    st.markdown("Số liệu phục vụ nghiệm thu PoC của đề tài:")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng số ca theo dõi", len(pd.read_sql("SELECT student_id FROM students", conn)))
    c2.metric("Mục tiêu IEP đang chạy", len(pd.read_sql("SELECT plan_id FROM iep_plans", conn)))
    c3.metric("Số bản ghi tiến triển", len(pd.read_sql("SELECT id FROM progress_logs", conn)))
    
    st.subheader("Toàn bộ 6 ca bệnh giả định chuẩn (Benchmark Profiles)")
    st.dataframe(pd.read_sql("SELECT * FROM students", conn), use_container_width=True)
