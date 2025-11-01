import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os
from PIL import Image
import io
import base64
import google.generativeai as genai

# Page Configuration
st.set_page_config(
    page_title="PharmaBiz Pro",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #f8fafc;}
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    h1 {color: #1e293b;}
    .stAlert {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.users = []
    st.session_state.stocks = []
    st.session_state.doctors = []

# Data Persistence
def load_data():
    os.makedirs('data', exist_ok=True)
    try:
        if os.path.exists('data/users.json'):
            with open('data/users.json', 'r') as f:
                st.session_state.users = json.load(f)
    except:
        st.session_state.users = []
    try:
        if os.path.exists('data/stocks.json'):
            with open('data/stocks.json', 'r') as f:
                st.session_state.stocks = json.load(f)
    except:
        st.session_state.stocks = []
    try:
        if os.path.exists('data/doctors.json'):
            with open('data/doctors.json', 'r') as f:
                st.session_state.doctors = json.load(f)
    except:
        st.session_state.doctors = []

def save_data():
    os.makedirs('data', exist_ok=True)
    with open('data/users.json', 'w') as f:
        json.dump(st.session_state.users, f)
    with open('data/stocks.json', 'w') as f:
        json.dump(st.session_state.stocks, f)
    with open('data/doctors.json', 'w') as f:
        json.dump(st.session_state.doctors, f)

load_data()

# Authentication
def register_user(email, password, business_name):
    user = {'email': email, 'password': password, 'business_name': business_name, 'created_at': datetime.now().isoformat()}
    st.session_state.users.append(user)
    save_data()
    return True

def login_user(email, password):
    for user in st.session_state.users:
        if user['email'] == email and user['password'] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            return True
    return False

# AI Image Generation using Google Generative AI API
def generate_image_google(prompt):
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/imagen-2")
    response = model.generate_content(prompt)
    try:
        image_data = response.candidates[0].content.parts[0].inline_data.data
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        return image
    except Exception as e:
        st.error(f"Failed to generate or display image: {e}")
        return None

# Main App
def main():
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_dashboard()

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>💊 PharmaBiz Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>Professional Pharmaceutical Business Management</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login to Your Account")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", type="primary"):
                if login_user(email, password):
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials!")
        
        with tab2:
            st.subheader("Create New Account")
            reg_business = st.text_input("Business Name", key="reg_business")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            if st.button("Register", type="primary"):
                if reg_business and reg_email and reg_password:
                    register_user(reg_email, reg_password, reg_business)
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Please fill all fields!")

def show_dashboard():
    with st.sidebar:
        st.markdown("### 💊 PharmaBiz Pro")
        st.markdown(f"**User:** {st.session_state.user_email}")
        st.markdown("---")
        
        menu = st.radio("Navigation", ["📊 Dashboard", "📦 Stock Management", "👨‍⚕️ Doctor Tracking", "📈 Analytics", "🚨 Alerts", "🎨 AI Generator", "📄 Reports"], key="menu")
        st.markdown("---")
        if st.button("🚪 Logout", type="secondary"):
            st.session_state.logged_in = False
            st.experimental_rerun()

    if menu == "📊 Dashboard":
        show_dashboard_page()
    elif menu == "📦 Stock Management":
        show_stock_management()
    elif menu == "👨‍⚕️ Doctor Tracking":
        show_doctor_tracking()
    elif menu == "📈 Analytics":
        show_analytics()
    elif menu == "🚨 Alerts":
        show_alerts()
    elif menu == "🎨 AI Generator":
        show_ai_generator()
    elif menu == "📄 Reports":
        show_reports()

def show_dashboard_page():
    st.title("📊 Dashboard Overview")
    total_stock = sum([s['units'] for s in st.session_state.stocks])
    total_sold = sum([s['sold'] for s in st.session_state.stocks])
    total_revenue = sum([s['sold_amount'] for s in st.session_state.stocks])
    total_invested = sum([s['paid'] for s in st.session_state.stocks])
    profit = total_revenue - total_invested
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Stock Units", f"{total_stock:,}")
    with col2:
        st.metric("Total Sold", f"{total_sold:,}")
    with col3:
        st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    with col4:
        st.metric("Profit", f"₹{profit:,.0f}")
    st.markdown("---")
    if st.session_state.stocks:
        st.markdown("### 📋 Recent Activity")
        recent_df = pd.DataFrame(st.session_state.stocks[-5:])
        st.dataframe(recent_df[['name', 'batch_no', 'units', 'sold', 'sold_amount']], use_container_width=True)

def show_stock_management():
    st.title("📦 Stock Management")
    with st.expander("➕ Add New Stock", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Product Name")
            batch_no = st.text_input("Batch Number")
            received = st.date_input("Received Date")
            expired = st.date_input("Expiry Date")
        with col2:
            paid = st.number_input("Amount Paid (₹)", min_value=0)
            units = st.number_input("Total Units", min_value=0)
            sold = st.number_input("Units Sold", min_value=0)
            sold_amount = st.number_input("Sale Amount (₹)", min_value=0)
        prescribed_by = st.selectbox("Prescribed By", [""] + [d['name'] for d in st.session_state.doctors])
        if st.button("Add Stock", type="primary"):
            if name and batch_no:
                stock = {'id': len(st.session_state.stocks) + 1, 'name': name, 'batch_no': batch_no, 
                         'received': received.isoformat(), 'expired': expired.isoformat(), 'paid': paid,
                         'units': units, 'sold': sold, 'sold_amount': sold_amount, 'prescribed_by': prescribed_by}
                st.session_state.stocks.append(stock)
                save_data()
                st.success("✓ Stock added!")
                st.experimental_rerun()
    st.markdown("### 📋 Stock Inventory")
    if st.session_state.stocks:
        df = pd.DataFrame(st.session_state.stocks)
        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, f"stock_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        st.dataframe(df, use_container_width=True)

def show_doctor_tracking():
    st.title("👨‍⚕️ Doctor Tracking")
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Add Doctor", expanded=True):
            doc_name = st.text_input("Doctor Name")
            doc_clinic = st.text_input("Clinic")
            doc_phone = st.text_input("Phone")
            doc_sales = st.number_input("Total Sales (₹)", min_value=0)
            if st.button("Add Doctor", type="primary"):
                if doc_name:
                    doctor = {'id': len(st.session_state.doctors) + 1, 'name': doc_name, 
                              'clinic': doc_clinic, 'phone': doc_phone, 'total_sales': doc_sales}
                    st.session_state.doctors.append(doctor)
                    save_data()
                    st.success("✓ Doctor added!")
                    st.experimental_rerun()
    if st.session_state.doctors:
        st.markdown("### 📋 Doctor List")
        df = pd.DataFrame(st.session_state.doctors)
        st.dataframe(df, use_container_width=True)

def show_analytics():
    st.title("📈 Analytics")
    if not st.session_state.stocks:
        st.info("No data available")
        return
    df = pd.DataFrame(st.session_state.stocks)
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df, x='name', y='sold', title="Product Sales")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.pie(df, values='sold_amount', names='name', title="Revenue Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_alerts():
    st.title("🚨 Expiry Alerts")
    today = datetime.now()
    expiring = []
    for stock in st.session_state.stocks:
        try:
            expiry = datetime.fromisoformat(stock['expired'])
            days = (expiry - today).days
            if 0 < days <= 90:
                expiring.append((stock, days))
        except:
            pass
    if expiring:
        st.warning("🔴 Products Expiring Soon")
        for stock, days in expiring:
            st.info(f"• {stock['name']} - {days} days remaining")
    else:
        st.success("✓ All stocks in good condition!")

def show_ai_generator():
    st.title("🎨 AI Content Generator")
    st.info("Generate images and videos for your business")
    prompt = st.text_area("Enter prompt:", placeholder="E.g., pharmacy interior, promotional image of medicine named ASDFG (Pain killer)")
    if st.button("Generate", type="primary"):
        if prompt:
            with st.spinner("Generating with Google Imagen..."):
                image = generate_image_google(prompt)
                if image:
                    st.image(image, caption="AI Generated Image (Google Imagen)")
                else:
                    st.warning("No image generated. Try a different prompt.")

def show_reports():
    st.title("📄 Reports & Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🤖 AI Recommendations")
        st.info("""
        1. Focus on high-selling products
        2. Monitor expiry dates closely
        3. Strengthen doctor relationships
        4. Maintain optimal stock levels
        5. Track profit margins
        """)
    with col2:
        st.markdown("### 📊 Business Metrics")
        if st.session_state.stocks:
            revenue = sum([s['sold_amount'] for s in st.session_state.stocks])
            invested = sum([s['paid'] for s in st.session_state.stocks])
            st.metric("Revenue", f"₹{revenue:,.0f}")
            st.metric("Profit", f"₹{revenue - invested:,.0f}")

if __name__ == "__main__":
    main()
