import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
# from streamlit_authenticator.utilities.hasher import Hasher
# import hmac
import extra_streamlit_components as stx
import datetime
from st_pages import show_pages, hide_pages, Page

st.set_page_config(
    page_title='Home',
    initial_sidebar_state='auto',
    layout='centered',
)

show_pages(
    [
        Page("Home.py", "Home", "🏠"),
        Page("./pages/2_Dashboard.py", "Dashboard"),
        Page("./pages/3_Contact_Us.py", "Contact Us"),
        Page('./pages/99_Login.py', 'Login'),
    ]
)
hide_pages(['Login'])

ss = st.session_state

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()
cookie_manager = get_manager()

with st.container(border=False, height=1):
    cookie_manager.set('last_page', './Home.py')

# Login
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )

authenticator.login()

if ss.get("authentication_status") is None:
    st.switch_page('./pages/99_Login.py')
elif st.session_state["authentication_status"] is False:
    st.error('Username or password is incorrect')
else:
    # cookie_manager = get_manager()
    with st.sidebar:
        authenticator.logout()

st.write('Hello')

# cookie_manager = get_manager()



# st.subheader("All Cookies:")
# cookies = cookie_manager.get_all()
# st.write(cookies)

# c1, c2, c3 = st.columns(3)

# with c1:
#     st.subheader("Get Cookie:")
#     cookie = st.text_input("Cookie", key="0")
#     clicked = st.button("Get")
#     if clicked:
#         value = cookie_manager.get(cookie=cookie)
#         st.write(value)
# with c2:
#     st.subheader("Set Cookie:")
#     cookie = st.text_input("Cookie", key="1")
#     val = st.text_input("Value")
#     if st.button("Add"):
#         cookie_manager.set(cookie, val) # Expires in a day by default
# with c3:
#     st.subheader("Delete Cookie:")
#     cookie = st.text_input("Cookie", key="2")
#     if st.button("Delete"):
#         cookie_manager.delete(cookie)

# st.write(cookie_manager.get(cookie='authentication_cookie'))
# cookie_manager.set('test_cookie', '123')
# st.write(cookie_manager.get(cookie='test_cookie'))
# cookie_manager.set('test_cookie', '456')
# st.write(cookie_manager.get(cookie='test_cookie'))


















# st.write(ss)

# def check_password():
#     """Returns `True` if the user had the correct password."""

#     def password_entered():
#         """Checks whether a password entered by the user is correct."""
#         if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
#             st.session_state["password_correct"] = True
#             del st.session_state["password"]  # Don't store the password.
#         else:
#             st.session_state["password_correct"] = False

#     # Return True if the password is validated.
#     if st.session_state.get("password_correct", False):
#         return True

#     # Show input for password.
#     st.text_input(
#         "Password", type="password", on_change=password_entered, key="password"
#     )
#     if "password_correct" in st.session_state:
#         st.error("😕 Password incorrect")
#     return False

# if not check_password():
#     st.stop()  # Do not continue if check_password is not True.

# # Main Streamlit app starts here
# st.write("Here goes your normal Streamlit app...")
# st.button("Click me")


# # Login
# with open('config.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)

#     authenticator = stauth.Authenticate(
#         config['credentials'],
#         config['cookie']['name'],
#         config['cookie']['key'],
#         config['cookie']['expiry_days'],
#         config['pre-authorized']
#     )

# st.write(ss.get("authentication_status"))
# authenticator.login()

# # if ss.get("authentication_status") is None:
# #     # st.markdown(
# #     # """
# #     # <style>
# #     #     [data-testid="collapsedControl"] {
# #     #         display: none
# #     #     }
# #     # </style>
# #     # """,
# #     #     unsafe_allow_html=True,
# #     # )
# #     authenticator.login()
# if ss.get("authentication_status") is None:
#     pass
# elif st.session_state["authentication_status"] is False:
#     st.error('Username or password is incorrect')
# else:
#     # cookie_manager = get_manager()
#     with st.sidebar:
#         authenticator.logout()




# # Authenticating
# if st.session_state["authentication_status"]:
#     authenticator.logout()
#     st.write(f'Welcome *{st.session_state["name"]}*')
#     st.title('Some content')
# elif st.session_state["authentication_status"] is False:
#     st.error('Username/password is incorrect')
# elif st.session_state["authentication_status"] is None:
#     st.warning('Please enter your username and password')

# # Changing Password
# if st.session_state["authentication_status"]:
#     try:
#         if authenticator.reset_password(st.session_state["username"]):
#             st.success('Password modified successfully')
#     except Exception as e:
#         st.error(e)
