from dotenv import load_dotenv
import os
import streamlit as st
from openai import OpenAI
import PyPDF2
import pandas as pd
import time

load_dotenv()


def chat_gpt(prompt):
    response = client.chat.completions.create(
        model=st.session_state['openai_model'],
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def chat_gpt2(prompt):
    response2 = client.chat.completions.create(
        model=st.session_state['openai_model'],
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        max_tokens=4096,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response2.choices[0].message.content.strip()


# Session state
if "openai_model" not in st.session_state:
    st.session_state['openai_model'] = 'gpt-3.5-turbo'

if "summary" not in st.session_state:
    st.session_state['summary'] = ' '

if "simplified" not in st.session_state:
    st.session_state['simplified'] = ' '

if "generated_exist" not in st.session_state:
    st.session_state['generated_exist'] = False

# OpenAI API
API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=API_KEY)

# Main
st.title("Make It Simple")
st.write("Turn research paper into easy to read pdf")


# Reasearch Paper Uploader
uploaded_file = st.file_uploader(
    "Upload a PDF file for analysis", type=['PDF'])

# Generate Summary
if st.button("Generate"):
    if uploaded_file is not None:
        with st.spinner('Please wait...'):
            st.session_state['generated_exist'] = False
            #### Reading entire PDF files ####
            # creating a pdf reader object
            text = []
            pdfReader = PyPDF2.PdfReader(uploaded_file)
            st.session_state['summary'] = ' '
            # Storing the pages in a list
            for i in range(0, len(pdfReader.pages)):
                # creating a page object
                pageObj = pdfReader.pages[i].extract_text()
                pageObj = pageObj.replace('\t\r', '')
                pageObj = pageObj.replace('\xa0', '')
                # extracting text from page
                text.append(pageObj)

            #### Generating Summary ####
            for i in range(len(text)):
                prompt = f"""
                    i = {i}
                    if i = 0 then do the following:
                    Extract TITLE of research paper from the text and use that as the title of summary.
                    If there's no TITLE from the research, then make one that's appropriate.
                    Your task is to extract relevant information from a text on the page of a research paper. This information will be used to create a research paper summary.
                    Extract relevant information from the following text, which is delimited with triple backticks.\
                    Avoid writing 'Research Paper Summary' unless explicitly specified in the research paper.
                    Be sure to use Markdown to help organize the summary into heading, subheading, bullet points, etc.

                    if i != 0 then do the following:
                    Your task is to extract relevant information from a text on the page of a research paper. This information will be used to create a research paper summary.
                    Extract relevant information from the following text, which is delimited with triple backticks.\
                    Avoid writing 'Research Paper Summary' unless explicitly specified in the research paper.
                    Be sure to use Markdown to help organize the summary into heading, subheading, bullet points, etc.

                    Text: ```{text[i]}```
                    """
                try:
                    response = chat_gpt(prompt)
                except:
                    response = chat_gpt(prompt)
                # st.markdown(response)
                st.session_state['summary'] = st.session_state['summary'] + \
                    ' ' + response + '\n\n'
                # result.append(response)
                # You can query the model only 3 times in a minute for free, so we need to put some delay
                time.sleep(19)

            # # Showing results of the summary
            # with st.expander("See the Summary"):
            #     st.write(rf"""{st.session_state['summary']}""")

            #### Generating Simplified Version ####
            st.session_state['simplified'] = ' '
            prompt_simplify = f"""
                    You are a professional journalist that's very good at explaining science and medical stuff in simple way that everyone can read and enjoy like an article.
                    Turn this text below into an article that everyone can understand easily whilst keeping as much science details as possible.
                    Use markup and Heading to help. Avoid making statements that may be untrue and not based on this text.
                    Extract relevant information from the following text.
                    Be sure to preserve the important details.

                    Text: ```{st.session_state['summary']}```
                    """
            try:
                response2 = chat_gpt2(prompt_simplify)
            except:
                response2 = chat_gpt2(prompt_simplify)

            st.session_state['simplified'] = st.session_state['simplified'] + \
                ' ' + response2 + '\n\n'
            # result.append(response)
            # You can query the model only 3 times in a minute for free, so we need to put some delay
            time.sleep(19)

        st.success('Task Complete')
        st.session_state['generated_exist'] = True

    else:
        st.warning("Please upload a Journal.")
        st.session_state['generated_exist'] = False

if st.session_state['generated_exist'] == True:

    # Showing results of the summary
    with st.expander("See the Summary"):
        st.write(rf"""{st.session_state['summary']}""")

    # Download summary txt
    st.download_button(
        label="Download Summary TXT",
        data=st.session_state['summary'],
        file_name='summary.txt',
        mime='text/csv',
    )
    # Showing results of the simplified version
    with st.expander("See the Simplified Version"):
        st.write(rf"""{st.session_state['simplified']}""")

    # Download simplified txt
    st.download_button(
        label="Download Simplified TXT",
        data=st.session_state['simplified'],
        file_name='simplified.txt',
        mime='text/csv',
    )
