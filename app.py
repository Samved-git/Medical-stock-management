import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import google.generativeai as genai
import matplotlib.pyplot as plt

# Configure API key globally even if chatbot removed
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.session_state["_rerun_flag"] = not st.session_state.get("_rerun_flag", False)

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

for key in ['logged_in','user_email','users','stocks','doctors','_rerun_flag']:
    if key not in st.session_state:
        if key in ['logged_in','_rerun_flag']:
            st.session_state[key] = False
        else:
            st.session_state[key] = []

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
            st.session_state.logged_in = True
            st.session_state.user_email = email
            return True
    return False

def page_login():
    col1, col2, col3 = st.columns([1,2,1])
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
                        st.error("Email already registered")
                else:
                    st.error("Fill all fields")

def page_stock():
    st.title("📦 Stock Management")
    uploaded = st.file_uploader("Upload Excel", type=["xlsx"])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, engine="openpyxl")
            required = {'name','batch_no','received','expired','paid','units','sold','sold_amount','prescribed_by'}
            if not required.issubset(df.columns.str.lower()):
                st.error(f"Need columns: {required}")
            else:
                df.columns = df.columns.str.lower()
                st.session_state.stocks.extend(df.to_dict(orient='records'))
                save_all()
                st.success(f"Added {len(df)} records")
                safe_rerun()
        except Exception as e:
            st.error(f"Excel error: {e}")

    st.markdown("### Add Stock Manually")
    with st.form("stock_form", clear_on_submit=True):
        name = st.text_input("Product Name")
        batch_no = st.text_input("Batch Number")
        received = st.date_input("Received Date")
        expired = st.date_input("Expiry Date")
        paid = st.number_input("Paid Amount", min_value=0.0)
        units = st.number_input("Units")
        sold = st.number_input("Sold")
        sold_amount = st.number_input("Sold Amount", min_value=0.0)
        prescribed = st.text_input("Prescribed By")
        submit = st.form_submit_button("Add Stock")
        if submit:
            st.session_state.stocks.append({
                "name": name,
                "batch_no": batch_no,
                "received": str(received),
                "expired": str(expired),
                "paid": paid,
                "units": units,
                "sold": sold,
                "sold_amount": sold_amount,
                "prescribed_by": prescribed
            })
            save_all()
            st.success("Stock added")
            safe_rerun()

    if st.session_state.stocks:
        df_stocks = pd.DataFrame(st.session_state.stocks)
        st.dataframe(df_stocks)

        # Expiry Alert within 30 days
        today = date.today()
        expiry_alerts = []
        for _, row in df_stocks.iterrows():
            try:
                exp_date = pd.to_datetime(row['expired']).date()
                days_left = (exp_date - today).days
                if 0 <= days_left <= 30:
                    expiry_alerts.append(f"⚠️ Stock '{row['name']}' batch {row['batch_no']} expires in {days_left} days.")
            except Exception:
                pass

        if expiry_alerts:
            st.warning("\n".join(expiry_alerts))
        else:
            st.success("No stocks are expiring within 30 days.")

def page_doctor():
    st.title("👨‍⚕️ Doctor Tracking")
    uploaded = st.file_uploader("Upload Excel", type=["xlsx"])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, engine="openpyxl")
            required = {'name','clinic','phone','total_sales'}
            if not required.issubset(df.columns.str.lower()):
                st.error(f"Need columns: {required}")
            else:
                df.columns = df.columns.str.lower()
                st.session_state.doctors.extend(df.to_dict(orient='records'))
                save_all()
                st.success(f"Added {len(df)} doctors")
                safe_rerun()
        except Exception as e:
            st.error(f"Excel error: {e}")

    st.markdown("### Add Doctor Manually")
    with st.form("doctor_form", clear_on_submit=True):
        name = st.text_input("Doctor Name")
        clinic = st.text_input("Clinic")
        phone = st.text_input("Phone")
        sales = st.number_input("Total Sales", min_value=0.0)
        submit = st.form_submit_button("Add Doctor")
        if submit:
            st.session_state.doctors.append({
                "name": name,
                "clinic": clinic,
                "phone": phone,
                "total_sales": sales
            })
            save_all()
            st.success("Doctor added")
            safe_rerun()

    if st.session_state.doctors:
        st.dataframe(pd.DataFrame(st.session_state.doctors))

def page_dashboard():
    st.title("📊 Dashboard Overview")
    total_units = sum(s.get("units", 0) for s in st.session_state.stocks)
    total_sold = sum(s.get("sold", 0) for s in st.session_state.stocks)
    total_revenue = sum(s.get("sold_amount", 0) for s in st.session_state.stocks)
    total_invested = sum(s.get("paid", 0) for s in st.session_state.stocks)
    profit = total_revenue - total_invested
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Stock Units", f"{total_units:,}")
    col2.metric("Total Sold", f"{total_sold:,}")
    col3.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    col4.metric("Profit", f"₹{profit:,.0f}")

def page_diagrams():
    st.title("📈 Visualizations & Reports")

    # Stocks units bar chart
    st.subheader("Stock Units by Product")
    if st.session_state.stocks:
        df_stocks = pd.DataFrame(st.session_state.stocks)
        df_grouped = df_stocks.groupby('name')['units'].sum().reset_index()
        st.bar_chart(df_grouped.set_index('name'))

    # Profit vs Loss pie chart
    st.subheader("Profit vs Loss Overview")
    if st.session_state.stocks:
        df_stocks = pd.DataFrame(st.session_state.stocks)
        revenue = df_stocks['sold_amount'].sum()
        invested = df_stocks['paid'].sum()
        profit = revenue - invested
        loss = invested - revenue if invested > revenue else 0
        profit = profit if profit > 0 else 0
        st.write(f"Total Revenue: ₹{revenue:,.0f}")
        st.write(f"Total Investment: ₹{invested:,.0f}")
        st.write(f"Profit: ₹{profit:,.0f}")
        st.write(f"Loss: ₹{loss:,.0f}")
        pie_data = pd.DataFrame({
            'Amount': [profit, loss],
            'Category': ['Profit', 'Loss']
        }).set_index('Category')
        fig, ax = plt.subplots()
        pie_data.plot.pie(y='Amount', autopct='%1.1f%%', ax=ax)
        ax.set_ylabel('')
        st.pyplot(fig)

    # Doctor total sales bar chart
    st.subheader("Doctor Total Sales")
    if st.session_state.doctors:
        df_doctors = pd.DataFrame(st.session_state.doctors)
        df_sales = df_doctors.groupby('name')['total_sales'].sum().reset_index()
        if not df_sales.empty:
            df_sales = df_sales.sort_values('total_sales', ascending=True)
            st.bar_chart(df_sales.set_index('name'))

def main():
    if st.session_state.logged_in:
        with st.sidebar:
            st.title("💊 PharmaBiz Pro")
            st.write(f"User: {st.session_state.user_email}")
            menu = st.radio("Menu", [
                "Dashboard",
                "Stock Management",
                "Doctor Tracking",
                "Diagrams & Reports"
            ])
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_email = ""
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
