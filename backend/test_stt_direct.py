import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:] if API_KEY else 'None'}")

if not API_KEY:
    print("Error: No API key found")
    exit(1)

genai.configure(api_key=API_KEY)

def test_upload():
    # Create a dummy small wav file if one doesn't exist
    test_file = "test_audio.wav"
    if not os.path.exists(test_file):
        with open(test_file, "wb") as f:
            f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
            
    try:
        print(f"Uploading {test_file}...")
        audio_file = genai.upload_file(path=test_file)
        print(f"Upload successful. Name: {audio_file.name}, State: {audio_file.state.name}")
        
        while audio_file.state.name == "PROCESSING":
            print("Processing...")
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)
            
        print(f"Final State: {audio_file.state.name}")
        
        if audio_file.state.name == "ACTIVE":
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(["Transcribe this", audio_file])
            print(f"Response: {response.text}")
        else:
            print(f"File state is not ACTIVE: {audio_file.state.name}")
            
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_upload()
