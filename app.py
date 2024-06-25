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
import streamlit.components.v1 as components


# API_KEYS
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()
suno_api_key = st.secrets["SUNOAI_API_KEY"]

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

def remove_bg(image_url):
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        data={
            'image_url': image_url,
            'size': 'auto'
        },
        headers={'X-Api-Key': st.secrets["REMOVE_BG_API_KEY"]},
    )
    if response.status_code == requests.codes.ok:
        with open('no-bg.png', 'wb') as out:
            out.write(response.content)
            st.image("no-bg.png",use_column_width=True)
    else:
        print("Error:", response.status_code, response.text)

import streamlit as st
import requests
import time

def Home():
    st.title("Home")
    with st.form(key='home_form'):
        idea = st.text_input("Enter your idea:")
        submit_button = st.form_submit_button(label='Submit', type="primary")
    
    if submit_button:
        st.session_state['idea'] = idea
    
    if 'idea' in st.session_state:
        st.write("### Current Idea:")
        st.write(st.session_state['idea'])

def CompanyName():
    st.title("Company Name")
    if 'idea' in st.session_state:
        with st.form(key='company_name_form'):
            if 'cn_prompt' not in st.session_state:
                company_name_prompt = '''I'm starting a business.
                    This is my idea: [[''' + st.session_state['idea'] + ''']]
                    Please provide me with 3 different business name options (1. Direct and clear, 2. Approachable and friendly: 3. Sticky and memorable (if possible try to use alliteration)).
                    Below is a template for what / how I want you to output the business names.
                    Note: “*business-name*” represents the part I want you to replace with the corresponding business name. For your response, just provide me with the business name and nothing else.
                    1. Direct: *business-name*
                    2. Approachable: *business-name*
                    3. Sticky: *business-name*
                    Context: Before you suggest options, look for existing companies that are similar and use their names as a reference point. Strongly weigh the attributes of the business name of the most successful businesses within my field to generate your suggestions.
                    Additional criteria for business name:
                    1. It should be pithy and clearly describe what the business does to a layman
                    2. They should be intriguing but not cringy
                    2. It should be memorable (very important)
                    3. It should ideally describe how we're a solution to a problem without the need for additional explanation
                    4. It should inspire confidence and make you want to trust and pay for the service / product
                    5. Whenever possible try to use alliteration to make it catchy, but don’t sacrifice accuracy and clarity for it for alliteration.'''
                prompt = st.text_area("Prompt", company_name_prompt, key="oneliner")
            else:
                prompt = st.text_area("Prompt", st.session_state['cn_prompt'], key="businessname")
            
            submit_button = st.form_submit_button(label='Submit',type="primary")
        
        if submit_button:
            st.session_state['cn_prompt'] = prompt
            st.session_state['cn_response'] = ChatGPT(prompt)
        
        if 'cn_response' in st.session_state:
            st.write(st.session_state['cn_response'])
    else:
        st.write("Please enter an idea on the Input page.")

def OneLiners():
    st.title("One Liners")
    if 'idea' in st.session_state:
        with st.form(key='one_liners_form'):
            if 'ol_prompt' not in st.session_state:
                one_liner_prompt = '''I'm starting a business.
                    This is my idea:[[''' + st.session_state['idea'] + ''']]
                    Please provide me with 3 different one-liners (1. Direct and clear, 2. Approachable and friendly: 3. Sticky and memorable (if possible try to use alliteration)) to be used as a public facing company slogan that described my business.
                    Below is a template for what / how I want you to output the one-liners.
                    Note: "*insert respective one-liner*" represents the part I want you to replace with the corresponding one liners. For your response, just provide me with the one-liners and nothing else.
                    1. Direct: *insert respective one-liner*
                    2. Approachable: *insert respective one-liner*
                    3. Sticky: *insert respective one-liner*
                    Context: Before you suggest options, look for existing companies that are similar and use their one liners as a reference point for your suggestions. Strongly weigh the attributes of the one liners of the most successful businesses within my field to generate your suggestions.
                    Additional criteria for one-liners:
                    1. They should be pithy and clearly describe what the business does to a layman
                    2. They should be intriguing but not cringy or fluffy
                    2. It should be memorable
                    3. They should clearly describe how we're a solution to a problem
                    4. They should inspire confidence and make you want to trust and pay for the service / product
                    5. Whenever possible try to use alliteration to make it catchy, but don’t sacrifice accuracy and clarity for it for alliteration'''
                prompt = st.text_area("Prompt", one_liner_prompt, key="oneliner")
            else:
                prompt = st.text_area("Prompt", st.session_state['ol_prompt'], key="oneliner")
            
            submit_button = st.form_submit_button(label='Submit',type="primary")
        
        if submit_button:
            st.session_state['ol_prompt'] = prompt
            st.session_state['ol_response'] = ChatGPT(prompt)
        
        if 'ol_response' in st.session_state:
            st.write(st.session_state['ol_response'])
    else:
        st.write("Please enter an idea on the Input page.")

