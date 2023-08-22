
import streamlit as st
from requests.auth import HTTPBasicAuth
from env_utilities import get_backend_username,get_localsystem_api, get_testsystem_api

def get_auth():
    return HTTPBasicAuth(get_backend_username(), st.session_state.shopware_api_key)
def get_auth_local():
    return HTTPBasicAuth(get_backend_username(), get_localsystem_api())
def get_auth_test():
    return HTTPBasicAuth(get_backend_username(), get_testsystem_api())
