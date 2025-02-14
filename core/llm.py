import os
import openai
import json
from django.utils import timezone
from datetime import timedelta

# Initialize OpenAI API key from environment
openai.api_key = os.environ.get("OPENAI_API_KEY")

def process_note_with_llm(raw_note: str):
    """
    Uses OpenAI's GPT API to extract actionable steps from a doctor's note.
    
    The prompt instructs GPT to return a JSON object with two keys: 'checklist' and 'plan'.
    - 'checklist': A list of immediate one-time tasks, each as a dict with 'description'.
    - 'plan': A list of scheduled actions, each as a dict with 'description' and 
      'scheduled_time_offset' (in days from now).

    The function then converts the scheduled_time_offset into an actual datetime value.
    """
    prompt = (
        "You are a medical assistant. Given the following doctor's note, extract actionable steps. "
        "Return a JSON object with two keys: 'checklist' and 'plan'. "
        "The 'checklist' should be a list of immediate one-time tasks, each with a 'description'. "
        "The 'plan' should be a list of scheduled actions, each with a 'description' and a 'scheduled_time_offset' (in days from now). "
        "Doctor's note: '''{}'''".format(raw_note)
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # use an appropriate model
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300,
        )
        answer = response.choices[0].message['content']
        
        # Attempt to parse the returned JSON.
        data = json.loads(answer)
        checklist = data.get("checklist", [])
        plan = data.get("plan", [])

        # Process plan items: convert scheduled_time_offset to actual scheduled datetime.
        processed_plan = []
        for item in plan:
            offset = item.get("scheduled_time_offset", 1)  # Default to 1 day if missing.
            scheduled_time = timezone.now() + timedelta(days=offset)
            processed_plan.append({
                "description": item.get("description", ""),
                "scheduled_time": scheduled_time
            })

        return checklist, processed_plan

    except Exception as e:
        # In case of error, log it and fallback to a simulated response.
        print("Error in LLM integration:", e)
        checklist = [{"description": "Buy prescribed drug"}]
        plan = [{
            "description": "Take drug daily for 7 days",
            "scheduled_time": (timezone.now() + timedelta(days=1))
        }]
        return checklist, plan
