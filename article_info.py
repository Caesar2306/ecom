import streamlit as st
import csv

def show_articles_information(df):
    for index, row in df.iterrows():
        images = row['product_photos']
        if images is not None:  # Add a check for None values
            with st.expander(row['artikelordernummer'], expanded=index<3):  # Expand the first 3 products
                # Create columns for product visualization
                cols = st.columns([1,2])  # Adjust the width of the columns
                # Create a new column for each image and display it
                for i in range(0, len(images), 2):  # Loop through images two at a time
                    with cols[0].container():
                        image_cols = st.columns(2)  # Create two columns for images
                        image_cols[0].image(images[i], use_column_width="auto")
                        if i+1 < len(images):  # Check if there is a second image to display
                            image_cols[1].image(images[i+1], use_column_width="auto")
                # Display product details in the second column
                cols[1].markdown(f"**Artikelname:** {row['Artikelname']}")
                cols[1].markdown(f"**EAN:** {row['EAN']}")
                cols[1].markdown(f"**Meta titel:** {row['Meta titel']}")
                cols[1].markdown(f"**Produktbeschreibung:** {row['Produktbeschreibung']}")
                cols[1].markdown(f"**Anwendung:** {row['Anwendung']}")
                cols[1].markdown(f"**Inhaltsstoffe:** {row['Inhaltsstoffe']}")
                cols[1].markdown(f"**product_description:** {row['product_description']}")
                cols[1].markdown(f"**product_attributes:** {row['product_attributes']}")