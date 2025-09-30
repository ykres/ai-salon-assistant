from __future__ import annotations
import json
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import load_config
from app.assistants import AssistantRunner
from app.thread_store import ThreadStore
from app.sheets_tool import SheetsClient


cfg = load_config()
threads = ThreadStore("data/web_threads.json")
runner = AssistantRunner(api_key=cfg.openai_api_key, assistant_id=cfg.openai_assistant_id)
sheets = SheetsClient(cfg.gsa_file, cfg.sheet_id, worksheet_title=cfg.sheet_worksheet)


def tool_dispatch(tc) -> str:
    # lightweight inline tool dispatcher for web
    if tc.name == "save_booking_data":
        args = tc.arguments or {}
        result = sheets.save_booking_data(
            name=args.get("name", ""),
            phone=args.get("phone", ""),
            service=args.get("service", ""),
            datetime=args.get("datetime", ""),
            master_category=args.get("master_category", ""),
            comments=args.get("comments", ""),
        )
        return json.dumps(result, ensure_ascii=False)
    return json.dumps({"error": f"Unknown tool: {tc.name}"}, ensure_ascii=False)


class StartResponse(BaseModel):
    sessionId: str


class MessageRequest(BaseModel):
    sessionId: str
    text: str


class MessageResponse(BaseModel):
    reply: str


app = FastAPI(title="Zerocode Chat Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat/start", response_model=StartResponse)
def chat_start() -> StartResponse:
    session_id = str(uuid.uuid4())
    thread_id = runner.create_thread()
    threads.set(session_id, thread_id)
    return StartResponse(sessionId=session_id)


@app.post("/chat/message", response_model=MessageResponse)
def chat_message(req: MessageRequest) -> MessageResponse:
    thread_id = threads.get(req.sessionId)
    if not thread_id:
        raise HTTPException(status_code=400, detail="Unknown sessionId. Call /chat/start first.")
    try:
        reply = runner.send_and_respond(thread_id, req.text, tool_dispatch)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return MessageResponse(reply=reply or "")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
