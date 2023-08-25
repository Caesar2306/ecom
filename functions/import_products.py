
import streamlit as st
import pandas as pd
import requests
from functions.shared_functions import get_auth,sanitize_data
from functions.rapidapi import extend_dataframe 
from functions.article_info import show_articles_information_fetched,show_articles_information_csv

def process_row_for_import(row):
    # the product_data for each row
    if 'manufacturer' in row:
        supplierId = get_supplier_id(row['manufacturer'])

        category = getCategories(row['manufacturer'])

    # Strip product photos, get every photo back, remove indexes.
    if isinstance(row['product_photos'], str):
        links = [link.strip(" '") for link in row['product_photos'][1:-1].split(",")]
    else:
        links = row['product_photos']
    images = []
    for index, link in enumerate(links):
        image_dict = {
            "link": link,
            "description": f"{row['articleordernumber']}_{index+1}"
        }
        if index == 0:
            image_dict["main"] = 1
        images.append(image_dict)

    product_data = {
        'name': row['Artikelname'],
        'taxId': 1,
        'supplierId': supplierId,
        'description_long': row['Beschreibung'],
        'active': True,
        'mainDetail': {
            'number': f"{row['articleordernumber']}_1",
            'active': True,
            'inStock': (row['purchaseunitdetail'] if 'purchaseunitdetail' in row else 1) * (row['Menge'] if 'Menge' in row else 1),
            'purchasePrice': float(row['Purchaseprice'].replace(',', '.').replace('€', '').strip()),
            'EAN': row['EAN'],
            'prices': [
                {
                    "customerGroupKey": "EK",
                    "price": float(row['UVP'].replace(',', '.').replace('€', '').strip()),
                    "pseudoprice": float(row['UVP'].replace(',', '.').replace('€', '').strip()),
                }
            ],
        },
        'images': images,
        'seoCategories': [
            {
                "shopId": 1,
                "categoryId": category
            }
        ],
        'categories': [
            {
                "id": category
            }
        ]
    }
    return product_data

def import_given_df(df):
    success_count = 0
    failed_rows = []
    error_messages = []

    for idx, row in df.iterrows():
        product_data = sanitize_data(process_row_for_import(row))
        success, message = add_product(product_data)
        if success:
            success_count += 1
        else:
            failed_rows.append(idx)
            error_messages.append(message)

    st.write(f"Successfully added {success_count} products.")
    if failed_rows:
        st.write(f"Failed to add products at rows: {failed_rows}")
        st.write(f"Error messages: {error_messages}")

def import_products():
    st.title("Import Products")

    nrows = st.number_input("Enter the number of rows to read", min_value=1, value=5)

    #  upload a CSV file
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    # Check if a file has been uploaded. If not, use the sample file
    if uploaded_file:
        df = pd.read_csv(uploaded_file, delimiter=';', encoding='utf-8', nrows=nrows)
    else:
        default_file_path = "/Users/euphorika/Desktop/ecom/inputs/compagnie_de_provence_extended.csv"
        df = pd.read_csv(default_file_path, delimiter=';', encoding='utf-8', nrows=nrows)

    # If the button to extend the dataframe is pressed
    if st.button('Extend dataframe using Real-time-product-search?'):
        df = extend_dataframe(df)
        st.session_state.df_files = df  # Store in session state
        st.write(df)
        show_articles_information_fetched(df)
    elif "df_files" in st.session_state:  # If the dataframe is already in session state, use
        df = st.session_state.df_files
        st.write(df)
    else:
        st.write('used sample from local data')
        st.write(df)
        show_articles_information_csv(df)

    if st.button('Import Products'):
        import_given_df(df)

def add_product(data):
    response = requests.post(f"{st.session_state.shopware_url}articles/", auth=get_auth(), json=data)
    if response.status_code == 200 or response.status_code == 201:
        return True, ''
    else:
        return False, response.text  # Return the API error message
def get_supplier_id(supplier_name): 
    response = requests.get(f"{st.session_state.shopware_url}manufacturers/", auth=get_auth())
    
    if response.status_code != 200:
        st.write(f"Failed to fetch manufacturers. Status code: {response.status_code}")
        return None

    response_data = response.json()
    manufacturers = response_data.get("data", [])

    for manufacturer in manufacturers:
        if manufacturer['name'].lower() == supplier_name.lower():
            return manufacturer['id']

    return None
def getCategories(category_name):
    # parent id = 100 is the case in the local system where apear all suppliers
    response = requests.get(f"{st.session_state.shopware_url}categories/?parentId=100", auth=get_auth())
    if response.status_code != 200:
        st.warning(f"Failed to receive to fetch categories. Status code {response.status_code}")
        return None
    response_data = response.json()
    categories = response_data.get("data", [])

    for category in categories:
        if category['name'].lower() == category_name.lower():
            return category['id']
        