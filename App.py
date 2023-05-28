import streamlit as st
import pandas as pd
from rapidapi import extend_dataframe
from article_info import show_articles_information
from gpt_functions import ChatGPT


chat_gpt = ChatGPT("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")

st.set_page_config(
   page_title="Product Extender",
   page_icon=":smile:",
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
    df = pd.read_csv('inputs/output.csv', sep=',')
    st.session_state.uploaded_file = df
    st.write('Uploaded file not found, preset used')

if st.button('Extend file'):
    with st.spinner('Wait for it...'):
        if  st.session_state.uploaded_file is not None:
            st.session_state.extended_df = extend_dataframe(st.session_state.uploaded_file)  
            st.dataframe(st.session_state.extended_df[["EAN","artikelordernummer","Artikelname","product_description", "product_photos", "product_attributes"]])
            st.success('Done!')
    
    if st.session_state.extended_df is not None:
        show_articles_information(st.session_state.extended_df)

        st.download_button('Download file', st.session_state.extended_df.to_csv(index=False), file_name='output.csv')
else:
    st.write('File is not extended')

# if st.session_state.extended_df is not None:
# else: st.write('you must download file')

# show_articles_information(inputdf)
cols = st.columns([1,2])
with cols[0].container():
    inputtxt = st.text_area('User Input')
with cols[1].container():
    systeminputtxt = st.text_area('System Input')
if st.button('Ask chat GPT-3.5'):
    with st.spinner('Wait for it...'):
        st.write(chat_gpt.make_response(systeminputtxt, inputtxt))

if st.session_state.uploaded_file is not None:
    options = st.multiselect('Which columns should be analyzed?', st.session_state.uploaded_file.columns)
for option in options:
    cols = st.columns([0.5,2,1])
    with cols[0].container():
        st.write(option);
    with cols[1].container():
        inputtxt = st.text_area('User Input for ' + option)
    with cols[2].container():
        systeminputtxt = st.text_area('System Input for ' + option)
    if st.button('Ask chat GPT-3.5'):
        with st.spinner('Wait for it...'):
            st.write(chat_gpt.make_response(systeminputtxt + " " + option, inputtxt))
    st.divider()
