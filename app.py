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
    page_title="CRM Pro Bulk Dispatcher",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Original Dark Theme App Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .main-title {
        color: #38bdf8;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .logo-frame {
        display: inline-block;
        padding: 8px;
        border-radius: 16px;
        background: #1e293b;
        border: 1px solid #38bdf8;
    }

    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .metric-title {
        font-size: 13px;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
    }

    .metric-value {
        font-size: 32px;
        font-weight: 800;
        margin-top: 5px;
        color: #38bdf8;
    }

    .stButton>button {
        border-radius: 8px !important;
        font-weight: 700 !important;
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

# 4. Default 100 Records Data
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

# Session State Setup
if 'crm_data' not in st.session_state:
    st.session_state['crm_data'] = load_default_100_records()
if 'sent_count' not in st.session_state:
    st.session_state['sent_count'] = 0
if 'failed_count' not in st.session_state:
    st.session_state['failed_count'] = 0

# 5. Sidebar Controls
with st.sidebar:
    st.markdown("### 🖼️ Branding Configuration")
    logo_file = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])

    st.divider()

    st.markdown("### 🔑 SMTP Mailer Setup")
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)
    sender_email = st.text_input("Sender Email ID", placeholder="your_email@gmail.com")
    app_password = st.text_input("16-Digit App Password", type="password")
    dispatch_delay = st.slider("Delay Between Emails (Seconds)", 0.5, 5.0, 1.0)

# 6. Header
col_logo, col_title = st.columns([1, 5])

with col_logo:
    if logo_file is not None:
        st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
        st.image(logo_file, width=90)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="logo-frame" style="font-size: 45px; text-align: center; width: 70px;">⚡</div>', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 class='main-title'>CRM Pro Bulk Dispatcher</h1>", unsafe_allow_html=True)
    st.caption("Automated Dispatch Notice System for Abbott India Ltd, Patna")

st.divider()

# 7. File Import
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
        st.error(f"❌ Loading failed: {e}")

# 8. Counter Grid
df = st.session_state['crm_data']
total_records = len(df)
pending_records = total_records - (st.session_state['sent_count'] + st.session_state['failed_count'])

st.markdown("### 📊 Status Overview")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Records</div><div class="metric-value">{total_records}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Sent Success</div><div class="metric-value" style="color:#4ade80;">{st.session_state["sent_count"]}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Failed / Bounces</div><div class="metric-value" style="color:#f87171;">{st.session_state["failed_count"]}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Pending Queue</div><div class="metric-value" style="color:#fbbf24;">{max(0, pending_records)}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# 9. Live Data Grid
edited_df = st.data_editor(
    st.session_state['crm_data'],
    num_rows="dynamic",
    use_container_width=True,
    height=380,
    key="data_editor_main"
)
st.session_state['crm_data'] = edited_df
df = st.session_state['crm_data']

# 10. Dispatch Motor
if 'stop_dispatch' not in st.session_state:
    st.session_state['stop_dispatch'] = False

col_start, col_stop = st.columns([2, 1])
with col_start:
    start_btn = st.button("🚀 Send Bulk Emails", type="primary", use_container_width=True)
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
                    msg['Subject'] = f"Dispatch Invoice Notice - #{inv_no}"

                    # Exact Screenshot Replicated Email Design
                    body_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <body style="margin: 0; padding: 0; background-color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #ffffff; padding: 20px 0;">
                        <tr>
                          <td align="center">
                            <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #0b0f19; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                              
                              <!-- Banner Header (Exact Screenshot Match) -->
                              <tr>
                                <td style="background: linear-gradient(180deg, #180943 0%, #0d0728 100%); padding: 40px 20px 30px 20px; text-align: center; border-bottom: 2px solid #38bdf8;">
                                  <div style="display: inline-block; background: linear-gradient(90deg, #1d82b6, #e052a0); padding: 8px 18px; border-radius: 4px; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);">
                                    <h1 style="font-size: 26px; font-weight: 900; color: #000000; letter-spacing: 3px; margin: 0; text-transform: uppercase;">
                                      RAMA ENTERPRISES
                                    </h1>
                                  </div>
                                  <div style="font-size: 15px; font-weight: 800; color: #38bdf8; letter-spacing: 1px; margin-top: 14px;">
                                    Abbott India Ltd, Patna
                                  </div>
                                </td>
                              </tr>

                              <!-- Email Body Content -->
                              <tr>
                                <td style="padding: 30px 28px; color: #ffffff;">
                                  <p style="font-size: 16px; margin-top: 0; color: #ffffff;">Dear <b style="color: #a855f7; font-size: 17px;">{cust_name}</b>,</p>
                                  <p style="color: #cbd5e1; font-size: 14px; line-height: 1.5; margin-bottom: 25px;">
                                    Your consignment has been dispatched successfully. Below are your invoice & shipment details:
                                  </p>

                                  <!-- Exact Replicated Dark Table Card -->
                                  <table width="100%" cellspacing="0" cellpadding="14" style="background-color: #111827; border: 1px solid #1e293b; border-radius: 12px; border-collapse: collapse;">
                                    <tr style="border-bottom: 1px solid #1e293b;">
                                      <td width="42%" style="color: #94a3b8; font-weight: 700; font-size: 14px;">📄 Invoice Number</td>
                                      <td style="color: #6366f1; font-weight: 800; font-size: 15px;">{inv_no}</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #1e293b;">
                                      <td style="color: #94a3b8; font-weight: 700; font-size: 14px;">📅 Invoice Date</td>
                                      <td style="color: #38bdf8; font-weight: 800; font-size: 14px;">{inv_date}</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #1e293b;">
                                      <td style="color: #94a3b8; font-weight: 700; font-size: 14px;">🚚 Dispatch Date</td>
                                      <td style="color: #38bdf8; font-weight: 800; font-size: 14px;">{disp_date}</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #1e293b;">
                                      <td style="color: #94a3b8; font-weight: 700; font-size: 14px;">🚛 Transporter Name</td>
                                      <td style="color: #e052a0; font-weight: 800; font-size: 14px;">{transporter_val}</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #1e293b;">
                                      <td style="color: #94a3b8; font-weight: 700; font-size: 14px;">📦 Stock Quantity</td>
                                      <td style="color: #38bdf8; font-weight: 800; font-size: 14px;">{qty}</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #1e293b;">
                                      <td style="color: #94a3b8; font-weight: 700; font-size: 14px;">🧰 Number of Cases</td>
                                      <td style="color: #38bdf8; font-weight: 800; font-size: 14px;">{cases} Cases</td>
                                    </tr>
                                    <tr>
                                      <td style="color: #94a3b8; font-weight: 700; font-size: 14px;">💰 Total Amount</td>
                                      <td style="color: #4ade80; font-weight: 900; font-size: 16px;">{amount_val}</td>
                                    </tr>
                                  </table>

                                </td>
                              </tr>

                              <!-- Footer -->
                              <tr>
                                <td style="text-align: center; padding: 16px; background-color: #070a12; color: #64748b; font-size: 12px; border-top: 1px solid #1e293b;">
                                  RAMA ENTERPRISES Abbott India Ltd, Patna
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
                st.success("🎉 All bulk dispatch emails processed and sent successfully!")

        except Exception as smtp_err:
            st.error(f"❌ SMTP Connection Error: {smtp_err}")
