from __future__ import annotations
import json
import time
from typing import Any, Callable
from dataclasses import dataclass

from openai import OpenAI


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


def _extract_text_from_message(message: Any) -> str:
    # message.content is a list of content parts; we collect text parts
    parts = []
    for part in getattr(message, "content", []) or []:
        if getattr(part, "type", None) == "text":
            text = getattr(part, "text", None)
            if text and getattr(text, "value", None):
                parts.append(text.value)
    return "\n\n".join(parts).strip()


class AssistantRunner:
    def __init__(self, api_key: str, assistant_id: str):
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id

    def send_and_respond(
        self,
        thread_id: str,
        user_text: str,
        tool_dispatch: Callable[[ToolCall], str | dict[str, Any]],
        poll_interval: float = 0.8,
        max_wait_seconds: float = 120.0,
    ) -> str:
        # 1) Add user message
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_text,
        )

        # 2) Create run
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
        )

        # 3) Loop until completed or requires_action handled
        start_time = time.time()
        while True:
            if time.time() - start_time > max_wait_seconds:
                raise TimeoutError("Assistant run timed out")

            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )

            if run.status == "completed":
                break

            if run.status == "requires_action":
                tool_outputs = []
                for tc in run.required_action.submit_tool_outputs.tool_calls:
                    name = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    output_value = tool_dispatch(
                        ToolCall(id=tc.id, name=name, arguments=args)
                    )
                    if isinstance(output_value, (dict, list)):
                        output_str = json.dumps(output_value, ensure_ascii=False)
                    else:
                        output_str = str(output_value)

                    tool_outputs.append({
                        "tool_call_id": tc.id,
                        "output": output_str,
                    })

                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )

            elif run.status in {"queued", "in_progress", "cancelling"}:
                time.sleep(poll_interval)
            else:
                # failed, cancelled, or other terminal state
                raise RuntimeError(f"Assistant run ended with status: {run.status}")

        # 4) Fetch the latest assistant reply
        msgs = self.client.beta.threads.messages.list(thread_id=thread_id, limit=10)
        for msg in msgs.data:
            if msg.role == "assistant":
                text = _extract_text_from_message(msg)
                if text:
                    return text
        return ""

    def create_thread(self) -> str:
        t = self.client.beta.threads.create()
        return t.id
