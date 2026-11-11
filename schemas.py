from typing import List

from pydantic import BaseModel


class ActionItem(BaseModel):
    task: str
    owner: str
    deadline: str
    priority: str  # High / Medium / Low


class MeetingSummary(BaseModel):
    summary: str
    decisions: List[str]
    action_items: List[ActionItem]
    open_questions: List[str]


def summary_to_markdown(r: MeetingSummary) -> str:
    """Readable version of the result, stored as the assistant message for follow-up chat."""
    lines = [f"**Summary:** {r.summary}", "", "**Decisions:**"]
    lines += [f"- {d}" for d in r.decisions] or ["- None"]
    lines += ["", "**Action items:**"]
    lines += [
        f"- {a.task} (owner: {a.owner}, deadline: {a.deadline}, priority: {a.priority})"
        for a in r.action_items
    ] or ["- None"]
    lines += ["", "**Open questions:**"]
    lines += [f"- {q}" for q in r.open_questions] or ["- None"]
    return "\n".join(lines)