def Domains():
    st.title("Domains")
    if 'idea' in st.session_state:
        with st.form(key='domains_form'):
            if 'domain_prompt' not in st.session_state:
                dom_prompt = '''I'm starting a business.
                        This is my idea: [[''' + st.session_state['idea'] + ''']].
                        I need to come up with a domain for my idea.
                        Please provide me with 3 different domains that would be suitable for my business name.
                        Below is a template for what / how I want you to output the domains.
                        Note: "*domain-name*" represents the part I want you to replace with the corresponding domain name. For your response, just provide me with the domain name (*domain-name*) and a concise and very short 1-sentence description (try to keep this under 10 words) for why that domain is suitable (*description*).
                        1. *domain-name* – *description*
                        2. *domain-name* – *description*
                        3. *domain-name* – *description*
                        Context: Before you suggest options, look for existing companies that are similar and use their domains relative to the business name as a reference point for your suggestions. Strongly weigh the domains of the most successful businesses within the respective field / industry to generate your suggestions.'''
                domain_prompt_edit = st.text_area("Prompt", dom_prompt, key="domain")
            else:
                domain_prompt_edit = st.text_area("Prompt", st.session_state['domain_prompt'], key="domain")
            
            submit_button = st.form_submit_button(label='Submit',type="primary")
        
        if submit_button:
            st.session_state['domain_prompt'] = domain_prompt_edit
            st.session_state['domain_response'] = ChatGPT(domain_prompt_edit)
        
        if 'domain_response' in st.session_state:
            st.write(st.session_state['domain_response'])
    else:
        st.write("Please enter an idea on the Input page.")

def MarketSizing():
    st.title("Market Sizing")
    if 'idea' in st.session_state:
        with st.form(key='market_sizing_form'):
            if 'ms_prompt' not in st.session_state:
                ms_prompt_default = st.text_area("Prompt", "I'm starting a company. This is my idea " + st.session_state['idea'] + ". Please provide me with detailed yet concise bullet points detailing the market sizing. Use real numbers and figures. Just provide me with the market sizing and nothing else. Cap the response to < 10 bullets.")
            else:
                ms_prompt_default = st.text_area("Prompt", st.session_state['ms_prompt'], key="domain")
            
            submit_button = st.form_submit_button(label='Submit',type="primary")
        
        if submit_button:
            st.session_state['ms_prompt'] = ms_prompt_default
            st.session_state['ms_response'] = ChatGPT(ms_prompt_default)
        
        if 'ms_response' in st.session_state:
            st.write(st.session_state['ms_response'])
    else:
        st.write("Please enter an idea on the Input page.")

