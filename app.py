import streamlit as st
import pandas as pd
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="CRM Pro Bulk Dispatcher", layout="wide")

# Custom Dark/Premium Styling
st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color:#1E88E5; text-align:center; margin-bottom:5px; }
    .sub-title { font-size:16px; color:#888; text-align:center; margin-bottom:20px; }
    .metric-box { background-color:#1e1e24; padding:12px; border-radius:10px; text-align:center; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# 🔐 SECRET PASSWORD CONFIGURATION
# Aap jo bhi password rakhna chahte hain, use niche "MeraSecretPass123" ki jagah likh dein
SECRET_PASSWORD = "MONSTER@3992"

# Initialize Login State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 1. LOGIN SCREEN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("## 🔒 Secure Admin Login")
        user_pass = st.text_input("Secret Admin Password Enter Karen", type="password")
        if st.button("Login", use_container_width=True):
            if user_pass == SECRET_PASSWORD:
                st.session_state.logged_in = True
                st.rerun() # Refresh app to show contents
            else:
                st.error("❌ Galat Password! Kripya sahi password dalein.")
    st.stop() # Stops execution here so unauthenticated users see nothing else

# --- 2. MAIN APP CONTENTS (Only shows after successful login) ---
# Logout Button on Top Right
col_title, col_logout = st.columns([9, 1])
with col_logout:
    if st.button("🔒 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Company Brand Identity Header (Logo & Title)
logo_col1, logo_col2, logo_col3 = st.columns(3)
with logo_col2:
    logo_url = st.file_uploader("🏢 Company Logo Upload Karen (Optional)", type=["png", "jpg", "jpeg"])
    if logo_url:
        st.image(logo_url, width=150, use_container_width=False)
    else:
        st.markdown("<h3 style='text-align: center; color: #777;'>[ Company Logo Placeholder ]</h3>", unsafe_allow_html=True)
        
    st.markdown('<div class="main-title">📈 CRM Bulk Invoice & Stock Dispatcher</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Personalized Billing & Inventory Delivery Engine</div>', unsafe_allow_html=True)

# Sidebar - SMTP Settings
st.sidebar.header("🔑 SMTP Server Connection")
smtp_server = st.sidebar.text_input("SMTP Server", "://gmail.com")
smtp_port = st.sidebar.number_input("SMTP Port", value=587)
sender_email = st.sidebar.text_input("Sender Email ID")
sender_password = st.sidebar.text_input("16-Digit App Password", type="password")
dispatch_speed = st.sidebar.slider("Dispatch Rate Delay (Seconds)", 0.5, 5.0, 1.0)

# Dynamic Template Builder
st.write("---")
st.write("### ✉️ Smart Template Customizer")
col_sub, col_tokens = st.columns()
with col_sub:
    subject = st.text_input("Email Subject Line", value="Important: Invoice {InvoiceNo} and Stock Update")
with col_tokens:
    st.caption("Available Dynamic Tokens:")
    st.code("{Name} | {Company} | {InvoiceNo} | {StockQty} | {SpecialMsg}")

email_template = st.text_area(
    "Message Body Builder",
    value="Swagat hai {Name}!\n\nThank you for partnering with us. Your invoice details are as follows:\n🧾 Invoice Number: {InvoiceNo}\n📦 Available Stock Quantity: {StockQty}\n\n📝 Special Note for Your Team:\n{SpecialMsg}\n\nBest regards,\nCRM Distribution Management Team",
    height=200
)

# Data Source - Pre-populated Base Sheet
st.write("---")
st.write("### 📊 Excel Data Grid (Click any cell to Edit directly)")

if 'crm_data' not in st.session_state:
    initial_rows = {
        "Name": ["Aarav Sharma", "Priya Patel", "Rahul Verma", "Ananya Iyer", "Amit Gupta"],
        "Email": ["aarav@sharma.com", "priya@patel.io", "rahul@verma.in", "ananya@iyer.co", "amit@gupta.org"],
        "Company": ["Sharma Tech", "Patel Corp", "Verma Digital", "Iyer Solutions", "Gupta Retail"],
        "InvoiceNo": ["INV-2026-001", "INV-2026-002", "INV-2026-003", "INV-2026-004", "INV-2026-005"],
        "StockQty": ["150 Units", "420 Units", "85 Units", "610 Units", "300 Units"],
        "SpecialMsg": ["Immediate dispatch scheduled.", "Please clear previous due balance.", "Stock allocation running low.", "Festive season bonus discount applied.", "Standard delivery timelines apply."]
    }
    st.session_state.crm_data = pd.DataFrame(initial_rows)

uploaded_file = st.file_uploader("🔄 Raw Excel File (.xlsx) Se Fresh Records Import Karen", type=["xlsx", "csv"])
if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        st.session_state.crm_data = pd.read_csv(uploaded_file)
    else:
        st.session_state.crm_data = pd.read_excel(uploaded_file)

edited_df = st.data_editor(st.session_state.crm_data, num_rows="dynamic", use_container_width=True)

# Live Queue Metrics Dashboard
st.write("---")
st.write("### 📈 Live Processing Counters")
total_recipients = len(edited_df)

m_col1, m_col2, m_col3 = st.columns(3)
m_col1.markdown(f"<div class='metric-box'>⚙️ Total Queue<br><h2>{total_recipients} Recipients</h2></div>", unsafe_allow_html=True)
p_success = m_col2.empty()
p_failed = m_col3.empty()

p_success.markdown("<div class='metric-box'>✅ Sent Success<br><h2>0 Successful</h2></div>", unsafe_allow_html=True)
p_failed.markdown("<div class='metric-box'>❌ Failed Bounces<br><h2>0 Failed</h2></div>", unsafe_allow_html=True)

# Bulk Transmission Loop Execution
if st.button("🚀 Execute Smart Bulk Mail Dispatch", use_container_width=True):
    if not sender_email or not sender_password:
        st.error("🔒 Please establish secure server authentication credentials inside the Sidebar panel first!")
    else:
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            
            success_count = 0
            failed_count = 0
            progress_bar = st.progress(0)
            
            for index, row in edited_df.iterrows():
                try:
                    to_email = str(row["Email"]).strip()
                    formatted_subject = subject.format(
                        Name=str(row.get("Name","")), Company=str(row.get("Company","")),
                        InvoiceNo=str(row.get("InvoiceNo","")), StockQty=str(row.get("StockQty","")),
                        SpecialMsg=str(row.get("SpecialMsg",""))
                    )
                    formatted_body = email_template.format(
                        Name=str(row.get("Name","")), Company=str(row.get("Company","")),
                        InvoiceNo=str(row.get("InvoiceNo","")), StockQty=str(row.get("StockQty","")),
                        SpecialMsg=str(row.get("SpecialMsg",""))
                    )
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = to_email
                    msg['Subject'] = formatted_subject
                    msg.attach(MIMEText(formatted_body, 'plain'))
                    
                    server.sendmail(sender_email, to_email, msg.as_string())
                    success_count += 1
                except Exception:
                    failed_count += 1
                    
                p_success.markdown(f"<div class='metric-box'>✅ Sent Success<br><h2>{success_count} Successful</h2></div>", unsafe_allow_html=True)
                p_failed.markdown(f"<div class='metric-box'>❌ Failed Bounces<br><h2>{failed_count} Failed</h2></div>", unsafe_allow_html=True)
                progress_bar.progress((index + 1) / total_recipients)
                time.sleep(dispatch_speed)
                
            server.quit()
            st.success("🎯 Batch transmission cycle concluded efficiently!")
        except Exception as e:
            st.error(f"Critical System Integration Error: {str(e)}")
