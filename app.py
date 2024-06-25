import time
import json
import openai
import random
import requests
import anthropic
import streamlit as st


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

def createVideo(script):
    avatarArray = ["anna_costume1_cameraA","bridget_costume1_cameraA","isabella_costume1_cameraA","jack_costume2_cameraA","james_costume1_cameraA","jonathan_costume1_cameraA","laura_costume1_cameraA"]
    backgroundArray = ["white_studio","white_cafe","luxury_lobby","large_window","white_meeting_room","open_office"]

    url = "https://api.synthesia.io/v2/videos"
    payload = {
        "test": "false",
        "visibility": "public",
        "title": st.session_state['idea'],
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
                "scriptText": script,
                "avatar": random.choice(avatarArray),
                "background": random.choice(backgroundArray)
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
    return json_data

def getVideo(vid):
    url = "https://api.synthesia.io/v2/videos/" + vid
    headers = {
        "accept": "application/json",
        "Authorization": "ddea6a53e118514eaaa402be5b5e2ab3"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def askClaude(prompt):
    client = anthropic.Anthropic(
    api_key=st.secrets["CLAUDE_API_KEY"]
    )
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
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
    ]
    )
    return message.content[0].text

## PAGES 
def Home():
    st.title("Home")
    # st.html(askClaude("Please provide html and css for a basic website. Provide just the code and nothing else."))
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

    if 'idea' in st.session_state:
        with st.form(key='video_form'):
            if 'video_prompt' not in st.session_state:
                company_name = ChatGPT(f"Create a pithy company name for {st.session_state['idea']}. Just return the name and nothing else.")
                st.session_state['video_prompt'] = f'''Create a less than 25 word speech to promote the following [[Company Name]] and [[Business Idea]]. It should just be a speech no other items. It should get the listener excited about the business. 
                    Company Name: {company_name}
                    BusinessIdea: {st.session_state['idea']}'''
            
            video_prompt = st.text_area("Video Script Prompt", st.session_state['video_prompt'])
            
            submit_button = st.form_submit_button(label='Generate', type="primary")
        
        if submit_button:
            st.session_state['video_prompt'] = video_prompt
            st.session_state['video_script'] = ChatGPT(video_prompt)
            st.write(st.session_state['video_script'])
            
            createVideoResponse = createVideo(st.session_state['video_script'])
            st.session_state['video_id'] = createVideoResponse["id"]

            counter = 0
            latest_iteration = st.empty()
            bar = st.progress(0)

            while getVideo(st.session_state['video_id'])["status"] != "complete":
                latest_iteration.text(f'Making magic {counter + 1}')
                bar.progress((counter + 1) % 100)
                time.sleep(5)
                counter += 5
            
            st.session_state['video_url'] = getVideo(st.session_state['video_id'])["download"]

            latest_iteration.empty()
            bar.empty()

        if 'video_url' in st.session_state:
            st.video(st.session_state['video_url'])
    else:
        st.write("Please enter an idea on Home.")