def Jingle():
    st.title("Jingle")
    if 'idea' in st.session_state:
        with st.form(key='jingle_form'):
            if 'jingle_prompt' not in st.session_state:
                st.session_state['jingle_prompt'] = "Create 1 stanza of song lyrics for a pop, marketing song about my business idea. It should be a short jingle. Here's the idea: " + st.session_state['idea'] + ". Just provide the lyrics, no extraneous or confirmation text. It should start with (Verse 1)."
                st.session_state['jingle_title_prompt'] = "Create a title for a poppy, marketing song for my business idea. Here's the idea: " + st.session_state['idea'] + ". Just provide the title, nothing else."
            
            jingle_prompt = st.text_area("Jingle Lyrics Prompt", st.session_state['jingle_prompt'])
            jingle_title_prompt = st.text_area("Jingle Title Prompt", st.session_state['jingle_title_prompt'])
            
            submit_button = st.form_submit_button(label='Submit',type="primary")
        
        if submit_button:
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
        with st.form(key='logo_form'):
            if 'logo_prompt' not in st.session_state:
                st.session_state['logo_prompt'] = "Simplify the idea in brackets to just 2 words [[" + st.session_state['idea'] + "‌]]. Store that answer in SIMPLIFIED_IDEA. For the SIMPLIFIED_IDEA, what's the single object that best represents the idea? Store that in OBJECT. Produce a simple yet geometric icon of just that OBJECT (no letters), in black, on a white circle, in the style of Pentagram (the famous logo design agency)."
            logo_prompt = st.text_area("Prompt", st.session_state['logo_prompt'])
            submit_button = st.form_submit_button(label='Submit',type="primary")
        
        if submit_button:
            st.session_state['logo_prompt'] = logo_prompt
            st.session_state['logo_response_one'] = image_generation(st.session_state['logo_prompt'])
            st.session_state['logo_response_two'] = image_generation(st.session_state['logo_prompt'])
            st.session_state['logo_response_three'] = image_generation(st.session_state['logo_prompt'])
        
        if all(key in st.session_state for key in ['logo_response_one', 'logo_response_two', 'logo_response_three']):
            col1, col2, col3 = st.columns(3)
            with col1:
                # st.image(st.session_state['logo_response_one'], use_column_width=True)
                remove_bg(st.session_state['logo_response_one'])
            with col2:
                # st.image(st.session_state['logo_response_two'], use_column_width=True)
                remove_bg(st.session_state['logo_response_two'])
            with col3:
                # st.image(st.session_state['logo_response_three'], use_column_width=True)
                remove_bg(st.session_state['logo_response_three'])
    else:
        st.write("Please enter an idea on the Input page.")
    
def Video():
    st.title("Intro Video")
    def createVideo():
        url = "https://api.synthesia.io/v2/videos"
        payload = {
            "test": "false",
            "visibility": "public",
            "title": "My first Synthetic video",
            "description": "Intro Test",
            "input": [
                {
                    "avatarSettings": {
                        "horizontalAlign": "center",
                        "scale": 1,
                        "style": "rectangular",
                        "seamless": False
                    },
                    "backgroundSettings": { "videoSettings": {
                            "shortBackgroundContentMatchMode": "freeze",
                            "longBackgroundContentMatchMode": "trim"
                        } },
                    "scriptText": st.session_state['idea'],
                    "avatar": "anna_costume1_cameraA",
                    "background": "large_window"
                }
            ],
            "soundtrack": "modern"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "ddea6a53e118514eaaa402be5b5e2ab3"
        }
        response = requests.post(url, json=payload, headers=headers)
        json_data = response.json()
        video_id = json_data["id"]
        return json_data
        # st.write(video_id)
        # return video_id

    def getVideo(vid):
        url = "https://api.synthesia.io/v2/videos/" + vid
        headers = {
            "accept": "application/json",
            "Authorization": "ddea6a53e118514eaaa402be5b5e2ab3"
        }
        response = requests.get(url, headers=headers)
        return response.json()
    
    with st.form(key='video_form'):
        submit_button = st.form_submit_button(label='Generate',type="primary")
    
    if submit_button:
        counter = 0
        createVideoResponse = createVideo()
        st.write(createVideoResponse["id"])
        while getVideo(createVideoResponse["id"])["status"] is not "complete":
            st.write(str(counter) + " — " + getVideo(createVideoResponse["id"])["status"])
            time.sleep(5)
            counter = counter + 5
        st.write("🎉 " + str(counter) + " — " + getVideo(createVideoResponse["id"])["status"])
        # st.write(getVideo(createVideoResponse["id"]))
        # getVideoResponse = getVideo(createVideo())
        # st.video(getVideoResponse["download"])

# # PAGE FUNCTIONS 

# def Home():
#     st.title("Home")
#     idea = st.text_input("Enter your idea:")
#     if idea:
#         st.session_state['idea'] = idea
#     if 'idea' in st.session_state:
#         st.write("### Current Idea:")
#         st.write(st.session_state['idea'])

