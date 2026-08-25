import streamlit as st
import pandas as pd
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import random

# 1. Ultra 4K Page Configuration
st.set_page_config(
    page_title="CRM Pro Bulk Dispatcher 4K Ultra",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 4K Ultra CSS Styling with Dynamic Visual Effects
st.markdown("""
<style>
    /* Global 4K Ultra Background with Dynamic Gradient */
    .stApp {
        background: linear-gradient(-45deg, #020617, #0f172a, #1e1b4b, #2e1065, #020617);
        background-size: 400% 400%;
        animation: gradientBG 12s ease infinite;
        color: #f8fafc;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Dynamic Dynamic Title Effect */
    .floating-header {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc, #f472b6);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 48px;
        font-weight: 900;
        letter-spacing: -1px;
        animation: gradientShift 6s ease infinite, floatTitle 3s ease-in-out infinite;
        margin-bottom: 0px;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes floatTitle {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
        100% { transform: translateY(0px); }
    }

    /* Glowing Dynamic Logo Frame */
    .logo-frame {
        display: inline-block;
        padding: 8px;
        border-radius: 24px;
        background: linear-gradient(135deg, #38bdf8, #c084fc, #f472b6);
        animation: pulse4K 2.5s infinite alternate;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.6);
    }

    @keyframes pulse4K {
        0% { transform: scale(0.97); box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
        100% { transform: scale(1.03); box-shadow: 0 0 35px rgba(244, 114, 182, 0.9); }
    }

    /* 4K Glassmorphism Neon Metric Cards */
    .metric-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 22px;
        text-align: center;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: #38bdf8;
        box-shadow: 0 15px 45px rgba(56, 189, 248, 0.35);
    }

    .metric-title {
        font-size: 14px;
        color: #94a3b8;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .metric-value {
        font-size: 36px;
        font-weight: 900;
        margin-top: 8px;
        background: linear-gradient(90deg, #38bdf8, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Smart Robust Helper Function for Column Value Extraction
def get_field_value(row, possible_keys, default_val="N/A"):
    for key in possible_keys:
        for col in row.index:
            if str(col).strip().lower() == str(key).strip().lower():
                val = str(row[col]).strip()
                if val and val.lower() != "nan" and val.lower() != "none":
                    return val
    return default_val

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

# Session State Initialization
if 'crm_data' not in st.session_state:
    st.session_state['crm_data'] = load_default_100_records()
if 'sent_count' not in st.session_state:
    st.session_state['sent_count'] = 0
if 'failed_count' not in st.session_state:
    st.session_state['failed_count'] = 0

# 4. Sidebar Controls
with st.sidebar:
    st.markdown("### 🖼️ 4K Branding Studio")
    logo_file = st.file_uploader("Upload High-Res Logo", type=["png", "jpg", "jpeg"])

    st.divider()

    st.markdown("### 🔑 Secure SMTP Engine")
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)
    sender_email = st.text_input("Sender Email ID", placeholder="your_email@gmail.com")
    app_password = st.text_input("16-Digit App Password", type="password")
    dispatch_delay = st.slider("Dispatch Rate Delay (Seconds)", 0.5, 5.0, 1.0)

# 5. Dynamic Header Section
col_logo, col_title = st.columns([1, 5])

with col_logo:
    if logo_file is not None:
        st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
        st.image(logo_file, width=110)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="logo-frame" style="font-size: 55px; padding: 12px 24px;">⚡</div>', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 class='floating-header'>CRM Pro Bulk Dispatcher 4K</h1>", unsafe_allow_html=True)
    st.caption("✨ Ultra-Fast Automated Dispatcher with High-Speed Mailer & Live Dynamic Grid")

st.divider()

# 6. Excel/CSV Import
st.markdown("### 📂 Raw Excel / CSV Import (Data Preserved)")
uploaded_file = st.file_uploader(
    "Upload fresh Excel file to replace or update active queue", 
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
        st.success(f"✅ Successfully loaded {len(new_df)} records from file!")
    except Exception as e:
        st.error(f"❌ File loading failed: {e}")

# 7. Live 4K Dynamic Counters
df = st.session_state['crm_data']
total_records = len(df)
pending_records = total_records - (st.session_state['sent_count'] + st.session_state['failed_count'])

st.markdown("### 📊 4K Live Processing Dashboard")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Records</div><div class="metric-value">{total_records}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Sent Success</div><div class="metric-value" style="color:#4ade80;">{st.session_state["sent_count"]}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Failed / Bounces</div><div class="metric-value" style="color:#f87171;">{st.session_state["failed_count"]}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Queue Pending</div><div class="metric-value" style="color:#fbbf24;">{max(0, pending_records)}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# 8. Live Editable Data Table Grid
st.markdown(f"### ✏️ Interactive Live Grid ({len(df)} Records Ready)")
st.caption("💡 Tip: Double click any cell to instantly modify Name, Email, Invoice Number, or Transporter Name.")

edited_df = st.data_editor(
    st.session_state['crm_data'],
    num_rows="dynamic",
    use_container_width=True,
    height=420,
    key="data_editor_4k"
)

st.session_state['crm_data'] = edited_df
df = st.session_state['crm_data']

# 9. Smart Dispatch Engine with Guaranteed Transporter Inclusion
if 'stop_dispatch' not in st.session_state:
    st.session_state['stop_dispatch'] = False

col_start, col_stop = st.columns([2, 1])

with col_start:
    start_btn = st.button("🚀 Launch Bulk Email Dispatching", type="primary", use_container_width=True)

with col_stop:
    stop_btn = st.button("🛑 Emergency Stop", use_container_width=True)

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
        st.markdown("### 📡 Real-time Dispatch Progress Monitor")
        progress_bar = st.progress(0)
        status_box = st.empty()

        try:
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls()
            server.login(sender_email, app_password)

            for idx in range(len(df)):
                if st.session_state['stop_dispatch']:
                    st.error("🛑 Dispatch process halted manually!")
                    break

                row = df.iloc[idx]

                # Intelligent Column Value Fetching (Solves Transporter & Invoice Blank Issue)
                cust_name = get_field_value(row, ["Name", "Customer Name", "Client Name"], "Customer")
                target_email = get_field_value(row, ["Email", "Email ID", "Mail", "Email Address"], "").strip()
                inv_no = get_field_value(row, ["Invoice Number", "Invoice No", "Inv No", "Invoice_Number", "Invoice"], "N/A")
                disp_date = get_field_value(row, ["Dispatch Date", "Dispatch_Date", "Date"], "N/A")
                transporter_val = get_field_value(row, ["Transporter Name", "Transporter", "Transporter_Name", "Courier", "Transport"], "N/A")
                qty = get_field_value(row, ["Stock Qty", "Stock Quantity", "Qty", "Quantity"], "N/A")
                cases = get_field_value(row, ["Number of Case", "Cases", "Case Qty"], "N/A")

                if "@" in target_email:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = sender_email
                    msg['To'] = target_email
                    msg['Subject'] = f"Dispatch Invoice Notice - #{inv_no}"

                    body_html = f"""
                    <html>
                      <body style="font-family: Arial, sans-serif; color: #1e293b; line-height: 1.6;">
                        <div style="max-width: 600px; margin: auto; padding: 24px; border: 1px solid #cbd5e1; border-radius: 14px; background-color: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                          <h2 style="color: #4f46e5; margin-bottom: 6px;">Shipment Dispatch Notification</h2>
                          <p style="color: #64748b; font-size: 14px; margin-top: 0;">Automated Dispatch Tracker</p>
                          <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 16px 0;">
                          <p>Dear <b>{cust_name}</b>,</p>
                          <p>Your consignment has been dispatched successfully. Here are your details:</p>
                          <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
                            <tr style="background-color: #f8fafc;">
                              <td style="padding: 12px; border: 1px solid #cbd5e1;"><b>Invoice Number</b></td>
                              <td style="padding: 12px; border: 1px solid #cbd5e1; color: #4f46e5;"><b>{inv_no}</b></td>
                            </tr>
                            <tr>
                              <td style="padding: 12px; border: 1px solid #cbd5e1;"><b>Dispatch Date</b></td>
                              <td style="padding: 12px; border: 1px solid #cbd5e1;"><b>{disp_date}</b></td>
                            </tr>
                            <tr style="background-color: #f8fafc;">
                              <td style="padding: 12px; border: 1px solid #cbd5e1;"><b>Transporter Name</b></td>
                              <td style="padding: 12px; border: 1px solid #cbd5e1; color: #0284c7;"><b>{transporter_val}</b></td>
                            </tr>
                            <tr>
                              <td style="padding: 12px; border: 1px solid #cbd5e1;"><b>Quantity / Cases</b></td>
                              <td style="padding: 12px; border: 1px solid #cbd5e1;"><b>{qty} ({cases} Cases)</b></td>
                            </tr>
                          </table>
                          <p style="margin-top: 22px;">Thank you for your business!</p>
                          <hr style="border: 0; border-top: 1px solid #e2e8f0; margin-top: 20px;">
                          <p style="font-size: 11px; color: #94a3b8; text-align: center;">This is an automated CRM Pro dispatch email.</p>
                        </div>
                      </body>
                    </html>
                    """
                    msg.attach(MIMEText(body_html, 'html'))

                    try:
                        server.sendmail(sender_email, target_email, msg.as_string())
                        st.session_state['sent_count'] += 1
                        status_box.markdown(f"✅ Mail Sent: **{cust_name}** (`{target_email}`) | Inv: `{inv_no}` | Transporter: **{transporter_val}**")
                    except Exception as send_err:
                        st.session_state['failed_count'] += 1
                        status_box.markdown(f"❌ Failed: `{target_email}`")
                else:
                    st.session_state['failed_count'] += 1

                pct = (idx + 1) / len(df)
                progress_bar.progress(pct)
                time.sleep(dispatch_delay)

            server.quit()
            if not st.session_state['stop_dispatch']:
                st.balloons()
                st.success("🎉 All bulk dispatch emails sent successfully!")

        except Exception as smtp_err:
            st.error(f"❌ SMTP Error: {smtp_err}. Please check your credentials in the sidebar.")
