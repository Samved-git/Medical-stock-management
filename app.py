import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import google.generativeai as genai
import matplotlib.pyplot as plt
import altair as alt

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.session_state["_rerun_flag"] = not st.session_state.get("_rerun_flag", False)

def page_welcome():
    st.markdown("<h1 style='text-align:center; color:#1e293b;'>Welcome to ABCD Pharma</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Your trusted pharma business management solution.</p>", unsafe_allow_html=True)
    if st.button("Continue"):
        st.session_state['welcome_done'] = True

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []

def save_json(data, file):
    os.makedirs("data", exist_ok=True)
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def load_all():
    st.session_state.users = load_json("data/users.json")
    st.session_state.stocks = load_json("data/stocks.json")
    st.session_state.doctors = load_json("data/doctors.json")

def save_all():
    save_json(st.session_state.users, "data/users.json")
    save_json(st.session_state.stocks, "data/stocks.json")
    save_json(st.session_state.doctors, "data/doctors.json")

load_all()

def register(email, password, business):
    email = email.strip().lower()
    password = password.strip()
    business = business.strip()
    if any(u['email'] == email for u in st.session_state.users):
        st.warning("User already registered.")
        return False
    st.session_state.users.append({
        "email": email,
        "password": password,
        "business_name": business,
        "created_at": datetime.now().isoformat()
    })
    save_all()
    return True

def login(email, password):
    email = email.strip().lower()
    password = password.strip()
    for u in st.session_state.users:
        if u['email'] == email and u['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['user_email'] = email
            return True
    return False

def page_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("💊 PharmaBiz Pro")
        tabs = st.tabs(["Login", "Register"])
        with tabs[0]:
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                if login(email, password):
                    st.success("Logged in")
                    safe_rerun()
                else:
                    st.error("Invalid credentials")
        with tabs[1]:
            st.subheader("Register")
            business = st.text_input("Business Name", key="reg_business")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            if st.button("Register"):
                if business and email and password:
                    if register(email, password, business):
                        st.success("Registered! Please login.")
                    else:
                        st.error("Already registered.")
                else:
                    st.error("Fill all fields")

def page_stock():
    st.title("📦 Stock Management")
    uploaded = st.file_uploader("Upload Excel", type=["xlsx"])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, engine="openpyxl")
            required = {'name', 'batch_no', 'received', 'expired', 'paid', 'units'}
            if not required.issubset(df.columns.str.lower()):
                st.error(f"Need columns: {required}")
            else:
                df.columns = df.columns.str.lower()
                st.session_state.stocks.extend(df.to_dict(orient='records'))
                save_all()
                st.success(f"Added {len(df)} records")
                safe_rerun()
        except Exception as e:
            st.error(str(e))
    st.markdown("### Add Product")
    with st.form("product_form", clear_on_submit=True):
        name = st.text_input("Product Name")
        batch_no = st.text_input("Batch No")
        received = st.date_input("Received Date")
        expired = st.date_input("Expiry Date")
        paid = st.number_input("Paid", min_value=0.0)
        units = st.number_input("Units")
        submit = st.form_submit_button("Add Product")
        if submit:
            st.session_state.stocks.append({
                "name": name,
                "batch_no": batch_no,
                "received": str(received),
                "expired": str(expired),
                "paid": paid,
                "units": units
            })
            save_all()
            st.success("Product added")
            safe_rerun()

    if st.session_state.stocks:
        df = pd.DataFrame(st.session_state.stocks)
        stock_cols = ['name', 'batch_no', 'received', 'expired', 'paid', 'units']
        st.dataframe(df[stock_cols])
        today = date.today()
        expiry_alerts = []
        for _, row in df.iterrows():
            try:
                exp_date = pd.to_datetime(row['expired']).date()
                days_left = (exp_date - today).days
                if 0 <= days_left <= 30:
                    expiry_alerts.append(f"⚠️ '{row['name']}' batch {row['batch_no']} expires in {days_left} days")
            except:
                continue
        if expiry_alerts:
            st.warning("\n".join(expiry_alerts))
        else:
            st.success("No stocks expiring soon.")

