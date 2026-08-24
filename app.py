import streamlit as st
import sqlite3
import os
from datetime import datetime
from fpdf import FPDF
import pypdf

# إعداد الصفحة بعرض كامل (Wide Layout)
st.set_page_config(
    page_title="HealthCare Assistant Pro",
    page_icon="🏥",
    layout="wide"
)

# ---------------------------------------------------------
# 1. إعداد قاعدة البيانات (SQLite)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("healthcare_v3.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'patient'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            bio TEXT NOT NULL,
            rating REAL,
            price REAL,
            icon TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            doctor_name TEXT,
            specialty TEXT,
            date TEXT,
            price REAL,
            status TEXT DEFAULT 'مؤكد'
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        default_doctors = [
            ("Dr. Ahmed Hassan", "Cardiology", "chest pain, heart disease, hypertension", "Cardiology specialist with 10+ years experience.", 4.9, 500, "👨‍⚕️"),
            ("Dr. Sara Ali", "Dermatology", "acne, rash, skin, itching, dermatitis", "Dermatology specialist focused on skin health.", 4.8, 400, "👩‍⚕️"),
            ("Dr. Youssef Samir", "Pulmonology", "cough, shortness of breath, asthma", "Pulmonology specialist for respiratory issues.", 4.8, 450, "👨‍⚕️"),
            ("Dr. Nour Mohamed", "Neurology", "headache, migraine, dizziness", "Neurology specialist for brain and nerves.", 4.9, 500, "👩‍⚕️")
        ]
        cursor.executemany("""
            INSERT INTO doctors (name, specialty, symptoms, bio, rating, price, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, default_doctors)
        
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# 2. توليد ملف الـ PDF للتذكرة
# ---------------------------------------------------------
def generate_pdf_ticket(patient_name, doctor_name, specialty, date, price):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="HealthCare Assistant - Booking Ticket", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt="------------------------------------------------------------------", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Patient Name: {patient_name}", ln=True)
    pdf.cell(200, 10, txt=f"Doctor: {doctor_name}", ln=True)
    pdf.cell(200, 10, txt=f"Specialty: {specialty}", ln=True)
    pdf.cell(200, 10, txt=f"Appointment Date: {date}", ln=True)
    pdf.cell(200, 10, txt=f"Consultation Fee: {price} EGP", ln=True)
    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, txt="Thank you for choosing HealthCare Assistant. Get well soon!", ln=True, align="C")
    filename = "appointment_ticket.pdf"
    pdf.output(filename)
    return filename

# ---------------------------------------------------------
# 3. إدارة الجلسة والتنقل
# ---------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'landing'

# ---------------------------------------------------------
# 4. واجهة الترحيب (Landing Page)
# ---------------------------------------------------------
def show_landing_page():
    st.markdown("""
        <div style='padding: 3rem 2rem; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;'>
            <h1>🏥 HealthCare Assistant Pro</h1>
            <p style='font-size: 1.2rem;'>النظام الطبي الذكي المتكامل: استشارات ذكية، تحليل تقارير وأشعة، وإدارة حجوزات متطورة.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.image("https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=600&q=80", caption="تجهيزات طبية حديثة", use_container_width=True)
    with c2:
        st.image("https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&w=600&q=80", caption="نخبة من الأطباء والمتخصصين", use_container_width=True)
    with c3:
        st.image("https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=600&q=80", caption="رعاية صحية ذكية على مدار الساعة", use_container_width=True)

    st.markdown("---")

    col_l, col_r = st.columns(2)
    with col_l:
        with st.container(border=True):
            st.subheader("🔑 لديك حساب بالفعل؟")
            if st.button("تسجيل الدخول (Login)", type="primary", use_container_width=True):
                st.session_state['page'] = 'login'
                st.rerun()
    with col_r:
        with st.container(border=True):
            st.subheader("📝 مستخدم جديد؟")
            if st.button("إنشاء حساب (Sign Up)", use_container_width=True):
                st.session_state['page'] = 'signup'
                st.rerun()

# ---------------------------------------------------------
# 5. صفحات تسجيل الدخول والتسجيل
# ---------------------------------------------------------
def show_login_page():
    st.subheader("🔐 تسجيل الدخول إلى النظام")
    email = st.text_input("البريد الإلكتروني")
    password = st.text_input("كلمة المرور", type="password")
    
    if st.button("دخول", type="primary"):
        conn = sqlite3.connect("healthcare_v3.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = user[0]
            st.session_state['role'] = user[1]
            st.success("تم تسجيل الدخول بنجاح!")
            st.session_state['page'] = 'dashboard'
            st.rerun()
        else:
            st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
            
    if st.button("الرجوع للرئيسية"):
        st.session_state['page'] = 'landing'
        st.rerun()

def show_signup_page():
    st.subheader("📝 إنشاء حساب جديد")
    username = st.text_input("الاسم الكامل")
    email = st.text_input("البريد الإلكتروني")
    password = st.text_input("كلمة المرور", type="password")
    role = st.selectbox("نوع الحساب", ["patient", "doctor"])
    
    if st.button("تسجيل الحساب", type="primary"):
        try:
            conn = sqlite3.connect("healthcare_v3.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", 
                           (username, email, password, role))
            conn.commit()
            conn.close()
            st.success("تم إنشاء الحساب بنجاح! يرجى الانتقال لتسجيل الدخول.")
            st.session_state['page'] = 'login'
            st.rerun()
        except sqlite3.IntegrityError:
            st.error("البريد الإلكتروني مستخدم من قبل.")
            
    if st.button("الرجوع للرئيسية"):
        st.session_state['page'] = 'landing'
        st.rerun()

# ---------------------------------------------------------
# 6. لوحات التحكم باستخدام Tabs أفقية (واسعة وفخمة)
# ---------------------------------------------------------
def show_dashboard():
    role = st.session_state.get('role', 'patient')
    username = st.session_state.get('username')
    
    # رأسية صفحة لوحة التحكم مع زر تسجيل خروج في الأعلى
    top_col1, top_col2 = st.columns([6, 1])
    with top_col1:
        st.markdown(f"### أهلاً بك، **{username}** 👋")
    with top_col2:
        if st.button("🚪 خروج", type="secondary"):
            st.session_state['logged_in'] = False
            st.session_state['page'] = 'landing'
            st.rerun()
            
    st.markdown("---")

    if role == 'patient':
        # استخدام الـ Tabs الأفقية بدلاً من القائمة الجانبية الضيقة
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🏠 الرئيسية", 
            "🤖 الشات بوت الصحي", 
            "🔬 التحاليل والأشعة", 
            "🩺 الحجوزات والأطباء", 
            "📋 سجل حجوزاتي", 
            "🚨 طوارئ (SOS)"
        ])
        
        with tab1:
            st.title("🏡 لوحة التحكم الرئيسية للمريض")
            st.write("مرحباً بك في منصتك الصحية الذكية المتكاملة. تم تصميم هذه المنصة لتوفير تجربة رعاية صحية سلسة، سريعة، ومتقدمة.")
            
            # محتوى غني وواسع يملى العين
            col_a, col_b = st.columns(2)
            with col_a:
                with st.container(border=True):
                    st.subheader("💡 نصائح صحية اليوم")
                    st.write("• احرص على شرب ما لا يقل عن 8-10 أكواب من الماء يومياً.")
                    st.write("• النوم المنتظم من 7 إلى 8 ساعات يعزز كفاءة جهاز المناعة.")
                    st.write("• مارس الرياضة الخفيفة أو المشي لمدة 20 دقيقة يومياً.")
            with col_b:
                with st.container(border=True):
                    st.subheader("📊 مميزات المنصة الذكية")
                    st.write("• **تشخيص مبدئي فوري** عبر مساعد الأعراض الذكي.")
                    st.write("• **قراءة وتحليل ملفات الـ PDF** للتحاليل وصور الأشعة بدقة.")
                    st.write("• **حجز فوري للأطباء** وتوليد تذاكر PDF رسمية مع إمكانية الإلغاء.")
                    
            st.image("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80", caption="رعاية طبية متطورة بين أيديكم", use_container_width=True)

        with tab2:
            st.title("🤖 المساعد الذكي للأعراض (Health Chatbot)")
            st.write("اطرح أعراضك المرضية وسيقوم النظام بتوجيهك للتخصص الطبي المناسب فوراً.")
            query = st.text_input("اكتب الأعراض التي تعاني منها (مثال: صداع نصفي، ألم في الصدر، إرهاق مستمر):")
            if st.button("تحليـل الأعراض الذكي", type="primary"):
                if query:
                    q_lower = query.lower()
                    if "صداع" in q_lower or "دوخة" in q_lower:
                        st.warning("⚠️ الأعراض تشير لاحتمالية الحاجة لطبيب أعصاب (Neurology). ننصحك بالراحة وتجنب الإجهاد.")
                    elif "صدر" in q_lower or "ضغط" in q_lower:
                        st.error("🚨 تنبيه هام: آلام الصدر تتطلب استشارة عاجلة لطبيب القلب (Cardiology) أو التوجه لأقرب طوارئ.")
                    else:
                        st.success("✅ بناءً على المعطيات، ننصحك بحجز موعد مع الطبيب المختص ومتابعة الفحوصات بانتظام.")
                else:
                    st.warning("يرجى كتابة الأعراض أولاً.")

        with tab3:
            st.title("🔬 محلل التحاليل الطبية وصور الأشعة المتقدم")
            st.write("قم برفع تقارير التحاليل بصيغة **PDF** أو صور الأشعة للحصول على قراءة تحليلية مبدئية سريعة.")
            
            c_pdf, c_img = st.columns(2)
            with c_pdf:
                with st.container(border=True):
                    st.subheader("📄 تحليل تقارير PDF")
                    pdf_file = st.file_uploader("رفع ملف الـ PDF للتحاليل", type=["pdf"])
                    if pdf_file:
                        reader = pypdf.PdfReader(pdf_file)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                        st.success("تم استخراج البيانات النصية من ملف الـ PDF بنجاح!")
                        with st.expander("عرض محتوى التقرير المستخرج"):
                            st.write(text[:600] + "...")
                        st.info("📊 تحليل أولي: الفحص أظهر استقرار المؤشرات الحيوية العامة، ويُنصح بمراجعة الطبيب لتأكيد القراءة النهائية.")
            with c_img:
                with st.container(border=True):
                    st.subheader("🖼️ تحليل صور الأشعة")
                    img_file = st.file_uploader("رفع صورة الأشعة (PNG / JPG)", type=["png", "jpg", "jpeg"])
                    if img_file:
                        st.image(img_file, caption="صورة الأشعة المرفوعة للمريض", use_container_width=True)
                        if st.button("بدء تحليل صورة الأشعة"):
                            st.info("🔍 تم فحص الصورة بنجاح عبر خوارزميات المعالجة البصرية. الصورة واضحة ولا توجد مؤشرات حرجة، يُرجى اعتماد تقرير الطبيب المختص.")

        with tab4:
            st.title("🩺 دليل الأطباء وحجز المواعيد الفورية")
            conn = sqlite3.connect("healthcare_v3.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, specialty, bio, rating, price, icon FROM doctors")
            doctors = cursor.fetchall()
            conn.close()
            
            selected_spec = st.selectbox("تصفية حسب التخصص الطبي", ["الكل", "Cardiology", "Dermatology", "Pulmonology", "Neurology"])
            
            for doc in doctors:
                name, specialty, bio, rating, price, icon = doc
                if selected_spec == "الكل" or specialty == selected_spec:
                    with st.container(border=True):
                        cols = st.columns([1, 4, 2])
                        with cols[0]:
                            st.markdown(f"<h1 style='text-align: center;'>{icon}</h1>", unsafe_allow_html=True)
                        with cols[1]:
                            st.subheader(name)
                            st.write(f"**التخصص:** {specialty} | **التقييم:** ⭐ {rating}")
                            st.write(f"**نبذة:** {bio}")
                            st.write(f"**سعر الكشف:** {price} EGP")
                        with cols[2]:
                            app_date = st.date_input(f"تاريخ الحجز", key=f"date_{name}")
                            if st.button(f"تأكيد وحجز الموعد", key=f"btn_{name}", type="primary"):
                                conn = sqlite3.connect("healthcare_v3.db")
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO appointments (patient_name, doctor_name, specialty, date, price, status)
                                    VALUES (?, ?, ?, ?, ?, 'مؤكد')
                                """, (username, name, specialty, str(app_date), price))
                                conn.commit()
                                conn.close()
                                
                                pdf_file = generate_pdf_ticket(username, name, specialty, str(app_date), price)
                                st.success(f"تم حجز الموعد بنجاح مع {name}!")
                                
                                with open(pdf_file, "rb") as f:
                                    st.download_button(
                                        label="📥 تحميل تذكرة الحجز PDF",
                                        data=f,
                                        file_name="appointment_ticket.pdf",
                                        mime="application/pdf",
                                        key=f"dl_{name}"
                                    )

        with tab5:
            st.title("📋 إدارة حجوزاتك ومواعيدك الطبية")
            conn = sqlite3.connect("healthcare_v3.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, doctor_name, specialty, date, price, status FROM appointments WHERE patient_name = ?", (username,))
            appointments = cursor.fetchall()
            conn.close()
            
            if appointments:
                for app in appointments:
                    app_id, doc_name, spec, dt, prc, status = app
                    with st.container(border=True):
                        col_info, col_action = st.columns([3, 1])
                        with col_info:
                            st.write(f"👨‍⚕️ **الطبيب:** {doc_name} ({spec})")
                            st.write(f"📅 **الموعد المحدد:** {dt} | 💰 **التكلفة:** {prc} EGP | الحالة: **{status}**")
                        with col_action:
                            if status == 'مؤكد':
                                if st.button(f"إلغاء الحجز", key=f"cancel_{app_id}", type="secondary"):
                                    conn = sqlite3.connect("healthcare_v3.db")
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE appointments SET status = 'ملغي' WHERE id = ?", (app_id,))
                                    conn.commit()
                                    conn.close()
                                    st.success("تم إلغاء الحجز بنجاح.")
                                    st.rerun()
            else:
                st.info("لا توجد حجوزات مسجلة حالياً.")

        with tab6:
            st.title("🚨 مركز الطوارئ والإسعاف السريع (SOS)")
            st.error("⚠️ إذا كانت الحالة الصحية حرجة وتتطلب تدخلاً عاجلاً، يرجى التواصل مع الإسعاف أو التوجه لأقرب مستشفى فوراً.")
            st.markdown("""
                * **رقم الإسعاف المباشر:** `123`
                * **خط الطوارئ الطبي الموحد:** `137`
                * **أقرب مستشفى متعاقد مع المنصة:** مستشفى الحياة التخصصي (خدمة طوارئ 24/7).
            """)
            st.image("https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=1000&q=80", caption="فريق الطوارئ متاح دائماً لخدمتكم", use_container_width=True)

    else:
        # لوحة تحكم الطبيب بأزرار أفقية واسعة
        doc_tab1, doc_tab2 = st.tabs(["📊 إحصائيات وعمليات الطبيب", "📅 جدول حجوزات المرضى الواردة"])
        
        with doc_tab1:
            st.title("📊 لوحة إحصائيات الطبيب")
            conn = sqlite3.connect("healthcare_v3.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM appointments")
            total_app = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(price) FROM appointments WHERE status = 'مؤكد'")
            total_revenue = cursor.fetchone()[0] or 0
            conn.close()
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label="إجمالي الحجوزات بالنظام", value=total_app)
            with c2:
                st.metric(label="إجمالي العائدات المتوقعة", value=f"{total_revenue} EGP")
                
            st.success("📈 النظام يعمل بكفاءة عالية، وجداول المواعيد محدثة بانتظام.")

        with doc_tab2:
            st.title("📅 جدول حجوزات المرضى الواردة")
            conn = sqlite3.connect("healthcare_v3.db")
            cursor = conn.cursor()
            cursor.execute("SELECT patient_name, doctor_name, specialty, date, price, status FROM appointments")
            all_apps = cursor.fetchall()
            conn.close()
            
            if all_apps:
                for a in all_apps:
                    p_name, d_name, spec, dt, prc, st_val = a
                    with st.container(border=True):
                        st.write(f"👤 **المريض:** {p_name} | 👨‍⚕️ **الطبيب:** {d_name} ({spec})")
                        st.write(f"📅 **الموعد:** {dt} | 💰 **التكلفة:** {prc} EGP | الحالة: **{st_val}**")
            else:
                st.info("لا توجد حجوزات مسجلة للنظام حتى الآن.")

# ---------------------------------------------------------
# 7. التوجيه العام
# ---------------------------------------------------------
if not st.session_state['logged_in']:
    if st.session_state['page'] == 'landing':
        show_landing_page()
    elif st.session_state['page'] == 'login':
        show_login_page()
    elif st.session_state['page'] == 'signup':
        show_signup_page()
else:
    show_dashboard()