import streamlit as st
import pandas as pd
import requests
from shared_functions import get_auth
import os
from dotenv import load_dotenv
from gpt_functions import ChatGPT
from env_utilities import get_chat_gpt_api_key,get_backend_username,get_rapid_api_key,get_testsystem_api,get_testsystem_url,get_localsystem_api,get_localsystem_url
load_dotenv()
# Access the environment variables
chat_gpt_api = get_chat_gpt_api_key()
backend_username = get_backend_username()
rapid_api = get_rapid_api_key()
testsystem_api = get_testsystem_api()
testsystem_url = get_testsystem_url()
localsystem_api = get_localsystem_api()
localsystem_url = get_localsystem_url()
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