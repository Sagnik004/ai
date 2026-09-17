import os
from dotenv import load_dotenv
import anthropic
from anthropic.types import MessageParam

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Example pairs are prepended before the real query
messages: list[MessageParam] = [
  # Example 1 — routine inquiry
  {"role": "user", "content": "How do I reset my password?"},
  {"role": "assistant", "content": "Category: account | Priority: low | Route: self-service"},
  # Example 2 — billing issue
  {"role": "user", "content": "I was charged twice this month"},
  {"role": "assistant", "content": "Category: billing | Priority: high | Route: billing-team"},
  # Real query — same format inferred from examples
  {"role": "user", "content": "My account is locked and I have a demo in 30 minutes"}
]

response = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=256,
  messages=messages
)

for block in response.content:
  if block.type == "text":
    print(block.text) # Category: account | Priority: urgent | Route: support-team
