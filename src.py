import os
import sys
import whisper
from dotenv import load_dotenv
from google import genai
model = whisper.load_model("turbo")
result=model.transcribe("test_audio/jawwal.mp3", language="ar")
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
model = 'gemini-1.5-flash-latest'
prompt = f"""
You are an AI assistant tasked with analyzing customer service call transcripts. Your goal is to provide a concise summary of the customer's sentiment, identify key issues, and flag any calls requiring escalation or follow-up.

Analyze the following customer call transcript and provide the following output:

Overall customer sentiment: [Positive/Neutral/Negative]
Key issues or topics mentioned:

[Issue 1]

[Issue 2]

[Issue 3] (List up to 5, or fewer if not applicable)
Escalation or follow-up required: [Yes/No]

Customer Call Transcript:
{result['text']}

Guidelines for analysis:

Overall customer sentiment: Determine the primary emotional tone of the customer throughout the call.

Positive: Customer expresses satisfaction, gratitude, or a generally happy demeanor.

Neutral: Customer's tone is factual, unemotional, or neither overtly positive nor negative.

Negative: Customer expresses frustration, anger, disappointment, or dissatisfaction.

Key issues or topics mentioned: Identify the core reasons the customer contacted support. Focus on concrete problems or subjects discussed. Examples: 'late delivery,' 'billing issue,' 'poor service,' 'technical problem,' 'product inquiry,' 'account update.'

Escalation or follow-up required: Flag a call as 'Yes' if:

The customer explicitly requests to speak with a manager or higher authority.

The agent is unable to resolve the issue during the call.

The customer expresses extreme dissatisfaction, threatens to churn, or indicates a significant, unresolved problem.

The issue requires action outside of the current call (e.g., a refund processing, a technical team to investigate).

There is any ambiguity or uncertainty about the resolution.

Ensure your output strictly adheres to the requested format. Do not include any additional commentary or conversational text.
    """

res = client.models.generate_content(model=model, contents=prompt)
print(res.text)
print(f"\nPrompt tokens: {res.usage_metadata.prompt_token_count}")
print(f"\nResponse tokens: {res.usage_metadata.candidates_token_count}")

print(f"\n Actual call text: {result["text"]}")



