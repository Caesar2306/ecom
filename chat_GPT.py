import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
from gpt_functions import ChatGPT
load_dotenv()
# Access the environment variables
chat_gpt_api = os.getenv('CHATGPT_API_KEY')
backend_username = os.getenv('BACKEND_USERNAME')
rapid_api = os.getenv('RAPID_API_KEY')
testsystem_api = os.getenv('TESTSYSTEM_API')
testsystem_url = os.getenv('TESTSYSTEM_URL')
localsystem_api = os.getenv('LOCALSYSTEM_API')
localsystem_url = os.getenv('LOCALSYSTEM_URL')
# Initialize ChatGPT
chat_gpt = ChatGPT(chat_gpt_api)

def chat_page():
    st.title("chat")

    with st.container():
        cols = st.columns([1,2])
        with cols[0].container():
            inputtxt = st.text_area('User Input')
        with cols[1].container():
            systeminputtxt = st.text_area('System Input')
        if st.button('Ask chat GPT-4.0'):
            with st.spinner('Wait for it...'):
                st.write(chat_gpt.make_response(systeminputtxt, inputtxt))