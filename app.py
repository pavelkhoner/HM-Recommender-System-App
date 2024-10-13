import streamlit as st
from core import main

import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

USERS_DB_PATH = './users_config.yml'

with open(USERS_DB_PATH) as file:
    config = yaml.load(file, Loader=SafeLoader)


# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

def login():
    try:
        authenticator.login()
    except stauth.LoginError as e:
        st.error("There is error during login process")


def register():
    status = None
    try:
        email_of_registered_user, \
        username_of_registered_user, \
        name_of_registered_user = authenticator.register_user()
        print('dir(authenticator)')
        print(dir(authenticator))
        if email_of_registered_user and username_of_registered_user and name_of_registered_user:
            with open(USERS_DB_PATH, 'w') as file:
                first_name, last_name = name_of_registered_user.split(' ')

                config['credentials']['usernames'].update({
                    username_of_registered_user: {
                        'email': email_of_registered_user,
                        'first_name': first_name,
                        'last_name': last_name,
                        'roles': ['admin', 'editor', 'viewer'],
                        'password': 'TestPassword5$',
                    }
                })
                yaml.dump(config, file, default_flow_style=False)
            status = True
        else:
            status = False
    except stauth.RegisterError as e:
        st.error(f"There is error during register process: {e}")
    else:
        if status:
            st.success('Successfully registered! Try to log in!')

if st.session_state['authentication_status']:
    authenticator.logout()
    main()
elif st.session_state['authentication_status'] is False:
    login()
    st.error('Wrong account! Try to register!')
    register()
elif st.session_state['authentication_status'] is None:
    login()
    st.warning('Please enter your username and password! Or Register:')
    register()
