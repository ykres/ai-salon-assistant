from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass
class Config:
    openai_api_key: str
    openai_assistant_id: str
    tg_bot_token: str
    gsa_email: str | None
    gsa_file: str
    sheet_id: str
    sheet_worksheet: str | None


def load_config() -> Config:
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_assistant_id = os.getenv("OPENAI_ASSISTANT_ID", "").strip()
    tg_bot_token = os.getenv("TG_BOT_TOKEN", "").strip()
    gsa_email = os.getenv("GOOGLE_SERVICE_ACCOUNT", "").strip() or None
    gsa_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()
    sheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "").strip()
    sheet_worksheet = os.getenv("GOOGLE_SHEETS_WORKSHEET", "").strip() or None

    missing = []
    if not openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not openai_assistant_id:
        missing.append("OPENAI_ASSISTANT_ID")
    if not tg_bot_token:
        missing.append("TG_BOT_TOKEN")
    if not gsa_file:
        missing.append("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not sheet_id:
        missing.append("GOOGLE_SHEETS_SPREADSHEET_ID")

    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return Config(
        openai_api_key=openai_api_key,
        openai_assistant_id=openai_assistant_id,
        tg_bot_token=tg_bot_token,
        gsa_email=gsa_email,
        gsa_file=gsa_file,
    sheet_id=sheet_id,
    sheet_worksheet=sheet_worksheet,
    )
