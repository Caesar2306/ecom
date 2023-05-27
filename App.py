import streamlit as st
import pandas as pd
from rapidapi import extend_dataframe
import csv
import ast


def read_input_data(input_csv_path):
    data = pd.read_csv(input_csv_path, sep=';', skip_blank_lines=False, quoting=csv.QUOTE_ALL, skipinitialspace=True)
    data = data.replace(r'^\s*$', pd.NA, regex=True)
    data['EAN'] = data['EAN'].apply(lambda x: str(int(x)) if pd.notnull(x) and str(x).isnumeric() else pd.NA)
    return data


st.set_page_config(
   page_title="Product Extender",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded",
)
st.title('Product Extender')

# Initialize session state for uploaded_file and extended_df
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'extended_df' not in st.session_state:
    st.session_state.extended_df = None

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=';')
    st.session_state.uploaded_file = df
    st.dataframe(df)
else:
    st.write('Upload file')

if st.button('Extend file'):
    with st.spinner('Wait for it...'):
        if st.session_state.uploaded_file is not None:
            st.session_state.extended_df = extend_dataframe(st.session_state.uploaded_file)  
            st.dataframe(st.session_state.extended_df[["EAN","artikelordernummer","Artikelname","product_description", "product_photos", "product_attributes"]])
            st.success('Done!')
    
    if st.session_state.extended_df is not None:
        for index, row in st.session_state.extended_df.iterrows():
            images = row['product_photos']
            if images is not None:  # Add a check for None values
                # Create columns for each image
                cols = st.columns(len(images) + 1)
                cols[0].write(row['Artikelname'])
                for i, link in enumerate(images):
                    # Display image in each column
                    cols[i+1].image(link, width=200)

        st.download_button('Download file', st.session_state.extended_df.to_csv(index=False), file_name='output.csv')
else:
    st.write('File is not extended')

inputdf = pd.read_csv('inputs/output.csv', sep=',', skipinitialspace=True)
st.dataframe(inputdf)

for index, row in inputdf.iterrows():
    images = ast.literal_eval(row['product_photos'])
    if images is not None:  # Add a check for None values
        # Create columns for product visualization
        cols = st.columns([1,2])  # Adjust the width of the columns
        # Create a new column for each image and display it
        for i in range(0, len(images), 2):  # Loop through images two at a time
            with cols[0].container():
                image_cols = st.columns(2)  # Create two columns for images
                image_cols[0].image(images[i], width=200)
                if i+1 < len(images):  # Check if there is a second image to display
                    image_cols[1].image(images[i+1], width=200)
        # Display product details in the second column
        cols[1].markdown(f"**Artikelname:** {row['Artikelname']}")
        cols[1].markdown(f"**EAN:** {row['EAN']}")
        cols[1].markdown(f"**Meta titel:** {row['Meta titel']}")
        cols[1].markdown(f"**Produktbeschreibung:** {row['Produktbeschreibung']}")
        cols[1].markdown(f"**Anwendung:** {row['Anwendung']}")
        cols[1].markdown(f"**Inhaltsstoffe:** {row['Inhaltsstoffe']}")
        cols[1].markdown(f"**product_description:** {row['product_description']}")
        cols[1].markdown(f"**product_attributes:** {row['product_attributes']}")
    st.markdown("---")  # Add a visual division between articles
