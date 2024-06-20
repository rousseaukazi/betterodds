import io
import os
import time
import json
import openai
import requests
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
# PAGE FUNCTIONS 

def Home():
    st.title("Home")
    idea = st.text_input("Enter your idea:")
    if idea:
        st.session_state['idea'] = idea
        # st.write(check_remaining_quota(suno_api_key))
        
        song_prompt = "Create 1 stanzas of song lyrics for a pop, marketing song about my business idea. It should be a short jingle. Here's the idea: " + st.session_state['idea'] + ". Just provide the lyrics no extranerous or confirmation text. It should start with (Verse 1)."
        song_title_prompt = "Create a title for a poppy, marketing song for my business idea. Here's the idea: " + st.session_state['idea'] + ". Just provide the title, nothing else."

        title = ChatGPT(song_title_prompt)
        lyrics = ChatGPT(song_prompt)

        music_generation_info = generate_music(suno_api_key, title, lyrics)
        song_id = music_generation_info[0]["song_id"]
        song_id = [song_id]

        "## Surprise"
        latest_iteration = st.empty()
        bar = st.progress(0)

        for i in range(100):
            latest_iteration.text(f'Making magic {i+1}')
            bar.progress(i + 1)
            time.sleep(.5)

        generated_results = query_generated_results(suno_api_key, song_id)

        # Clear the placeholders
        latest_iteration.empty()
        bar.empty()

        "### ...and now we\'re done! Your very own marketing jingle 🎶"
        generated_results = query_generated_results(suno_api_key, song_id)
        st.audio(generated_results[0]["audio_url"])
        st.write(title)
        st.write(lyrics)

    if 'idea' in st.session_state:
        st.write("### Current Idea:")
        st.write(st.session_state['idea'])

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

# NAVIGATION
pages = {
    "Home": Home,
    "One Liners": OneLiners,
    "Domains": Domains,
    "Market Sizing": MarketSizing
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

page = pages[selection]
page()




