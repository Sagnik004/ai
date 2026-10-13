import os
from dotenv import load_dotenv
import anthropic
from anthropic.types import ToolUnionParam

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# MCP tool definition — matches what .mcp.json declares for the github server
github_tool: ToolUnionParam = {
  "name": "list_pull_requests",
  "description": "List open pull requests for a repo on the GitHub MCP server",
  "input_schema": {
    "type": "object",
    "properties": {
      "repo": {"type": "string", "description": "Repository name"},
      "reviewer": {"type": "string"}
    },
    "required": ["repo"],
  },
}

response = client.messages.create(
  model="claude-haiku-4-5-20251001",
  max_tokens=1024,
  tools=[github_tool],
  messages=[
    {
      "role": "user",
      "content": "Show PRs waiting for my review in auth-service. My GitHub username is Sagnik004 and repository is eshop"
    }
  ]
)

# Claude returns tool_use when it selects a tool
if (response.stop_reason == "tool_use" and
    response.content[0].type == "tool_use"):
  tool_block = response.content[0]
  # tool_block.input contains the extracted arguments — our code calls the MCP server
  print(f"Tool ID: {tool_block.id}") # toolu_XXXXXXXXXXXXXXXXXXXXXXXX
  print(f"Tool Name: {tool_block.name}") # list_pull_requests
  print(f"Tool Input: {tool_block.input}") # {'repo': 'eshop', 'reviewer': 'Sagnik004'}
elif (response.stop_reason == "end_turn" and 
      response.content[0].type == "text"):
  content_block = response.content[0]
  print(f"Context text: {content_block.text}") # I'd be happy to help you see the PRs waiting for your review in auth-service. However, I need to know your GitHub username to filter for PRs where you're a reviewer.
