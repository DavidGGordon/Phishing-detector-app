import streamlit as st
from analyzer import is_phishing, analyze_email_content
from email_utils import fetch_emails

st.set_page_config(page_title="Phishing Analyzer", page_icon="✉️", layout="centered")
st.title("📨 Phishing Analyzer")
st.caption("Analyze incoming emails using both heuristics and AI.")

# API Key Setup
api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else st.text_input("Enter your OpenAI API Key")

# Email Fetching
st.subheader("📬 Analyze Your Inbox")

if st.button("Fetch & Analyze Emails"):
    try:
        with st.spinner("Connecting to your inbox..."):
            email_user = st.secrets["EMAIL_ADDRESS"]
            email_pass = st.secrets["EMAIL_PASSWORD"]
            fetched = fetch_emails(email_user, email_pass)

        if not fetched:
            st.warning("No emails found or failed to fetch.")
        else:
            for i, (subject, body) in enumerate(fetched):
                with st.expander(f"✉️ Email {i+1}: {subject}", expanded=False):
                    st.markdown("##### 📝 Preview:")
                    st.code(body[:1000] + ("..." if len(body) > 1000 else ""), language="markdown")

                    # GPT Analysis
                    gpt_result = analyze_email_content(body, openai_api_key=api_key)
                    st.info(f"**🤖 GPT Verdict:** {gpt_result}")

                    # Heuristic Check
                    if is_phishing(body):
                        st.error("⚠️ Heuristic: This email might be phishing.")
                    else:
                        st.success("✅ Heuristic: This email looks safe.")

    except Exception as e:
        st.error(f"Something went wrong while fetching or analyzing emails:\n\n`{e}`")

# Manual Analysis Section
st.subheader("🔍 Manual Email Check")
email_content = st.text_area("Paste the email content here:")

if st.button("Analyze"):
    with st.spinner("Analyzing email..."):
        gpt_result = analyze_email_content(email_content, openai_api_key=api_key)
        st.info(f"**🤖 GPT Verdict:** {gpt_result}")

        if is_phishing(email_content):
            st.error("⚠️ Heuristic: This email might be phishing.")
        else:
            st.success("✅ Heuristic: This email looks safe.")
