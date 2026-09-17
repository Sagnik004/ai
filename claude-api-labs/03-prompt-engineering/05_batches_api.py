import os
from dotenv import load_dotenv
import anthropic
from anthropic.types.messages import (
  MessageBatchCanceledResult,
  MessageBatchErroredResult,
  MessageBatchExpiredResult,
  MessageBatchSucceededResult,
)
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
from anthropic.types import TextBlock
import time

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Contents
input_1 = """
MUTUAL NON-DISCLOSURE AGREEMENT
This Agreement is entered into on September 16, 2026, between Acme Corp and Stark Industries. The parties wish to explore a potential business relationship. During this process, they may disclose proprietary "Confidential Information," including technical data, financial plans, and customer lists. The receiving party agrees to maintain strict confidentiality and protect this information using the same degree of care it uses for its own secrets, but no less than reasonable care. This obligation shall survive for a period of three (3) years from the date of disclosure.
"""

input_2 = """
EMPLOYMENT AGREEMENT: SECTION 9 (TERMINATION)
The Company may terminate Employee’s employment at any time without Cause by providing thirty (30) days' written notice or payment in lieu of notice. Upon termination, Employee shall receive all accrued, unpaid base salary up to the termination date. If Employee is terminated for "Cause" (including gross misconduct, fraud, or material breach of contract), the Company may terminate employment immediately without prior notice or severance. Upon termination for any reason, Employee must immediately return all company property, intellectual property, and confidential electronic files.
"""

# Phase 1: Submit — returns immediately
batch = client.messages.batches.create(
  requests=[
    Request(
      custom_id="doc-001", # correlate by id,
      params=MessageCreateParamsNonStreaming(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": f"Summarize: [{input_1}]"}]
      )
    ),
    Request(
      custom_id="doc-002",
      params=MessageCreateParamsNonStreaming(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": f"Summarize: [{input_2}]"}]
      ),
    ),
  ]
)

print("Submitted batch details:")

print(batch)
"""
MessageBatch(
  id='msgbatch_xxxxxxxxxxxxxxxxxxxxxxxx',
  archived_at=None,
  cancel_initiated_at=None,
  created_at=datetime.datetime(2026, 9, 16, 16, 59, 28, 837393, tzinfo=datetime.timezone.utc),
  ended_at=None,
  expires_at=datetime.datetime(2026, 9, 17, 16, 59, 28, 837393, tzinfo=datetime.timezone.utc),
  processing_status='in_progress',
  request_counts=MessageBatchRequestCounts(
    canceled=0, errored=0, expired=0, processing=2, succeeded=0
  ),
  results_url=None,
  type='message_batch'
)
"""

print() # for a line break
print(f"Submitted: {batch.id}, Status: {batch.processing_status}\n") # Submitted: msgbatch_xxxxxxxxxxxxxxxxxxxxxxxx, Status: in_progress

# Phase 2: Poll until processing_status == "ended"
status = client.messages.batches.retrieve(batch.id)
print(f"Current Status: {status.processing_status}") # in_progress

# Phase 3: Retrieve results when ended
while True:
  message_batch = client.messages.batches.retrieve(batch.id)

  if message_batch.processing_status == "ended": # processing complete
    for response in client.messages.batches.results(batch.id):
      result = response.result

      if isinstance(result, MessageBatchSucceededResult):
        output = "".join(
          block.text                          # Extract the text
          for block in result.message.content # From every content block
          if isinstance(block, TextBlock)     # But, only if it is a text block
        )
        print(f"Custom ID: {response.custom_id}, Output: {output}")
      elif isinstance(result, MessageBatchErroredResult):
        if result.error.error.type == "invalid_request_error":
          # Request body must be fixed before re-sending request
          print(f"Validation Error! Custom ID: {response.custom_id}")
        else:
          # Request can be retried directly
          print(f"Server Error! Custom ID: {response.custom_id}")
      elif isinstance(result, MessageBatchExpiredResult):
        print(f"Request Expired! Custom ID: {response.custom_id}")
      elif isinstance(result, MessageBatchCanceledResult):
        print(f"Request Canceled! Custom ID: {response.custom_id}")

    break

  print(f"Batch {batch.id} still processing...")
  time.sleep(60) # 60 seconds wait then check again
