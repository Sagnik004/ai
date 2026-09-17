import os
from dotenv import load_dotenv
import anthropic
from anthropic.types import ToolUnionParam

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Define the schema as a tool
tools: list[ToolUnionParam] = [
  {
    "name": "extract_paper",
    "description": "Extract structured metadata from a research paper",
    "input_schema": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "authors": {"type": "array", "items": {"type": "string"}},
        "year": {"type": "integer"},
        "methodology": {
          "type": "string",
          # enum constrains to allowed values only
          "enum": ["quantitative", "qualitative", "mixed-methods"]
        }
      },
      "required": ["title", "authors", "year"]
    }
  }
]

response = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=1024,
  tools=tools,
  # Force the tool — guarantees schema compliance
  tool_choice={"type": "tool", "name": "extract_paper"},
  messages=[
    {"role": "user", "content": "Extract from: Smith & Lee (2023). Neural Scaling Laws. Nature AI. Mixed-methods study."}
  ]
)

"""
Message(
  id='msg_xxxxxxxxxxxxxxxxxxxxxxxx',
  container=None,
  content=[
    ToolUseBlock(
      id='toolu_xxxxxxxxxxxxxxxxxxxxxxxx',
      caller=DirectCaller(type='direct'),
      input={'title': 'Neural Scaling Laws', 'authors': ['Smith', 'Lee'], 'year': 2023, 'methodology': 'mixed-methods'},
      name='extract_paper',
      type='tool_use',
      toolset_name=None
    )
  ],
  model='claude-haiku-4-5-20251001',
  role='assistant',
  stop_details=None,
  stop_reason='tool_use',
  stop_sequence=None,
  type='message',
  usage=Usage(
    cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0),
    cache_creation_input_tokens=0,
    cache_read_input_tokens=0,
    inference_geo='not_available',
    input_tokens=740,
    output_tokens=95,
    output_tokens_details=None,
    server_tool_use=None,
    service_tier='standard'
  )
)
"""
# print(response)

print(response.stop_reason) # 🚨 stop_reason is "tool_use" — not "end_turn"

for block in response.content:
  if block.type == "tool_use":
    print(block.input) # Result: {'title': 'Neural Scaling Laws', 'authors': ['Smith', 'Lee'], 'year': 2023, 'methodology': 'mixed-methods'}
    print(block.name)  # Tool name: extract_paper
