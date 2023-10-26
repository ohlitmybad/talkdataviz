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

OPENAI_API_KEY = "QOxvASrYaXeRFFHgajIdT3BlbkFJkQ37OFVOZVOc8t07WJI5"

def get_text():
    input_text = st.text_area('', value="", height=1, placeholder='Enter query here ...')
    return input_text
    
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
    st.title("DataMB Chat ⚽📊")
    setOpenAIKey()
    agent, selected_df, selected_df_names = save_uploaded_file()

    # User login
    username = st.text_input('', placeholder='Username')
    
    st.header("")
    if st.button('Load visuals'):
        current_dir = os.getcwd()
        if platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", current_dir])
        elif platform.system() == "Windows":
            subprocess.Popen(["explorer", current_dir])
        else:
            print("Directory opened:", current_dir)
    imgs_png = glob.glob('*.png')
    imgs_jpg = glob.glob('*.jpg')
    imgs_jpeeg = glob.glob('*.jpeg')
    imgs_ = imgs_png + imgs_jpg + imgs_jpeeg
    if len(imgs_) > 0:
        img = image_select("", imgs_, captions=imgs_, return_value='index')
        st.write(img)    
    


    query_counts = load_query_counts()

    if user_exists(username):
        if not is_query_limit_reached(username, query_counts):

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


        else:
            st.error('Daily query limit (25) reached for this user.')
    else:
        st.error('User not found. Please check your username.')

if __name__ == "__main__":
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    main()
