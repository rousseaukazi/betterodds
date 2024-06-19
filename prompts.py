
def get_prompts(var):
    return {
        "OneLiner": f"I'm starting a company. This is my idea " + var + ". Please provide me with 3 different one-liners I can use in my seed deck. Just provide me with the one-liners and nothing else."
    }


# "OL": f"I'm starting a company. This is my idea " + {var} + ". Please provide me with 3 different one-liners I can use in my seed deck. Just provide me with the one-liners and nothing else."
#     domain_prompt = "I'm starting a company. This is my idea " + idea + ". Please provide me with 3 different domains I can use in my seed deck. Just provide the domain name, a reason why, and nothing else."
#     ms_prompt = "I'm starting a company. This is my idea " + idea + ". Please provide me with detailed yet concise bullet points detailing the market sizing. Use real numbers and figures. Just provide me with the market sizing and nothing else."
#     income_prompt = "I'm starting a company. This is my idea " + idea + ". Please provide me with a few bullet points detailing the conservative to aggressive income projections based on the business model and various timelines. Just provide the income projections, reasoning behind it, and the unit economics and nothing else."
#     proto_prompt = "I'm starting a company. My idea: " + idea + ". Provide a code block for the HTML and CSS for a modern looking website (with a beautiful gradient header) that has a clear marketing header, get started button, footer, and black border around the entire site so it's visible on a whitebackground. Your response should start and end with '''. Nothing else but just the code block. If you provide anything, it will break my product."
#     logo_prompt = "I'm starting a company. This is my idea " + idea + ". Generate a simple, black icon for it similar to the style of the iconic apple or nike logo."
#     song_prompt = "Create 4 stanzas of song lyrics for a pop, marketing song about my business idea. Here's the idea: " + idea + ". Just provide the lyrics no extranerous or confirmation text. It should start with (Verse 1)."
#     song_title_prompt = "Create a title for a poppy, marketing song for my business idea. Here's the idea: " + idea + ". Just provide the title, nothing else."