EXTRACT_SYSTEM = """You turn raw meeting notes into structured output.
Rules:
- summary: 2-3 sentences.
- decisions: only decisions that were actually made.
- action_items: each needs task, owner, deadline, priority (High, Medium or Low).
  If owner or deadline is missing use "Unassigned" or "Not specified". Never invent them.
- open_questions: unresolved items."""

CHAT_SYSTEM = """You answer follow-up questions about a meeting.
Use only the meeting notes and summary in the conversation. If the answer is not there, say so.
Keep answers short."""

SAMPLE_NOTES = """Weekly sync - Product team
Priya said the login bug is fixed in staging, Rahul will verify and push to prod by Friday.
We decided to postpone the dashboard redesign to next sprint.
Amit needs to send the Q4 report to finance by Nov 20, it's urgent.
Someone should look at the slow search API, not sure who yet.
Open question: do we need a new analytics vendor?"""
