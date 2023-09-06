import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

import components.authenticate as authenticate

st.set_page_config(layout = "wide", 
                    page_title='EasyPie Finance Portfolio Manager',
                    initial_sidebar_state="auto") 
pd.set_option('display.max_colwidth', None)

st.title("EasyPie Finance Portfolio Manager")
st.write('''
        Welcome to EasyPie Finance Portfolio Manager, your all-in-one solution for managing your financial portfolio with ease.
        ''')
st.write('''
        Whether you're a seasoned investor or just starting your financial journey, our powerful tools and intuitive interface make managing your investments a breeze.
        ''')
with st.expander('Privacy Policy | Terms of Service'):
    st.write('''
    Disclaimer: EasyPie Finance Portfolio Manager is for informational purposes only and not financial advice. Consult a qualified advisor for personalized guidance.
    ''')

with st.sidebar:
    # image = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Zotero_logo.svg/1920px-Zotero_logo.svg.png'
    # st.image(image, width=150)
    # st.sidebar.markdown("# EasyPie Finance Portfolio Manager")
    with st.expander('About'):
        st.write('''
        Enter your credentials and click 'Display dashboard' to open EasyPie Finance Portfolio Manager.
        ''')

        st.write('This app was built and is managed by [Non Standard Logic](https://www.nonstandardlogic.com)  and is not affiliated with EasyPie Finance.')

        components.html(
        """
        <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0" 
        src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />
        © 2022 All rights reserved. This website is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
        """
        )

# Check authentication when user lands on the home page.
authenticate.set_st_state_vars()

# Add login/logout buttons
if st.session_state["authenticated"]:
    authenticate.button_logout()
else:
    authenticate.button_login()


components.html(
"""
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0" 
src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />
© 2022 All rights reserved. This website is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
"""
)  