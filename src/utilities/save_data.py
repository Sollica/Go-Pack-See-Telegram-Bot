import asyncio
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiofiles

logger = logging.getLogger(__name__)

SUGGESTIONS_PATH = Path(__file__).resolve().parent.parent / "data" / "jsons" / "suggestions.jsonl"
BUG_REPORTS_PATH = SUGGESTIONS_PATH.parent / "bug_reports.jsonl"
write_lock = asyncio.Lock()


async def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    async with write_lock, aiofiles.open(path, "a", encoding="utf-8") as f:
        await f.write(line)


async def save_suggestion(user_id: int, username: str | None,  region_name: str | None, tour: str | None) -> None:
    await append_jsonl(
        SUGGESTIONS_PATH,
        {
            "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "user_id": user_id,
            "username": username,
            "region_name": region_name,
            "tour": tour or None,
        },
    )

async def save_bug_report(user_id: int, username: str | None, report: str | None) -> None:
    await append_jsonl(
        BUG_REPORTS_PATH,
        {
            "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "user_id": user_id,
            "username": username,
            "report": report,
        },
    )
