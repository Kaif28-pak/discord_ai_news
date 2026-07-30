import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import google.generativeai as genai
import random

# .env file load karna
load_dotenv()

# ==================== CONFIGURATION ====================
# Yahan ab direct os.getenv se key utha rahe hain
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Agar API key load nahi hui toh script yahin rok dega aur batayega
if not GEMINI_API_KEY:
    raise ValueError("Error: GEMINI_API_KEY .env file se load nahi hui! Check karein ke asli key daali hai ya nahi.")

# Naye Google GenAI SDK ka client setup
client = genai.Client(api_key=GEMINI_API_KEY)


def fetch_ai_news():
    # 1. Yahan 4 alag alag tech aur coding ki images hain, har baar koi nayi aayegi
    banner_images = [
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1627398240309-089a14405537?auto=format&fit=crop&w=800&q=80"
    ]
    selected_image = random.choice(banner_images)

    raw_news_text = "..." # (Aapka RSS fetch karne wala code jo pehle se hai wo waise hi rahega, main sirf prompt update kar raha hoon)
    
    # 2. Behtareen Prompt (Drama Ignore + Web Dev Tools Focus)
    prompt = f"""
    Tum ek expert Tech Journalist ho.
    
    CRITERIA:
    1. SIRF aur SIRF tab hi OpenAI, Gemini, ya Claude ka zikar karo agar unka koi NEW MODEL ya MAJOR FEATURE launch hua ho.
    2. Agar in badi companies ki sirf policy, security breach, tanqeed, ya CEO ki baatein hain, toh unhein MUKAMMAL IGNORE kar do. Mujhe drama nahi chahiye.
    3. NEW AI WEB DEV TOOLS: Agar koi major model update nahi hai, toh apna poora focus **Naye AI Web Development Tools** par shift kar do. Aisi news ya tools dhoondo jo React frontends, backend APIs, database migrations (jaise MySQL/PostgreSQL), ya code structure validations ko asaan banate hon.
    4. Muje seedha news chahiye. Apni taraf se "Robot" ya "AI Agent" ban kar meta-commentary mat do.
    5. STRICT RULE: Pura response 1500 characters se lamba nahi hona chahiye. Sirf top 3-4 news do.

    FORMAT:
    - Shuru mein is image ko as a banner lagao: ![AI News]({selected_image})
    - Discord ke liye appealing format use karo (Emojis, bold headings, aur bullet points).
    - 🔗 **LINKS LAZMI HAIN:** Har tool, software, ya nayi AI ke naam ke sath uska official link ya URL lazmi shamil karo clickable format mein (jaise: [Cursor IDE](https://cursor.com)).
    
    Headlines:
    {raw_news_text}
    """
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
    )
    return response.text

def send_to_discord(message):
    if not message:
        return
        
    print("Discord par message bhej raha hoon...")
    final_message = "🤖 **Daily AI Updates** 🤖\n\n" + message
    
    # Discord ki 2000 character limit ko handle karne ke liye text ko hisson mein divide kar rahe hain
    max_length = 1900
    chunks = [final_message[i:i+max_length] for i in range(0, len(final_message), max_length)]
    
    for chunk in chunks:
        payload = {"content": chunk}
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        
        if res.status_code in [200, 204]:
            print("Message successfully Discord par bhej diya gaya!")
        else:
            print(f"Discord Error: {res.status_code}, {res.text}")

if __name__ == "__main__": 
    processed_news = fetch_ai_news()
    send_to_discord(processed_news)