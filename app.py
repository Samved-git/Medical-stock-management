import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import base64
import io

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.session_state["_rerun_flag"] = not st.session_state.get("_rerun_flag", False)

st.set_page_config(page_title="PharmaBiz Pro", page_icon="💊", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
  .main {background-color: #f8fafc;}
  .stButton>button {width: 100%; border-radius: 8px; height: 3em; font-weight: 600;}
  h1 {color: #1e293b;}
  .stAlert {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

for key in ['logged_in', 'user_email', 'users', 'stocks', 'doctors', '_rerun_flag']:
    if key not in st.session_state:
        st.session_state[key] = False if key in ['logged_in', '_rerun_flag'] else []

def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return []

def load_all_data():
    st.session_state.users = load_json("data/users.json")
    st.session_state.stocks = load_json("data/stocks.json")
    st.session_state.doctors = load_json("data/doctors.json")

def save_json(data, filepath):
    os.makedirs("data", exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def save_data():
    save_json(st.session_state.users, "data/users.json")
    save_json(st.session_state.stocks, "data/stocks.json")
    save_json(st.session_state.doctors, "data/doctors.json")

# Load all data fresh at app start or rerun
load_all_data()

def register_user(email, password, business_name):
    email = email.strip().lower()
    password = password.strip()
    business_name = business_name.strip()
    # Prevent duplicate email
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

def generate_image_google(prompt):
    genai.configure()  # API key managed by Streamlit Cloud environment
    model = genai.GenerativeModel("models/imagen-2")
    try:
        response = model.generate_content(prompt)
        image_data = response.candidates[0].content.parts[0].inline_data.data
        image_bytes = base64.b64decode(image_data)
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return None

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
                    success = register_user(email, password, business_name)
                    if success:
                        st.success("Registration successful! Please login.")
                else:
                    st.error("Please fill all fields!")

def show_stock_management():
    st.title("📦 Stock Management")
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx) to bulk add stocks", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            required_cols = {'name', 'batch_no', 'received', 'expired', 'paid', 'units', 'sold', 'sold_amount', 'prescribed_by'}
            if not required_cols.issubset(set(df.columns.str.lower())):
                st.error(f"Excel missing required columns: {required_cols}")
            else:
                df = df.rename(columns=str.lower)
                new_stocks = df.to_dict(orient='records')
                st.session_state.stocks.extend(new_stocks)
                save_data()
                st.success(f"{len(new_stocks)} stock records added!")
                safe_rerun()
        except Exception as e:
            st.error(f"Error processing file: {e}")

    st.markdown("### Add Stock Manually")
    with st.form("add_stock_form", clear_on_submit=True):
        name = st.text_input("Product Name")
        batch_no = st.text_input("Batch Number")
        received = st.date_input("Received Date")
        expired = st.date_input("Expiry Date")
        paid = st.number_input("Amount Paid", min_value=0.0, step=0.01)
        units = st.number_input("Total Units", min_value=0)
        sold = st.number_input("Units Sold", min_value=0)
        sold_amount = st.number_input("Sale Amount", min_value=0.0, step=0.01)
        prescribed_by = st.text_input("Prescribed By")
        submitted = st.form_submit_button("Add Stock")
        if submitted:
            new_stock = {
                "name": name,
                "batch_no": batch_no,
                "received": str(received),
                "expired": str(expired),
                "paid": paid,
                "units": units,
                "sold": sold,
                "sold_amount": sold_amount,
                "prescribed_by": prescribed_by,
            }
            st.session_state.stocks.append(new_stock)
            save_data()
            st.success("Stock added!")
            safe_rerun()

    st.dataframe(pd.DataFrame(st.session_state.stocks))

def show_doctor_tracking():
    st.title("👨‍⚕️ Doctor Tracking")
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx) to bulk add doctors", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            required_cols = {'name', 'clinic', 'phone', 'total_sales'}
            if not required_cols.issubset(set(df.columns.str.lower())):
                st.error(f"Excel missing required columns: {required_cols}")
            else:
                df = df.rename(columns=str.lower)
                new_docs = df.to_dict(orient='records')
                st.session_state.doctors.extend(new_docs)
                save_data()
                st.success(f"{len(new_docs)} doctor records added!")
                safe_rerun()
        except Exception as e:
            st.error(f"Error processing file: {e}")

    st.markdown("### Add Doctor Manually")
    with st.form("add_doctor_form", clear_on_submit=True):
        name = st.text_input("Doctor Name")
        clinic = st.text_input("Clinic")
        phone = st.text_input("Phone")
        total_sales = st.number_input("Total Sales", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Add Doctor")
        if submitted:
            new_doc = {
                "name": name,
                "clinic": clinic,
                "phone": phone,
                "total_sales": total_sales,
            }
            st.session_state.doctors.append(new_doc)
            save_data()
            st.success("Doctor added!")
            safe_rerun()

    st.dataframe(pd.DataFrame(st.session_state.doctors))

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

def show_analytics():
    st.info("Analytics features coming soon.")

def show_alerts():
    st.info("Alerts features coming soon.")

def show_ai_generator():
    st.info("AI Generator coming soon.")

def show_reports():
    st.info("Reports coming soon.")

def main():
    if st.session_state.logged_in:
        show_dashboard()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
