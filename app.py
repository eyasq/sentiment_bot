import os
import json
from dotenv import load_dotenv
import whisper
import google.generativeai as genai
import streamlit as st
from prompt import CALL_ANALYSIS_PROMPT
from reps_data import reps_data
import random
# Page config
st.set_page_config(page_title="Call Center Dashboard", page_icon="📞")

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not set. Please add it to your .env file or Streamlit secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
model_name = 'gemini-1.5-flash-latest'

# Cache models
@st.cache_resource
def load_whisper_model():
    """Load and cache Whisper model"""
    return whisper.load_model("turbo")

@st.cache_resource
def get_gemini_model():
    """Load and cache Gemini model"""
    return genai.GenerativeModel(model_name)

# Initialize models
try:
    whisper_model = load_whisper_model()
    gemini_model = get_gemini_model()
except Exception as e:
    st.error(f"Error loading models: {str(e)}")
    st.stop()

# Helper functions
def find_rep_by_id(rep_id):
    """Find representative by ID"""
    return next((r for r in reps_data if r['id'] == rep_id), None)

def get_sentiment_color(sentiment_score):
    """Get color based on sentiment score"""
    if sentiment_score >= 80:
        return "green"
    elif sentiment_score >= 60:
        return "orange"
    else:
        return "red"

def clean_json_response(response_text):
    """Clean JSON response by removing markdown code blocks and extra formatting"""
    # Remove markdown code blocks
    response_text = response_text.strip()
    
    # Remove ```json and ``` markers
    if response_text.startswith('```json'):
        response_text = response_text[7:]  # Remove ```json
    elif response_text.startswith('```'):
        response_text = response_text[3:]   # Remove ```
    
    if response_text.endswith('```'):
        response_text = response_text[:-3]  # Remove closing ```
    
    # Clean up any extra whitespace
    response_text = response_text.strip()
    
    return response_text

def parse_text_response(response_text):
    """Parse the text format response from Gemini into a structured format"""
    try:
        lines = response_text.strip().split('\n')
        parsed_data = {}
        key_issues = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Final Customer Sentiment:'):
                parsed_data['final_customer_sentiment'] = line.split(':', 1)[1].strip()
            elif line.startswith('Resolution Summary:'):
                parsed_data['resolution_summary'] = line.split(':', 1)[1].strip()
            elif line.startswith('Escalation Required:'):
                parsed_data['escalation_required'] = line.split(':', 1)[1].strip()
            elif line.startswith('[') and line.endswith(']') and line != '[Issue 1]' and line != '[Issue 2]':
                # Extract issues from brackets
                issue = line[1:-1].strip()
                if issue and not issue.startswith('Issue'):
                    key_issues.append(issue)
        
        if key_issues:
            parsed_data['key_issues'] = key_issues
        
        return parsed_data if parsed_data else None
    except Exception as e:
        print(f"Error parsing text response: {e}")
        return None

def safe_transcribe_audio(audio_file, whisper_model):
    """Safely transcribe audio with error handling"""
    try:
        # Create temp directory if it doesn't exist
        temp_dir = "/tmp"
        if not os.path.exists(temp_dir):
            temp_dir = "."  # Fallback to current directory
        
        temp_path = os.path.join(temp_dir, audio_file.name)
        
        with open(temp_path, "wb") as f:
            f.write(audio_file.getbuffer())
        
        result = whisper_model.transcribe(temp_path, language="ar")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return result
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

# Initialize session state
if 'selected_rep_id' not in st.session_state:
    st.session_state.selected_rep_id = None

# Query params for deep linking
params = st.query_params
url_rep_id = params.get("rep_id")

# Update session state from URL params
if url_rep_id and url_rep_id != st.session_state.selected_rep_id:
    st.session_state.selected_rep_id = url_rep_id