def page_doctor():
    st.title("👨‍⚕️ Doctor Tracking")
    uploaded = st.file_uploader("Upload Excel", type=["xlsx"])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, engine="openpyxl")
            required = {'name', 'clinic', 'phone', 'total_sales', 'subscribed_products', 'total_units_bought'}
            if not required.issubset(df.columns.str.lower()):
                st.error(f"Need columns: {required}")
            else:
                df.columns = df.columns.str.lower()
                df['subscribed_products'] = df['subscribed_products'].apply(
                    lambda x: [p.strip() for p in x.split(",")] if isinstance(x, str) else []
                )
                st.session_state.doctors.extend(df.to_dict(orient='records'))
                save_all()
                st.success(f"Added {len(df)} doctors")
                safe_rerun()
        except Exception as e:
            st.error(str(e))

    st.markdown("### Add Doctor")
    with st.form("doctor_form", clear_on_submit=True):
        name = st.text_input("Doctor Name")
        clinic = st.text_input("Clinic")
        phone = st.text_input("Phone")
        total_sales = st.number_input("Total Sales", min_value=0.0)
        subscribed_products = st.text_input("Subscribed Products (comma separated)")
        total_units_input = st.number_input("Total Units Bought", min_value=0)
        submit = st.form_submit_button("Add")
        if submit:
            products_list = [p.strip() for p in subscribed_products.split(",") if p.strip()] if subscribed_products else []

            st.session_state.doctors.append({
                "name": name,
                "clinic": clinic,
                "phone": phone,
                "total_sales": total_sales,
                "subscribed_products": products_list,
                "total_units_bought": int(total_units_input)
            })
            save_all()
            st.success(f"Doctor added! Total Units Bought: {int(total_units_input)}")
            safe_rerun()

    if st.session_state.doctors:
        df_doctors = pd.DataFrame(st.session_state.doctors)
        if 'subscribed_products' in df_doctors.columns:
            df_doctors['subscribed_products'] = df_doctors['subscribed_products'].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else "")
        st.dataframe(df_doctors[['name', 'clinic', 'phone', 'total_sales', 'subscribed_products', 'total_units_bought']])

def page_dashboard():
    st.title("📊 Dashboard Overview")
    total_units = sum(s.get("units", 0) for s in st.session_state.stocks)
    total_revenue = sum(s.get("paid", 0) for s in st.session_state.stocks)
    total_invested = total_revenue
    profit = total_revenue - total_invested
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Stock Units", f"{total_units}")
    col2.metric("Revenue", f"₹{total_revenue:,.0f}")
    col3.metric("Investment", f"₹{total_invested:,.0f}")
    col4.metric("Profit", f"₹{profit:,.0f}")

def page_diagrams():
    st.title("📈 Visual Reports")
    if st.session_state.stocks:
        df = pd.DataFrame(st.session_state.stocks)
        prod_amount = df.groupby('name')['paid'].sum().reset_index().rename(columns={'paid': 'total_amount'})
        st.subheader("Product-wise Amount Table")
        st.dataframe(prod_amount)

        st.subheader("Product-wise Amount Pie Chart")
        pie_chart = alt.Chart(prod_amount).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="total_amount", type="quantitative"),
            color=alt.Color("name:N", legend=alt.Legend(title="Product Name")),
            tooltip=["name", "total_amount"]
        ).properties(width=400, height=400)

        st.altair_chart(pie_chart, use_container_width=False)

    if st.session_state.doctors:
        df_doctors = pd.DataFrame(st.session_state.doctors)
        df_doctors['total_sales'] = pd.to_numeric(df_doctors['total_sales'], errors='coerce').fillna(0)
        sales_grouped = df_doctors.groupby('name')['total_sales'].sum().reset_index()
        st.subheader("Doctor-wise Total Sales Table")
        st.dataframe(sales_grouped)
        sales_chart = alt.Chart(sales_grouped).mark_bar(color="#ff7f0e").encode(
            x=alt.X('total_sales', title='Total Sales'),
            y=alt.Y('name', sort='-x', title='Doctor'),
            tooltip=['name', 'total_sales']
        ).properties(width=700, height=400)
        st.altair_chart(sales_chart, use_container_width=True)

def main():
    if 'welcome_done' not in st.session_state:
        st.session_state['welcome_done'] = False
    if not st.session_state['welcome_done']:
        page_welcome()
        return
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = ''
    if st.session_state['logged_in']:
        with st.sidebar:
            st.title("💊 PharmaBiz Pro")
            st.write(f"User: {st.session_state['user_email']}")
            menu = st.radio("Menu", ["Dashboard", "Stock Management", "Doctor Tracking", "Diagrams & Reports"])
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.session_state['user_email'] = ''
                safe_rerun()
        if menu == "Dashboard":
            page_dashboard()
        elif menu == "Stock Management":
            page_stock()
        elif menu == "Doctor Tracking":
            page_doctor()
        elif menu == "Diagrams & Reports":
            page_diagrams()
    else:
        page_login()

if __name__=="__main__":
    main()
