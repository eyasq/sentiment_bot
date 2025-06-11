import os
from dotenv import load_dotenv
import whisper
import google.generativeai as genai
import streamlit as st
from prompt import CALL_ANALYSIS_PROMPT

# Early Streamlit config: must be first Streamlit command
st.set_page_config(page_title="Audio Sentiment Analysis", page_icon="🔊")

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not set. Please add it to your .env file or Streamlit secrets.")
    st.stop()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model_name = 'gemini-1.5-flash-latest'

# Cache Whisper model to avoid reloading on every run
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("turbo")

# Cache Gemini client
@st.cache_resource
def get_gemini_model():
    return genai.GenerativeModel(model_name)

# Initialize models
whisper_model = load_whisper_model()
gemini_model = get_gemini_model()

# Streamlit UI
st.title("🔊→📝→😊 Audio Sentiment Analysis")

# File uploader
audio_file = st.file_uploader(
    "Upload an audio file (mp3, wav, m4a, mp4)",
    type=["mp3", "wav", "m4a", "mp4"]
)

if audio_file:
    st.audio(audio_file)
    if st.button("Transcribe & Analyze"):
        with st.spinner("Transcribing audio with Whisper..."):
            # Whisper expects a path or file-like. Save temp.
            temp_path = os.path.join("/tmp", audio_file.name)
            with open(temp_path, "wb") as f:
                f.write(audio_file.getbuffer())
            result = whisper_model.transcribe(temp_path, language="ar")  # adjust language if needed
            transcript = result.get('text', '')

        st.subheader("Transcript")
        st.write(transcript)

        with st.spinner("Analyzing sentiment with Gemini..."):
            prompt = CALL_ANALYSIS_PROMPT.format(transcript=transcript)
            response = gemini_model.generate_content(prompt)
            sentiment_json = response.text

        st.subheader("Sentiment Analysis Result")
        # Attempt to parse JSON
        try:
            import json
            parsed = json.loads(sentiment_json)
            st.json(parsed)
        except Exception:
            st.text(sentiment_json)

        # Show token usage
        st.text(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        st.text(f"Response tokens: {response.usage_metadata.candidates_token_count}")

# Footer
st.markdown("---")
st.caption("Built with Whisper, Gemini, and Streamlit")
