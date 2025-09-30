import json
from pathlib import Path
from typing import Optional


class ThreadStore:
    """
    Very small on-disk mapping of Telegram chat_id -> OpenAI thread_id.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({})

    def _read(self) -> dict[str, str]:
        try:
            return json.loads(self.path.read_text() or "{}")
        except Exception:
            return {}

    def _write(self, data: dict[str, str]):
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def get(self, chat_id: int) -> Optional[str]:
        data = self._read()
        return data.get(str(chat_id))

    def set(self, chat_id: int, thread_id: str):
        data = self._read()
        data[str(chat_id)] = thread_id
        self._write(data)
