import streamlit as st
from utils.helper import send_email

st.set_page_config(
    page_title="Portfolio Contact",
    page_icon="📮",
    initial_sidebar_state="expanded",
    layout="wide",
)
padding_top = 0
st.markdown(f"""
    <style>
        .block-container{{
            padding-top: {padding_top}rem;
        }}
    </style>""",
    unsafe_allow_html=True,
)
hide_streamlit_style = """
    <style>
        [data-testid="stToolbar"] {visibility: hidden !important;}
        footer {visibility: hidden !important;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.header("Contact Information")


with st.form(key="Email", clear_on_submit=True):
    subject = st.text_input(
        label="Subject", placeholder="Please enter the subject of your email"
    )

    name = st.text_input(label="Full name", placeholder="Please Enter Your full Name")
    email = st.text_input(label="Email Adress", placeholder="Please Enter Your Email")
    text = st.text_input(label="Message", placeholder="Please Enter Your Message")
    uploadedfile = st.file_uploader("Attachment")
    submitted = st.form_submit_button(label='Submit')

    if submitted:
        st.write(
            "Thanks for your contacting us. We will respond to your questions or inquiries as soon as possible!"
        )

        extra_info = """
        -------------------------------------------------------
        Email Address of Sender {} \n
        Full Name of Sender {} \n
        -------------------------------------------------------\n\n
         """.format(
            email, name
        )

        message = extra_info + text

        send_email(
            sender=st.secrets["smtp"]["SENDER_ADDRESS"],
            password=st.secrets["smtp"]["SENDER_PASSWORD"],
            receiver=email,
            smtp_server=st.secrets["smtp"]["SMTP_SERVER_ADDRESS"],
            smtp_port=st.secrets["smtp"]["PORT"],
            email_message=message,
            subject=subject,
            attachment=uploadedfile,
        )