# def CompanyName():
#     st.title("Company Name")
#     if 'idea' in st.session_state:
#         if 'cn_prompt' not in st.session_state:
#             company_name_prompt = '''I'm starting a business.
#                 This is my idea: [[''' + st.session_state['idea'] + ''']]
#                 Please provide me with 3 different business name options (1. Direct and clear, 2. Approachable and friendly: 3. Sticky and memorable (if possible try to use alliteration)).
#                 Below is a template for what / how I want you to output the business names.
#                 Note: “*business-name*” represents the part I want you to replace with the corresponding business name. For your response, just provide me with the business name and nothing else.
#                 1. Direct: *business-name*
#                 2. Approachable: *business-name*
#                 3. Sticky: *business-name*
#                 Context: Before you suggest options, look for existing companies that are similar and use their names as a reference point. Strongly weigh the attributes of the business name of the most successful businesses within my field to generate your suggestions.
#                 Additional criteria for business name:
#                 1. It should be pithy and clearly describe what the business does to a layman
#                 2. They should be intriguing but not cringy
#                 2. It should be memorable (very important)
#                 3. It should ideally describe how we're a solution to a problem without the need for additional explanation
#                 4. It should inspire confidence and make you want to trust and pay for the service / product
#                 5. Whenever possible try to use alliteration to make it catchy, but don’t sacrifice accuracy and clarity for it for alliteration.'''
#             prompt = st.text_area("Prompt", company_name_prompt, key="oneliner")
#             if st.button("Submit", type="primary"):
#                 st.session_state['cn_prompt'] = prompt
#                 st.session_state['cn_response'] = ChatGPT(prompt)
#         else:
#             cn_prompt = st.text_area("Prompt", st.session_state['cn_prompt'], key="businessname")
#             if st.button("Submit", type="primary"):
#                 st.session_state['cn_prompt'] = cn_prompt
#                 st.session_state['cn_response'] = ChatGPT(cn_prompt)
#         if 'cn_response' in st.session_state:
#             st.write(st.session_state['cn_response'])
#     else:
#         "Please enter an idea on the Input page."

# def OneLiners():
#     st.title("One Liners")
#     if 'idea' in st.session_state:
#         if 'ol_prompt' not in st.session_state:
#             one_liner_prompt = '''I'm starting a business.
#                 This is my idea:[[''' + st.session_state['idea'] + ''']]
#                 Please provide me with 3 different one-liners (1. Direct and clear, 2. Approachable and friendly: 3. Sticky and memorable (if possible try to use alliteration)) to be used as a public facing company slogan that described my business.
#                 Below is a template for what / how I want you to output the one-liners.
#                 Note: "*insert respective one-liner*" represents the part I want you to replace with the corresponding one liners. For your response, just provide me with the one-liners and nothing else.
#                 1. Direct: *insert respective one-liner*
#                 2. Approachable: *insert respective one-liner*
#                 3. Sticky: *insert respective one-liner*
#                 Context: Before you suggest options, look for existing companies that are similar and use their one liners as a reference point for your suggestions. Strongly weigh the attributes of the one liners of the most successful businesses within my field to generate your suggestions.
#                 Additional criteria for one-liners:
#                 1. They should be pithy and clearly describe what the business does to a layman
#                 2. They should be intriguing but not cringy or fluffy
#                 2. It should be memorable
#                 3. They should clearly describe how we're a solution to a problem
#                 4. They should inspire confidence and make you want to trust and pay for the service / product
#                 5. Whenever possible try to use alliteration to make it catchy, but don’t sacrifice accuracy and clarity for it for alliteration'''
#             prompt = st.text_area("Prompt", one_liner_prompt, key="oneliner")
#             if st.button("Submit", type="primary"):
#                 st.session_state['ol_prompt'] = prompt
#                 st.session_state['ol_response'] = ChatGPT(prompt)
#         else:
#             ol_prompt = st.text_area("Prompt", st.session_state['ol_prompt'], key="oneliner")
#             if st.button("Submit", type="primary"):
#                 st.session_state['ol_prompt'] = ol_prompt
#                 st.session_state['ol_response'] = ChatGPT(ol_prompt)
#         if 'ol_response' in st.session_state:
#             st.write(st.session_state['ol_response'])
#     else:
#         "Please enter an idea on the Input page."

