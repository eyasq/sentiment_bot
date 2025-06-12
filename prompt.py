CALL_ANALYSIS_PROMPT = """
You are an expert AI assistant tasked with analyzing customer service call transcripts. Your primary goal is to understand the full context of the conversation, from the initial problem to the final resolution.

Analyze the following customer call transcript and provide your analysis in STRICT JSON format only.

Customer Call Transcript:
{transcript}

Guidelines for analysis:

Final Customer Sentiment: Determine the customer's emotional state **at the end of the call**. This is the most important sentiment metric.

Resolution Summary: Briefly describe the action the agent took that led to the final sentiment.

Key Issues Mentioned: Identify the core reasons the customer initially contacted support.

Escalation Required: Flag a call as 'Yes' only if the issue remains unresolved at the end of the call. An issue is considered resolved if the agent provides a solution (like a credit, a refund, or a successful explanation) and the customer's final sentiment is Positive or Neutral.

Specifically, flag as 'Yes' if:
- The agent is unable to resolve the issue.
- The customer is still audibly dissatisfied or angry at the end of the call.
- The customer explicitly requests to speak with a manager and the issue is not resolved.
- The issue requires an action that was not confirmed as completed during the call (e.g., "a technical team will call you back").

Do not flag for escalation if the customer was initially angry but was successfully de-escalated and satisfied by the agent's solution.

IMPORTANT: Return ONLY valid JSON in this exact format. Do not include any other text:

{{
    "final_customer_sentiment": "Positive|Neutral|Negative|Mixed",
    "sentiment_score": 85,
    "resolution_summary": "Brief one-sentence summary of resolution",
    "key_issues": [
        "Issue 1",
        "Issue 2"
    ],
    "escalation_required": "Yes|No",
    "outcome": "resolved|unresolved"
}}

The sentiment_score should be a number from 0-100 where:
- 0-30: Very Negative
- 31-50: Negative  
- 51-70: Neutral
- 71-85: Positive
- 86-100: Very Positive
"""