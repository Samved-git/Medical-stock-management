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

# Rerun helper using stable API
def rerun():
    try:
        st.experimental_rerun()
    except Exception as e:
        st.warning(f"Could not auto-refresh the app. Please manually reload the page. Error: {e}")

# -- Your existing app logic below --

# Example usage inside login function:
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
                    rerun()
                    return
                else:
                    st.error("Invalid credentials!")

# Similarly, use rerun() after data changes or logout

# Continue your full app code with all occurrences replaced by rerun() for reruns.

# -- rest of your app.py --
