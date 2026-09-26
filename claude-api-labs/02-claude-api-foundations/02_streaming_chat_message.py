import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

full_text = ""

with client.messages.stream(  # Python Context Manager — closes the stream on exit
  model="claude-haiku-4-5-20251001",
  max_tokens=1024,
  messages=[
    {"role": "user", "content": "Explain rainbow in 5 sentences."}
  ]
) as stream:
  for event in stream:
    if (event.type == "content_block_delta" and
        event.delta.type == "text_delta"):       # filter: text only, not tool/thinking
      full_text += event.delta.text
      print(event.delta.text, end="", flush=True)

final = stream.get_final_message()
print(f"\nStop Reason: {final.stop_reason}") # "end_turn" = complete  "max_tokens" = cut off
