import streamlit as st
import requests
from shared_functions import get_auth_local
from env_utilities import get_localsystem_url

st.subheader("Delete Products")
def delete_products():
    def delete_articles(product_ids_list, product_numbers_list):
        # Constructing the payload based on provided product IDs and numbers
        payload = []
        for product_id in product_ids_list:
            payload.append({"id": product_id})
        
        for product_number in product_numbers_list:
            payload.append({"mainDetail": {"number": product_number}})
        
        # Making the DELETE request to Shopware 5 API
        url = get_localsystem_url() + "articles/"
        response = requests.delete(url, auth=get_auth_local(), json=payload)
        
        if response.status_code == 200:
            st.success(f"Successfully deleted {len(payload)} articles!")
        else:
            st.error(f"Failed to delete articles! Error: {response.text}")

    # Input for product IDs
    product_ids = st.text_area("Enter Product IDs (comma-separated)", "")
    product_ids_list = [int(i.strip()) for i in product_ids.split(",") if i.strip()]

    # Input for product numbers
    product_numbers = st.text_area("Enter Product Numbers (comma-separated)", "")
    product_numbers_list = [num.strip() for num in product_numbers.split(",") if num.strip()]

    if st.button("Delete Specified Articles"):
        delete_articles(product_ids_list, product_numbers_list)
