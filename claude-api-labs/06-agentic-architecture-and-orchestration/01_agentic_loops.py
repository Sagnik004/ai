import os
from dotenv import load_dotenv
import anthropic
from anthropic.types import ToolUnionParam, MessageParam
import logging

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ---------- Log Configs ----------
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("agent")


# ---------- Program Constants ----------
MODEL = "claude-haiku-4-5-20251001"
MAX_ITERATIONS = 10  # safety bound only; normal exit is stop_reason != "tool_use"


# ---------- Tool Definitions ----------
tools:list[ToolUnionParam] = [
  {
    "name": "calculator",
    "description": "Perform simple mathematical calculations and return results. Use this for any arithmetic operations including addition, subtraction, multiplication, division, and exponentiation.",
    "input_schema": {
      "type": "object",
      "properties": {
        "expression": {"type": "string"},
      },
      "required": ["expression"],
    },
  },
  {
    "name": "web_search",
    "description": "Executes a web search. Accepts a text query string and returns search results. Use this when web search is required with a query string.",
    "input_schema": {
      "type": "object",
      "properties": {
        "query": {"type": "string"},
      },
      "required": ["query"],
    },
  },
]


# ---------- Simulated Tool Implementations ----------
def calculator(expression: str) -> str:
  print(f"[🛠️ calculator_tool] Expression: {expression}")
  output = round(45000 * 0.01198, 2)
  return str(output)

def web_search(query: str) -> str:
  print(f"[🛠️ web_search_tool] Query: {query}")
  return (
    "Search results for: " + query + "\n"
    "1. Today's USD to INR exchange rate: 1 USD = 83.50 INR\n"
    "2. Currency converter: 1 INR = 0.01198 USD"
  )

TOOL_REGISTRY = {
  "calculator": calculator,
  "web_search": web_search,
}


# ---------- Execute Tool ----------
def execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
  """Returns (result_text, is_error)"""
  func = TOOL_REGISTRY.get(name)
  if func is None:
    return f"Unknown tool: {name}", True
  try:
    return func(**tool_input), False # ** = dictionary unpacking operator. Takes tool_input dict, extracts all of its key-value pairs, passes them into the function func as individual keyword arguments.
  except Exception as e:
    return f"Tool error: {e}", True


# ---------- Agentic loop ----------
def run_agent(user_prompt: str) -> None:
  print(f"👽 User Prompt: {user_prompt}")
  
  messages: list[MessageParam] = [{"role": "user", "content": user_prompt}]
  last_stop_reason: str | None = None
  
  for iteration in range(1, MAX_ITERATIONS + 1):
    logger.info("➰ Iteration %d/%d", iteration, MAX_ITERATIONS)

    response = client.messages.create(
      model=MODEL,
      max_tokens=1024,
      tools=tools,
      messages=messages
    )
    last_stop_reason = response.stop_reason

    # Always append the assistant's full turn (text + tool_use blocks)
    messages.append({"role": "assistant", "content": response.content})

    # If stop reason is tool_use, then execute each tool requested by model,
    # append the tool results as a single user message, and continue with the loop
    if last_stop_reason == "tool_use":
      tool_results = []
      for block in response.content:
        if block.type == "tool_use":
          print(f"[🛠️ tool_call] Tool_ID: {block.id}, Tool_Name: {block.name}, Tool_Input: {block.input}")
          output, is_error = execute_tool(block.name, block.input)
          print(f"[🛠️ tool_result] {output}\n")
          tool_results.append(
            {
              "type": "tool_result",
              "tool_use_id": block.id,
              "content": output,
              "is_error": is_error
            }
          )
        elif block.type == "text":
          print(f"🤖 {block.text}...")

      # All tool results go back in a single user message
      messages.append({"role": "user", "content": tool_results})
      continue

    # end_turn (or max_tokens, stop_sequence, etc.) -> we're done
    final_text = "".join(b.text for b in response.content if b.type == "text")
    print(f"[✅ final_answer]\n{final_text}")
    break
  else:
    # Runs only if the for-loop was exhausted without hitting 'break'
    logger.warning(
      "Agent stopped after reaching the safety cap of %d iterations "
      "without a final answer (last stop_reason=%s).",
      MAX_ITERATIONS,
      last_stop_reason,
    )

if __name__ == "__main__":
  run_agent("Look up the latest USD to INR exchange rate today, "
            "and calculate how much ₹45,000 is worth in US Dollars.")

# Output
"""
👽 User Prompt: Look up the latest USD to INR exchange rate today, and calculate how much ₹45,000 is worth in US Dollars.
2026-10-21 23:39:34,473 [INFO] ➰ Iteration 1/10
2026-10-21 23:39:36,116 [INFO] HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
🤖 I'll help you find the latest USD to INR exchange rate and convert ₹45,000 to US Dollars....
[🛠️ tool_call] Tool_ID: toolu_XXXXXXXXXXXXXXXXXXXXXXXX, Tool_Name: web_search, Tool_Input: {'query': 'USD to INR exchange rate today'}
[🛠️ web_search_tool] Query: USD to INR exchange rate today
[🛠️ tool_result] Search results for: USD to INR exchange rate today
1. Today's USD to INR exchange rate: 1 USD = 83.50 INR
2. Currency converter: 1 INR = 0.01198 USD

2026-10-21 23:39:36,128 [INFO] ➰ Iteration 2/10
2026-10-21 23:39:37,497 [INFO] HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
🤖 Great! Now let me calculate how much ₹45,000 is worth in US Dollars using the exchange rate....
[🛠️ tool_call] Tool_ID: toolu_XXXXXXXXXXXXXXXXXXXXXXXX, Tool_Name: calculator, Tool_Input: {'expression': '45000 * 0.01198'}
[🛠️ calculator_tool] Expression: 45000 * 0.01198
[🛠️ tool_result] 539.1

2026-10-21 23:39:37,498 [INFO] ➰ Iteration 3/10
2026-10-21 23:39:39,048 [INFO] HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
[✅ final_answer]
Perfect! Here are the results:

**Current Exchange Rate (Today):**
- 1 USD = 83.50 INR
- 1 INR = 0.01198 USD

**Conversion:**
₹45,000 = **$539.10 USD**

So ₹45,000 is worth approximately **$539.10 in US Dollars** at today's exchange rate.
"""
