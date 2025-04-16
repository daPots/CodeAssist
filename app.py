import streamlit as st
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
import os
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from datetime import datetime

float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", 
             "content": "Code Assist smart AI system activated. Check if the patient is responsive."
            }
        ]
    if "action_logs" not in st.session_state:
        st.session_state.action_logs = []  # Initialize action log

initialize_session_state()

# Add custom CSS to create a hover effect
st.markdown(""" <style>
        .hover-message-container {
            position: relative;
            display: inline-block;
            cursor: pointer;
        }

        .hover-message-container .hover-message {
            visibility: hidden;
            width: 400px;
            background-color: #f9f9f9;
            color: black;
            text-align: center;
            border-radius: 5px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            top: 125%; /* Position the message above the div */
            left: 80%;
            margin-left: -100px; /* Offset for centering */
            opacity: 0;
            transition: opacity 0.3s;
        }

        .hover-message-container:hover .hover-message {
            visibility: visible;
            opacity: 1;
        }
    </style> """, unsafe_allow_html=True)

# Header images
col1, col2, col5 = st.columns([4, 1, 2])
with col1: st.image("name.png")
with col2: st.image("logo.png")
with col5:
    st.markdown("""
        <div class="hover-message-container">
            <button style="font-size: 20px; border: none; background-color: transparent; color: #79aaf7;">ⓘ How To Use</button>
            <div class="hover-message">
                <p> CodeAssist is an AI-powered smart system intended to guide EMT workers through a patient cardiac arrest event using ACLS protocols.
                    To begin, simply click on the microphone and say "Begin the protocol". 
                    The system will start giving you tasks, and you must respond with an acknowledgement that you finished the task. 
                    All events are logged below the chat.
            </div>
        </div>
    """, unsafe_allow_html=True)

# Centered layout for 'Click to Record' and audio recorder
col3, col4 = st.columns([1, 1])
with col3:
    st.markdown("<h1 style='text-align: center; color: #0f71e5;'>Click to Record</h1>", unsafe_allow_html=True)
with col4:
    # Use a div to wrap and apply vertical alignment for the microphone
    st.markdown("""
        <div style="display: flex; align-items: center; height: 100%;">
            <div style="margin-left: auto; margin-right: auto;">
                """ , unsafe_allow_html=True)
    audio_bytes = audio_recorder(text="", icon_size="5x", recording_color="#FF0000", neutral_color="#79aaf7")
    st.markdown("</div></div>", unsafe_allow_html=True)  # Close the divs after the recorder


for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.write(message["content"])

# Handle audio input and transcription
if audio_bytes:
    with st.spinner("Acknowledging Task Completion..."):
        webm_file_path = "temp_audio.webm"
        with open(webm_file_path, "wb") as f: f.write(audio_bytes)
        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"): st.write(transcript)
            os.remove(webm_file_path)

            # Log the task completion
            log_entry = {"task": transcript, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            st.session_state.action_logs.append(log_entry)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Generating Next Task..."): final_response = get_answer(st.session_state.messages)
        with st.spinner("Broadcasting Task..."):
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file)
        st.write(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        os.remove(audio_file)

# Display action logs in the app (optional, for debugging or tracking purposes)
if st.session_state.action_logs:
    st.write("Action Logs:")
    for log in st.session_state.action_logs:
        st.write(f"Task: {log['task']} | Time: {log['time']}")