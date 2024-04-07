import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import extra_streamlit_components as stx
import time

st.set_page_config(
    page_title='Home',
    initial_sidebar_state='auto',
    layout='centered',
)

def get_cookie_manager(key: str = 'init'):
    @st.cache_resource(experimental_allow_widgets=True)
    def get_manager():
        return stx.CookieManager(key=key)
    cookie_manager = get_manager()
    return cookie_manager

def authenticate(auth_config_file_name: str = 'config.yaml'):
    # Login
    with open(auth_config_file_name) as file:
        config = yaml.load(file, Loader=SafeLoader)

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['pre-authorized']
        )

    authenticator.login(
        location='main',
        max_concurrent_users=5, 
        max_login_attempts=3, 
        clear_on_submit=True,
    )

    if st.session_state['authentication_status']:
        authenticator.logout(
            location='sidebar',
        )
        st.write(f'Hello {st.session_state["name"]}!')
    elif st.session_state['authentication_status'] == False:
        st.error('Username or password is incorrect')
    elif st.session_state.get('authentication_status') is None:
        st.warning('Please enter your username and password. Use "jsmith" and "abc" for this demo.')

if __name__ == '__main__':
    # cookie_manager = get_cookie_manager('streamlit-demo-1-cookies')
    authenticate()
