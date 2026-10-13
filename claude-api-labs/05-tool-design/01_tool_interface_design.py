import os
from dotenv import load_dotenv
import anthropic
from anthropic.types import ToolUnionParam

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

lookup_order_tool_def: ToolUnionParam = {
  "name": "lookup_order",
  "description": (         # primary selection signal — should be specific
    "Look up a customer order by ID or email. "
    "Use when asked about order status, shipping, or history. "
    "Example: 'where is order #5291' or 'what did I order last month'."
  ),
  "input_schema": {       # JSON Schema — required field
    "type": "object",
    "properties": {
      "identifier": {
        "type": "string",
        "description": "order ID (e.g. #5291) or customer email"
      },
    },
    "required": ["identifier"],
  },
}

response = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=1024,
  tools=[lookup_order_tool_def],
  tool_choice={"type": "auto"},        # Claude decides whether to call
  messages=[{"role": "user", "content": "Where is order #5291?"}]
)

# Claude returns tool_use when it selects a tool
if (response.stop_reason == "tool_use" and 
    response.content[0].type == "tool_use"):
  tool_block = response.content[0]
  print(f"Tool ID: {tool_block.id}") # toolu_XXXXXXXXXXXXXXXXXXXXXXXX
  print(f"Tool Name: {tool_block.name}") # lookup_order
  print(f"Tool Input: {tool_block.input}") # {'identifier': '#5291'}
