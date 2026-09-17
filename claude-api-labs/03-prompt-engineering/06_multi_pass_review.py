import os
from dotenv import load_dotenv
import anthropic
from anthropic.types import MessageParam

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

code = """
def process(data):
  result = eval(data['cmd'])
  return result
"""

# Base messages — used in EVERY pass unchanged
base_message: list[MessageParam] = [
  {"role": "user", "content": f"Review this code:\n```python\n{code}\n```"}
]

# Pass 1 — security lens, independent instance
pass1 = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=1024,
  system="You are a security auditor. Report only security vulnerabilities.",
  messages=base_message
)

security_report = None

if pass1.content[0].type == "text":
  security_report = pass1.content[0].text
  print(f"Security Findings: {security_report}")

# Pass 2 — logic lens, independent instance
pass2 = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=1024,
  system="You are a logic reviewer. Report only logic errors and edge cases.",
  messages=base_message
)

logic_report = None

if pass2.content[0].type == "text":
  logic_report = pass2.content[0].text
  print(f"Logical Findings: {logic_report}")

# Integration pass — receives findings, not raw code
integration = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=2048,
  system="Synthesize findings into a priority-ordered report.",
  messages=[{"role": "user", "content": f"Security: {security_report}\n\nLogic: {logic_report}"}]
)

if integration.content[0].type == "text":
  print(f"Final review: {integration.content[0].text}")
