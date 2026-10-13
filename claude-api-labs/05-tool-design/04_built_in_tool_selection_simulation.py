import os
from dotenv import load_dotenv
import anthropic
from anthropic.types import ToolUnionParam

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

tools:list[ToolUnionParam] = [
  {
    "name": "Grep",
    "description": "Search inside file contents for a pattern.",
    "input_schema": {
      "type": "object",
      "properties": {
        "pattern": {"type": "string"}
      },
      "required": ["pattern"],
    },
  },
  {
    "name": "Glob",
    "description": "Find files by name or path pattern. Never reads file contents.",
    "input_schema": {
      "type": "object",
      "properties": {
        "pattern": {"type": "string"}
      },
      "required": ["pattern"]
    },
  },
]

response = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=512,
  tools=tools,
  messages=[
    {"role": "user", "content": "Find every file that imports createStore"}
  ]
)

for block in response.content:
  if block.type == "tool_use":
    print(f"Tool ID: {block.id}") # toolu_XXXXXXXXXXXXXXXXXXXXXXXX
    print(f"Tool Name: {block.name}") # Grep
    print(f"Tool Input: {block.input}") # {'pattern': 'import.*createStore'}
    # Now OUR code runs the actual grep — Claude never touches the filesystem
  elif block.type == "text":
    print(f"Context text: {block.text}") # I'll search for files that import createStore.
