# Issue Detection from Call Centre Voice Conversations: A Solution for Churn Solution, built in SPARK's 2025 Hackathon

**Installation**

**1. Install core dependencies:**

```bash
pip install -r requirements.txt
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**2. Download Whisper model:**

The application uses the Whisper "turbo" model for audio transcription. Download it by running:

```bash
python3 -c "import whisper; whisper.load_model('turbo')"
```

This will automatically download and cache the model (~1.5GB) to your system.

**3. Obtain Google Gemini API Key:**

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

**4. Set up environment variables:**

Create a `.env` file in the project root:

```bash
touch .env
```

Add your API key to the `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

**Verify it works**

Test in a fresh venv:

```bash
python3 -m venv testenv
source testenv/bin/activate
pip install -r requirements.txt
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Download Whisper model
python3 -c "import whisper; whisper.load_model('turbo')"

# Set up your .env file with GEMINI_API_KEY
# Then run the app
streamlit run app.py
```

### Main Page:
![Main Page Screenshot](https://files.catbox.moe/sdcvav.png)