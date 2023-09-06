import  streamlit as st

st.set_page_config(
        page_title="Portfolio Contact", 
        page_icon="📈", 
        initial_sidebar_state="expanded",
        layout="wide",
)

st.header("Contact Information")

with st.form(key='columns_in_form2',clear_on_submit=True): #set clear_on_submit=True so that the form will be reset/cleared once it's submitted
    Name=st.text_input(label='Please Enter Your Name') #Collect user feedback
    Email=st.text_input(label='Please Enter Your Email') #Collect user feedback
    Message=st.text_input(label='Please Enter Your Message') #Collect user feedback
    submitted = st.form_submit_button('Submit')
    if submitted:
        st.write('Thanks for your contacting us. We will respond to your questions or inquiries as soon as possible!')

