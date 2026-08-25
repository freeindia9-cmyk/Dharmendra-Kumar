import streamlit as st
import pandas as pd
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import random

# 1. Page Configuration
st.set_page_config(
    page_title="CRM Pro Bulk Dispatcher",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS (Floating Header, Pulsing Logo Frame, Glassmorphism Cards)
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

# Live Counters State Initialization
if 'sent_count' not in st.session_state:
    st.session_state['sent_count'] = 0
if 'failed_count' not in st.session_state:
    st.session_state['failed_count'] = 0

# 4. Sidebar Controls
with st.sidebar:
    st.markdown("### 🖼️ Company Branding")
    logo_file = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])

    st.divider()

    st.markdown("### 🔑 SMTP Server Connection")
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)
    sender_email = st.text_input("Sender Email ID", placeholder="your_email@gmail.com")
    app_password = st.text_input("16-Digit App Password", type="password")
    dispatch_delay = st.slider("Dispatch Rate Delay (Seconds)", 0.5, 5.0, 1.0)

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
        st.session_state['sent_count'] = 0
        st.session_state['failed_count'] = 0
        st.success(f"✅ Successfully imported {len(new_df)} records from file!")
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

df = st.session_state['crm_data']
total_records = len(df)
pending_records = total_records - (st.session_state['sent_count'] + st.session_state['failed_count'])

# 7. Live Counters Section
st.markdown("### 📊 Live Processing Counters")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Queue</div><div class="metric-value">{total_records}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Sent Success</div><div class="metric-value" style="color:#4ade80;">{st.session_state["sent_count"]}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Failed Bounces</div><div class="metric-value" style="color:#f87171;">{st.session_state["failed_count"]}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Pending</div><div class="metric-value" style="color:#fbbf24;">{max(0, pending_records)}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# 8. Data Preview Table
st.markdown(f"### 📋 Dispatch Records Preview ({len(df)} Records Available)")
st.dataframe(df, use_container_width=True, height=380)

# 9. Real SMTP Bulk Email Dispatching Logic with Stop Control
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
    st.session_state['sent_count'] = 0
    st.session_state['failed_count'] = 0

    if not sender_email or not app_password:
        st.warning("⚠️ Kripya sidebar me Sender Email ID aur 16-digit App Password enter karein!")
    else:
        st.markdown("---")
        st.markdown("### 📡 Live Progress Monitor")
        progress_bar = st.progress(0)
        status_box = st.empty()

        try:
            # Login to SMTP Server
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls()
            server.login(sender_email, app_password)

            for idx in range(len(df)):
                if st.session_state['stop_dispatch']:
                    st.error("🛑 Dispatching process manually stopped by user!")
                    break

                row = df.iloc[idx]
                target_email = str(row.get('Email', '')).strip()

                if "@" in target_email:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = sender_email
                    msg['To'] = target_email
                    msg['Subject'] = f"Dispatch Invoice Update - #{row.get('Invoice Number', 'N/A')}"

                    # HTML Template for High Deliverability (Primary Inbox Landing)
                    body_html = f"""
                    <html>
                      <body style="font-family: Arial, sans-serif; color: #1e293b; line-height: 1.6;">
                        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff;">
                          <h2 style="color: #4f46e5; margin-bottom: 5px;">Dispatch Update Notification</h2>
                          <p style="color: #64748b; font-size: 14px;">Automated Dispatch Notice</p>
                          <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">
                          <p>Dear <b>{row.get('Name', 'Customer')}</b>,</p>
                          <p>Your dispatch shipment details have been generated successfully:</p>
                          <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                            <tr style="background-color: #f8fafc;">
                              <td style="padding: 10px; border: 1px solid #cbd5e1;"><b>Invoice Number</b></td>
                              <td style="padding: 10px; border: 1px solid #cbd5e1;">{row.get('Invoice Number', 'N/A')}</td>
                            </tr>
                            <tr>
                              <td style="padding: 10px; border: 1px solid #cbd5e1;"><b>Dispatch Date</b></td>
                              <td style="padding: 10px; border: 1px solid #cbd5e1;">{row.get('Dispatch Date', 'N/A')}</td>
                            </tr>
                            <tr style="background-color: #f8fafc;">
                              <td style="padding: 10px; border: 1px solid #cbd5e1;"><b>Transporter</b></td>
                              <td style="padding: 10px; border: 1px solid #cbd5e1;">{row.get('Transporter Name', 'N/A')}</td>
                            </tr>
                            <tr>
                              <td style="padding: 10px; border: 1px solid #cbd5e1;"><b>Quantity / Cases</b></td>
                              <td style="padding: 10px; border: 1px solid #cbd5e1;">{row.get('Stock Qty', 'N/A')} ({row.get('Number of Case', 'N/A')} Cases)</td>
                            </tr>
                          </table>
                          <p style="margin-top: 20px;">Thank you for your business!</p>
                          <hr style="border: 0; border-top: 1px solid #e2e8f0; margin-top: 20px;">
                          <p style="font-size: 11px; color: #94a3b8; text-align: center;">This is an automated system dispatch email.</p>
                        </div>
                      </body>
                    </html>
                    """
                    msg.attach(MIMEText(body_html, 'html'))

                    try:
                        server.sendmail(sender_email, target_email, msg.as_string())
                        st.session_state['sent_count'] += 1
                        status_box.markdown(f"✅ Mail Sent to: **{row.get('Name', 'Customer')}** (`{target_email}`) | Invoice: `{row.get('Invoice Number', 'N/A')}`")
                    except Exception as send_err:
                        st.session_state['failed_count'] += 1
                        status_box.markdown(f"❌ Failed sending to: `{target_email}`")
                else:
                    st.session_state['failed_count'] += 1

                pct = (idx + 1) / len(df)
                progress_bar.progress(pct)
                time.sleep(dispatch_delay)

            server.quit()
            if not st.session_state['stop_dispatch']:
                st.balloons()
                st.success("🎉 All bulk dispatch emails processed and dispatched successfully!")

        except Exception as smtp_err:
            st.error(f"❌ SMTP Server Connection Error: {smtp_err}. Please check your Sender Email ID and 16-digit App Password.")