# def Domains():
#     st.title("Domains")
#     if 'idea' in st.session_state:
#         if 'domain_prompt' not in st.session_state:
#             dom_prompt = '''I'm starting a business.
#                     This is my idea: [[''' + st.session_state['idea'] + ''']].
#                     I need to come up with a domain for my idea.
#                     Please provide me with 3 different domains that would be suitable for my business name.
#                     Below is a template for what / how I want you to output the domains.
#                     Note: "*domain-name*" represents the part I want you to replace with the corresponding domain name. For your response, just provide me with the domain name (*domain-name*) and a concise and very short 1-sentence description (try to keep this under 10 words) for why that domain is suitable (*description*).
#                     1. *domain-name* – *description*
#                     2. *domain-name* – *description*
#                     3. *domain-name* – *description*
#                     Context: Before you suggest options, look for existing companies that are similar and use their domains relative to the business name as a reference point for your suggestions. Strongly weigh the domains of the most successful businesses within the respective field / industry to generate your suggestions.'''
#             domain_prompt_edit = st.text_area("Prompt", dom_prompt, key="domain")
#             if st.button("Submit", type="primary"):
#                 st.session_state['domain_prompt'] = domain_prompt_edit
#                 st.session_state['domain_response'] = ChatGPT(domain_prompt_edit)
#         if 'domain_response' in st.session_state:
#             st.write(st.session_state['domain_response'])
#     else:
#         "Please enter an idea on the Input page."

# def MarketSizing():
#     st.title("Market Sizing")
#     if 'idea' in st.session_state:
#         if 'ms_prompt' not in st.session_state:
#             ms_prompt_default = st.text_area("Prompt", "I'm starting a company. This is my idea " + st.session_state['idea'] + ". Please provide me with detailed yet concise bullet points detailing the market sizing. Use real numbers and figures. Just provide me with the market sizing and nothing else. Cap the response to < 10 bullets.")
#             if st.button("Submit", type="primary"):
#                 st.session_state['ms_prompt'] = ms_prompt_default
#                 st.session_state['ms_response'] = ChatGPT(ms_prompt_default)
#         else:
#             ms_prompt_edit = st.text_area("Prompt", st.session_state['ms_prompt'], key="domain")
#             if st.button("Submit", type="primary"):
#                 st.session_state['ms_prompt'] = ms_prompt_edit
#                 st.session_state['ms_response'] = ChatGPT(ms_prompt_edit)
#         if 'ms_response' in st.session_state:
#             st.write(st.session_state['ms_response'])
#     else:
#         "Please enter an idea on the Input page."

# def Jingle():
#     st.title("Jingle")
#     if 'idea' in st.session_state:
#         if 'jingle_prompt' not in st.session_state:
#             st.session_state['jingle_prompt'] = "Create 1 stanza of song lyrics for a pop, marketing song about my business idea. It should be a short jingle. Here's the idea: " + st.session_state['idea'] + ". Just provide the lyrics, no extraneous or confirmation text. It should start with (Verse 1)."
#             st.session_state['jingle_title_prompt'] = "Create a title for a poppy, marketing song for my business idea. Here's the idea: " + st.session_state['idea'] + ". Just provide the title, nothing else."
        
#         jingle_prompt = st.text_area("Jingle Lyrics Prompt", st.session_state['jingle_prompt'])
#         jingle_title_prompt = st.text_area("Jingle Title Prompt", st.session_state['jingle_title_prompt'])
        
#         if st.button("Submit", type="primary"):
#             st.session_state['jingle_prompt'] = jingle_prompt
#             st.session_state['jingle_title_prompt'] = jingle_title_prompt
#             st.session_state['jingle_title'] = ChatGPT(jingle_title_prompt)
#             st.session_state['jingle_lyrics'] = ChatGPT(jingle_prompt)
            
#             music_generation_info = generate_music(suno_api_key, st.session_state['jingle_title'], st.session_state['jingle_lyrics'])
#             song_id = music_generation_info[0]["song_id"]
#             song_id = [song_id]

#             latest_iteration = st.empty()
#             bar = st.progress(0)

#             for i in range(100):
#                 latest_iteration.text(f'Making magic {i+1}')
#                 bar.progress(i + 1)
#                 time.sleep(.5)

#             generated_results = query_generated_results(suno_api_key, song_id)
#             st.session_state['jingle_audio'] = generated_results[0]["audio_url"]

#             latest_iteration.empty()
#             bar.empty()

#         if 'jingle_audio' in st.session_state:
#             st.audio(st.session_state['jingle_audio'])
#             st.write(st.session_state['jingle_title'])
#             st.write(st.session_state['jingle_lyrics'])
#     else:
#         st.write("Please enter an idea on the Input page.")

