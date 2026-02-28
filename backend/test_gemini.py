import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini():
    # Try finding .env in same dir or one level up
    load_dotenv('.env')
    load_dotenv('../.env')
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment!")
        return

    print(f"Using API Key: {api_key[:5]}...{api_key[-5:]}")
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Gemini is working' if you can read this.")
        print(f"Response: {response.text}")
        print("✅ Gemini API is functional!")
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")

if __name__ == "__main__":
    test_gemini()
