import streamlit as st
import pandas as pd
from rapidapi import extend_dataframe

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