# Sidebar styling and navigation
st.sidebar.markdown("""
<style>
    .block-container { 
        padding-top: 5rem; 
        padding-bottom: 2rem;
    }
    .main .block-container {
        padding-top: 5rem;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
    }
    /* Sidebar title */
    .sidebar h1 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: 700;
        margin-bottom: 2rem;
    }
    /* Radio buttons styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stRadio > div > label {
        color: white !important;
        font-weight: 500;
        font-size: 1.1rem;
    }
    /* Radio button options */
    .stRadio div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        color: white !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        backdrop-filter: blur(5px) !important;
    }
    .stRadio div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
        transform: translateX(5px) !important;
    }
    .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background: rgba(255, 255, 255, 0.25) !important;
        border-color: #ffd700 !important;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3) !important;
        transform: translateX(5px) !important;
    }
    /* Hide radio circles */
    .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    /* Custom icons for navigation */
    .stRadio div[role="radiogroup"] > label:nth-child(1)::before {
        content: "🔊 ";
        margin-right: 8px;
    }
    .stRadio div[role="radiogroup"] > label:nth-child(2)::before {
        content: "📊 ";
        margin-right: 8px;
    }
    .stRadio div[role="radiogroup"] > label:nth-child(3)::before {
        content: "👤 ";
        margin-right: 8px;
    }
    /* Alerts and warnings */
    .stAlert {
        margin-top: 1rem;
        z-index: 999;
        position: relative;
    }
    div[data-testid="stAlert"] {
        z-index: 999;
        position: relative;
    }
    /* Main content area improvements */
    .main .block-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    /* Custom scrollbar for sidebar */
    .sidebar .sidebar-content::-webkit-scrollbar {
        width: 6px;
    }
    .sidebar .sidebar-content::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
    .sidebar .sidebar-content::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 3px;
    }
    .sidebar .sidebar-content::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("📞 Call Center Dashboard")

# Determine default page based on selected rep
default_page_index = 2 if st.session_state.selected_rep_id else 0
page = st.sidebar.radio("Navigate", ["Upload & Analyze", "Reps Overview", "Rep Profiles"], index=default_page_index)

# Clear selected rep when navigating away from profiles
if page != "Rep Profiles" and st.session_state.selected_rep_id:
    st.session_state.selected_rep_id = None
    st.query_params.clear()

# Upload & Analyze tab
if page == "Upload & Analyze":
    st.title("🔊 Upload and Analyze Call")
    
    # File uploader with better validation
    audio_file = st.file_uploader(
        "Upload audio file", 
        type=["mp3", "wav", "m4a", "mp4"],
        help="Supported formats: MP3, WAV, M4A, MP4"
    )

    if audio_file:
        # Display file info
        st.info(f"File: {audio_file.name} ({audio_file.size / 1024 / 1024:.2f} MB)")
        st.audio(audio_file)
        
        if st.button("🔄 Transcribe & Analyze", type="primary"):
            # Transcription
            with st.spinner("🎤 Transcribing with Whisper..."):
                result = safe_transcribe_audio(audio_file, whisper_model)
                
            if result:
                transcript = result.get('text', '')
                segments = result.get('segments', [])
                
                # Display transcript with confidence info
                st.subheader("📝 Transcript")
                st.write(transcript)
                
                if segments:
                    avg_confidence = sum(seg.get('avg_logprob', 0) for seg in segments) / len(segments)
                    st.info(f"Average confidence: {avg_confidence:.2f}")

                # Sentiment analysis
                if transcript.strip():
                    with st.spinner("🧠 Analyzing with Gemini..."):
                        try:
                            prompt = CALL_ANALYSIS_PROMPT.format(transcript=transcript)
                            response = gemini_model.generate_content(prompt)
                            sentiment_response = response.text.strip()

                            st.subheader("📊 Sentiment Analysis Result")
                            
                            # Clean the response to remove markdown formatting
                            clean_response = clean_json_response(sentiment_response)
                            
                            # Try to parse as JSON first
                            try:
                                parsed = json.loads(clean_response)
                                
                                # Display key metrics in columns
                                col1, col2, col3 = st.columns(3)
                                
                                if 'sentiment_score' in parsed:
                                    with col1:
                                        score = parsed['sentiment_score']
                                        color = get_sentiment_color(score)
                                        st.metric("Sentiment Score", f"{score}/100", delta=None)
                                        st.markdown(f"<div style='color: {color}'>●</div>", unsafe_allow_html=True)
                                
                                if 'outcome' in parsed:
                                    with col2:
                                        st.metric("Outcome", parsed['outcome'].title())
                                
                                if 'escalation_required' in parsed:
                                    with col3:
                                        risk = parsed['escalation_required']
                                        st.metric("Escalation Required", risk)
                                
                                # Full JSON display
                                with st.expander("View Full Analysis", expanded=True):
                                    st.json(parsed)
                                    
                            except json.JSONDecodeError:
                                # If JSON parsing fails, parse the text format
                                st.info("Received text format response. Parsing...")
                                parsed_data = parse_text_response(sentiment_response)
                                
                                if parsed_data:
                                    # Display parsed data
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        sentiment = parsed_data.get('final_customer_sentiment', 'Unknown')
                                        st.metric("Final Sentiment", sentiment)
                                    
                                    with col2:
                                        outcome = "resolved" if parsed_data.get('escalation_required', 'Yes') == 'No' else "unresolved"
                                        st.metric("Outcome", outcome.title())
                                    
                                    with col3:
                                        escalation = parsed_data.get('escalation_required', 'Unknown')
                                        st.metric("Escalation Required", escalation)
                                    
                                    # Show resolution summary
                                    if 'resolution_summary' in parsed_data:
                                        st.subheader("Resolution Summary")
                                        st.write(parsed_data['resolution_summary'])
                                    
                                    # Show key issues
                                    if 'key_issues' in parsed_data and parsed_data['key_issues']:
                                        st.subheader("Key Issues")
                                        for issue in parsed_data['key_issues']:
                                            st.write(f"• {issue}")
                                    
                                    # Show raw response in expander
                                    with st.expander("View Raw Response"):
                                        st.text(sentiment_response)
                                else:
                                    st.warning("Could not parse response. Raw output:")
                                    st.text(sentiment_response)

                            # Token usage info
                            if hasattr(response, 'usage_metadata'):
                                st.caption(f"Tokens used - Prompt: {response.usage_metadata.prompt_token_count}, Response: {response.usage_metadata.candidates_token_count}")
                        
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
                else:
                    st.warning("No transcript text found to analyze.")

# Reps Overview tab
elif page == "Reps Overview":
    st.title("📊 Call Center Reps Overview")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_reps = len(reps_data)
    total_calls = sum(len(rep['calls']) for rep in reps_data)
    avg_sentiment = sum(rep['sentiment_score'] for rep in reps_data) / total_reps if total_reps > 0 else 0
    total_escalations = sum(rep['escalations'] for rep in reps_data)
    
    with col1:
        st.metric("Total Reps", total_reps)
    with col2:
        st.metric("Total Calls", total_calls)
    with col3:
        st.metric("Avg Resolution", f"{avg_sentiment:.1f}")
    with col4:
        st.metric("Escalations", total_escalations)

    # Sorting options
    sort_by = st.selectbox("Sort by", ["Sentiment Score", "Call Volume", "Escalations"])
    
    if sort_by == "Sentiment Score":
        sorted_reps = sorted(reps_data, key=lambda r: r['sentiment_score'], reverse=True)
    elif sort_by == "Call Volume":
        sorted_reps = sorted(reps_data, key=lambda r: len(r['calls']), reverse=True)
    else:
        sorted_reps = sorted(reps_data, key=lambda r: r['escalations'], reverse=True)

    # Display reps in a more structured way
    for i, rep in enumerate(sorted_reps):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                sentiment_color = get_sentiment_color(rep['sentiment_score'])
                st.markdown(f"### {rep['name']}")

                # Progress bar for sentiment
                st.progress(rep['sentiment_score'] / 100)

                # Metrics in columns
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1:
                    st.markdown(f"**Resolution:** {rep['sentiment_score']}/100")
                with metric_col2:
                    st.markdown(f"**Calls:** {len(rep['calls'])}")
                with metric_col3:
                    st.markdown(f"**Escalations:** {rep['escalations']}")

                # Example churn rate (replace with real logic if available)
                churn_rate = random.choice([3, 5, 13, 12, 15]) if rep["name"] == "Liam Novak" else random.randint(1, 10)

                # Churn color coding
                if churn_rate >= 12:
                    churn_color = "red"
                    st.markdown(f"<div style='color:red;font-weight:bold;'>⚠️ Flagged for Review</div>", unsafe_allow_html=True)
                elif churn_rate >= 5:
                    churn_color = "orange"
                else:
                    churn_color = "green"

                st.markdown(
                    f"<div style='margin-top:8px;'>"
                    f"<strong>Churn Rate (month):</strong> "
                    f"<span style='color:{churn_color}; font-weight:bold;'>{churn_rate}%</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with col2:
                if st.button(f"👤 View Profile", key=f"view_{rep['id']}", type="secondary"):
                    st.session_state.selected_rep_id = rep['id']
                    st.query_params.update(rep_id=rep['id'])
                    st.rerun()

        if i < len(sorted_reps) - 1:
            st.divider()

# Rep Profiles tab
elif page == "Rep Profiles":
    rep_id = st.session_state.selected_rep_id
    
    if not rep_id:
        st.warning("⚠️ Please select a representative from the overview tab.")
        if st.button("← Go to Overview"):
            st.switch_page("Reps Overview")
    else:
        rep = find_rep_by_id(rep_id)
        
        if rep:
            # Header with back button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("← Back to Overview"):
                    st.session_state.selected_rep_id = None
                    st.query_params.clear()
                    st.rerun()
            
            with col2:
                st.title(f"👤 {rep['name']} - Profile")
            
            # Rep metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                sentiment_color = get_sentiment_color(rep['sentiment_score'])
                st.metric("Sentiment Score", f"{rep['sentiment_score']}/100")
            with col2:
                st.metric("Total Calls", len(rep['calls']))
            with col3:
                st.metric("Escalations", rep['escalations'])
            
            st.divider()
            
            # Recent calls section
            st.subheader("📞 Recent Calls")
            
            if rep['calls']:
                for i, call in enumerate(rep['calls']):
                    with st.expander(f"Call {i+1} - {call['date']} ({call['sentiment']['outcome'].title()})"):
                        # Call outcome badge
                        outcome = call['sentiment']['outcome']
                        badge_color = "green" if outcome == "resolved" else "red"
                        st.markdown(
                            f"**Status:** <span style='color:{badge_color}; font-weight: bold'>{outcome.upper()}</span>",
                            unsafe_allow_html=True
                        )
                        
                        # Transcript
                        st.text_area("Transcript", call['transcript'], height=120, key=f"transcript_{rep['id']}_{i}")
                        
                        # Sentiment analysis - using columns instead of nested expander
                        st.subheader("Sentiment Analysis")
                        
                        # Display key metrics in a structured way
                        if 'sentiment_score' in call['sentiment']:
                            sentiment_col1, sentiment_col2 = st.columns(2)
                            with sentiment_col1:
                                st.metric("Sentiment Score", f"{call['sentiment']['sentiment_score']}/100")
                            with sentiment_col2:
                                if 'escalation_risk' in call['sentiment']:
                                    st.metric("Escalation Risk", call['sentiment']['escalation_risk'].title())
                        
                        # Show full JSON in a code block instead of expander
                        st.subheader("Full Analysis")
                        st.json(call['sentiment'])
            else:
                st.info("No calls recorded for this representative.")
        else:
            st.error("❌ Representative not found. Please try selecting again from the overview tab.")
            if st.button("← Go to Overview"):
                st.session_state.selected_rep_id = None
                st.query_params.clear()
                st.rerun()