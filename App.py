

import streamlit as st
import pandas as pd
from rapidapi import extend_dataframe
from article_info import show_articles_information
from gpt_functions import ChatGPT
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
load_dotenv()


# Access the environment variables
chat_gpt_api = os.getenv('CHATGPT_API_KEY')
backend_username = os.getenv('BACKEND_USERNAME')
rapid_api = os.getenv('RAPID_API_KEY')
testsystem_api = os.getenv('TESTSYSTEM_API')
testsystem_url = os.getenv('TESTSYSTEM_URL')
localsystem_api = os.getenv('LOCALSYSTEM_API')
localsystem_url = os.getenv('LOCALSYSTEM_URL')

if 'shopware_api_key' not in st.session_state:
    st.session_state.shopware_api_key = None
if 'shopware_url' not in st.session_state:
    st.session_state.shopware_url = None


st.set_page_config(
   page_title="Product Extender",
   page_icon=":smile:",
   layout="wide",
   initial_sidebar_state="expanded",
)

import streamlit as st
# Import our sub-pages
from get_products import get_products_page
from update_products import update_products_page
from import_products import import_products_page
from delete_products import delete_products_page
from chat_GPT import chat_page

# System Selection

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
    get_products_page()
elif selection == "Update Products":
    update_products_page()
elif selection == "Import Products":
    import_products_page()
elif selection == "Chat GPT":
    chat_page()
else:
    delete_products_page()

#cache for df if provided
if 'df' not in st.session_state:
    st.session_state.df = None