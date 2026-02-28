import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

load_dotenv()

def run_diagnostics():
    print("--- Gemini API Diagnostics ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment.")
        return

    print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        genai.configure(api_key=api_key)
        print("Configuration: SUCCESS")
        
        print("Listing models...")
        models = genai.list_models()
        flash_found = False
        for m in models:
            print(f"Available model: {m.name} (Methods: {m.supported_generation_methods})")
            if 'gemini-1.5-flash' in m.name:
                flash_found = True
                print(f"** MATCH FOUND: {m.name} **")
        
        if not flash_found:
            print("ERROR: gemini-1.5-flash NOT found in available models.")
        else:
            print("Model Check: SUCCESS")

        # Test simple generation
        print("Testing simple generation with models/gemini-flash-latest...")
        model = genai.GenerativeModel('models/gemini-flash-latest')
        response = model.generate_content("Hello, are you active?")
        print(f"Generation Response: {response.text}")
        print("Generation Test: SUCCESS")

    except Exception as e:
        print(f"DIAGNOSTICS FAILED: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_diagnostics()
