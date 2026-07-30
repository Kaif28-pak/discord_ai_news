import os
import sys
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import random

# Error pakadne ke liye try-except block (jaisa report ne bataya)
try:
    from google import genai
except ImportError as e:
    print("Failed to import google.genai:", e)
    print("sys.path:", sys.path)
    try:
        import google
        print("google package location:", getattr(google, "__file__", "<namespace package, no file>"))
    except Exception as e2:
        print("Importing top-level 'google' also failed:", e2)
    raise

# .env file load karna
load_dotenv()

# ==================== CONFIGURATION ====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

if not GEMINI_API_KEY:
    raise ValueError("Error: GEMINI_API_KEY .env file se load nahi hui!")

# Naye SDK ka client setup
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_rss_news():
    rss_url = "https://news.google.com/rss/search?q=artificial+intelligence+OR+web+development&hl=en-US&gl=US&ceid=US:en"
    try:
        response = requests.get(rss_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        news_items = []
        for item in root.findall('./channel/item')[:5]:
            title = item.find('title').text
            link = item.find('link').text
            news_items.append(f"- [{title}]({link})")
            
        return "\n".join(news_items)
    except Exception as e:
        print(f"RSS Fetch Error: {e}")
        return "Aaj ki taza khabrein laane mein masla hua."

def fetch_ai_news():
    banner_images = [
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1627398240309-089a14405537?auto=format&fit=crop&w=800&q=80"
    ]
    selected_image = random.choice(banner_images)
    raw_news_text = fetch_rss_news()
    
    prompt = f"""
    Tum ek expert Tech Journalist ho.
    
    CRITERIA:
    1. SIRF aur SIRF tab hi OpenAI, Gemini, ya Claude ka zikar karo agar unka koi NEW MODEL ya MAJOR FEATURE launch hua ho.
    2. Agar in badi companies ki sirf policy, security breach, tanqeed, ya CEO ki baatein hain, toh unhein MUKAMMAL IGNORE kar do. Mujhe drama nahi chahiye.
    3. NEW AI WEB DEV TOOLS: Agar koi major model update nahi hai, toh apna poora focus **Naye AI Web Development Tools** par shift kar do.
    4. Muje seedha news chahiye. Apni taraf se "Robot" ya "AI Agent" ban kar meta-commentary mat do.
    5. STRICT RULE: Pura response 1500 characters se lamba nahi hona chahiye. Sirf top 3-4 news do.

    FORMAT:
    - Shuru mein is image ko as a banner lagao: ![AI News]({selected_image})
    - Discord ke liye appealing format use karo.
    - 🔗 **LINKS LAZMI HAIN.**
    
    Headlines:
    {raw_news_text}
    """
    
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
    )
    return response.text

def send_to_discord(message):
    if not message:
        return
        
    print("Discord par message bhej raha hoon...")
    final_message = "🤖 **Daily AI Updates** 🤖\n\n" + message
    
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
