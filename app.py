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

# Helper to force rerun if supported
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.warning("Please refresh the page to complete login.")

# Page setup & styles
st.set_page_config(page_title="PharmaBiz Pro", page_icon="💊", layout="wide", initial_sidebar_state="expanded")
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

# Initialize session state keys
for key in ['logged_in', 'user_email', 'users', 'stocks', 'doctors']:
    if key not in st.session_state:
        st.session_state[key] = False if key == 'logged_in' else []

# Data persistence helpers
def load_data():
    os.makedirs('data', exist_ok=True)
    try:
        with open('data/users.json', 'r') as f:
            st.session_state.users = json.load(f)
    except:
        st.session_state.users = []
    try:
        with open('data/stocks.json', 'r') as f:
            st.session_state.stocks = json.load(f)
    except:
        st.session_state.stocks = []
    try:
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

# Auth helpers
def register_user(email, password, business_name):
    st.session_state.users.append({'email': email, 'password': password, 'business_name': business_name, 'created_at': datetime.now().isoformat()})
    save_data()

def login_user(email, password):
    for user in st.session_state.users:
        if user['email'] == email and user['password'] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            return True
    return False

# Google Imagen AI generation (unchanged)
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
                if login_user(email, password):
                    st.success("Login successful!")
                    safe_rerun()  # rerun or ask for refresh
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

# Dashboard and navigation
def show_dashboard():
    with st.sidebar:
        st.markdown("### 💊 PharmaBiz Pro")
        st.markdown(f"**User:** {st.session_state.user_email}")
        st.markdown("---")
        menu = st.radio("Navigation", ["📊 Dashboard","📦 Stock Management","👨‍⚕️ Doctor Tracking","📈 Analytics","🚨 Alerts","🎨 AI Generator","📄 Reports"], index=0)
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            safe_rerun()  # rerun or warn

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

# Example Dashboard Page
def show_dashboard_page():
    st.title("📊 Dashboard Overview")
    total_stock = sum([s.get("units",0) for s in st.session_state.stocks])
    total_sold = sum([s.get("sold",0) for s in st.session_state.stocks])
    total_revenue = sum([s.get("sold_amount",0) for s in st.session_state.stocks])
    total_invested = sum([s.get("paid",0) for s in st.session_state.stocks])
    profit = total_revenue - total_invested
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Stock Units", f"{total_stock:,}")
    col2.metric("Total Sold", f"{total_sold:,}")
    col3.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    col4.metric("Profit", f"₹{profit:,.0f}")

# Dummy placeholders for other pages
def show_stock_management():
    st.title("📦 Stock Management")
    st.info("Stock management section.")

def show_doctor_tracking():
    st.title("👨‍⚕️ Doctor Tracking")
    st.info("Doctor tracking section.")

def show_analytics():
    st.title("📈 Analytics")
    st.info("Analytics section.")

def show_alerts():
    st.title("🚨 Expiry Alerts")
    st.info("Alerts section.")

def show_ai_generator():
    st.title("🎨 AI Content Generator")
    prompt = st.text_area("Enter prompt:", placeholder="E.g., promotional image of medicine named ASDFG (Pain killer)")
    if st.button("Generate"):
        if prompt:
            image = generate_image_google(prompt)
            if image:
                st.image(image, caption="AI Generated Image")
            else:
                st.error("Failed to generate image.")
        else:
            st.warning("Please enter a prompt.")

def show_reports():
    st.title("📄 Reports")
    st.info("Reports & insights section.")

# Main control
def main():
    if st.session_state.logged_in:
        show_dashboard()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
