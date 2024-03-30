import streamlit as st

st.set_page_config(
    page_title='Home',
    initial_sidebar_state='auto',
    layout='wide',
)

ss = st.session_state

# st.markdown(
#     """
#     <style>
#         section[data-testid="stSidebar"] {
#             width: 300px !important; # Set the width to your desired value
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

st.write("Hello!")