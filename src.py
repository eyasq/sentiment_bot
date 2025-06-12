import os
import sys
import whisper
from dotenv import load_dotenv
import google.generativeai as genai
from prompt import CALL_ANALYSIS_PROMPT
model = whisper.load_model("turbo")
result=model.transcribe("test_audio/jawwal3.mp3", language="ar")
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model_name = 'gemini-1.5-flash-latest'

prompt = CALL_ANALYSIS_PROMPT.format(transcript=result['text'])

model = genai.GenerativeModel(model_name)
res = model.generate_content(prompt)
print(res.text)
print(f"\nPrompt tokens: {res.usage_metadata.prompt_token_count}")
print(f"\nResponse tokens: {res.usage_metadata.candidates_token_count}")

print(f"\n Actual call text: {result["text"]}")



