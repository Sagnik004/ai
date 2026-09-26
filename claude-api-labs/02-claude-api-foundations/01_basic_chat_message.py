import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create( # synchronous — waits for the full reply
  model="claude-haiku-4-5-20251001", # required, no default
  max_tokens=1024, # required, caps output length
  system="You are a concise geography assistant.", # optional — sets Claude's persona/rules
  messages=[
    {"role": "user", "content": "What is the capital of France?"}
  ]
)

if response.content[0].type == "text":
  print(f"Response text: {response.content[0].text}") # text reply is always at index 0

print(f"Stop reason: {response.stop_reason}") # "end_turn" = complete · "max_tokens" = truncated
print(f"Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}")
