import pandas as pd
import streamlit as st
import joblib
import re
import string
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set page configuration
st.set_page_config(
    page_title="Phishing Email Detector",
    page_icon="📧",
    layout="centered",
    initial_sidebar_state="auto",
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .stTextArea textarea {
        background-color: #ffffff;
        color: #000000;
    }
    .stAlert {
        background-color: #ffcccb;
        color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# Load trained model and TF-IDF vectorizer with error handling
try:
    model = joblib.load("phishing_detector_model.pkl")
    vectorizer = joblib.load("tfidf_vectorizer.pkl")
except Exception as e:
    st.error("Error loading model or vectorizer. Please check the files.")
    logging.error(f"Error loading model/vectorizer: {e}")
    st.stop()

# Cleaning function
def clean_email(text):
    if pd.isna(text):
        return ""
    text = re.sub(r"<.*?>", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Callback function to clear the text area
def clear_text():
    st.session_state.email_input = ""

# Streamlit UI
st.title("📧 Phishing Email Detector")

# Initialize session state for email input
if "email_input" not in st.session_state:
    st.session_state.email_input = ""

# Buttons first
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    analyze_button = st.button("🔍 Analyze Email", type="primary")
with col2:
    clear_button = st.button("🧹 Clear", on_click=clear_text)
with col3:
    sample_button = st.button("📋 Load Sample Email")

# Handle button clicks BEFORE rendering text_area
if sample_button:
    st.session_state.email_input = """Dear User,

Your account has been flagged for suspicious activity. Please click the link below to verify your identity and avoid service interruption.

Verify Now: http://suspicious-link.com

Thank you,
Support Team
"""

# Input field - created AFTER session state is updated
email_input = st.text_area(
    "Paste the email content here:",
    value=st.session_state.email_input,
    height=300,
    key="email_input",
    help="Enter the full email you want to analyze."
)

# Main functionality
if analyze_button:
    if email_input.strip() == "":
        st.warning("Please enter email content to analyze.")
    else:
        cleaned_input = clean_email(email_input)
        transformed_input = vectorizer.transform([cleaned_input])
        prediction = model.predict(transformed_input)[0]

        if prediction == 1.0:
            st.error("⚠️ This email is likely a phishing attempt!")
        else:
            st.success("✅ This email appears to be safe.")

        logging.info(f"Email analyzed: {email_input}")
