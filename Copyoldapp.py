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

# # Initialize session state for uploaded_file and extended_df
# if 'uploaded_file' not in st.session_state:
#     st.session_state.uploaded_file = None

# if 'extended_df' not in st.session_state:
#     st.session_state.extended_df = None

# uploaded_file = st.file_uploader("Choose a file")

# if uploaded_file is not None:
#     df = pd.read_csv(uploaded_file, sep=';')
#     st.session_state.uploaded_file = df
#     st.dataframe(df)
# else:
#     df = pd.read_csv('inputs/output_short.csv', sep=',')
#     st.session_state.uploaded_file = df
#     st.write('Uploaded file not found, preset used')

# if st.button('Extend file'):
#     with st.spinner('Wait for it...'):
#         if  st.session_state.uploaded_file is not None:
#             st.session_state.extended_df = extend_dataframe(st.session_state.uploaded_file)  
#             st.dataframe(st.session_state.extended_df[["EAN","artikelordernummer","Artikelname","product_description", "product_photos", "product_attributes"]])
#             st.success('Done!')
    
#     if st.session_state.extended_df is not None:
#         show_articles_information(st.session_state.extended_df)
#         st.download_button('Download file', st.session_state.extended_df.to_csv(index=False), file_name='output.csv')
# else:
#     st.write('File is not extended')

# # if st.session_state.extended_df is not None:
# # else: st.write('you must download file')

# tab1, tab2, tab3 = st.tabs(["options", ":chat: Chat", "🗃 Data"])

# tab1.subheader("options")
# # show_articles_information(inputdf)
# tab2.write("tab2")

# tab2.subheader(":chat: Chat")
# with tab2.container():
#     cols = st.columns([1,2])
#     with cols[0].container():
#         inputtxt = st.text_area('User Input')
#     with cols[1].container():
#         systeminputtxt = st.text_area('System Input')
#     if st.button('Ask chat GPT-3.5'):
#         with st.spinner('Wait for it...'):
#             st.write(chat_gpt.make_response(systeminputtxt, inputtxt))


# tab3.subheader("🗃 Data")
# tab3.write("tab3")



# if st.session_state.uploaded_file is not None:
#     options = st.multiselect('Which columns should be analyzed?', st.session_state.uploaded_file.columns)
# for option in options:
#     cols = st.columns([0.5,2,1])
#     with cols[0].container():
#         st.write(option)
#     with cols[1].container():
#         inputtxt = st.text_area('User input (option information fetched automatically)' + option)
#     with cols[2].container():
#         systeminputtxt = st.text_area('System (Product name added automatically) ' + option)
#     if st.button('Ask chat GPT-3.5 to update ' + option):
#         with st.spinner('Wait for it...'):
#             new_column = []
#             for index, row in st.session_state.uploaded_file.iterrows():
#                 success=False
#                 ean = row['EAN']
#                 while not success:
#                     try:
#                         extended_value = chat_gpt.make_response(systeminputtxt + " for the product " + str(row['Artikelname']), inputtxt + ' ' + str(row[option]))
#                         new_column.append(extended_value)
#                         st.write('trying '+str(ean))
#                         success=True
#                     except openai.error.RateLimitError as e:
#                         print(f"Rate limit error: {e}. Retrying in 5 seconds...")
#                         time.sleep(5)
#                     except openai.error.APIError as e:
#                         print(f"API error: {e}. Retrying in 5 seconds...")
#                         time.sleep(5)
#                     except Exception as e:
#                         print(f"Unexpected error: {e}. Retrying in 5 seconds...")
#                         time.sleep(5)
#                         print(f"No data returned from API for product with EAN {ean}.")
#             st.session_state.uploaded_file[option+"_extended"] = new_column
#             with st.spinner('Waiting for updates'):
#                 st.dataframe(st.session_state.uploaded_file[['EAN',option,option+'_extended']])
#     st.divider()

# URL and credentials


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
if st.button("Get Articles") and selected_columns:
    articles = get_all_articles(selected_columns, filters, sorts, limit, offset)
    if articles:
        st.write("Displaying articles:")
        df = pd.DataFrame(articles)
        st.dataframe(df)
    else:
        st.write("Failed to retrieve articles.")
