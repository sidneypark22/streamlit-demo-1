import streamlit as st
import duckdb
import re
import streamlit_authenticator as stauth
import extra_streamlit_components as stx
import yaml
from yaml.loader import SafeLoader
import requests

st.set_page_config(
    page_title='Contact Us',
    initial_sidebar_state='auto',
    layout='centered',
)

# @st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager(key='streamlit-demo-1-cookies')
cookie_manager = get_manager()

with st.container(border=False, height=1):
    cookie_manager.set('last_page', './pages/3_Contact_Us.py')

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

authenticator.login()

if st.session_state.get("authentication_status") is None:
    st.switch_page('Home.py')
else:
    with st.sidebar.container():
        authenticator.logout()
    db_name = 'website1'

    conn = duckdb.connect(db_name)

    conn.execute(
        """create table if not exists contact_request (
            first_name string,
            last_name string,
            email string,
            phone_number string,
            mesession_stateage string,
            request_timestamp timestamp
        )"""
    )

    df = conn.execute(
        """select * from contact_request"""
    ).df()

    phone_number_pattern = r"^\d+-\d+-\d+$"
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    c_top_message_form = st.container()
    c_contact_form = st.container()
    c_message = st.container()
    c3 = st.container()

    if 'contact_request_submitted' not in st.session_state:
        st.session_state['contact_request_submitted'] = False

    if 'contact_form_submit_count' not in st.session_state:
        st.session_state.contact_form_submit_count = 0

    if 'on_change_first_name_count' not in st.session_state:
        st.session_state.on_change_first_name_count = 0

    if 'default_values' not in st.session_state:
        st.session_state.default_values = {}

    def get_session_value_for_default(key):
        st.session_state.get(key, '') if st.session_state.form_error_count > 0 else '',

    if 'form_error_count' not in st.session_state:
        st.session_state.form_error_count = 0

    error_messages = {}

    def get_state_session_value_form_submit(key: str):
        if st.session_state.form_error_count > 0:
            return st.session_state.get(key)
        else:
            return None

    def on_change_first_name(first_name):
        if st.session_state.on_change_first_name_count == 0:
            st.session_state.on_change_first_name_count += 1
        else:
            if first_name == '':
                error_messages['first_name'] = 'First Name should not be blank.'
                st.error('First Name should not be blank.')
                st.session_state.form_error_count += 1

    def on_submit_contact_request(first_name, last_name, email, phone_number, mesession_stateage, contact_form_submit_count):
        if not st.session_state.get('FormSubmitter:contact_request-Submit', False):
            st.session_state.contact_form_submit_count += 1
        else:
            st.session_state.form_error_count = 0
            
            if first_name == '':
                error_messages['first_name'] = 'First Name should not be blank.'
                st.session_state.form_error_count += 1
            
            if last_name == '':
                error_messages['last_name'] = 'Last Name should not be blank.'
                st.session_state.form_error_count += 1
            
            # email validation
            email_validation_result = re.findall(email_pattern, email)
            if email == '':
                error_messages['email'] = 'Email should not be blank.'
                st.session_state.form_error_count += 1
            elif len(email_validation_result) == 0:
                error_messages['email'] = 'Email is not in the correct format.'
                st.session_state.form_error_count += 1
            else:
                pass

            # phone_number validation
            phone_number_validation_result = re.findall(phone_number_pattern, phone_number)
            if phone_number == '':
                error_messages['phone_number'] = 'Phone number should not be blank.'
                st.session_state.form_error_count += 1
            elif len(phone_number_validation_result) == 0:
                error_messages['phone_number'] = 'Phone number is not in the correct format.'
                st.session_state.form_error_count += 1
            else:
                pass
                
            if message == '':
                error_messages['message'] = 'Message should not be blank.'
                st.session_state.form_error_count += 1
            
            if st.session_state.form_error_count == 0:
                conn.execute(
                    """insert into contact_request
                    (first_name, last_name, email, phone_number, message, request_timestamp)
                    values
                    (?, ?, ?, ?, ?, current_timestamp)""", [first_name, last_name, email, phone_number, message]
                )
                st.session_state['contact_request_submitted'] = True
                with c_message:
                    st.success("Message has been successfully submitted.")

                    st.write('Request has been saved to database. Further works can be done to send an email when a request is logged.')
                    st.write('- First name:', first_name)
                    st.write('- Last name:', last_name)
                    st.write('- Email:', email)
                    st.write('- Phone number:', phone_number)
                    st.write('- Message:', message)
                    
            else:
                with c_message:
                    for _, v in error_messages.items():
                        st.error(v)
            
            st.session_state.contact_form_submit_count += 1    

    with c_top_message_form:
        st.write('Details entered in the form will be saved to a temporary database.')

    with c_contact_form:
        with st.form(
            key='contact_request',
            clear_on_submit=False,
            border=True
        ):       
                first_name = st.text_input(
                    key='first_name',
                    label='First Name',
                    placeholder="Enter Your First Name",
                )

                last_name = st.text_input(
                    key='last_name',
                    label='Last Name',
                    placeholder="Enter Your Last Name"
                )

                email = st.text_input(
                    key="email_address",
                    label="Email Address",
                    placeholder="Enter Email Address",
                )

                phone_number = st.text_input(
                    key='phone_number',
                    label='Phone Number',
                    placeholder="000-000-0000"
                )

                message = st.text_input(
                    key='message',
                    label='Message'
                )

                submitted = st.form_submit_button(
                    on_click=on_submit_contact_request(first_name, last_name, email, phone_number, message, st.session_state.contact_form_submit_count),
                )
