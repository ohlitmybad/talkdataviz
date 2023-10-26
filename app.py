import os
import streamlit as st
from functions import *
import platform
import openai
from streamlit_chat import message
from streamlit_image_select import image_select
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import datetime

# Define the path to the users.txt file
USERS_FILE = 'users.txt'

# Define a file to store user query counts
QUERY_COUNT_FILE = 'query_counts.txt'

DAILY_QUERY_LIMIT = 2

def setOpenAIKey():
    os.environ['OPENAI_API_KEY'] = "sk-" + OPENAI_API_KEY

def user_exists(username):
    with open(USERS_FILE, 'r') as users_file:
        for line in users_file:
            user, _ = line.strip().split(':')
            if user == username:
                return True
    return False

def load_query_counts():
    if os.path.exists(QUERY_COUNT_FILE):
        with open(QUERY_COUNT_FILE, 'r') as count_file:
            query_counts = {}
            for line in count_file:
                user, date, count = line.strip().split(':')
                if user not in query_counts:
                    query_counts[user] = {}
                query_counts[user][date] = int(count)
            return query_counts
    return {}

def save_query_counts(query_counts):
    with open(QUERY_COUNT_FILE, 'w') as count_file:
        for user, data in query_counts.items():
            for date, count in data.items():
                count_file.write(f"{user}:{date}:{count}\n")

def is_query_limit_reached(username, query_counts, limit=DAILY_QUERY_LIMIT):
    today = datetime.date.today().isoformat()
    user_data = query_counts.get(username, {})
    
    if today in user_data:
        return user_data[today] >= limit
    return False

def main():
    st.title("DataMB Chat ⚽")
    setOpenAIKey()
    agent, selected_df, selected_df_names = save_uploaded_file()

    st.header("User Login and Query Counting")

    # User login
    username = st.text_input('Username:')

    query_counts = load_query_counts()

    if user_exists(username):
        if not is_query_limit_reached(username, query_counts):
            st.header('Chat with the AI')

            user_input = get_text()

            if st.button('Query'):
                response, thought, action, action_input, observation = run_query(agent, user_input)
                st.session_state.past.append(user_input)
                st.session_state.generated.append(response)

                # Display the generated response messages
                for i in range(len(st.session_state['generated']) - 1, -1, -1):
                    message(st.session_state["generated"][i], key=str(i))
                    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

                # Increment the query count
                user_data = query_counts.get(username, {})
                today = datetime.date.today().isoformat()
                user_data[today] = user_data.get(today, 0) + 1
                query_counts[username] = user_data
                save_query_counts(query_counts)

            st.header("Query Limit Information")
            st.write(f"User: {username}")
            st.write(f"Queries today: {user_data.get(today, 0)}")

        else:
            st.error('Query limit reached for today. You have exceeded the daily limit.')
    else:
        st.error('User not found. Please check your username.')

if __name__ == "__main__":
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    main()
