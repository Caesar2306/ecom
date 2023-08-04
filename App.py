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
url = "https://schoenheitsberatung.de/euphorika-dev-2021/api/articles"
api_key = "NtFc6aIB9kyktckuRqb4mTkkcC8iVvxNSHLSaf4F"
backend_username = "vadim"

# Available MySQL expressions
mysql_expressions = ["LIKE", "=", ">=", "<=", ">", "<"]

# Authentication function
def get_auth():
    return HTTPBasicAuth(backend_username, api_key)

# Get articles function with filter, sort, limit, and offset
def get_all_articles(selected_columns, filters, sorts, limit, offset):
    params = {
        "filter": filters,
        "sort": sorts
    }
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
# Available columns
columns = [
    "id", "mainDetailId", "supplierId", "taxId", "priceGroupId", "filterGroupId",
    "configuratorSetId", "name", "description", "descriptionLong", "added", "active",
    "pseudoSales", "highlight", "keywords", "metaTitle", "changed", "priceGroupActive",
    "lastStock", "crossBundleLook", "notification", "template", "mode", "availableFrom",
    "availableTo", "mainDetail"
]
default_columns = ["id", "mainDetailId", "supplierId", "name", "description", "active"]
# Multiselect box for columns
selected_columns = st.multiselect("Select Columns", options=columns, default=default_columns)

# Filter options
filters = []
st.write("Filters:")
for i in range(3):  # Allowing up to 3 filter conditions
    property_filter = st.selectbox(f"Filter Property {i+1}", options=columns, index=0, key=f"property{i}")
    expression_filter = st.selectbox(f"Expression {i+1}", options=mysql_expressions, index=0, key=f"expression{i}")
    value_filter = st.text_input(f"Value {i+1}", key=f"value{i}")
    operator_filter = st.selectbox(f"Operator {i+1} (AND: AND, OR: OR)", options=['AND', 'OR'], index=0, key=f"operator{i}")
    if property_filter and value_filter:
        filters.append({
            "property": property_filter,
            "expression": expression_filter,
            "value": value_filter,
            "operator": operator_filter
        })

# Sort options
sorts = []
st.write("Sorts:")
for i in range(3):  # Allowing up to 3 sort conditions
    property_sort = st.selectbox(f"Sort Property {i+1}", options=columns, index=0, key=f"sort_property{i}")
    direction_sort = st.selectbox(f"Direction {i+1}", options=["ASC", "DESC"], index=0, key=f"direction{i}")
    if property_sort:
        sorts.append({
            "property": property_sort,
            "direction": direction_sort
        })

# Limit and Offset options
limit = st.number_input("Limit:", min_value=1, max_value=1000, value=1000, step=1)
offset = st.number_input("Offset:", min_value=0, max_value=999, value=0, step=1)

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