# def Logos():
#     st.title("Logos")

#     if 'idea' in st.session_state:
#         if 'logo_prompt' not in st.session_state:
#             st.session_state['logo_prompt'] = "Simplify the idea in brackets to just 2 words [[" + st.session_state['idea'] + "‌]]. Store that answer in SIMPLIFIED_IDEA. For the SIMPLIFIED_IDEA, what's the single object that best represents the idea? Store that in OBJECT. Produce a simple yet geometric icon of just that OBJECT (no letters), in black, on a white circle, in the style of Pentagram (the famous logo design agency)."
#         with st.form(key='logo_form'):
#             logo_prompt = st.text_area("Prompt", st.session_state['logo_prompt'])
#             submit_button = st.form_submit_button(label='Submit')

#         if submit_button:
#             st.session_state['logo_prompt'] = logo_prompt  # Update the prompt in the session state
#             st.session_state['logo_response_one'] = image_generation(st.session_state['logo_prompt'])  # Generate the image using the updated prompt
#             # if 'logo_response_one' in st.session_state:
#             #     st.image(st.session_state['logo_response_one'])
#             #     remove_bg(st.session_state['logo_response_one'])
#             st.session_state['logo_response_two'] = image_generation(st.session_state['logo_prompt'])  # Generate the image using the updated prompt
#             st.session_state['logo_response_three'] = image_generation(st.session_state['logo_prompt'])  # Generate the image using the updated prompt
        
#         if all(key in st.session_state for key in ['logo_response_one', 'logo_response_two', 'logo_response_three']):
#             # Create columns
#             col1, col2, col3 = st.columns(3)

#             # Add images to each column
#             with col1:
#                 st.image(st.session_state['logo_response_one'], use_column_width=True)
#                 remove_bg(st.session_state['logo_response_one'])

#             with col2:
#                 st.image(st.session_state['logo_response_two'], use_column_width=True)
#                 remove_bg(st.session_state['logo_response_two'])

#             with col3:
#                 st.image(st.session_state['logo_response_three'], use_column_width=True)
#                 remove_bg(st.session_state['logo_response_three'])
#     else:
#         st.write("Please enter an idea on the Input page.")
    
# def Video():

#     def createVideo():

#         url = "https://api.synthesia.io/v2/videos"

#         payload = {
#             "test": "false",
#             "visibility": "public",
#             "title": "My first Synthetic video",
#             "description": "Intro Test",
#             "input": [
#                 {
#                     "avatarSettings": {
#                         "horizontalAlign": "center",
#                         "scale": 1,
#                         "style": "rectangular",
#                         "seamless": False
#                     },
#                     "backgroundSettings": { "videoSettings": {
#                             "shortBackgroundContentMatchMode": "freeze",
#                             "longBackgroundContentMatchMode": "trim"
#                         } },
#                     "scriptText": "Hello, World! This is my first synthetic video, made with the Synthesia API!",
#                     "avatar": "anna_costume1_cameraA",
#                     "background": "large_window"
#                 }
#             ],
#             "soundtrack": "modern"
#         }
#         headers = {
#             "accept": "application/json",
#             "content-type": "application/json",
#             "Authorization": "ddea6a53e118514eaaa402be5b5e2ab3"
#         }

#         response = requests.post(url, json=payload, headers=headers)

#         json_data = response.json()
#         video_id = json_data["id"]
#         st.write(json_data)
#         st.write(video_id)

#     def getVideo(vid):
#         import requests

#         url = "https://api.synthesia.io/v2/videos/" + vid

#         headers = {
#             "accept": "application/json",
#             "Authorization": "ddea6a53e118514eaaa402be5b5e2ab3"
#         }

#         response = requests.get(url, headers=headers)
#         return response.json()
    
#     if st.button("Generate", type="primary"):
#             # createVideo()
#             getVideoResponse = getVideo("b12cd015-9da1-4ce4-b93a-40b6033a0a23")
#             st.video(getVideoResponse["download"])

# NAVIGATION
pages = {
    "Home": Home,
    "Company Name": CompanyName,
    "One Liners": OneLiners,
    "Domains": Domains,
    "Market Sizing": MarketSizing,
    "Jingle": Jingle,
    "Logos": Logos,
    "Videos": Video
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

page = pages[selection]
page()