import streamlit as st

# Title of App
st.title("Web Development Lab03")

# Assignment Data 
# TODO: Fill out your team number, section, and team members

st.header("CS 1301")
st.subheader("Team 68, Web Development - Section A")
st.subheader("David Hill, Elle Garman")


# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
#       1. **Page Name**: Description
#       2. **Page Name**: Description
#       3. **Page Name**: Description
#       4. **Page Name**: Description

st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1. Home Page: Introduces the purpose of the app and provides navigation to all other pages.
2. Data Explorer: Fetches and analyzes real-time data from a public web API, displaying it with interactive charts.
3. LLM Insights: Uses a pre-trained large language model to interpret and summarize the API data with natural language.
4. Gemini Chatbot: Integrates Google Gemini to create a chatbot that specializes in answering questions based on the API's domain
""")
