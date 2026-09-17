import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Explicit criteria live in the system prompt
system = """You are a security code reviewer.
flag: [
  "SQL injection via string concatenation",
  "Unvalidated user input in file paths",
  "Secrets hardcoded in source"
]
skip: [
  "TODO comments",
  "Style and formatting issues"
]
severity: {
  "critical": "Remotely exploitable, no auth required",
  "high": "Exploitable with valid user session"
}"""

user_content = """Review this:
def get_user(id):
  query = f'SELECT * FROM users WHERE id = {id}'
  return db.execute(query)
"""

response = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=1024,
  system=system,
  messages=[
    {"role": "user", "content": user_content}
  ]
)

for block in response.content:
  if block.type == "text":
    print(block.text)
