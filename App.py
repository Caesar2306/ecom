

import streamlit as st
from dotenv import load_dotenv
from functions.get_products import get_products
from functions.update_products import update_products
from functions.delete_products import delete_products
from functions.import_products import import_products
from functions.chat_GPT import chat_GPT
from env_utilities import get_backend_username,get_rapid_api_key,get_testsystem_api,get_testsystem_url,get_localsystem_api,get_localsystem_url,get_chat_gpt_api_key
load_dotenv()

st.set_page_config(
   page_title="Product Extender",
   page_icon=":smile:",
   layout="wide",
   initial_sidebar_state="expanded",
)

# Access the environment variables

chat_gpt_api = get_chat_gpt_api_key()
backend_username = get_backend_username()
rapid_api = get_rapid_api_key()
testsystem_api = get_testsystem_api()
testsystem_url = get_testsystem_url()
localsystem_api = get_localsystem_api()
localsystem_url = get_localsystem_url()

st.session_state.backend_username = backend_username

if 'backend_username' not in st.session_state:
    st.session_state.backend_username = None
if 'shopware_api_key' not in st.session_state:
    st.session_state.shopware_api_key = None
if 'shopware_url' not in st.session_state:
    st.session_state.shopware_url = None



st.sidebar.title("Navigation")

systemSelected = st.sidebar.radio("What System should I use?", ('Testsystem','localhost'))
if systemSelected == 'Testsystem':
    st.session_state.shopware_api_key = testsystem_api
    st.session_state.shopware_url = testsystem_url
else: 
    st.session_state.shopware_api_key = localsystem_api
    st.session_state.shopware_url = localsystem_url

selection = st.sidebar.radio("Pages:", ["Get Products", "Update Products", "Import Products", "Delete Products","Chat GPT"])

if selection == "Get Products":
    get_products()
elif selection == "Update Products":
    update_products()
elif selection == "Import Products":
    import_products()
elif selection == "Chat GPT":
    chat_GPT()
else:
    delete_products()


#cache for df if provided
if 'df' not in st.session_state:
    st.session_state.df = None