def Website():
    websiteIdea = st.session_state['idea']
    template_code = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Online Store</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 16px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        header {
            background-color: #f8f8f8;
            padding: 15px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            text-decoration: none;
        }
        .nav-links {
            list-style: none;
            display: flex;
        }
        .nav-links li {
            margin-left: 20px;
        }
        .nav-links a {
            text-decoration: none;
            color: #333;
            font-weight: bold;
        }
        .hero {
            background-color: #e3f2fd;
            padding: 40px 0;
            text-align: center;
            position: relative;
        }
        .hero-content h1 {
            font-size: 36px;
            margin-bottom: 20px;
            color: #333;
        }
        .hero-emoji {
            font-size: 60px;
            margin-bottom: 20px;
        }
        .cta-button {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .cta-button:hover {
            background-color: #45a049;
        }
        .featured-product {
            padding: 40px 0;
            background-color: #f8f8f8;
        }
        .featured-product h2 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
        }
        .product-showcase {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .product-image {
            width: 100%;
            max-width: 300px;
            margin-bottom: 20px;
        }
        .product-image .placeholder-rect {
            width: 100%;
            padding-bottom: 100%; /* 1:1 Aspect Ratio */
            background-color: #bbdefb;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            position: relative;
        }
        .product-image .placeholder-rect::after {
            content: '🌟';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        .product-details {
            text-align: center;
        }
        .product-details h3 {
            font-size: 24px;
            margin-bottom: 15px;
        }
        .product-description {
            margin-bottom: 15px;
        }
        .product-price {
            font-size: 22px;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 15px;
        }
        .product-grid {
            padding: 40px 0;
        }
        .product-grid h2 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
        }
        .product-card {
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        .product-card:hover {
            transform: translateY(-5px);
        }
        .product-card .placeholder-rect {
            width: 100%;
            padding-bottom: 100%; /* 1:1 Aspect Ratio */
            background-color: #c8e6c9;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            position: relative;
        }
        .product-card .placeholder-rect::after {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        .product-card:nth-child(1) .placeholder-rect::after { content: '📱'; }
        .product-card:nth-child(2) .placeholder-rect::after { content: '💻'; }
        .product-card:nth-child(3) .placeholder-rect::after { content: '🎧'; }
        .product-card:nth-child(4) .placeholder-rect::after { content: '⌚'; }
        .product-card-content {
            padding: 15px;
        }
        .product-card h3 {
            margin-bottom: 10px;
            font-size: 18px;
        }
        .product-card .price {
            font-weight: bold;
            color: #4CAF50;
        }
        footer {
            background-color: #333;
            color: #fff;
            padding: 30px 0;
        }
        .footer-content {
            display: flex;
            flex-direction: column;
        }
        .footer-section {
            margin-bottom: 20px;
        }
        .footer-section h3 {
            margin-bottom: 15px;
            font-size: 20px;
        }
        .footer-section ul {
            list-style: none;
        }
        .footer-section ul li {
            margin-bottom: 8px;
        }
        .footer-section ul li a {
            color: #fff;
            text-decoration: none;
        }
        .footer-bottom {
            text-align: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #555;
        }

        @media (min-width: 768px) {
            .product-showcase {
                flex-direction: row;
                justify-content: space-between;
                align-items: flex-start;
            }
            .product-image {
                margin-right: 40px;
                margin-bottom: 0;
            }
            .product-details {
                text-align: left;
                flex: 1;
            }
            .footer-content {
                flex-direction: row;
                justify-content: space-between;
            }
            .footer-section {
                flex: 1;
                margin-right: 40px;
            }
        }

        @media (max-width: 767px) {
            .nav-links {
                display: none; /* Hide nav links on mobile */
            }
            .hero-content h1 {
                font-size: 28px;
            }
            .featured-product h2, .product-grid h2 {
                font-size: 24px;
            }
            .product-details h3 {
                font-size: 20px;
            }
            .product-price {
                font-size: 18px;
            }
            .grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <nav>
                <a href="#" class="logo">Your Store</a>
                <ul class="nav-links">
                    <li><a href="#">Home</a></li>
                    <li><a href="#">Products</a></li>
                    <li><a href="#">About</a></li>
                    <li><a href="#">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <div class="hero-emoji">🛍️</div>
            <div class="hero-content">
                <h1>Welcome to Your Online Store</h1>
                <a href="#" class="cta-button">Shop Now</a>
            </div>
        </div>
    </section>

    <section class="featured-product">
        <div class="container">
            <h2>Featured Product</h2>
            <div class="product-showcase">
                <div class="product-image">
                    <div class="placeholder-rect"></div>
                </div>
                <div class="product-details">
                    <h3>Amazing Product</h3>
                    <p class="product-description">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                    <p class="product-price">$99.99</p>
                    <a href="#" class="cta-button">Add to Cart</a>
                </div>
            </div>
        </div>
    </section>

    <section class="product-grid">
        <div class="container">
            <h2>Our Products</h2>
            <div class="grid">
                <div class="product-card">
                    <div class="placeholder-rect"></div>
                    <div class="product-card-content">
                        <h3>Product 1</h3>
                        <p class="price">$49.99</p>
                    </div>
                </div>
                <div class="product-card">
                    <div class="placeholder-rect"></div>
                    <div class="product-card-content">
                        <h3>Product 2</h3>
                        <p class="price">$39.99</p>
                    </div>
                </div>
                <div class="product-card">
                    <div class="placeholder-rect"></div>
                    <div class="product-card-content">
                        <h3>Product 3</h3>
                        <p class="price">$59.99</p>
                    </div>
                </div>
                <div class="product-card">
                    <div class="placeholder-rect"></div>
                    <div class="product-card-content">
                        <h3>Product 4</h3>
                        <p class="price">$69.99</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>About Us</h3>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                </div>
                <div class="footer-section">
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="#">Home</a></li>
                        <li><a href="#">Products</a></li>
                        <li><a href="#">About</a></li>
                        <li><a href="#">Contact</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Contact Us</h3>
                    <ul>
                        <li>Email: info@yourstore.com</li>
                        <li>Phone: (123) 456-7890</li>
                        <li>Address: 123 Store St, City, Country</li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2024 Your Online Store. All rights reserved.</p>
            </div>
        </div>
    </footer>
</body>
</html>'''
    final_code = askClaude(f"Rewritre this html & css code [[{template_code}]] to be about this business idea [[{websiteIdea}]]. Keep the everything about the format the same. You should only change the text, the emojis to be more relevant, and the prices to fit the text you're putting next to it. Only return the code and nothing else.")
    st.html(final_code)
        



# NAVIGATION
pages = {
    "Home": Home,
    "Company Name": CompanyName,
    "One Liners": OneLiners,
    "Domains": Domains,
    "Market Sizing": MarketSizing,
    "Jingle": Jingle,
    "Logos": Logos,
    "Videos": Video,
    "Website": Website
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

page = pages[selection]
page()