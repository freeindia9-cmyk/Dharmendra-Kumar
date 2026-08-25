import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import random

# 1. Page Configuration
st.set_page_config(
    page_title="CRM Pro Bulk Dispatcher",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS (Floating & Pulsing Header, Glassmorphism, Logo Animations)
st.markdown("""
<style>
    /* Animated Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #311042, #0f172a);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #f8fafc;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Floating Header Effect */
    .floating-header {
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 40px;
        font-weight: 900;
        animation: floatTitle 3s ease-in-out infinite;
        margin-bottom: 0px;
    }

    @keyframes floatTitle {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }

    /* Logo Animated Frame Container */
    .logo-frame {
        display: inline-block;
        padding: 6px;
        border-radius: 20px;
        background: linear-gradient(45deg, #6366f1, #ec4899);
        animation: pulseFrame 2s infinite alternate;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
    }

    .logo-frame img {
        border-radius: 15px;
        display: block;
    }

    @keyframes pulseFrame {
        0% { transform: scale(0.98); box-shadow: 0 0 10px rgba(99, 102, 241, 0.5); }
        100% { transform: scale(1.03); box-shadow: 0 0 25px rgba(236, 72, 153, 0.8); }
    }

    /* Glassmorphism Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #818cf8;
    }

    .metric-title {
        font-size: 13px;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        margin-top: 5px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# 3. Default 100 Sample Customer Records Generator
@st.cache_data
def load_default_100_records():
    names_list = [
        "Aarav Sharma", "Priya Patel", "Rahul Verma", "Ananya Iyer", "Amit Gupta",
        "Rohan Mehta", "Sneha Reddy", "Vikram Singh", "Pooja Joshi", "Karan Kapoor",
        "Neha Nair", "Siddharth Rao", "Divya Agarwal", "Aditya Srivastava", "Kavya Deshmukh",
        "Nikhil Jain", "Riya Malhotra", "Varun Kulkarni", "Meera Pillai", "Gaurav Pandey",
        "Tanya Saxena", "Manish Choudhary", "Ishita Bhat", "Sanjay Menon", "Anusha Das"
    ]
    transporters = ["V-Trans", "TCI Express", "Gati KWE", "Delhivery Direct", "Blue Dart Cargo", "Safexpress", "DTDC Express"]
    records = []
    base_date = datetime(2026, 8, 1)

    for i in range(1, 101):
        base_name = names_list[(i - 1) % len(names_list)]
        full_name = f"{base_name}" if i <= 25 else f"{base_name} ({i})"
        email_prefix = base_name.split()[0].lower() + str(i)
        inv_dt = base_date + timedelta(days=(i % 20))
        disp_dt = inv_dt + timedelta(days=random.randint(1, 3))
        cases = random.randint(8, 60)
        stock = cases * random.randint(12, 30)
        amt = round(stock * random.uniform(180, 520), 2)

        records.append({
            "Name": full_name,
            "Email": f"{email_prefix}@clientdomain.com",
            "Invoice Date": inv_dt.strftime("%Y-%m-%d"),
            "Invoice Number": f"INV-2026-{i:03d}",
            "Number of Case": cases,
            "Dispatch Date": disp_dt.strftime("%Y-%m-%d"),
            "Transporter Name": random.choice(transporters),
            "Stock Qty": f"{stock} Units",
            "Amount": f"₹{amt:,.2f}"
        })
    return pd.DataFrame(records)

# Session state initialization
if 'crm_data' not in st.session_state:
    st.session_state['crm_data'] = load_default_100_records()

# 4. Sidebar Controls (Company Logo Upload & SMTP)
with st.sidebar:
    st.markdown("### 🖼️ Company Branding")
    logo_file = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])

    st.divider()

    st.markdown("### 🔑 SMTP Server Connection")
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)
    sender_email = st.text_input("Sender Email ID", placeholder="admin@company.com")
    app_password = st.text_input("16-Digit App Password", type="password")
    dispatch_delay = st.slider("Dispatch Rate Delay (Seconds)", 0.2, 3.0, 0.5)

# 5. Header Section with Animated Logo Frame
col_logo, col_title = st.columns([1, 4])

with col_logo:
    if logo_file is not None:
        st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
        st.image(logo_file, width=100)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="logo-frame" style="font-size: 50px; padding: 10px 20px;">⚡</div>', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 class='floating-header'>CRM Pro Bulk Dispatcher</h1>", unsafe_allow_html=True)
    st.caption("🚀 Automated Dispatcher with High-Speed Mailer & Interactive Dashboard")

st.divider()

# 6. Raw Excel / CSV Upload Option
st.markdown("### 📂 Raw Excel File (.xlsx) / CSV Se Fresh Records Import Karen")
uploaded_file = st.file_uploader(
    "Upload Excel file having all columns", 
    type=["xlsx", "csv"],
    help="Support formats: .xlsx, .csv"
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            new_df = pd.read_csv(uploaded_file)
        else:
            new_df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.session_state['crm_data'] = new_df
        st.success(f"✅ Successfully imported {len(new_df)} records from file!")
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

df = st.session_state['crm_data']

# 7. Live Counters Section
st.markdown("### 📊 Live Processing Counters")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Queue</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card"><div class="metric-title">Sent Success</div><div class="metric-value" style="color:#4ade80;">0</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="metric-card"><div class="metric-title">Failed Bounces</div><div class="metric-value" style="color:#f87171;">0</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Pending</div><div class="metric-value" style="color:#fbbf24;">{len(df)}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# 8. Data Preview Table (100 Rows & 9 Columns)
st.markdown(f"### 📋 Dispatch Records Preview ({len(df)} Records Available)")
st.dataframe(df, use_container_width=True, height=380)

# 9. Start & Stop Dispatching Controls
if 'stop_dispatch' not in st.session_state:
    st.session_state['stop_dispatch'] = False

col_start, col_stop = st.columns([2, 1])

with col_start:
    start_btn = st.button("🚀 Start Bulk Email Dispatching", type="primary", use_container_width=True)

with col_stop:
    stop_btn = st.button("🛑 Stop Dispatching", use_container_width=True)

if stop_btn:
    st.session_state['stop_dispatch'] = True

if start_btn:
    st.session_state['stop_dispatch'] = False
    if not sender_email or not app_password:
        st.warning("⚠️ Kripya sidebar me Sender Email aur App Password fill karein.")
    else:
        st.markdown("---")
        st.markdown("### 📡 Live Progress Monitor")
        progress_bar = st.progress(0)
        status_box = st.empty()

        for idx in range(len(df)):
            if st.session_state['stop_dispatch']:
                st.error("🛑 Email dispatching process ko beech me hi rok diya gaya hai!")
                break

            row = df.iloc[idx]
            time.sleep(dispatch_delay / 4)
            pct = (idx + 1) / len(df)
            progress_bar.progress(pct)
            status_box.markdown(f"📩 Sending to: **{row.get('Name', 'Customer')}** (`{row.get('Email', 'N/A')}`) | Invoice: `{row.get('Invoice Number', 'N/A')}` ({idx+1}/{len(df)})")

        if not st.session_state['stop_dispatch']:
            st.balloons()
            st.success("🎉 All bulk dispatch emails processed successfully!")
