import os
import streamlit as st
import platform
import subprocess
import openai
import numpy as np
import matplotlib.pyplot as plt
import glob

from functions import *
from streamlit_chat import message
from streamlit_image_select import image_select

OPENAI_API_KEY = "QOxvASrYaXeRFFHgajIdT3BlbkFJkQ37OFVOZVOc8t07WJI5"

def setOpenAIKey():
    os.environ['OPENAI_API_KEY'] = "sk-" + OPENAI_API_KEY

def get_text(n):
    input_text = st.text_input('', key="input{}".format(n), placeholder='Enter query here ...')
    return input_text

def main():
    st.title("DataMB Chat ⚽📊")
    setOpenAIKey()
    agent, selected_df, selected_df_names = save_uploaded_file()
    
    st.header("")
    if st.button('Refresh visuals'):
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

    st.header("")
    x = 0
    user_input = get_text(x)

    query_button = st.button('Query', key="query_button")

    if query_button:
        x += 1
        print(user_input, len(user_input))
        response, thought, action, action_input, observation = run_query(agent, user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)

        # Display the generated response messages
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

if __name__ == "__main__":
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'tabs' not in st.session_state:
        st.session_state['tabs'] = []

    main()
