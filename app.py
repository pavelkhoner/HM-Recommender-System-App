import streamlit as st
from core import main

import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
with open('./users_config.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)


# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

try:
    authenticator.login()
except stauth.LoginError as e:
    st.error("There is error during login process")


if st.session_state['authentication_status']:
    authenticator.logout()
    main()
elif st.session_state['authentication_status'] is False:
    st.error('Wrong account!')
