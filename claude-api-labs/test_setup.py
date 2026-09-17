import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=1024,
  system="You are a concise geography assistant.",
  messages=[
    {"role": "user", "content": "What is the capital of France?"}
  ]
)

print(response)

"""
Message(
  id='msg_xxxxxxxxxxxxxxxxxxxxxxxx',
  container=None,
  content=[TextBlock(citations=None, text='Paris is the capital of France.', type='text')],
  model='claude-haiku-4-5-20251001', 
  role='assistant',
  stop_details=None,
  stop_reason='end_turn',
  stop_sequence=None,
  type='message',
  usage=Usage(
    cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0),
    cache_creation_input_tokens=0,
    cache_read_input_tokens=0,
    inference_geo='not_available',
    input_tokens=22,
    output_tokens=10,
    output_tokens_details=None,
    server_tool_use=None,
    service_tier='standard'
  )
)
"""

for block in response.content:
  if block.type == "text":
    print(block.text)

print(response.stop_reason)
print(response.usage.input_tokens, response.usage.output_tokens)
