from __future__ import annotations

import json
from pathlib import Path

from worklog_app.models import WorklogEntry


class WorklogStorage:
    """JSON 파일 기반 저장소.

    나중에 Excel, DB, Markdown 저장소로 바꿔도
    CLI 쪽 코드는 최대한 그대로 둘 수 있게 클래스로 분리했다.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.entries = self._load()

    def _load(self) -> list[WorklogEntry]:
        if not self.file_path.exists():
            return []

        with self.file_path.open("r", encoding="utf-8") as file:
            raw_items = json.load(file)
        return [WorklogEntry.from_dict(item) for item in raw_items]

    def _save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump([entry.to_dict() for entry in self.entries], file, ensure_ascii=False, indent=2)

    def add_entry(self, entry: WorklogEntry) -> None:
        self.entries.append(entry)
        self._save()

    def get_entries_by_date(self, work_date: str) -> list[WorklogEntry]:
        return [entry for entry in self.entries if entry.work_date == work_date]
