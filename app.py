import streamlit as st
import pandas as pd
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import random
import re

# 1. Page Configuration
st.set_page_config(
    page_title="CRM Pro Bulk Dispatcher 4K Dynamic",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Dynamic Cyber Ambient CSS & Glassmorphism UI (Restored Original Dynamic Effects)
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%);
        color: #f8fafc;
        font-family: 'Segoe UI', Inter, system-ui, -apple-system, sans-serif;
    }

    .stApp::before {
        content: "";
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, rgba(168, 85, 247, 0.05) 40%, transparent 70%);
        animation: rotateAmbient 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes rotateAmbient {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .floating-header {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc, #f472b6, #38bdf8);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 44px;
        font-weight: 900;
        letter-spacing: -1px;
        animation: shimmer 5s ease infinite, floatTitle 3s ease-in-out infinite;
        margin-bottom: 0px;
        text-shadow: 0 0 30px rgba(56, 189, 248, 0.4);
    }

    @keyframes shimmer {
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
        padding: 10px;
        border-radius: 22px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.5);
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.4), inset 0 0 15px rgba(56, 189, 248, 0.2);
        animation: pulse4K 3s infinite alternate;
    }

    @keyframes pulse4K {
        0% { border-color: rgba(56, 189, 248, 0.4); box-shadow: 0 0 20px rgba(56, 189, 248, 0.3); }
        50% { border-color: rgba(192, 132, 252, 0.8); box-shadow: 0 0 35px rgba(192, 132, 252, 0.6); }
        100% { border-color: rgba(244, 114, 182, 0.9); box-shadow: 0 0 40px rgba(244, 114, 182, 0.7); }
    }

    .metric-card {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 18px;
        text-align: center;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-card:hover {
        transform: translateY(-8px) scale(1.03);
        border-color: #38bdf8;
        box-shadow: 0 15px 40px rgba(56, 189, 248, 0.35);
    }

    .metric-title {
        font-size: 13px;
        color: #94a3b8;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .metric-value {
        font-size: 38px;
        font-weight: 900;
        margin-top: 6px;
        background: linear-gradient(90deg, #38bdf8, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stButton>button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.6) !important;
        transform: translateY(-2px) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Strict Field Extractor
def get_field_strict(row, column_aliases, default_val="N/A"):
    aliases_clean = [re.sub(r'[^a-zA-Z0-9]', '', str(a)).lower() for a in column_aliases]
    
    for col in row.index:
        col_clean = re.sub(r'[^a-zA-Z0-9]', '', str(col)).lower()
        if col_clean in aliases_clean:
            val = str(row[col]).strip()
            if val and val.lower() not in ["nan", "none", "n/a", ""]:
                return val
                
    return default_val

# 4. Default 100 Sample Records Generator
@st.cache_data
def load_default_100_records():
    names_list = [
        "Aarav Sharma", "Priya Patel", "Rahul Verma", "Ananya Iyer", "Amit Gupta",
        "Rohan Mehta", "Sneha Reddy", "Vikram Singh", "Pooja Joshi", "Karan Kapoor"
    ]
    transporters = ["V-Trans", "TCI Express", "Gati KWE", "Blue Dart Cargo", "Safexpress"]
    records = []
    base_date = datetime(2026, 8, 1)

    for i in range(1, 101):
        base_name = names_list[(i - 1) % len(names_list)]
        full_name = f"{base_name}" if i <= 10 else f"{base_name} ({i})"
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
    st.markdown("### 🖼️ Branding Studio")
    logo_file = st.file_uploader("Upload High-Res Logo", type=["png", "jpg", "jpeg"])

    st.divider()

    st.markdown("### 🔑 Secure SMTP Engine")
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)
    sender_email = st.text_input("Sender Email ID", placeholder="your_email@gmail.com")
    app_password = st.text_input("16-Digit App Password", type="password")
    dispatch_delay = st.slider("Dispatch Rate Delay (Sec)", 0.5, 5.0, 1.0)

# 6. Top Header Section
col_logo, col_title = st.columns([1, 5])

with col_logo:
    if logo_file is not None:
        st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
        st.image(logo_file, width=110)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="logo-frame" style="font-size: 55px; text-align: center; width: 80px;">⚡</div>', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 class='floating-header'>CRM Pro Bulk Dispatcher 4K</h1>", unsafe_allow_html=True)
    st.caption("✨ Ultra-Fast Automated Dispatcher with High-Glow Multi-Color Email Templates")

st.divider()

# 7. Excel Import Handler
uploaded_file = st.file_uploader("Upload Excel / CSV file", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            new_df = pd.read_csv(uploaded_file)
        else:
            new_df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.session_state['crm_data'] = new_df
        st.session_state['sent_count'] = 0
        st.session_state['failed_count'] = 0
        st.success(f"✅ Loaded {len(new_df)} records!")
    except Exception as e:
        st.error(f"❌ File loading error: {e}")

# 8. Live Metrics Dashboard
df = st.session_state['crm_data']
total_records = len(df)
pending_records = total_records - (st.session_state['sent_count'] + st.session_state['failed_count'])

st.markdown("### 📊 Live Processing Dashboard")
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

# 9. Editable Live Table
edited_df = st.data_editor(
    st.session_state['crm_data'],
    num_rows="dynamic",
    use_container_width=True,
    height=380,
    key="data_editor_4k_dynamic"
)
st.session_state['crm_data'] = edited_df
df = st.session_state['crm_data']

# 10. Email Dispatcher Engine
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
        st.warning("⚠️ Kripya sidebar me Sender Email ID aur 16-digit App Password fill karein!")
    else:
        st.markdown("---")
        progress_bar = st.progress(0)
        status_box = st.empty()

        try:
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls()
            server.login(sender_email, app_password)

            for idx in range(len(df)):
                if st.session_state['stop_dispatch']:
                    st.error("🛑 Dispatch Process Stopped!")
                    break

                row = df.iloc[idx]

                cust_name = get_field_strict(row, ["Name", "Customer Name", "Client Name"], "Customer")
                target_email = get_field_strict(row, ["Email", "Email ID", "Mail", "Email Address"], "").strip()
                inv_no = get_field_strict(row, ["Invoice Number", "Invoice No", "Inv No", "Invoice"], "N/A")
                inv_date = get_field_strict(row, ["Invoice Date", "Inv Date", "Date Of Invoice"], "N/A")
                disp_date = get_field_strict(row, ["Dispatch Date", "Disp Date"], "N/A")
                transporter_val = get_field_strict(row, ["Transporter Name", "Transporter", "Courier"], "N/A")
                qty = get_field_strict(row, ["Stock Qty", "Stock Quantity", "Qty"], "N/A")
                cases = get_field_strict(row, ["Number of Case", "Cases", "Case Qty"], "N/A")
                amount_val = get_field_strict(row, ["Amount", "Total Amount", "Bill Amount"], "N/A")

                if "@" in target_email:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = sender_email
                    msg['To'] = target_email
                    msg['Subject'] = f"🚀 Dispatch Notice - #{inv_no} | RAMA ENTERPRISES"

                    # Email Template with High-Glowing Rainbow Animated Multi-Color Banner Header
                    body_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <body style="margin: 0; padding: 0; background-color: #020617; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #020617; padding: 25px 0;">
                        <tr>
                          <td align="center">
                            <table role="presentation" width="620" cellspacing="0" cellpadding="0" style="background-color: #0f172a; border: 2px solid #38bdf8; border-radius: 20px; overflow: hidden; box-shadow: 0 0 40px rgba(56, 189, 248, 0.4);">
                              
                              <!-- Vibrant Glowing Header with Rich Multi-Color Neon Effect -->
                              <tr>
                                <td style="background: linear-gradient(135deg, #020617, #1e1b4b, #2e1065); padding: 36px 20px; text-align: center; border-bottom: 2px solid #38bdf8;">
                                  <div style="display: inline-block; background: rgba(15, 23, 42, 0.8); padding: 12px 24px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.6); box-shadow: 0 0 25px rgba(56, 189, 248, 0.5);">
                                    <h1 style="font-size: 28px; font-weight: 900; letter-spacing: 3px; margin: 0; text-transform: uppercase; background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc, #f472b6, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: #38bdf8; text-shadow: 0 0 20px rgba(56, 189, 248, 0.8);">
                                      RAMA ENTERPRISES
                                    </h1>
                                  </div>
                                  <div style="font-size: 15px; font-weight: 800; color: #38bdf8; letter-spacing: 2px; margin-top: 12px; text-transform: uppercase; text-shadow: 0 0 12px rgba(192, 132, 252, 0.7);">
                                    Abbott India Ltd, Patna
                                  </div>
                                </td>
                              </tr>

                              <!-- Content Section -->
                              <tr>
                                <td style="padding: 30px; color: #f8fafc;">
                                  <p style="font-size: 16px; margin-top: 0; color: #f8fafc;">Dear <b style="color: #c084fc; font-size: 17px; text-shadow: 0 0 8px rgba(192, 132, 252, 0.4);">{cust_name}</b>,</p>
                                  <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6; margin-bottom: 22px;">Your consignment has been dispatched successfully. Below are your invoice & shipment details:</p>
                                  
                                  <table width="100%" cellspacing="0" cellpadding="13" style="background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; border-collapse: separate; border-spacing: 0; overflow: hidden;">
                                    <tr style="background-color: #0f172a;">
                                      <td width="42%" style="color: #94a3b8; font-weight: 700; border-bottom: 1px solid #334155;">📄 Invoice Number</td>
                                      <td style="color: #818cf8; font-weight: 900; border-bottom: 1px solid #334155; font-size: 15px;">{inv_no}</td>
                                    </tr>
                                    <tr style="background-color: #1e293b;">
                                      <td style="color: #94a3b8; font-weight: 700; border-bottom: 1px solid #334155;">📅 Invoice Date</td>
                                      <td style="color: #38bdf8; font-weight: 800; border-bottom: 1px solid #334155;">{inv_date}</td>
                                    </tr>
                                    <tr style="background-color: #0f172a;">
                                      <td style="color: #94a3b8; font-weight: 700; border-bottom: 1px solid #334155;">🚚 Dispatch Date</td>
                                      <td style="color: #38bdf8; font-weight: 800; border-bottom: 1px solid #334155;">{disp_date}</td>
                                    </tr>
                                    <tr style="background-color: #1e293b;">
                                      <td style="color: #94a3b8; font-weight: 700; border-bottom: 1px solid #334155;">🚛 Transporter Name</td>
                                      <td style="color: #f472b6; font-weight: 900; border-bottom: 1px solid #334155;">{transporter_val}</td>
                                    </tr>
                                    <tr style="background-color: #0f172a;">
                                      <td style="color: #94a3b8; font-weight: 700; border-bottom: 1px solid #334155;">📦 Stock Quantity</td>
                                      <td style="color: #38bdf8; font-weight: 800; border-bottom: 1px solid #334155;">{qty}</td>
                                    </tr>
                                    <tr style="background-color: #1e293b;">
                                      <td style="color: #94a3b8; font-weight: 700; border-bottom: 1px solid #334155;">🧰 Number of Cases</td>
                                      <td style="color: #38bdf8; font-weight: 800; border-bottom: 1px solid #334155;">{cases} Cases</td>
                                    </tr>
                                    <tr style="background-color: #0f172a;">
                                      <td style="color: #94a3b8; font-weight: 700;">💰 Invoice Amount</td>
                                      <td style="color: #4ade80; font-weight: 900; font-size: 17px;">{amount_val}</td>
                                    </tr>
                                  </table>

                                  <p style="margin-top: 25px; color: #94a3b8; font-size: 13px; line-height: 1.5;">Thank you for your business with <b>RAMA ENTERPRISES Abbott India Ltd, Patna</b>!</p>
                                </td>
                              </tr>

                              <!-- Footer -->
                              <tr>
                                <td style="text-align: center; padding: 18px; background-color: #020617; color: #64748b; font-size: 12px; border-top: 1px solid #1e293b;">
                                  ⚡ Powered by RAMA ENTERPRISES Abbott India Ltd, Patna • Automated 4K Dispatcher
                                </td>
                              </tr>
                            </table>
                          </td>
                        </tr>
                      </table>
                    </body>
                    </html>
                    """
                    msg.attach(MIMEText(body_html, 'html'))

                    try:
                        server.sendmail(sender_email, target_email, msg.as_string())
                        st.session_state['sent_count'] += 1
                        status_box.markdown(f"✅ Mail Sent: **{cust_name}** (`{target_email}`) | Inv: `{inv_no}`")
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
                st.success("🎉 All bulk emails processed and sent successfully!")

        except Exception as smtp_err:
            st.error(f"❌ SMTP Error: {smtp_err}")
