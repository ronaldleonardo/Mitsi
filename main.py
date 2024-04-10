import io
from markdown_pdf import Section
from markdown_pdf import MarkdownPdf
from dotenv import load_dotenv
import os
import streamlit as st
from openai import OpenAI
# import PyPDF2
import pypdf
from pypdf import PdfReader
import pandas as pd
import time
import streamlit as st
from st_keyup import st_keyup

load_dotenv()

# Page config
PAGE_CONFIG = {"page_title": "Mitsi - Make It Simple",
               "page_icon": ":hatching_chick:"}
st.set_page_config(**PAGE_CONFIG)

# Hide streamlit style
hide_st_style = """
                <style>
                #MainMenu {visibility:hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)


# # OpenAI API
API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=API_KEY)

# # TogetherAI API
# API_KEY = os.environ['TOGETHER_API_KEY']
# BASE_URL = os.environ['TOGETHER_BASE_URL']
# client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# # Anyscale API
# API_KEY = os.environ['ANYSCALE_API_KEY']
# BASE_URL = os.environ['ANYSCALE_BASE_URL']
# client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def chat_gpt(prompt):
    response = client.chat.completions.create(
        model=st.session_state['openai_model'],
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4096,
        top_p=0.8,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content.strip()


def chat_gpt2(prompt):
    response2 = client.chat.completions.create(
        model=st.session_state['openai_model'],
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4096,
        top_p=0.8,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response2.choices[0].message.content.strip()


def main_process():
    with st.spinner('Please wait...'):
        st.session_state['generated_exist'] = False
        #### Reading entire PDF files ####
        # creating a pdf reader object
        pdfReader = PdfReader(st.session_state['uploaded_file'])
        text = []

        # [OLD]Fail when pdf has any kind of encryption
        # pdfReader = PyPDF2.PdfReader(st.session_state['uploaded_file'])

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
            if i == 0:
                prompt = f"""
                    Extract a single TITLE of research paper from the text and use that as the title of summary.
                    Translate the title to fit into {st.session_state['language_pref']} language (ignore if it's already in the same language).
                    Turn the Title into Heading Markdown
                    Your task is to extract relevant information from a text on the page of a research paper and rephrase it into {st.session_state['language_pref']} {st.session_state['understanding_level']}. This information will be used to create a research paper summary.
                    Extract relevant information from the following text, which is delimited with triple backticks.\
                    Do not write Research Paper Summary or something along the line.
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
            if i != 0:
                prompt = f"""
                    This is {i+1}/{len(text)} page of research paper. 
                    Your task is to extract relevant information from a text on the page of a research paper and rephrase it into {st.session_state['language_pref']} {st.session_state['understanding_level']}. This information will be used to create a research paper summary.
                    Extract relevant information from the following text, which is delimited with triple backticks.\
                    Do not write Research Paper Summary or something along the line.
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

        #### Generating Simplified Version ####
        st.session_state['simplified'] = ' '
        prompt_simplify = f"""
                You are a professional journalist that's very good at explaining science and medical stuff in simple way that everyone can read and enjoy like an article.
                Use {st.session_state['language_pref']}. {st.session_state['understanding_level']}.
                Turn this text below into an article that everyone can understand easily whilst keeping as much science details as possible.
                Use markup and Heading to help. Avoid making statements that may be untrue and not based on this text.
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
        # time.sleep(19)

        st.session_state['generated_exist'] = True


# Session state
if "openai_model" not in st.session_state:
    st.session_state['openai_model'] = 'gpt-3.5-turbo'
    # st.session_state['openai_model'] = "mistralai/Mixtral-8x7B-Instruct-v0.1" # If using other than GPT

if "password_verification" not in st.session_state:
    st.session_state['password_verification'] = False

if "uploaded_file" not in st.session_state:
    st.session_state['uploaded_file'] = None

if "difficulty_level" not in st.session_state:
    st.session_state['difficulty_level'] = "Default"

if "understanding_level" not in st.session_state:
    st.session_state['understanding_level'] = ''

if "language_pref" not in st.session_state:
    st.session_state['language_pref'] = "English"

if "summary" not in st.session_state:
    st.session_state['summary'] = ' '

if "simplified" not in st.session_state:
    st.session_state['simplified'] = ' '

if "generated_exist" not in st.session_state:
    st.session_state['generated_exist'] = False

if "processing" not in st.session_state:
    st.session_state['processing'] = False


# Main
st.title("Make It Simple :hatching_chick:")
st.write("Turn research paper into easy to read documents")

# Password Verification
if st.session_state['password_verification'] == False:
    password = st.text_input("Enter a password", type="password")
    if password == "keretakuda":
        st.session_state['password_verification'] = True
        st.rerun()
    elif password != '' and password != "keretakuda":
        st.warning("Wrong password")

    if st.button("Access"):
        if password == "keretakuda":
            st.session_state['password_verification'] = True
            st.rerun()
        else:
            st.warning("Wrong password")


if st.session_state['password_verification'] == True:
    # Reasearch Paper Uploader
    st.session_state['uploaded_file'] = st.file_uploader(
        "Upload a PDF file for analysis", type=['PDF'])

    # Column layout
    # col1, col2, col3 = st.columns(3)
    col1, col2 = st.columns([3, 1])
    with col1:
        # Language selection
        language = st.selectbox("Choose a language:",
                                ("English", "Indonesia", "Others"))
        if language == "English":
            st.session_state['language_pref'] = "English"
        if language == "Indonesia":
            st.session_state['language_pref'] = "Bahasa Indonesia"
        if language == "Others":
            language_other = st_keyup("Enter the language", key="0")
            st.session_state['language_pref'] = language_other
        st.write(f"You've selected: {st.session_state['language_pref']}")

    with col2:
        # Language difficulty
        st.session_state['difficulty_level'] = st.selectbox("Language difficulty: ",
                                                            ("Default", "Easier"))
        if st.session_state['difficulty_level'] == "Easier":
            st.session_state['understanding_level'] = "Please write it so that a 5 years old can understand"
        else:
            st.session_state['understanding_level'] = ""

    # Button disabled after Generate Summary
    with st.empty():
        if st.session_state['processing'] == False:
            if st.button("Generate :memo:"):
                if st.session_state['uploaded_file'] is not None:
                    st.session_state['processing'] = True
                    st.session_state['generated_exist'] = False
                    st.rerun()

                else:
                    st.warning("Please upload a Journal.")
                    st.session_state['generated_exist'] = False
                    st.session_state['processing'] = False
        elif st.session_state['processing'] == True:
            st.button("Processing :gear:", disabled=True)

    # Generating summary
    if st.session_state['processing'] == True:
        main_process()
        st.session_state['processing'] = False
        st.rerun()

    # Showing results if generated
    if st.session_state['generated_exist'] == True:
        # spacer
        st.markdown(f"#")
        # Showing results of the simplified version
        with st.expander("See the Simplified Version"):
            st.write(rf"""{st.session_state['simplified']}""")

        # # Download simplified md
        # st.download_button(
        #     label="Download Simplified MD",
        #     data=st.session_state['simplified'],
        #     file_name='simplified.md',
        #     mime='text/csv',
        # )

        # Download Simplified PDF
        simplified_pdf = MarkdownPdf(toc_level=2)
        simplified_pdf.add_section(
            Section(f"{st.session_state['simplified']}", toc=False))
        simplified_output_buffer = io.BytesIO()
        simplified_pdf.save(simplified_output_buffer)
        simplified_pdf_bytes = simplified_output_buffer.getvalue()

        st.download_button(
            label="Download Simplified PDF",
            data=simplified_pdf_bytes,
            file_name=f"mitsi_simplified_{st.session_state['uploaded_file'].name}.pdf",
            mime='application/pdf',
        )

        # Showing results of the summary
        with st.expander("See Detailed Summary"):
            st.write(rf"""{st.session_state['summary']}""")

        # # Download summary md
        # st.download_button(
        #     label="Download Summary MD",
        #     data=st.session_state['summary'],
        #     file_name='summary.md',
        #     mime='text/csv',
        # )

        # Download Summary PDF
        summary_pdf = MarkdownPdf(toc_level=2)
        summary_pdf.add_section(
            Section(f"{st.session_state['summary']}", toc=False))
        summary_output_buffer = io.BytesIO()
        summary_pdf.save(summary_output_buffer)
        summary_pdf_bytes = summary_output_buffer.getvalue()

        st.download_button(
            label="Download Summary PDF",
            data=summary_pdf_bytes,
            file_name=f"mitsi_summary_{st.session_state['uploaded_file'].name}.pdf",
            mime='application/pdf',
        )
