

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
backend_username = os.getenv('BACKEND_USERNAME')
rapid_api = os.getenv('RAPID_API_KEY')
testsystem_api = os.getenv('TESTSYSTEM_API')
testsystem_url = os.getenv('TESTSYSTEM_URL')
localsystem_api = os.getenv('LOCALSYSTEM_API')
localsystem_url = os.getenv('LOCALSYSTEM_URL')

# Initialize ChatGPT
chat_gpt = ChatGPT(chat_gpt_api)

st.set_page_config(
   page_title="Product Extender",
   page_icon=":smile:",
   layout="wide",
   initial_sidebar_state="expanded",
)

# System Selection
systemSelected = st.radio("What System should I use?", ('Testsystem','localhost'))
if systemSelected == 'Testsystem':
    shopware_api_key = testsystem_api
    shopware_url = testsystem_url
else: 
    shopware_api_key = localsystem_api
    shopware_url = localsystem_url

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
    return HTTPBasicAuth(backend_username, shopware_api_key)

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

    response = requests.get(shopware_url+'articles/', auth=get_auth(), json=params)
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

        response = requests.get(f"{shopware_url}articles/{number}", auth=get_auth(), params=params)
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

# if st.session_state.df is not None and not st.session_state.df.empty: 
#     st.data_editor(st.session_state.df, key="data_editor")
#     st.write("Here's the session state:")
#     st.write(st.session_state["data_editor"])

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
    response = requests.get(f"{shopware_url}articles/{article_id}", auth=get_auth())
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
    response = requests.put(f"{shopware_url}articles/{article_id}", auth=get_auth(), json=update_data)
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


st.subheader('Magie')



# import imageio
# from PIL import Image

# def convert_webp_to_jpg(input_path, output_path):
#     image_data = imageio.imread(input_path)
#     img = Image.fromarray(image_data)
#     img.convert('RGB').save(output_path, 'JPEG')


df_files = pd.read_csv("/Users/euphorika/Desktop/ecom/inputs/compagnie_de_provence_extended.csv", delimiter=';', encoding='utf-8', nrows=10)
# Display the first few rows
st.write(df_files.head())
# def convert_to_absolute_uri(relative_path):
#     # Get the absolute path
#     absolute_path = os.path.abspath(relative_path)
    
#     # Convert to URI format
#     uri = "file://" + absolute_path
    
#     return uri
# # Helper function to download images
# def get_image_extension_from_headers(headers):
#     content_type = headers.get('content-type')
#     if 'jpeg' in content_type or 'jpg' in content_type:
#         return 'jpg'
#     if 'png' in content_type:
#         return 'png'
#     if 'gif' in content_type:
#         return 'gif'
#     if 'webp' in content_type:
#         return 'webp'
#     return None  # default if we can't determine

# def download_image(shopware_url, file_path_without_extension):
#     try:
#         # Ensure the directory exists
#         directory = os.path.dirname(file_path_without_extension)
#         if not os.path.exists(directory):
#             os.makedirs(directory)
        
#         response = requests.get(shopware_url, stream=True)
#         response.raise_for_status()  # Raise an error for bad responses
        
#         # Get image format
#         extension = get_image_extension_from_headers(response.headers)
#         if not extension:
#             return

#         file_path = f"{file_path_without_extension}.{extension}"
        
#         with open(file_path, 'wb') as file:
#             for chunk in response.iter_content(chunk_size=8192): 
#                 file.write(chunk)
#                 return file_path
                

#     except Exception as e:
#         st.error(f"Error downloading image from {shopware_url}: {e}")


def add_product(data):
    response = requests.post(f"{shopware_url}articles/", auth=get_auth(), json=data)
    if response.status_code == 200 or response.status_code == 201:
        return True, ''
    else:
        return False, response.text  # Return the API error message
# def add_media(image_data):
#     st.write(urlImage)  # Print the URL
#     response = requests.post(f"http://localhost:8000/api/media", auth=get_auth(), json=image_data)
#     st.write(response.status_code, response.text)  # Print the status code and response text

#     if response.status_code == 200 or response.status_code == 201:
#         return response.json()['data']['id']  # Return the ID of the new media object
#     else:
#         return None  # Return None if the request failed
# Add products button
if st.button('Add Products from CSV'):
    success_count = 0
    failed_rows = []
    error_messages = []
    
    for idx, row in df_files.iterrows():
        # image_urls = ast.literal_eval(row['product_photos'])
        # images = []
        # for position, urlImage in enumerate(image_urls, start=1):
        #     local_file_path = f"./images/{row['mainDetailNumber']}_{position}"
        #     local_file_path = download_image(urlImage, local_file_path )
            
        #     image_data = {
        #         "file": convert_to_absolute_uri(convert_webp_to_jpg(local_file_path, local_file_path.replace('inputs','outputs'))),
        #         "album" : -1,
        #         "description": f"{row['mainDetailNumber']}_{position}"
        #     }
        #     media_id = add_media(image_data)
        #     st.write(f"media_id: {media_id}")  # Check the value of media_id
        #     if media_id is not None:
        #         images.append({"mediaId": media_id})
        # st.write(f"images: {images}")  # Check the value of images
        product_data = {
            'name': row['name'],
            'taxId': 1,
            'supplierId': 97,
            'description_long':row['description_long'],
            'active': True,
            'mainDetail': {
                'number': row['mainDetailNumber']+'_2',
                'active': True,
                'inStock': row['purchaseunitdetail'] * (row['Menge'] if not pd.isna(row['Menge']) else 1),
                'purchasePrice' : float(row['Purchaseprice'].replace(',', '.').replace('€', '').strip()),
                'EAN': row['mainDetailEAN'],
                'prices': [
                    {
                        "customerGroupKey": "EK",
                        "price": float(row['pseudoprice'].replace(',', '.').replace('€', '').strip()),
                        "pseudoprice": float(row['pseudoprice'].replace(',', '.').replace('€', '').strip())
                    }
                ]
            },
            # 'images': images, 
            'seoCategories': [
                {
                    "shopId": 1,
                    "categoryId": 1435
                }
            ],
            'categories': [
                {
                    "id": 1435
                }
            ]
        }
        # product_data['images'] = images

# Add the product
        success, error_msg = add_product(product_data)  
        if success:
            success_count += 1
        else:
            failed_rows.append(idx)
            error_messages.append(error_msg)
            st.error(error_msg)
    
    st.write(f"Added {success_count} products successfully!")
    if failed_rows:
        st.write(f"Failed to add products for rows: {', '.join(map(str, failed_rows))}")
        for idx, error in zip(failed_rows, error_messages):
            st.write(f"Row {idx} Error: {error}")  

st.subheader(":chat: Chat")
with st.container():
    cols = st.columns([1,2])
    with cols[0].container():
        inputtxt = st.text_area('User Input')
    with cols[1].container():
        systeminputtxt = st.text_area('System Input')
    if st.button('Ask chat GPT-4.0'):
        with st.spinner('Wait for it...'):
            st.write(chat_gpt.make_response(systeminputtxt, inputtxt))