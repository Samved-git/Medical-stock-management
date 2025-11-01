import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import base64
import io

# Safe rerun helper using experimental_rerun or session toggle
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.session_state["_rerun_flag"] = not st.session_state.get("_rerun_flag", False)

# Styling and page config
st.set_page_config(
    page_title="PharmaBiz Pro",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
  .main {background-color: #f8fafc;}
  .stButton>button {
    width: 100%; border-radius: 8px; height: 3em; font-weight: 600;
  }
  h1 {color: #1e293b;}
  .stAlert {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# Initialize all relevant session state variables
for key in ['logged_in', 'user_email', 'users', 'stocks', 'doctors', '_rerun_flag']:
    if key not in st.session_state:
        if key in ['logged_in', '_rerun_flag']:
            st.session_state[key] = False
        else:
            st.session_state[key] = []

# Cache data loading for better performance
@st.cache_data(show_spinner=False)
def load_json_data(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def load_all_data():
    os.makedirs('data', exist_ok=True)
    st.session_state.users = load_json_data('data/users.json')
    st.session_state.stocks = load_json_data('data/stocks.json')
    st.session_state.doctors = load_json_data('data/doctors.json')

def save_data():
    os.makedirs('data', exist_ok=True)
    with open('data/users.json', 'w') as f:
        json.dump(st.session_state.users, f)
    with open('data/stocks.json', 'w') as f:
        json.dump(st.session_state.stocks, f)
    with open('data/doctors.json', 'w') as f:
        json.dump(st.session_state.doctors, f)

# Load data at app start
load_all_data()

# Registration with normalization and duplicate email check
def register_user(email, password, business_name):
    email = email.strip().lower()
    password = password.strip()
    business_name = business_name.strip()

    # Check for duplicate email
    for user in st.session_state.users:
        if user['email'] == email:
            st.warning("User already registered with this email.")
            return False
    st.session_state.users.append({
        'email': email,
        'password': password,
        'business_name': business_name,
        'created_at': datetime.now().isoformat()
    })
    save_data()
    return True

# Login with normalization
def login_user(email, password):
    email = email.strip().lower()
    password = password.strip()
    for user in st.session_state.users:
        if user['email'] == email and user['password'] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            return True
    return False

# Google Imagen integration; assumes API key configured in env by Streamlit Cloud
def generate_image_google(prompt):
    genai.configure()  # API key picked from environment automatically
    model = genai.GenerativeModel("models/imagen-2")
    try:
        response = model.generate_content(prompt)
        image_data = response.candidates[0].content.parts[0].inline_data.data
        image_bytes = base64.b64decode(image_data)
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return None

# Login page UI
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
            if st.button("Login"):
                with st.spinner("Logging in..."):
                    if login_user(email, password):
                        st.success("Login successful!")
                        safe_rerun()
                    else:
                        st.error("Invalid credentials!")

        with tab2:
            st.subheader("Create New Account")
            business_name = st.text_input("Business Name", key="reg_business")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            if st.button("Register"):
                if business_name and email and password:
                    if register_user(email, password, business_name):
                        st.success("Registration successful! Please login.")
                    # Warning shown inside register_user for duplicates
                else:
                    st.error("Please fill all fields!")

# Dashboard sidebar and page navigation
def show_dashboard():
    with st.sidebar:
        st.markdown("### 💊 PharmaBiz Pro")
        st.markdown(f"User: {st.session_state.user_email}")
        st.markdown("---")
        menu = st.radio(
            "Navigation",
            [
                "📊 Dashboard",
                "📦 Stock Management",
                "👨‍⚕️ Doctor Tracking",
                "📈 Analytics",
                "🚨 Alerts",
                "🎨 AI Generator",
                "📄 Reports",
            ],
            index=0,
        )
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            safe_rerun()

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

# Dashboard main page
def show_dashboard_page():
    st.title("📊 Dashboard Overview")
    total_stock = sum(s.get("units", 0) for s in st.session_state.stocks)
    total_sold = sum(s.get("sold", 0) for s in st.session_state.stocks)
    total_revenue = sum(s.get("sold_amount", 0) for s in st.session_state.stocks)
    total_invested = sum(s.get("paid", 0) for s in st.session_state.stocks)
    profit = total_revenue - total_invested
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Stock Units", f"{total_stock:,}")
    col2.metric("Total Sold", f"{total_sold:,}")
    col3.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    col4.metric("Profit", f"₹{profit:,.0f}")

# Placeholder page implementations for navigation completeness
def show_stock_management(): st.info("Stock Management coming soon...")
def show_doctor_tracking(): st.info("Doctor Tracking coming soon...")
def show_analytics(): st.info("Analytics coming soon...")
def show_alerts(): st.info("Alerts coming soon...")
def show_ai_generator(): st.info("AI Generator coming soon...")
def show_reports(): st.info("Reports coming soon...")

# Main entrypoint
def main():
    if st.session_state.logged_in:
        show_dashboard()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
