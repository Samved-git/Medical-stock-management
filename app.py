import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from google import genai

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.session_state["_rerun_flag"] = not st.session_state.get("_rerun_flag", False)

st.set_page_config(page_title="PharmaBiz Pro", page_icon="💊", layout="wide", initial_sidebar_state="expanded")

for key in ['logged_in', 'user_email', 'users', 'stocks', 'doctors', 'chat_history', '_rerun_flag']:
    if key not in st.session_state:
        st.session_state[key] = False if key in ['logged_in', '_rerun_flag'] else ([] if key != 'chat_history' else [])

def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return []

def save_json(data, filepath):
    os.makedirs("data", exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def load_all_data():
    st.session_state.users = load_json("data/users.json")
    st.session_state.stocks = load_json("data/stocks.json")
    st.session_state.doctors = load_json("data/doctors.json")

def save_data():
    save_json(st.session_state.users, "data/users.json")
    save_json(st.session_state.stocks, "data/stocks.json")
    save_json(st.session_state.doctors, "data/doctors.json")

load_all_data()

def register_user(email, password, business_name):
    email = email.strip().lower()
    password = password.strip()
    business_name = business_name.strip()
    for user in st.session_state.users:
        if user['email'] == email:
            st.warning("User already registered.")
            return False
    st.session_state.users.append({
        "email": email,
        "password": password,
        "business_name": business_name,
        "created_at": datetime.now().isoformat()
    })
    save_data()
    return True

def login_user(email, password):
    email = email.strip().lower()
    password = password.strip()
    for user in st.session_state.users:
        if user['email'] == email and user['password'] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            return True
    return False

client = genai.Client()  # initialize once

def generate_chat_response(prompt):
    try:
        response = client.chat_completions.create(
            model="gemini-1.5-turbo",
            messages=[{"author": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI chat generation failed: {e}")
        return "Sorry, I couldn't process that."

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("💊 PharmaBiz Pro")
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
                else:
                    st.error("Please fill all fields!")

def show_ai_chatbot():
    st.title("🤖 AI Chatbot Assistant")
    st.markdown("Ask any questions about your pharmaceutical business or general queries.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def add_message(role, content):
        st.session_state.chat_history.append({"role": role, "content": content})

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Enter your question here:")
        submitted = st.form_submit_button("Send")
    if submitted and user_input.strip():
        add_message("user", user_input)
        with st.spinner("AI is thinking..."):
            ai_reply = generate_chat_response(user_input)
        add_message("assistant", ai_reply)
        safe_rerun()
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")

# Implement your other feature pages here (stock, doctor, dashboard, etc.) as before

def main():
    if st.session_state.logged_in:
        show_dashboard()
    else:
        show_login_page()

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
                "📄 Reports"
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
        show_ai_chatbot()
    elif menu == "📄 Reports":
        show_reports()

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

# Implement other feature placeholders...

def show_stock_management():
    st.info("Stock management coming soon.")

def show_doctor_tracking():
    st.info("Doctor tracking coming soon.")

def show_analytics():
    st.info("Analytics coming soon.")

def show_alerts():
    st.info("Alerts coming soon.")

def show_reports():
    st.info("Reports coming soon.")

if __name__ == "__main__":
    main()
