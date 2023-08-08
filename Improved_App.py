

import streamlit as st
import pandas as pd
from rapidapi import extend_dataframe
from article_info import show_articles_information
from gpt_functions import ChatGPT
import openai 
import time
import requests
from requests.auth import HTTPBasicAuth
import ast
import ssl
import os
from PIL import Image
from dotenv import load_dotenv
load_dotenv()


# Access the environment variables
chat_gpt_api = os.getenv('CHATGPT_API_KEY')
backend_user = os.getenv('BACKEND_USERNAME')
rapid_api = os.getenv('RAPID_API_KEY')
testsystem_api = os.getenv('TESTSYSTEM_API')
testsystem_url = os.getenv('TESTSYSTEM_URL')
localsystem_api = os.getenv('LOCALSYSTEM_API')
localsystem_url = os.getenv('LOCALSYSTEM_URL')

# Bypass SSL Verification (this may have security implications and should be reviewed)
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize ChatGPT
chat_gpt = ChatGPT(chat_gpt_api)

# Streamlit Page Configuration
st.set_page_config(
   page_title="Product Extender",
   page_icon=":moon:",
   layout="wide",
   initial_sidebar_state="expanded",
)

# System Selection
systemSelected = st.radio("What System should I use?", ('Testsystem','localhost'))
if systemSelected == 'Testsystem':
    api_key = testsystem_api
    url = testsystem_url
    backend_username = backend_user
else: 
    url = localsystem_url
    api_key = localsystem_api



# Constants for MySQL expressions
mysql_expressions = ["LIKE", "=", ">=", "<=", ">", "<", "IN"]

# Available columns for articles
columns = [
    "id", "mainDetailId", "supplierId", "taxId", "priceGroupId", "filterGroupId",
    "configuratorSetId", "name", "description", "descriptionLong", "added", "active",
    "pseudoSales", "highlight", "keywords", "metaTitle", "changed", "priceGroupActive",
    "lastStock", "crossBundleLook", "notification", "template", "mode", "availableFrom",
    "availableTo", "mainDetail"
]
default_columns = ["id", "supplierId", "name", "description", "active", "mainDetail"]



# Authentication function
def get_auth():
    return HTTPBasicAuth(backend_username, api_key)

# Get articles function with filter, sort, limit, and offset
def get_all_articles(selected_columns, filters, sorts, limit, offset):
    params = {}
    if filters:
        params["filters"] = filters
    if sorts:
        params["sorts"] = sorts
    if limit:
        params["limit"] = limit
    if offset:
        params["offset"] = offset
    response = requests.get(url, auth=get_auth(), params=params)
    data = response.json()
    return pd.DataFrame(data)


# Frontend UI Logic
# -----------------
# Here, you can add the Streamlit UI components, possibly integrating them with the sidebar for navigation.
# You can structure this section based on the original content or any additional requirements you have.

# For example:
# st.sidebar.title("Navigation")
# add_article_option = st.sidebar.button("Add Article")
# update_article_option = st.sidebar.button("Update Article")
# find_article_option = st.sidebar.button("Find Article")

# if add_article_option:
#     # Logic for adding an article
#     pass

# if update_article_option:
#     # Logic for updating an article
#     pass

# if find_article_option:
#     # Logic for finding an article
#     pass

# Frontend UI Logic
# -----------------
# Using Streamlit's sidebar for navigation
st.sidebar.title("Navigation")

# Sidebar options
find_products_option = st.sidebar.button("Find Products")
update_delete_products_option = st.sidebar.button("Update/Delete Products")
enhance_product_info_option = st.sidebar.button("Enhance Product Info with RapidAPI")
bulk_import_products_option = st.sidebar.button("Bulk Import Products")
content_generation_option = st.sidebar.button("Content Generation with ChatGPT")

if find_products_option:
    # Logic for finding products
    # You can call the necessary API here and display the products
    pass

if update_delete_products_option:
    # Logic for updating or deleting products
    # Provide UI components to modify product details or delete the product
    pass

if enhance_product_info_option:
    # Logic to fetch additional information for products using EAN and RapidAPI
    # Update the product details with the fetched data
    pass

if bulk_import_products_option:
    # Logic for bulk importing products using CSV files
    # Process the data and add multiple products at once
    pass

if content_generation_option:
    # Logic for content generation using ChatGPT
    # Provide a UI component to take user input and generate content
    # Update product details with the generated content
    pass
