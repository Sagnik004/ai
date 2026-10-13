import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Structured result returned by an MCP tool after a failure (simulated)
tool_result = {
  "isError": True, # MCP spec — optional
  "content": [     # MCP spec — mandatory
    {
      "type": "text",
      "text": "Artifact upload blocked: missing s3:PutObject permission"
    }
  ],
  "errorCategory": "permission", # Our convention
  "isRetryable": False           # Our convention
}

response = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=512,
  system="You are a CI orchestrator. Given a tool result, decide: retry, skip, or escalate.",
  messages=[
    {"role": "user", "content": str(tool_result)}
  ]
)

if response.content[0].type == "text":
  print(response.content[0].text) # Escalate: permission errors are non-retryable, page on-call engineer
