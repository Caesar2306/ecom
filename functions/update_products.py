

import streamlit as st
from gpt_functions import ChatGPT
import requests
from shared_functions import get_auth
from functions.get_products import get_articles_df_save_to_cache
from env_utilities import get_chat_gpt_api_key
def get_article_by_id(article_id):
        response = requests.get(f"{st.session_state.shopware_url}articles/{article_id}", auth=get_auth())
        if response.status_code == 200:
            return response.json()["data"]
        else:
            return None
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
def update_products():
    chat_gpt_api = get_chat_gpt_api_key()
    # Initialize ChatGPT
    chat_gpt = ChatGPT(chat_gpt_api)


    st.subheader("Update Products")

    get_articles_df_save_to_cache()

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
        elif 'selected_columns' in st.session_state and not st.session_state.selected_columns:
            st.write("Please select at least one column.")

    if 'selected_articles' in st.session_state and st.session_state.selected_articles:

        # Dropdown for selecting the column to update
        column_to_update = st.selectbox("Select Column to Update", options=st.session_state.columns)
        chat_input = st.columns([1,2])
        with chat_input[0].container():
            user_input = st.text_area('User Input')
        with chat_input[1].container():
            system_input = st.text_area('System Input')

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
    if article_id:
        article = get_article_by_id(article_id)
        if article is not None:
            desired_fields = {key: article[key] for key in ["id", "name", "description", "mainDetail"]}
            st.json(desired_fields)
        else:
            st.warning(f"Failed to retrieve article with ID {article_id}.")

    if article:
        if 'mainDetail' in article and 'prices' in article['mainDetail'] and article['mainDetail']['prices']:
            current_price = article['mainDetail']['prices'][0]['price']
            st.write(f"Current price: {current_price}")
            new_price = st.number_input("Enter the new price:", min_value=0.0, value=float(current_price))
            
            if st.button("Update price"):
                updated_article = update_article_price(article_id, new_price)
                if updated_article is not None:
                    st.success("Price updated successfully!")
                else:
                    st.error("Failed to update price.")
    else:
        st.warning("Failed to retrieve the article.")