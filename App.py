import streamlit as st
import pandas as pd
from rapidapi import extend_dataframe
from article_info import show_articles_information
from gpt_functions import ChatGPT
import openai 
import time
import requests
from requests.auth import HTTPBasicAuth

chat_gpt = ChatGPT("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")

st.set_page_config(
   page_title="Product Extender",
   page_icon=":smile:",
   layout="wide",
   initial_sidebar_state="expanded",
)
systemSelected = st.radio("What System should I use?", ('Testsystem','localhost'))

if systemSelected == 'Testsystem':
    api_key = "NtFc6aIB9kyktckuRqb4mTkkcC8iVvxNSHLSaf4F"
    url = "https://www.schoenheitsberatung.de/euphorika-dev-2021/api/articles"
    backend_username = "vadim"
else: 
    url = "http://localhost:8000/api/articles"
    api_key = "IbqzBaJMnif6qRwXGa4smXfWcsVvcn8iQDMiWgwF"
    backend_username = "vadim"

st.subheader('Get Products')
# Available MySQL expressions

if 'df' not in st.session_state:
    st.session_state.df = None


mysql_expressions = ["LIKE", "=", ">=", "<=", ">", "<", "IN"]

# Available columns
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
        params["filter"] = filters
    if sorts:
        params["sort"] = sorts
    if limit:
        params["limit"] = limit
    if offset:
        params["start"] = offset

    response = requests.get(url, auth=get_auth(), json=params)
    if response.status_code == 200:
        articles = response.json()["data"]
        filtered_articles = [{key: article[key] for key in selected_columns} for article in articles]
        return filtered_articles
    else:
        return None


# Multiselect box for columns
selected_columns = st.multiselect("Select Columns", options=columns, default=default_columns)

# Function to extract selected fields from article data
def extract_article_data(article, selected_fields):
    extracted_data = {}
    for field in selected_fields:
        if field in article:
            extracted_data[field] = article[field]
        else:
            # Check for nested fields
            for key, value in article.items():
                if isinstance(value, dict) and field in value:
                    extracted_data[field] = value[field]
    return extracted_data

# Function to get articles based on order numbers
def get_articles_by_order_numbers(order_numbers, filters=None, sort=None, limit=None):
    articles = []
    for number in order_numbers:
        params = {"useNumberAsId": "true"}
        if filters:
            params["filter"] = filters
        if sort:
            params["sort"] = sort
        if limit:
            params.update(limit)

        response = requests.get(f"{url}/{number}", auth=get_auth(), params=params)
        if response.status_code == 200:
            articles.append(response.json())
        else:
            st.warning(f"Failed to retrieve article with order number {number}. Status code: {response.status_code}")

    return articles



# Filter options
filters = []
use_filter = st.checkbox("Use Filter")
if use_filter:
    st.write("Filters:")
    filter_count = st.number_input("Number of Filters:", min_value=1, max_value=5, value=1, step=1)
    for i in range(filter_count):
        cols = st.columns(4)
        property_filter = cols[0].selectbox(f"Property {i+1}", options=columns, index=0, key=f"property{i}")
        expression_filter = cols[1].selectbox(f"Expression {i+1}", options=mysql_expressions, index=0, key=f"expression{i}")
        value_filter = cols[2].text_input(f"Value {i+1}", key=f"value{i}")
        operator_filter = cols[3].selectbox(f"Operator {i+1} ('AND': AND, 'OR': OR)", options=['AND', 'OR'], index=0, key=f"operator{i}")
        use_operator = cols[3].checkbox("Use Operator", key=f"use_operator{i}")
        if property_filter and value_filter:
            filter_dict = {
                "property": property_filter,
                "expression": expression_filter,
                "value": value_filter,
            }
            if use_operator:
                filter_dict["operator"] = operator_filter
            filters.append(filter_dict)

# Sort options
sorts = []
use_sort = st.checkbox("Use Sort")
if use_sort:
    st.write("Sorts:")
    sort_count = st.number_input("Number of Sorts:", min_value=1, max_value=5, value=1, step=1)
    for i in range(sort_count):
        cols = st.columns(2)
        property_sort = cols[0].selectbox(f"Sort Property {i+1}", options=columns, index=0, key=f"sort_property{i}")
        direction_sort = cols[1].selectbox(f"Direction {i+1}", options=["ASC", "DESC"], index=0, key=f"direction{i}")
        if property_sort:
            sorts.append({
                "property": property_sort,
                "direction": direction_sort
            })

