import streamlit as st

# Configure the application
st.set_page_config(
    page_title="Prep_AI",
    page_icon="📊",
    layout="wide"
)

# Application title
st.title("📊 Prep_AI")

st.subheader("AI-Powered Data Preprocessing and Visualization Platform")

st.write(
    "Upload, clean, transform, analyze and visualize "
    "your datasets in one place."
)

st.divider()

st.success("Welcome to Prep_AI!")

st.info("Your data analysis workspace is ready.")