import openai
import os
from dotenv import load_dotenv
import base64
import streamlit as st

# Load environment variables from .env locally
load_dotenv()

# Use local env or Streamlit Cloud secret
openai.api_key = os.getenv("openai_api_key") or st.secrets.get("openai_api_key")

def get_answer(messages):
    system_message = [{"role": "system", "content": "You are a helpful AI chatbot that answers questions asked by the user."}]
    messages = system_message + messages
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )
    return response.choices[0].message.content

def speech_to_text(audio_data):
    try:
        with open(audio_data, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return None

def text_to_speech(input_text):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
