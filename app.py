import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import google.generativeai as genai
import matplotlib.pyplot as plt
import altair as alt

# Configure API key (used for any AI features)
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.session_state["_rerun_flag"] = not st.session_state.get("_rerun_flag", False)

def page_welcome():
    st.markdown("<h1 style='text-align:center; color:#1e293b;'>Welcome to ABCD Pharma</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Your trusted pharma business management solution.</p>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; margin-top:40px;'>", unsafe_allow_html=True)
    if st.button("Continue"):
        st.session_state['welcome_done'] = True
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    if 'welcome_done' not in st.session_state:
        st.session_state['welcome_done'] = False

    if not st.session_state['welcome_done']:
        page_welcome()
        return

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = ''

    # Show login or main pages after welcome
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

# The rest of your app functions (page_login, page_stock, page_doctor, page_dashboard, page_diagrams, save/load, etc.)
# should be included here as previously specified, unchanged except for the above main() logic.

if __name__ == "__main__":
    main()
