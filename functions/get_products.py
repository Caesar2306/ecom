
import streamlit as st
import pandas as pd
import requests
from shared_functions import get_auth

def get_filters(columns, mysql_expressions,key):
    filters = []
    use_filter = st.checkbox("Use Filter", key=key)
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
    return filters
def get_limit_offset():
    use_limit_offset = st.checkbox("Use Limit/Offset",key="Use Limit get_product")
    limit = 30
    offset = None
    if use_limit_offset:
        limit = st.number_input("Limit:", min_value=1, max_value=10000, value=30, step=1)
        offset = st.number_input("Offset:", min_value=0, max_value=10000, value=0, step=1)
    return limit, offset
def get_sorts(columns):
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
    return sorts

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

        response = requests.get(f"{st.session_state.shopware_url}articles/{number}", auth=get_auth(), params=params)
        if response.status_code == 200:
            articles.append(response.json())
        else:
            st.warning(f"Failed to retrieve article with order number {number}. Status code: {response.status_code}")

    return articles
def get_articles_df_save_to_cache():
    mysql_expressions = ["LIKE", "=", ">=", "<=", ">", "<", "IN"]
    columns = [
        "id", "mainDetailId", "supplierId", "taxId", "priceGroupId", "filterGroupId",
        "configuratorSetId", "name", "description", "descriptionLong", "added", "active",
        "pseudoSales", "highlight", "keywords", "metaTitle", "changed", "priceGroupActive",
        "lastStock", "crossBundleLook", "notification", "template", "mode", "availableFrom",
        "availableTo", "mainDetail"
    ]
    default_columns = ["id", "supplierId", "name", "description", "active", "mainDetail", "descriptionLong"]


    # Multiselect box for columns
    selected_columns = st.multiselect("Select Columns", options=columns, default=default_columns, key="get_products_column")

    # Filter options
    filters = get_filters(columns, mysql_expressions,key="get_by_id")

    # Sort options
    sorts = get_sorts(columns)
    limit, offset = get_limit_offset()
    # Buttno to trigger api request

    if 'df' not in st.session_state:
        st.session_state.df = None

    if st.button("Get Articles",key="Get articles get_articles") and selected_columns:
        articles = get_all_articles(selected_columns, filters, sorts, limit, offset)
        if articles:
            st.session_state.df = pd.DataFrame(articles)
            st.session_state.selected_columns = selected_columns
            st.session_state.columns = columns
        else:
            st.write("Failed to retrieve articles.")
# Available columns
def get_products():
    st.title("Get Products")

    get_articles_df_save_to_cache()

    if 'df' in st.session_state and st.session_state.df is not None:
        st.write("Displaying articles:")
        st.dataframe(st.session_state.df)
    
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
    mysql_expressions = ["LIKE", "=", ">=", "<=", ">", "<", "IN"]
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
        filters = get_filters(available_fields, mysql_expressions,key="get_by_on")
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