import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities.hasher import Hasher
import extra_streamlit_components as stx

st.set_page_config(
    page_title='Home',
    initial_sidebar_state='collapsed',
    layout='centered',
)
st.markdown(
"""
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

ss = st.session_state

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager(key='streamlit-demo-1-cookies')
cookie_manager = get_manager()
with st.container(border=False, height=1):
    last_page = cookie_manager.get('last_page') # ss.get('init', {}).get('last_page', './Home.py')

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

authenticator.login()
if st.session_state["authentication_status"] is True:
    st.switch_page(last_page)
elif st.session_state["authentication_status"] is False:
    st.error('Username or password is incorrect')

