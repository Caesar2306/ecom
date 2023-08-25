import streamlit as st
from functions.gpt_functions import ChatGPT
from functions.env_utilities import get_chat_gpt_api_key

chat_gpt_api = get_chat_gpt_api_key()

# Initialize ChatGPT
def chat_GPT():
    chat_gpt = ChatGPT(chat_gpt_api)
    st.subheader("Chat")

    with st.container():
        cols = st.columns([1,2])
        with cols[0].container():
            inputtxt = st.text_area('User Input')
        with cols[1].container():
            systeminputtxt = st.text_area('System Input')
        if st.button('Ask chat GPT-4.0'):
            with st.spinner('Wait for it...'):
                st.write(chat_gpt.make_response(systeminputtxt, inputtxt))