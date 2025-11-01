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

# Helper to force app rerun (automatic page refresh)
def rerun():
    st.experimental_rerun()

# Page config & styling
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
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    h1 {color: #1e293b;}
    .stAlert {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# Initialize session-state entries
for key in ['logged_in', 'user_email', 'users', 'stocks', 'doctors']:
    if key not in st.session_state:
        if key == 'logged_in':
            st.session_state[key] = False
        else:
            st.session_state[key] = []

# Data persistence helpers
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

# Authentication functions
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

# Google AI Image generation
def generate_image_google(prompt):
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
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
        st.error(f"Image generation failed: {str(e)}")
        return None

# UI pages/functions

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
                    rerun()  # reload app immediately to show dashboard
                    return
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
            rerun()  # force immediate reload to login page

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

# (Implement other UI functions similarly, unchanged)

def main():
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
