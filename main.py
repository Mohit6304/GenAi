import os

from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
from IPython.display import Audio
import requests
from gemini_utility import (load_gemini_pro_model,
                            gemini_pro_response,
                            gemini_pro_vision_response,
                            embeddings_model_response)


working_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Syntax AI",
    page_icon="🧠",
    layout="centered",
)

with st.sidebar:
    selected = option_menu('Syntax AI',
                           ['ChatBot',
                            'Story Generator',
                            'Comic Generator',
                            'Video Generator'],
                           menu_icon='robot', icons=['chat-dots-fill', 'book-fill', 'image-fill', 'play-fill'],
                           default_index=0
                           )


# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# chatbot page
if selected == 'ChatBot':
    model = load_gemini_pro_model()

    # Initialize chat session in Streamlit if not already present
    if "chat_session" not in st.session_state:  # Renamed for clarity
        st.session_state.chat_session = model.start_chat(history=[])

    # Display the chatbot's title on the page
    st.title("🤖 ChatBot")

    # Display the chat history
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # Input field for user's message
    user_prompt = st.chat_input("Ask bot...")  # Renamed for clarity
    if user_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)

        # Send user's message to Gemini-Pro and get the response
        gemini_response = st.session_state.chat_session.send_message(user_prompt)  # Renamed for clarity

        # Display Gemini-Pro's response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)

def text2speech(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"
    headers = {"Authorization": "Bearer *****************"}
    payload = {"inputs": text}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        # Assuming the response is an audio file
        audio_bytes = response.content
        return audio_bytes
    else:
        st.error("Failed to generate audio. Please try again.")
        return None

# Image captioning page
if selected == "Story Generator":

    st.title("📷 Snap Narrate")

    uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

    if st.button("Generate Story"):
        image = Image.open(uploaded_image)

        col1, col2 = st.columns(2)

        with col1:
            resized_img = image.resize((800, 500))
            st.image(resized_img)

        default_prompt = "write a short below 20 lines children story with morale for this image"  # change this prompt as per your requirement

        # get the caption of the image from the gemini-pro-vision LLM
        caption = gemini_pro_vision_response(default_prompt, image)

        with col2:
            st.info(caption)
            audio_bytes = text2speech(caption)
            st.audio(audio_bytes, format="audio/ogg")
     


# text embedding model
if selected == "Comic Generator":

    st.title("Generate a Comic")

    # text box to enter prompt
    user_prompt = st.text_area(label='', placeholder="Enter the story to generate comic...")

    if st.button("Get Response"):
        response = embeddings_model_response(user_prompt)
        st.markdown(response)


# text embedding model
if selected == "Video Generator":

    st.title("Generate a Video")

    # text box to enter prompt
    user_prompt = st.text_area(label='', placeholder="Enter the story to generate video...")

    if st.button("Get Response"):
        response = gemini_pro_response(user_prompt)
        st.markdown(response)