elif not selected_columns:
    st.write("Please select at least one column.")

if 'df' in locals() and not df.empty: 
    st.data_editor(df, key="data_editor")
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

st.subheader('Update Products')
# Input for article ID
article_id = st.text_input("Enter the article ID:")

# Function to get article by order number
def get_article_by_order_number(order_number):
    response = requests.get(f"{url}/{order_number}?useNumberAsId=true", auth=get_auth())
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return None

# Function to update article by order number
def update_article_by_order_number(order_number, article):
    response = requests.put(f"{url}/{order_number}?useNumberAsId=true", auth=get_auth(), json=article)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return None

# Input for order number
order_number = st.text_input("Enter the order number:")

# Fetch and display article data
if order_number:
    article = get_article_by_order_number(order_number)
    if article is not None:
        # Display current price
        current_price = article['mainDetail']['prices'][0]['price']
        st.write(f"Current price: {current_price}")
        # Display article data
        st.table(article)

# Input for new price
new_price = st.number_input("Enter the new price:", min_value=0.0)

# Update price
if st.button("Update price"):
    if article and new_price >= 0:
        # Copy the article data to avoid modifying the original data
        updated_article = article.copy()
        updated_article['mainDetail']['prices'][0]['price'] = new_price
        updated_article = update_article_by_order_number(order_number, updated_article)
        if updated_article is not None:
            st.success("Price updated successfully!")
            st.table(updated_article)
        else:
            st.error("Failed to update price.")
    else:
        st.error("Please enter a valid order number and price.")


 # def generate_meta_title(self, product_title, product_description):
    #     message_content = f"Generate a meta title on german for the product with title '{product_title}' and description '{product_description}'"

    #     messages = [
    #         {"role": "system", "content": "You are given a product title and description. Your task is to generate a suitable short meta title on german for this product. Use informal style like 'du'."},
    #         {"role": "user", "content": message_content}
    #     ]
    #     try:
    #         response = openai.ChatCompletion.create(
    #             model="gpt-4",
    #             messages=messages,
    #             temperature=0.5,
    #             max_tokens=50,
    #             top_p=1,
    #             frequency_penalty=0.3,
    #             presence_penalty=0
    #         )
    #         meta_title = response.choices[0].message['content'].strip()
    #         return meta_title
    #     except ValueError as ve:
    #         if "tokens" in str(ve):
    #             print(f"Context length error for product {product_title}: {ve}. Skipping...")
    #             return None
    #         else:
    #             raise ve
    # def generate_skin_type(self, product_title, product_description, product_attributes):
    #     message_content = f"title: '{product_title}' description : '{product_description}' attributes: '{product_attributes}' "

    #     messages = [
    #         {"role": "system", "content": "Let's think step by step. You are analyzing product {title} (string), {description} (string)and {attributes}(json) on german to find out if this product is good for this 6 types of skin : sensitive, dry, normal, mix, fett, old or all types of skin. Keep in mind to check context to make right decision\nGive a list without any comments back.\n---\nEXPECTED OUTPUT:\n'sensitive, fett,mix'\n\nOR\n'mixed, fett,'\n\nOR\n 'sensitive, fett,mix'\n\nOR\n'all'\n---\nAfter you have the list, make sure there are only 6 skin types mentioned in the task on english divided by comma and enclosed in double quotes\n"},
    #         {"role": "user", "content": message_content}
    #     ]
    #     try:
    #         response = openai.ChatCompletion.create(
    #             model="gpt-4",
    #             messages=messages,
    #             temperature=0.75,
    #             max_tokens=256,
    #             top_p=1,
    #             frequency_penalty=0,
    #             presence_penalty=0
    #         )
    #         skin_type = response.choices[0].message['content'].strip()
    #         return skin_type
    #     except ValueError as ve:
    #         if "tokens" in str(ve):
    #             print(f"Context length error for product's skin_type {product_title}: {ve}. Skipping...\n\n")
    #             return None
    #         else:
    #             raise ve