
import streamlit as st
import pandas as pd
import requests
from shared_functions import get_auth
from rapidapi import extend_dataframe 
def add_product(data):
        response = requests.post(f"{st.session_state.shopware_url}articles/", auth=get_auth(), json=data)
        if response.status_code == 200 or response.status_code == 201:
            return True, ''
        else:
            return False, response.text  # Return the API error message
        
def import_products():
    st.title("Import Products")

    nrows = st.number_input("Enter the number of rows to read", min_value=1, value=5)  # Default value is 5
    # Allow users to upload a CSV file
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    # Check if a file has been uploaded. If not, use the default file
    if uploaded_file is not None:
        df_files = pd.read_csv(uploaded_file, delimiter=';', encoding='utf-8', nrows=nrows)
    else:
        default_file_path = "/Users/euphorika/Desktop/ecom/inputs/compagnie_de_provence_extended.csv"
        df_files = pd.read_csv(default_file_path, delimiter=';', encoding='utf-8', nrows=nrows)

    if st.button('Extend dataframe using Real-time-product-search?'):
        df_files = extend_dataframe(df_files)
    st.dataframe(df_files.head(nrows))


    if st.button('Add Products from CSV'):
        success_count = 0
        failed_rows = []
        error_messages = []
        
        for idx, row in df_files.iterrows():
            #strip product photos, get everyone back, remove indexes.
            links = [link.strip(" '") for link in row['product_photos'][1:-1].split(",")]
            images = []
            for index, link in enumerate(links):
                image_dict = {
                    "link": link,
                    "description": f"{row['mainDetailNumber']}_{index+1}"
                }
                if index == 0:
                    image_dict["main"] = 1
                images.append(image_dict)

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
                'images': images, 
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
