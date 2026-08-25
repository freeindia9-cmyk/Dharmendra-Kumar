import streamlit as st
import pandas as pd
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import random
import re

# 1. Ultra 4K Page Configuration
st.set_page_config(
    page_title="CRM Pro Bulk Dispatcher 4K Ultra",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 4K Ultra Web CSS Styling
st.markdown("""
<style>
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

# 3. Super Robust Value Extractor (Guaranteed Zero N/A Fix)
def extract_value_bulletproof(row, target_keys, default_val="N/A"):
    # Clean keys list
    clean_target_keys = [re.sub(r'[^a-zA-Z0-9]', '', str(k)).lower() for k in target_keys]
    
    # 1st Pass: Clean string match
    for col in row.index:
        clean_col = re.sub(r'[^a-zA-Z0-9]', '', str(col)).lower()
        if clean_col in clean_target_keys:
            val = str(row[col]).strip()
            if val and val.lower() not in ["nan", "none", "n/a", ""]:
                return val

    # 2nd Pass: Substring search (e.g. 'transporter' in 'transporter name')
    for col in row.index:
        clean_col = re.sub(r'[^a-zA-Z0-9]', '', str(col)).lower()
        for tk in clean_target_keys:
            if tk in clean_col or clean_col in tk:
                val = str(row[col]).strip()
                if val and val.lower() not in ["nan", "none", "n/a", ""]:
                    return val

    return default_val

# 4. Default 100 Sample Customer Records Generator
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

# 5. Sidebar Controls
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

# 6. Dynamic Header Section
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
    st.caption("✨ Ultra-Fast Automated Dispatcher with Dynamic UI Email Generator")

st.divider()

# 7. Excel/CSV Import
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

# 8. Live 4K Dynamic Counters
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

# 9. Live Editable Data Table Grid
st.markdown(f"### ✏️ Interactive Live Grid ({len(df)} Records Ready)")
st.caption("💡 Tip: Double click any cell to instantly modify details.")

edited_df = st.data_editor(
    st.session_state['crm_data'],
    num_rows="dynamic",
    use_container_width=True,
    height=420,
    key="data_editor_4k"
)

st.session_state['crm_data'] = edited_df
df = st.session_state['crm_data']

# 10. Smart Dispatch Engine
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

                # Guaranteed Extraction logic for all fields
                cust_name = extract_value_bulletproof(row, ["Name", "Customer Name", "Client Name", "Customer"], "Customer")
                target_email = extract_value_bulletproof(row, ["Email", "Email ID", "Mail", "Email Address"], "").strip()
                inv_no = extract_value_bulletproof(row, ["Invoice Number", "Invoice No", "Inv No", "Invoice_Number", "Invoice"], "N/A")
                inv_date = extract_value_bulletproof(row, ["Invoice Date", "Inv Date", "Date Of Invoice", "Invoice_Date"], "N/A")
                disp_date = extract_value_bulletproof(row, ["Dispatch Date", "Dispatch_Date", "Disp Date", "Dispatching Date"], "N/A")
                
                # Broad Match for Transporter Name
                transporter_val = extract_value_bulletproof(row, ["Transporter Name", "Transporter", "Transporter_Name", "Courier", "Transport", "Logistics", "Carrier"], "N/A")
                
                qty = extract_value_bulletproof(row, ["Stock Qty", "Stock Quantity", "Qty", "Quantity", "Stock"], "N/A")
                cases = extract_value_bulletproof(row, ["Number of Case", "Cases", "Case Qty", "No of Cases", "Number of Cases"], "N/A")
                amount_val = extract_value_bulletproof(row, ["Amount", "Total Amount", "Bill Amount", "Inv Amount"], "N/A")

                if "@" in target_email:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = sender_email
                    msg['To'] = target_email
                    msg['Subject'] = f"🚀 RAMA ENTERPRISES - Dispatch Invoice Notice #{inv_no}"

                    # Email Body with 4K Dynamic UI & 3-Sec Floating Dynamic RAMA ENTERPRISES Intro
                    body_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                      <meta charset="utf-8">
                      <style>
                        @keyframes bannerFade {{
                          0% {{ opacity: 1; transform: scale(1.08); filter: drop-shadow(0 0 20px #38bdf8); }}
                          80% {{ opacity: 1; transform: scale(1); filter: drop-shadow(0 0 10px #c084fc); }}
                          100% {{ opacity: 1; transform: scale(1); }}
                        }}
                        
                        body {{
                          margin: 0; padding: 0; background-color: #020617; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #f8fafc;
                        }}
                        .email-container {{
                          max-width: 650px; margin: 30px auto; background: #0f172a; border: 1px solid #38bdf8; border-radius: 20px; overflow: hidden; box-shadow: 0 0 35px rgba(56, 189, 248, 0.25);
                        }}
                        .company-intro-banner {{
                          background: linear-gradient(135deg, #020617, #1e1b4b, #2e1065);
                          padding: 28px 15px;
                          text-align: center;
                          border-bottom: 2px solid #38bdf8;
                          animation: bannerFade 3s ease-in-out;
                        }}
                        .company-name-text {{
                          font-size: 32px;
                          font-weight: 900;
                          letter-spacing: 2px;
                          background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc, #f472b6);
                          -webkit-background-clip: text;
                          -webkit-text-fill-color: transparent;
                          margin: 0;
                          text-transform: uppercase;
                        }}
                        .company-tagline {{
                          color: #94a3b8; font-size: 13px; font-weight: 600; letter-spacing: 1px; margin-top: 4px;
                        }}
                        .content-body {{
                          padding: 25px;
                        }}
                        .data-table {{
                          width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 20px; border-radius: 12px; overflow: hidden; border: 1px solid #334155;
                        }}
                        .data-table td {{
                          padding: 14px 18px; border-bottom: 1px solid #1e293b; font-size: 14px;
                        }}
                        .data-table tr:last-child td {{
                          border-bottom: none;
                        }}
                        .label-col {{
                          background-color: #1e293b; color: #94a3b8; font-weight: 700; width: 42%;
                        }}
                        .value-col {{
                          background-color: #0f172a; color: #38bdf8; font-weight: 800;
                        }}
                        .highlight-val {{
                          color: #4ade80 !important; font-size: 16px;
                        }}
                        .footer-note {{
                          text-align: center; padding: 18px; background-color: #020617; color: #64748b; font-size: 12px; border-top: 1px solid #1e293b;
                        }}
                      </style>
                    </head>
                    <body>
                      <div class="email-container">
                        <!-- 3-Second Dynamic Floating Company Header -->
                        <div class="company-intro-banner">
                          <h1 class="company-name-text">RAMA ENTERPRISES</h1>
                          <div class="company-tagline">✨ Premium Automated CRM Dispatch System ✨</div>
                        </div>

                        <div class="content-body">
                          <p style="font-size: 16px; color: #f8fafc;">Dear <b style="color: #c084fc;">{cust_name}</b>,</p>
                          <p style="color: #cbd5e1; font-size: 14px; line-height: 1.5;">Your consignment has been dispatched successfully. Here are your details:</p>
                          
                          <table class="data-table">
                            <tr>
                              <td class="label-col">📄 Invoice Number</td>
                              <td class="value-col" style="color: #818cf8;">{inv_no}</td>
                            </tr>
                            <tr>
                              <td class="label-col">📅 Invoice Date</td>
                              <td class="value-col">{inv_date}</td>
                            </tr>
                            <tr>
                              <td class="label-col">🚚 Dispatch Date</td>
                              <td class="value-col">{disp_date}</td>
                            </tr>
                            <tr>
                              <td class="label-col">🚛 Transporter Name</td>
                              <td class="value-col" style="color: #f472b6;">{transporter_val}</td>
                            </tr>
                            <tr>
                              <td class="label-col">📦 Stock Quantity</td>
                              <td class="value-col">{qty}</td>
                            </tr>
                            <tr>
                              <td class="label-col">🧰 Number of Cases</td>
                              <td class="value-col">{cases} Cases</td>
                            </tr>
                            <tr>
                              <td class="label-col">💰 Invoice Amount</td>
                              <td class="value-col highlight-val">{amount_val}</td>
                            </tr>
                          </table>

                          <p style="margin-top: 25px; color: #94a3b8; font-size: 13px;">Thank you for your business with RAMA ENTERPRISES!</p>
                        </div>
                        <div class="footer-note">
                          ⚡ Powered by RAMA ENTERPRISES • 4K Dynamic Dispatcher
                        </div>
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
                st.success("🎉 All bulk dispatch emails processed and dispatched successfully!")

        except Exception as smtp_err:
            st.error(f"❌ SMTP Error: {smtp_err}. Please check your credentials in the sidebar.")
