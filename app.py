import io
import os
import time
import json
import openai
from openai import OpenAI
import requests
import streamlit as st

# Set the OpenAI API key from the environment variable
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()

# Streamlit title
"# 021"

# Capturing the idea
idea = st.text_input("What's your idea?")
api_key = '72+hIHnhRYYVuu3v3CGc8P+QvZqSZJpk'

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


# OpenAI Request
def ChatGPTNoStream(prompt): 
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
    return response

def ChatGPT(prompt): 
    response = client.chat.completions.create(
        model="gpt-4o",
        stream=True,
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
    return st.write(response)

def ChatGPTCode(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt,
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
    return response.choices[0].message.content[3:-3]

def ImageGen(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

if idea: 
    # Prompts 
    ol_prompt = "I'm starting a company. This is my idea " + idea + ". Please provide me with 3 different one-liners I can use in my seed deck. Just provide me with the one-liners and nothing else."
    domain_prompt = "I'm starting a company. This is my idea " + idea + ". Please provide me with 3 different domains I can use in my seed deck. Just provide the domain name, a reason why, and nothing else."
    ms_prompt = "I'm starting a company. This is my idea " + idea + ". Please provide me with detailed yet concise bullet points detailing the market sizing. Use real numbers and figures. Just provide me with the market sizing and nothing else."
    income_prompt = "I'm starting a company. This is my idea " + idea + ". Please provide me with a few bullet points detailing the conservative to aggressive income projections based on the business model and various timelines. Just provide the income projections, reasoning behind it, and the unit economics and nothing else."
    proto_prompt = "I'm starting a company. My idea: " + idea + ". Provide a code block for the HTML and CSS for a modern looking website (with a beautiful gradient header) that has a clear marketing header, get started button, footer, and black border around the entire site so it's visible on a whitebackground. Your response should start and end with '''. Nothing else but just the code block. If you provide anything, it will break my product."
    logo_prompt = "I'm starting a company. This is my idea " + idea + ". Generate a simple, black icon for it similar to the style of the iconic apple or nike logo."
    song_prompt = "Create 4 stanzas of song lyrics for a pop, marketing song about my business idea. Here's the idea: " + idea + ". Just provide the lyrics no extranerous or confirmation text. It should start with (Verse 1)."
    song_title_prompt = "Create a title for a poppy, marketing song for my business idea. Here's the idea: " + idea + ". Just provide the title, nothing else."
    
    "## One Liner"
    ChatGPT(ol_prompt)

    "## Domains"
    ChatGPT(domain_prompt)

    # "## Market Sizing"
    # # ChatGPT(ms_prompt)

    # "## Income Projections"
    # # ChatGPT(income_prompt)

    # "## Logo"
    # # image_url = str(ImageGen(logo_prompt))
    # # st.image(image_url)
    
    "## Prototype"
    st.html(ChatGPTCode(proto_prompt))

    "## Surprise"
    title = ChatGPTNoStream(song_title_prompt).choices[0].message.content
    lyrics = ChatGPTNoStream(song_prompt).choices[0].message.content

    # Generate Song

    latest_iteration = st.empty()
    bar = st.progress(0)
    
    music_generation_info = generate_music(api_key, title, lyrics)
    song_id = music_generation_info[0]["song_id"]
    song_id = [song_id]

    for i in range(100):
        latest_iteration.text(f'Iteration {i+1}')
        bar.progress(i + 1)
        time.sleep(.5)

    generated_results = query_generated_results(api_key, song_id)

    # Clear the placeholders
    latest_iteration.empty()
    bar.empty()

    "### ...and now we\'re done! Your very own marketing jingle 🎶"
    st.audio(generated_results[0]["audio_url"])
    st.write(title)
    st.write(lyrics)

    "## Quota"
    quota_info = check_remaining_quota(api_key)
    st.write(quota_info)