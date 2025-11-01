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

# Safe rerun helper: tries st.experimental_rerun(), else no-op
def rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        # Fall back: show notice to user — manual refresh required
        st.warning("Please refresh the page to continue.")

# Page Config and CSS
st.set_page_config(page_title="PharmaBiz Pro", page_icon="💊", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .main {background-color: #f8fafc;}
    .stButton>button {width: 100%; border-radius: 8px; height: 3em; font-weight: 600;}
    h1 {color: #1e293b;}
    .stAlert {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# Session state init
for key in ['logged_in', 'user_email', 'users', 'stocks', 'doctors']:
    if key not in st.session_state:
        st.session_state[key] = False if key == "logged_in" else []

# Load/save data helpers
def load_data():
    os.makedirs("data", exist_ok=True)
    try:
        with open("data/users.json", "r") as f:
            st.session_state.users = json.load(f)
    except: st.session_state.users = []
    try:
        with open("data/stocks.json", "r") as f:
            st.session_state.stocks = json.load(f)
    except: st.session_state.stocks = []
    try:
        with open("data/doctors.json", "r") as f:
            st.session_state.doctors = json.load(f)
    except: st.session_state.doctors = []

def save_data():
    os.makedirs("data", exist_ok=True)
    with open("data/users.json", "w") as f:
        json.dump(st.session_state.users, f)
    with open("data/stocks.json", "w") as f:
        json.dump(st.session_state.stocks, f)
    with open("data/doctors.json", "w") as f:
        json.dump(st.session_state.doctors, f)

load_data()

# Authentication
def register_user(email, password, business_name):
    user = {'email': email, 'password': password, 'business_name': business_name, 'created_at': datetime.now().isoformat()}
    st.session_state.users.append(user)
    save_data()

def login_user(email, password):
    for user in st.session_state.users:
        if user['email'] == email and user['password'] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            return True
    return False

# Google Imagen AI generator
def generate_image_google(prompt):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("Missing GOOGLE_API_KEY in secrets")
        return None
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/imagen-2")
    try:
        response = model.generate_content(prompt)
        image_data = response.candidates[0].content.parts[0].inline_data.data
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        return image
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
                if login_user(email, password):
                    st.success("Login successful!")
                    rerun()
                else:
                    st.error("Invalid credentials!")

        with tab2:
            st.subheader("Create New Account")
            business = st.text_input("Business Name", key="reg_business")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            if st.button("Register"):
                if business and email and password:
                    register_user(email, password, business)
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Please fill all fields!")

# Dashboard UI and Navigation
def show_dashboard():
    with st.sidebar:
        st.markdown("### 💊 PharmaBiz Pro")
        st.markdown(f"**User:** {st.session_state.user_email}")
        st.markdown("---")
        menu = st.radio("Navigation", ["📊 Dashboard","📦 Stock Management","👨‍⚕️ Doctor Tracking","📈 Analytics","🚨 Alerts","🎨 AI Generator","📄 Reports"])
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            rerun()

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

# Example Dashboard page
def show_dashboard_page():
    st.title("📊 Dashboard Overview")
    total_stock = sum([s['units'] for s in st.session_state.stocks])
    total_sold = sum([s['sold'] for s in st.session_state.stocks])
    total_revenue = sum([s['sold_amount'] for s in st.session_state.stocks])
    total_invested = sum([s['paid'] for s in st.session_state.stocks])
    profit = total_revenue - total_invested
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Stock Units", f"{total_stock:,}")
    col2.metric("Total Sold", f"{total_sold:,}")
    col3.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    col4.metric("Profit", f"₹{profit:,.0f}")

# (Other pages implementation omitted for brevity: use your current code here.)

# Main app control
def main():
    if st.session_state.logged_in:
        show_dashboard()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
