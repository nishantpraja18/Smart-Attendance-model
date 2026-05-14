import streamlit as st
from nanc import run_attendance , show_record

# ================= PAGE CONFIG =================

st.set_page_config(page_title="Smart Attendance System",layout="wide")

# ================= CUSTOM UI =================

st.markdown("""
<style>

/* ================= SIMPLE DARK BACKGROUND ================= */

.stApp {
    background: linear-gradient(
        135deg,
        #0f172a,
        #1e293b,
        #0f172a
    );
}

/* ================= HEADER BOX ================= */

.main-box {
    background: rgba(255,255,255,0.08);
    padding: 35px;
    border-radius: 25px;
    backdrop-filter: blur(8px);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.45);
    margin-bottom: 25px;
}

/* ================= MAIN TITLE ================= */

.big-title {
    font-size: 55px;
    font-weight: 800;
    text-align: center;
    color: white;
}

/* ================= SUB TITLE ================= */

.sub-title {
    font-size: 22px;
    text-align: center;
    color: #E5E7EB;
}

/* ================= STATUS BOX ================= */

.status-box {
    background: rgba(17,24,39,0.85);
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    font-size: 22px;
    color: white;
    margin-top: 20px;
    border: 1px solid #374151;
    backdrop-filter: blur(5px);
    box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
}

/* ================= BUTTON ================= */

div.stButton > button {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 14px;
    font-size: 20px;
    font-weight: bold;
    transition: 0.3s;
    width: 100%;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.25);
}

div.stButton > button:hover {
    transform: scale(1.03);
    background: linear-gradient(90deg,#0072ff,#00c6ff);
}

/* ================= TAB DESIGN ================= */

.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
}

.stTabs [data-baseweb="tab"] {
    background-color: rgba(255,255,255,0.1);
    border-radius: 12px;
    color: white;
    padding: 12px 25px;
    font-size: 18px;
    font-weight: bold;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
}

/* ================= DATAFRAME ================= */

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.08);
    border-radius: 15px;
    padding: 10px;
}

/* ================= TEXT COLOR ================= */

label, .stMarkdown, .stText {
    color: white !important;
}

/* ================= HIDE STREAMLIT MENU ================= */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================

st.markdown("""
<div class="main-box">

<div class="big-title">
🎓 SMART ATTENDANCE SYSTEM
</div>

<div class="sub-title">
Face Recognition + Eye Blink + Voice Verification
</div>

</div>
""", unsafe_allow_html=True)

# ================= TABS =================

tab1, tab2 = st.tabs([ "🎯 Attendance System", "📊 Attendance Records"])

# ================= TAB 1 =================

with tab1:

    # ================= SESSION =================

    if "step" not in st.session_state:
        st.session_state.step = 0

    if "name" not in st.session_state:
        st.session_state.name = None

    if "blink" not in st.session_state:
        st.session_state.blink = 0

    # ================= BUTTONS =================

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🚀 Start Attendance",
            use_container_width=True
        ):
            st.session_state.step = 1

    with col2:

        if st.button("🔄 Restart System",use_container_width=True):

            st.session_state.step = 0
            st.session_state.name = None
            st.session_state.blink = 0

            st.success( "✅ System Restarted Successfully")

            st.rerun()

    # ================= STATUS =================

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.step == 0:

        st.markdown("""
        <div class="status-box">
        🟢 System Ready For Attendance
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.step == 1:

        st.markdown("""
        <div class="status-box">
        📸 Face Verification Running...
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.step == 2:

        st.markdown("""
        <div class="status-box">
        👁 Blink Detection Running...
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.step == 3:

        st.markdown("""
        <div class="status-box">
        🎤 Voice Verification Running...
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.step == 4:

        st.markdown("""
        <div class="status-box">
        ✅ Attendance Successfully Marked
        </div>
        """, unsafe_allow_html=True)

    # ================= RUN BACKEND =================

    run_attendance()

# ================= TAB 2 =================

with tab2:

    st.markdown("""<div class="main-box"><div class="big-title" style="font-size:40px;"> 📊 Attendance Records
        </div>
        <div class="sub-title">
            Student Attendance Database
        </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="status-box">
        📁 All Student Attendance Records
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    show_record()

    # ================= SHOW RECORDS =================   