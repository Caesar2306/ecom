import streamlit as st
import pandas as pd 
import ast

def show_articles_information_fetched(df):
    for index, row in df.iterrows():
        images = row['product_photos']
        if images is not None: 
            with st.expander(row['articleordernumber'], expanded=index<1):
                cols = st.columns([1,2]) 
                for i in range(0, len(images), 2):
                    with cols[0].container():
                        image_cols = st.columns(2)
                        image_cols[0].image(images[i], use_column_width="auto")
                        if i+1 < len(images): 
                            image_cols[1].image(images[i+1], use_column_width="auto")
                cols[1].markdown(f"**Artikelname:** {row['Artikelname']}" if 'Artikelname' in df.columns else "")
                cols[1].markdown(f"**EAN:** {row['EAN']}" if 'EAN' in df.columns else "")
                cols[1].markdown(f"**Meta titel:** {row['Metatitel']}" if 'Metatitel' in df.columns else "")
                cols[1].markdown(f"**Produktbeschreibung:** {row['Beschreibung']}" if 'Beschreibung' in df.columns else "")
                cols[1].markdown(f"**Anwendung:** {row['Anwendung']}" if 'Anwendung' in df.columns else "")
                cols[1].markdown(f"**Inhaltsstoffe:** {row['inci']}" if 'inci' in df.columns else "")
                cols[1].markdown(f"**product_description:** {row['product_description']}" if 'product_description' in df.columns else "")
                cols[1].markdown(f"**product_attributes:** {row['product_attributes']}" if 'product_attributes' in df.columns else "")
def show_articles_information_csv(df):
   for index, row in df.iterrows():
        images = row.get('product_photos', None)
        if images:

            images = ast.literal_eval(images)
        else:
            images = []

        with st.expander(row['articleordernumber'] if 'articleordernumber' in df.columns else "Unknown", expanded=index<1):
            cols = st.columns([1,2]) 

            for i in range(0, len(images), 2):
                with cols[0].container():
                    image_cols = st.columns(2)
                    image_cols[0].image(images[i], use_column_width="auto")
                    if i+1 < len(images): 
                        image_cols[1].image(images[i+1], use_column_width="auto")
                cols[1].markdown(f"**Artikelname:** {row['Artikelname']}" if 'Artikelname' in df.columns else "")
                cols[1].markdown(f"**EAN:** {row['EAN']}" if 'EAN' in df.columns else "")
                cols[1].markdown(f"**Meta titel:** {row['Metatitel']}" if 'Metatitel' in df.columns else "")
                cols[1].markdown(f"**Produktbeschreibung:** {row['Beschreibung']}" if 'Beschreibung' in df.columns else "")
                cols[1].markdown(f"**Anwendung:** {row['Anwendung']}" if 'Anwendung' in df.columns else "")
                cols[1].markdown(f"**Inhaltsstoffe:** {row['inci']}" if 'inci' in df.columns else "")
                cols[1].markdown(f"**product_description:** {row['product_description']}" if 'product_description' in df.columns else "")
                cols[1].markdown(f"**product_attributes:** {row['product_attributes']}" if 'product_attributes' in df.columns else "")