# Limit and Offset options
use_limit_offset = st.checkbox("Use Limit/Offset")
limit = 30
offset = None
if use_limit_offset:
    limit = st.number_input("Limit:", min_value=1, max_value=10000, value=30, step=1)
    offset = st.number_input("Offset:", min_value=0, max_value=10000, value=0, step=1)
# Button to trigger API request
if 'df' not in st.session_state:
    st.session_state.df = None

if st.button("Get Articles") and selected_columns:
    articles = get_all_articles(selected_columns, filters, sorts, limit, offset)
    if articles:
        st.write("Displaying articles:")
        df = pd.DataFrame(articles)
        st.session_state.df = df
        st.dataframe(df)
    else:
        st.write("Failed to retrieve articles.")
elif not selected_columns:
    st.write("Please select at least one column.")

if st.session_state.df is not None and not st.session_state.df.empty: 
    st.data_editor(st.session_state.df, key="data_editor")
    st.write("Here's the session state:")
    st.write(st.session_state["data_editor"])

# Finding product using Ordernumber

# List of available fields
available_fields = [
    "id", "active", "added", "changed", "crossBundleLook", "description", 
    "descriptionLong", "filterGroupId", "highlight", "keywords", 
    "lastStock", "metaTitle", "mode", "name", "notification", "priceGroupActive",
    "pseudoSales", "mainDetailId", "supplierId", "taxId", "priceGroupId",
    "configuratorSetId", "categories", "customerGroups", "details", "downloads",
    "images", "links", "mainDetail", "propertyGroup", "propertyValues",
    "seoCategories", "similar", "supplier", "tax", "template"
]
st.subheader('Find product using Ordernumber')
# Multi-select input in Streamlit
selected_fields = st.multiselect(
    "Choose the fields you want to display",
    options=available_fields,
    default=["id", "name", "description", "active", "mainDetail"]
)
order_numbers_input = st.text_input("Enter Article Order Numbers (comma separated):")
if order_numbers_input:
    order_numbers = [number.strip() for number in order_numbers_input.split(",")]

    # Retrieve articles based on order numbers
    articles = get_articles_by_order_numbers(order_numbers, filters=filters)  # Add sort and limit if needed

    # Extract only the selected fields
    articles_selected_fields = [extract_article_data(article, selected_fields) for article in articles]

    # Display articles
    if articles_selected_fields:
        st.write("Displaying articles:")
        for article in articles_selected_fields:
            st.write(f"Name: {article['name']}")
            st.write(f"Main Detail Number: {article['mainDetail']['number']}")
            st.json(article,expanded=False)
    else:
        st.write("Failed to retrieve articles.")



#Update products using id 

article = None
st.subheader('Update Products')
article_id = st.text_input("Enter the article ID:")
def get_article_by_id(article_id):
    response = requests.get(f"{url}/{article_id}", auth=get_auth())
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return None

if article_id:
    article = get_article_by_id(article_id)
    if article is not None:
        desired_fields = {key: article[key] for key in ["id", "name", "description", "mainDetail"]}
        st.json(desired_fields)
    else:
        st.warning(f"Failed to retrieve article with ID {article_id}.")
def update_article_price(article_id, new_price):
    update_data = {
        "mainDetail": {
            "prices": [
                {
                    "price": new_price
                }
            ]
        }
    }
    response = requests.put(f"{url}/{article_id}", auth=get_auth(), json=update_data)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return None

if article and 'mainDetail' in article and 'prices' in article['mainDetail'] and article['mainDetail']['prices']:
    current_price = article['mainDetail']['prices'][0]['price']
    st.write(f"Current price: {current_price}")
    new_price = st.number_input("Enter the new price:", min_value=0.0, value=current_price)
    
    if st.button("Update price"):
        updated_article = update_article_price(article_id, new_price)
        if updated_article is not None:
            st.success("Price updated successfully!")
        else:
            st.error("Failed to update price.")

st.subheader('Edit Article')

# Assuming the variable article contains the fetched article data

def display_nested_data(data, key_prefix=""):
    for key, value in data.items():
        new_key = f"{key_prefix}.{key}" if key_prefix else key
        
        if isinstance(value, dict):
            with st.expander(f"Edit {key}"):
                display_nested_data(value, new_key)
        elif isinstance(value, list):
            # Handle lists - you might need more specific handling here
            st.write(key)
            for idx, item in enumerate(value):
                with st.expander(f"Item {idx+1}"):
                    display_nested_data(item, f"{new_key}.{idx}")
        else:
            # Display simple field for editing
            data[key] = st.text_input(f"{key}", value)

display_nested_data(article)

# When user submits the edited data
if st.button("Submit Changes"):
    # Now the variable article contains the edited data
    # You can use it to send an update request to the API
    pass
