import io
import os
import time
import json
import openai
import requests
import pandas as pd
import streamlit as st
from openai import OpenAI
from prompts import get_prompts

# API_KEYS
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()
suno_api_key = '72+hIHnhRYYVuu3v3CGc8P+QvZqSZJpk'

# Streamlit title
"# 👌 ✌️ ☝️"

# FUNCTIONS 
def ChatGPT(prompt): 
    response = client.chat.completions.create(
        model="gpt-4o",
        stream=False,
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                }
            ]
            }
        ],
            temperature=1,
            max_tokens=4096,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
    )
    return response.choices[0].message.content

def check_remaining_quota(api_key):
    url = "https://api.sunoaiapi.com/api/v1/gateway/limit"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['code'] == 0:
            return data['data']
        else:
            return {"error": data['msg']}
    else:
        return {"error": f"HTTP {response.status_code}"}

def generate_music(api_key, title, prompt, mv="chirp-v3-5", continue_at=None, continue_clip_id=None):
    url = "https://api.sunoaiapi.com/api/v1/gateway/generate/music"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "title": title,
        "tags": 'pop, upbeat',
        "prompt": prompt,
        "mv": mv
    }
    
    if continue_at is not None:
        data["continue_at"] = continue_at
    
    if continue_clip_id is not None:
        data["continue_clip_id"] = continue_clip_id

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        result = response.json()
        if result['code'] == 0:
            return result['data']
        else:
            return {"error": result['msg']}
    else:
        return {"error": f"HTTP {response.status_code}"}

def query_generated_results(api_key, song_ids):
    url = f"https://api.sunoaiapi.com/api/v1/gateway/query?ids={','.join(song_ids)}"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Print the entire response for debugging purposes
        print("Response JSON:", data)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if data.get('code') == 0:
                return data.get('data', {})
            else:
                return {"error": data.get('msg', 'Unknown error')}
        else:
            return {"error": "Unexpected response format"}
    else:
        return {"error": f"HTTP {response.status_code}"}

def image_generation(prompt_arg):
        response = client.images.generate(
        model="dall-e-3",
        prompt=prompt_arg,
        size="1024x1024",
        quality="standard",
        n=1,
        )
        image_url = response.data[0].url
        return image_url

# PAGE FUNCTIONS 

def Home():
    st.title("Home")
    idea = st.text_input("Enter your idea:")
    if idea:
        st.session_state['idea'] = idea
    if 'idea' in st.session_state:
        st.write("### Current Idea:")
        st.write(st.session_state['idea'])

def CompanyName():
    st.title("Company Name")
    if 'idea' in st.session_state:
        if 'cn_prompt' not in st.session_state:
            prompt = st.text_area("Prompt", "I'm starting a company. This is my idea " + st.session_state['idea'] + ". Please provide me with 3 different Company Names. Just provide me with the Company Names and nothing else.", key="oneliner")
            if st.button("Submit", type="primary"):
                st.session_state['cn_prompt'] = prompt
                st.session_state['cn_response'] = ChatGPT(prompt)
        else:
            cn_prompt = st.text_area("Prompt", st.session_state['cn_prompt'], key="oneliner")
            if st.button("Submit", type="primary"):
                st.session_state['cn_prompt'] = cn_prompt
                st.session_state['cn_response'] = ChatGPT(cn_prompt)
        if 'cn_response' in st.session_state:
            st.write(st.session_state['cn_response'])
    else:
        "Please enter an idea on the Input page."

def OneLiners():
    st.title("One Liners")
    if 'idea' in st.session_state:
        if 'ol_prompt' not in st.session_state:
            prompt = st.text_area("Prompt", "I'm starting a company. This is my idea " + st.session_state['idea'] + ". Please provide me with 3 different one-liners I can use in my seed deck. Just provide me with the one-liners and nothing else.", key="oneliner")
            if st.button("Submit", type="primary"):
                st.session_state['ol_prompt'] = prompt
                st.session_state['ol_response'] = ChatGPT(prompt)
        else:
            ol_prompt = st.text_area("Prompt", st.session_state['ol_prompt'], key="oneliner")
            if st.button("Submit", type="primary"):
                st.session_state['ol_prompt'] = ol_prompt
                st.session_state['ol_response'] = ChatGPT(ol_prompt)
        if 'ol_response' in st.session_state:
            st.write(st.session_state['ol_response'])
    else:
        "Please enter an idea on the Input page."

def Domains():
    st.title("Domains")
    if 'idea' in st.session_state:
        if 'domain_prompt' not in st.session_state:
            domain_prompt_default = st.text_area("Prompt", "I'm starting a company. This is my idea " + st.session_state['idea'] + ". Please provide me with 3 different domains I can use in my seed deck. Just provide the domain name, a reason why, and nothing else.", key="domain")
            if st.button("Submit", type="primary"):
                st.session_state['domain_prompt'] = domain_prompt_default
                st.session_state['domain_response'] = ChatGPT(domain_prompt_default)
        else:
            domain_prompt_edit = st.text_area("Prompt", st.session_state['domain_prompt'], key="domain")
            if st.button("Submit", type="primary"):
                st.session_state['domain_prompt'] = domain_prompt_edit
                st.session_state['domain_response'] = ChatGPT(domain_prompt_edit)

        if 'domain_response' in st.session_state:
            st.write(st.session_state['domain_response'])
    else:
        "Please enter an idea on the Input page."

