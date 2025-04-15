import openai
import os
from dotenv import load_dotenv
import base64
import streamlit as st

# Load environment variables from .env locally
load_dotenv()

# Use local env or Streamlit Cloud secret
openai.api_key = os.getenv("api_key") or st.secrets.get("api_key")

def get_answer(messages):
    system_message = [
        {
            "role": "system",
            "content": 'You are a smart AI system that helps EMT workers during a cardiac arrest call.'
            'You are to give tasks to the EMT worker to save the patient\'s life based on ACLS protocols.'
            'Provide the most appropriate tasks based on the patient\'s condition and the ACLS protocol.'
            'Repeat the task if the EMT does not respond. Acknowledge the task as completed if the EMT responds. '
            'Your responses should be short and concise. Preferably no more than 10 words.'
            'The following are the protocols:'
            'Check for responsiveness and breathing (scan for 5-10 seconds).'
            'Activate emergency response system and get AED.'
            'Time to check for carotid pulse (5-10 seconds). If no pulse, begin CPR.'
            'If no pulse, check for a shockable rhythm with AED. Follow AED instructions.'
            'Ensure the airway is open. Use advanced airway if needed.'
            'Give bag-mask ventilation. Provide supplemental oxygen. Monitor ventilation.'
            'IV Access and ECG: Establish IV access. Attach ECG leads. Monitor for arrhythmias.'
            'Administer epinephrine 1mg in 1:10,000 saline solution every 3-5 minutes.'
            'Administer amiodarone 300mg IV push for shockable rhythms (repeat with 150mg if needed).'
            'Administer atropine 1mg IV for bradycardia (max 3mg).'
            'Administer sodium bicarbonate 1mEq/kg IV for acidosis if indicated.'
            'Assess patient\'s neurological status using AVPU scale.'
            'Exposure: Remove clothing for full visual assessment of trauma, bleeding, burns.'
            'Time to Reassess vitals. Continue with appropriate interventions.'
        }
    ]
    messages = system_message + messages
    response = openai.chat.completions.create(model="gpt-3.5-turbo-1106", messages=messages, max_completion_tokens=40)
    return response.choices[0].message.content

def speech_to_text(audio_data):
    try:
        with open(audio_data, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
        return transcript
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return None

def text_to_speech(input_text):
    response = openai.audio.speech.create(model="tts-1", voice="nova", input=input_text)
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f: response.stream_to_file(webm_file_path)
    return webm_file_path

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f: data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
    st.markdown(md, unsafe_allow_html=True)