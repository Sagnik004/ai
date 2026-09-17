import os
from dotenv import load_dotenv
import anthropic
from anthropic.types import MessageParam

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initial request
notes = "In this brief meeting excerpt, John reviews the Q3 marketing budget and notes that increased spending has not resulted in higher sales conversions. Sarah explains that funds were redirected toward brand awareness, prompting John to request a revised, lead-generation-focused plan by Friday."
messages: list[MessageParam] = [
  {"role": "user", "content": f"Summarize these meeting notes: [{notes}]"}
]
MAX_RETRIES = 2

# Final output
result = ""

for attempt in range(MAX_RETRIES + 1):
  response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=messages
  )

  if response.content[0].type == "text":
    text = response.content[0].text

    # Our code validates — not Claude
    if "action items:" in text.lower():
      result = text
      break  # passed — done

    if attempt == MAX_RETRIES:
      result = "Summarization aborted, no action item found"
      break  # hard cap — stop regardless

    # Append attempt + specific feedback to messages[]
    messages.append({"role": "assistant", "content": text})
    messages.append({"role": "user", "content": "Missing required section: add 'Action items:' with owner and deadline for each task."})
  else:
    result = "Summarization aborted, response context non-text type"
    break  # Response type non-text

print(result)
