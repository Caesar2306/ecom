import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
from gpt_functions import ChatGPT
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

def update_products_page():
    st.title("Update Products")


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
        else:
            return None

    # Multiselect box for columns
    selected_columns = st.multiselect("Select Columns", options=columns, default=default_columns, key="get_products_column")

    # Filter options
    filters = []
    use_filter = st.checkbox("Use Filter", key="Use filter get_product")
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
    use_sort = st.checkbox("Use Sort",key="Use Sort get_product")
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
    use_limit_offset = st.checkbox("Use Limit/Offset",key="Use Limit get_product")
    limit = 30
    offset = None
    if use_limit_offset:
        limit = st.number_input("Limit:", min_value=1, max_value=10000, value=30, step=1)
        offset = st.number_input("Offset:", min_value=0, max_value=10000, value=0, step=1)
    # Buttno to trigger api request
    if 'df' not in st.session_state:
        st.session_state.df = None

    if st.button("Get Articles",key="Get articles get_articles") and selected_columns:
        articles = get_all_articles(selected_columns, filters, sorts, limit, offset)
        if articles:
            st.session_state.df = pd.DataFrame(articles)
        else:
            st.write("Failed to retrieve articles.")

    if 'df' in st.session_state and st.session_state.df is not None:
        st.write("Displaying articles:")
        st.dataframe(st.session_state.df)
        # Checkbox for selecting all products
        select_all = st.checkbox("Select All Articles for Update")
        if 'selected_articles' not in st.session_state:
            st.session_state.selected_articles = []

        if not select_all:
            #  mapping from names to IDs
            name_to_id_mapping = dict(zip(st.session_state.df["name"].tolist(), st.session_state.df["id"].tolist()))
            selected_article_names = st.multiselect(
                "Select Articles for Update", 
                options=st.session_state.df["name"].tolist(), 
                default=[name_to_id_mapping[id] for id in st.session_state.selected_articles if id in name_to_id_mapping]
            )            
            
            # get the corresponding IDs for the selected article names
            selected_articles = [name_to_id_mapping[name] for name in selected_article_names]
        else:
            selected_articles = st.session_state.df["id"].tolist()

        st.session_state.selected_articles = selected_articles
        st.write(f"Selected Articles: {st.session_state.selected_articles}")

        if st.button("Proceed to Update Selected Articles"):
            st.session_state.selected_articles = selected_articles
            st.write(f"Selected Articles: {selected_articles}")
    elif not selected_columns:
        st.write("Please select at least one column.")

    if 'selected_articles' in st.session_state and st.session_state.selected_articles:

        # Dropdown for selecting the column to update
        chat_input = st.columns([1,2])
        with chat_input[0].container():
            user_input = st.text_area('User Input')
        with chat_input[1].container():
            system_input = st.text_area('System Input')
        column_to_update = st.selectbox("Select Column to Update", options=columns)

        if st.button("Generate Content with ChatGPT"):
            article_info = st.session_state.df[st.session_state.df['id'].isin(st.session_state.selected_articles)]
            
            # Setup the progress bar
            total_articles = len(st.session_state.selected_articles)
            progress_text = "Updating articles. Please wait."
            progress_bar = st.progress(0)
            progress_text_element = st.empty()

            # Iterate over selected articles and get content for each
            for idx, (_, row) in enumerate(article_info.iterrows()):
                article_name = row['name']
                article_id = row['id']
                article_description = row['descriptionLong']

                # add information to prompt for additional customization
                modified_user_input = f"{user_input} for article {article_name} with description {article_description}"
                modified_system_input = f"{system_input}"
                response = chat_gpt.make_response(modified_system_input, modified_user_input)
                
                st.write(f"Generated Content for {article_name}:", response)

                # Construct the payload for update
                payload = {column_to_update: response}
                
                # update the article
                update_response = requests.put(f"{st.session_state.shopware_url}articles/{article_id}", auth=get_auth(), json=payload)
                
                # progress bar
                progress = (idx + 1) / total_articles
                progress_bar.progress(progress)
                progress_text_element.text(f"{progress_text} ({idx + 1}/{total_articles})")

                if update_response.status_code == 200:
                    st.success(f"Successfully updated article with ID {article_id}")
                else:
                    st.error(f"Failed to update article with ID {article_id}. Status Code: {update_response.status_code}")
                    
            progress_text_element.text("Update completed!")
    article = None
    article_id = st.text_input("Enter the article ID:", key="Article_id")
    def get_article_by_id(article_id):
        response = requests.get(f"{st.session_state.shopware_url}articles/{article_id}", auth=get_auth())
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
        response = requests.put(f"{st.session_state.shopware_url}articles/{article_id}", auth=get_auth(), json=update_data)
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