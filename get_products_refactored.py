
import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from shared_functions import get_auth
from env_utilities import (get_chat_gpt_api_key, get_backend_username, 
                           get_rapid_api_key, get_testsystem_api, 
                           get_testsystem_url, get_localsystem_api, 
                           get_localsystem_url)

# Access the environment variables
chat_gpt_api = get_chat_gpt_api_key()
backend_username = get_backend_username()
rapid_api = get_rapid_api_key()
testsystem_api = get_testsystem_api()
testsystem_url = get_testsystem_url()
localsystem_api = get_localsystem_api()
localsystem_url = get_localsystem_url()

# Streamlit configurations
st.set_page_config(
   page_title="Product Extender",
   page_icon=":smile:",
   layout="wide",
   initial_sidebar_state="expanded",
)

st.sidebar.title("Navigation")

# Determine the system to use: Testsystem or localhost
systemSelected = st.sidebar.radio("What System should I use?", ('Testsystem', 'localhost'))
if systemSelected == 'Testsystem':
    st.session_state.shopware_api_key = testsystem_api
    st.session_state.shopware_url = testsystem_url
else:
    # Rest of the code will be appended here
    pass
 
    st.session_state.shopware_api_key = localsystem_api
    st.session_state.shopware_url = localsystem_url


#cache for df if provided
if 'df' not in st.session_state:
    st.session_state.df = None




st.title("Get Products")

mysql_expressions = ["LIKE", "=", ">=", "<=", ">", "<", "IN"]

# Available columns

columns = [
    "id", "mainDetailId", "supplierId", "taxId", "priceGroupId", "filterGroupId",
    "configuratorSetId", "name", "description", "descriptionLong", "added", "active",
    "pseudoSales", "highlight", "keywords", "metaTitle", "changed", "priceGroupActive",
    "lastStock", "crossBundleLook", "notification", "template", "mode", "availableFrom",
    "availableTo", "mainDetail"
]
default_columns = ["id", "supplierId", "name", "description", "active", "mainDetail", "descriptionLong"]
# Authentication function
def get_auth():
    return HTTPBasicAuth(backend_username, st.session_state.shopware_api_key)

# Get articles function with filter, sort, limit, and offset
def get_all_articles(selected_columns, filters, sorts, limit, offset):
    params = {}
    if filters:
        params["filter"] = filters
    if sorts:
        params["sort"] = sorts
    if limit:
        params["limit"] = limit
    if offset:
        params["start"] = offset

    response = requests.get(st.session_state.shopware_url+'articles/', auth=get_auth(), json=params)
    if response.status_code == 200:
        articles = response.json()["data"]
        filtered_articles = [{key: article[key] for key in selected_columns} for article in articles]
        return filtered_articles
    