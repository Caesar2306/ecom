
import streamlit as st
from requests.auth import HTTPBasicAuth
from functions.env_utilities import get_backend_username,get_localsystem_api, get_testsystem_api
import math

def get_auth():
    return HTTPBasicAuth(get_backend_username(), st.session_state.shopware_api_key)
def get_auth_local():
    return HTTPBasicAuth(get_backend_username(), get_localsystem_api())
def get_auth_test():
    return HTTPBasicAuth(get_backend_username(), get_testsystem_api())

def sanitize_data(data):
    #JSON compliant.
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(v) for v in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return 0.0
    return data