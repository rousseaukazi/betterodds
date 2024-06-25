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
    html_code = """
    <div style="border: 1px solid #ccc; padding: 10px; width: 100%; max-width: 1200px; height: 600px; overflow: auto;">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }
            body {
                background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
                color: #333;
                line-height: 1.6;
            }
            .container {
                width: 90%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 0;
            }
            .logo {
                font-size: 24px;
                font-weight: bold;
                color: #fff;
            }
            nav ul {
                display: flex;
                list-style-type: none;
            }
            nav ul li {
                margin-right: 20px;
            }
            nav ul li a {
                color: #fff;
                text-decoration: none;
            }
            .cta-buttons {
                display: flex;
            }
            .cta-button {
                padding: 10px 20px;
                margin-left: 10px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
            }
            .cta-primary {
                background-color: #4CAF50;
                color: white;
            }
            .cta-secondary {
                background-color: white;
                color: #333;
            }
            .hero {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 50px 0;
            }
            .hero-content {
                flex: 1;
            }
            .hero h1 {
                font-size: 48px;
                margin-bottom: 20px;
                color: #fff;
            }
            .hero p {
                font-size: 18px;
                margin-bottom: 30px;
                color: #fff;
            }
            .email-form {
                display: flex;
                margin-bottom: 30px;
            }
            .email-form input {
                flex: 1;
                padding: 10px;
                font-size: 16px;
                border: none;
                border-radius: 5px 0 0 5px;
            }
            .email-form button {
                padding: 10px 20px;
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 0 5px 5px 0;
                cursor: pointer;
            }
            .mockups {
                flex: 1;
                text-align: right;
            }
            .mockup-mobile,
            .mockup-desktop {
                max-width: 100%;
                height: auto;
            }
            .social-proof {
                background-color: rgba(255, 255, 255, 0.9);
                padding: 30px 0;
                text-align: center;
            }
            .client-logos {
                display: flex;
                justify-content: space-around;
                align-items: center;
                flex-wrap: wrap;
            }
            .client-logos img {
                max-width: 120px;
                height: auto;
                margin: 10px;
            }
            .features {
                background-color: #fff;
                padding: 50px 0;
            }
            .features h2 {
                text-align: center;
                margin-bottom: 40px;
            }
            .feature-list {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
            }
            .feature {
                flex-basis: calc(33.333% - 40px);
                text-align: center;
                margin: 20px;
            }
            .feature i {
                font-size: 48px;
                color: #4CAF50;
                margin-bottom: 20px;
            }
            .cta-section {
                text-align: center;
                padding: 50px 0;
                background-color: rgba(255, 255, 255, 0.9);
            }
            .cta-section h2 {
                margin-bottom: 30px;
            }
            @media (max-width: 768px) {
                .hero {
                    flex-direction: column;
                }
                .mockups {
                    margin-top: 30px;
                }
                .feature {
                    flex-basis: 100%;
                }
            }
        </style>
        <header>
            <div class="container">
                <div class="logo">FinTech Solutions</div>
                <nav>
                    <ul>
                        <li><a href="#products">Products</a></li>
                        <li><a href="#solutions">Solutions</a></li>
                        <li><a href="#developers">Developers</a></li>
                        <li><a href="#resources">Resources</a></li>
                        <li><a href="#pricing">Pricing</a></li>
                    </ul>
                </nav>
                <div class="cta-buttons">
                    <button class="cta-button cta-secondary">Contact sales</button>
                    <button class="cta-button cta-primary">Dashboard</button>
                </div>
            </div>
        </header>

        <section class="hero">
            <div class="container">
                <div class="hero-content">
                    <h1>Financial infrastructure to grow your revenue</h1>
                    <p>Empower your business with our cutting-edge financial technology solutions. Streamline payments, optimize cash flow, and accelerate growth.</p>
                    <form class="email-form">
                        <input type="email" placeholder="Enter your email">
                        <button type="submit">Start now</button>
                    </form>
                </div>
                <div class="mockups">
                    <img src="/api/placeholder/300/600" alt="Mobile app mockup" class="mockup-mobile">
                    <img src="/api/placeholder/500/300" alt="Desktop dashboard mockup" class="mockup-desktop">
                </div>
            </div>
        </section>

        <section class="social-proof">
            <div class="container">
                <div class="client-logos">
                    <img src="/api/placeholder/120/60" alt="Client 1">
                    <img src="/api/placeholder/120/60" alt="Client 2">
                    <img src="/api/placeholder/120/60" alt="Client 3">
                    <img src="/api/placeholder/120/60" alt="Client 4">
                    <img src="/api/placeholder/120/60" alt="Client 5">
                </div>
            </div>
        </section>

        <section class="features">
            <div class="container">
                <h2>A fully integrated suite of payments products</h2>
                <div class="feature-list">
                    <div class="feature">
                        <i class="fas fa-exchange-alt"></i>
                        <h3>Seamless Transactions</h3>
                        <p>Process payments quickly and securely across multiple channels and currencies.</p>
                    </div>
                    <div class="feature">
                        <i class="fas fa-chart-line"></i>
                        <h3>Advanced Analytics</h3>
                        <p>Gain valuable insights into your financial data with our powerful analytics tools.</p>
                    </div>
                    <div class="feature">
                        <i class="fas fa-shield-alt"></i>
                        <h3>Robust Security</h3>
                        <p>Protect your business and customers with state-of-the-art security measures.</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="cta-section">
            <div class="container">
                <h2>Ready to supercharge your financial operations?</h2>
                <button class="cta-button cta-primary">Get started today</button>
            </div>
        </section>
    </div>
    """

    # Display the HTML in Streamlit
    st.markdown(html_code, unsafe_allow_html=True)

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