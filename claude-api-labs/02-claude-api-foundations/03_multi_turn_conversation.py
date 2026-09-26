import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# messages[] is the only memory the API has
messages = []

while True:
  user_input = input("You: ")
  if user_input.lower() in ("exit", "quit"):
    break

  # Step 1 — append user turn to history
  messages.append({"role": "user", "content": user_input})

  # Step 2 — stream the response (full history sent every time)
  reply = ""
  with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=messages # entire conversation history
  ) as stream:
    print("Claude: ", end="", flush=True)

    for event in stream:
      if (event.type == "content_block_delta" and
          event.delta.type == "text_delta"):
        reply += event.delta.text
        print(event.delta.text, end="", flush=True)

    print() # newline after reply

  # Step 3 — append assistant turn so the next call remembers it
  messages.append({"role": "assistant", "content": reply})
