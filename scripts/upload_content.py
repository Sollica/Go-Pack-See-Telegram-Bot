"""Заливает тексты (src/data/markdown) и картинки (src/data/images) в Supabase.

Запуск из корня проекта после любых правок текстов или картинок:
    uv run python scripts/upload_content.py
"""
import mimetypes
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_DIR = ROOT / "src" / "data" / "markdown"
IMAGES_DIR = ROOT / "src" / "data" / "images"
IMAGES_BUCKET = "images"


def main() -> None:
    """Загружает все Markdown-файлы в таблицу markdown и все картинки в хранилище images."""
    load_dotenv(ROOT / ".env")
    url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
    if not url or not key:
        sys.exit("SUPABASE_URL или SUPABASE_KEY не заданы в .env")
    client = create_client(url, key)

    rows = [
        {"kind": path.parent.name, "name": path.stem, "content": path.read_text(encoding="utf-8")}
        for path in sorted(MARKDOWN_DIR.glob("*/*.md"))
    ]
    client.table("markdown").upsert(rows).execute()
    print(f"Тексты: загружено {len(rows)}")

    bucket = client.storage.from_(IMAGES_BUCKET)
    images = sorted(p for p in IMAGES_DIR.iterdir() if p.is_file() and not p.name.startswith("."))
    for path in images:
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        bucket.upload(
            path=path.name,
            file=path.read_bytes(),
            file_options={"content-type": content_type, "upsert": "true"},
        )
        print(f"   {path.name}")
    print(f"Картинки: загружено {len(images)}")


if __name__ == "__main__":
    main()
