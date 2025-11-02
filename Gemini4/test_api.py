import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from config.env file
load_dotenv('config.env')

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")

if api_key:
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, say 'API working' if you can hear me")
        print(f"API Response: {response.text}")
        print("✅ API is working correctly!")
    except Exception as e:
        print(f"❌ API Error: {e}")
else:
    print("❌ No API key found in config.env")