def MarketSizing():
    st.title("Market Sizing")
    if 'idea' in st.session_state:
        if 'ms_prompt' not in st.session_state:
            ms_prompt_default = st.text_area("Prompt", "I'm starting a company. This is my idea " + st.session_state['idea'] + ". Please provide me with detailed yet concise bullet points detailing the market sizing. Use real numbers and figures. Just provide me with the market sizing and nothing else. Cap the response to < 10 bullets.")
            if st.button("Submit", type="primary"):
                st.session_state['ms_prompt'] = ms_prompt_default
                st.session_state['ms_response'] = ChatGPT(ms_prompt_default)
        else:
            ms_prompt_edit = st.text_area("Prompt", st.session_state['ms_prompt'], key="domain")
            if st.button("Submit", type="primary"):
                st.session_state['ms_prompt'] = ms_prompt_edit
                st.session_state['ms_response'] = ChatGPT(ms_prompt_edit)
        if 'ms_response' in st.session_state:
            st.write(st.session_state['ms_response'])
    else:
        "Please enter an idea on the Input page."

def Jingle():
    st.title("Jingle")
    if 'idea' in st.session_state:
        if 'jingle_prompt' not in st.session_state:
            st.session_state['jingle_prompt'] = "Create 1 stanza of song lyrics for a pop, marketing song about my business idea. It should be a short jingle. Here's the idea: " + st.session_state['idea'] + ". Just provide the lyrics, no extraneous or confirmation text. It should start with (Verse 1)."
            st.session_state['jingle_title_prompt'] = "Create a title for a poppy, marketing song for my business idea. Here's the idea: " + st.session_state['idea'] + ". Just provide the title, nothing else."
        
        jingle_prompt = st.text_area("Jingle Lyrics Prompt", st.session_state['jingle_prompt'])
        jingle_title_prompt = st.text_area("Jingle Title Prompt", st.session_state['jingle_title_prompt'])
        
        if st.button("Submit", type="primary"):
            st.session_state['jingle_prompt'] = jingle_prompt
            st.session_state['jingle_title_prompt'] = jingle_title_prompt
            st.session_state['jingle_title'] = ChatGPT(jingle_title_prompt)
            st.session_state['jingle_lyrics'] = ChatGPT(jingle_prompt)
            
            music_generation_info = generate_music(suno_api_key, st.session_state['jingle_title'], st.session_state['jingle_lyrics'])
            song_id = music_generation_info[0]["song_id"]
            song_id = [song_id]

            latest_iteration = st.empty()
            bar = st.progress(0)

            for i in range(100):
                latest_iteration.text(f'Making magic {i+1}')
                bar.progress(i + 1)
                time.sleep(.5)

            generated_results = query_generated_results(suno_api_key, song_id)
            st.session_state['jingle_audio'] = generated_results[0]["audio_url"]

            latest_iteration.empty()
            bar.empty()

        if 'jingle_audio' in st.session_state:
            st.audio(st.session_state['jingle_audio'])
            st.write(st.session_state['jingle_title'])
            st.write(st.session_state['jingle_lyrics'])
    else:
        st.write("Please enter an idea on the Input page.")

def Logos():
    st.title("Logos")
    if 'idea' in st.session_state:
        if 'logo_prompt' not in st.session_state:
            st.session_state['logo_prompt'] = "I'm starting a company. This is my idea " + st.session_state['idea'] + ". Generate a simple, black icon for it similar to the style of the iconic apple or nike logo."

        with st.form(key='logo_form'):
            logo_prompt = st.text_area("Prompt", st.session_state['logo_prompt'])
            submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            st.session_state['logo_prompt'] = logo_prompt  # Update the prompt in the session state
            st.session_state['logo_response'] = image_generation(st.session_state['logo_prompt'])  # Generate the image using the updated prompt
        
        if 'logo_response' in st.session_state:
            st.image(st.session_state['logo_response'])
    else:
        st.write("Please enter an idea on the Input page.")

# def Logos():
#     st.title("Logos")
#     if 'idea' in st.session_state:
#         if 'logo_prompt' not in st.session_state:
#             st.session_state['logo_prompt'] = "I'm starting a company. This is my idea " + st.session_state['idea'] + ". Generate a simple, black icon for it similar to the style of the iconic apple or nike logo."

#         logo_prompt = st.text_area("Prompt", st.session_state['logo_prompt'], key="logo")

#         if st.button("Submit", type="primary"):
#             st.session_state['logo_prompt'] = logo_prompt  # Update the prompt in the session state
#             st.session_state['logo_response'] = image_generation(st.session_state['logo_prompt'])  # Generate the image using the updated prompt
        
#         if 'logo_response' in st.session_state:
#             st.image(st.session_state['logo_response'])
#     else:
#         st.write("Please enter an idea on the Input page.")

# def Logos():
#     st.title("Logos")
#     if 'idea' in st.session_state:
#         if 'logo_prompt' not in st.session_state:
#             prompt = st.text_area("Prompt", "I'm starting a company. This is my idea " + st.session_state['idea'] + ". Generate a simple, black icon for it similar to the style of the iconic apple or nike logo.")
#             if st.button("Submit", type="primary"):
#                 st.session_state['logo_prompt'] = prompt
#                 st.session_state['logo_response'] = image_generation(prompt)
#                 st.image(st.session_state['logo_response'])
#         else:
#             logo_prompt = st.text_area("Prompt", st.session_state['logo_prompt'], key="oneliner")
#             if st.button("Submit", type="primary"):
#                 st.session_state['logo_prompt'] = logo_prompt
#                 st.session_state['logo_response'] = image_generation(logo_prompt)
#                 st.image(st.session_state['logo_response'])
#         if 'logo_response' in st.session_state:
#             st.image(st.session_state['logo_response'])
#     else:
#         "Please enter an idea on the Input page."
    
# NAVIGATION
pages = {
    "Home": Home,
    "Company Name":, CompanyName,
    "One Liners": OneLiners,
    "Domains": Domains,
    "Market Sizing": MarketSizing,
    "Jingle": Jingle,
    "Logos": Logos
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

page = pages[selection]
page()