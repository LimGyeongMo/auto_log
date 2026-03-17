from __future__ import annotations

from dataclasses import asdict, dataclass

from worklog_app.utils import calculate_duration_minutes, validate_date_text


@dataclass
class WorklogEntry:
    """하나의 작업 기록을 표현하는 가장 기본 데이터 객체."""

    project_scope: str
    work_date: str
    start_time: str
    end_time: str
    tool: str
    project: str
    category: str
    task: str
    detail_memo: str = ""

    def __post_init__(self) -> None:
        if self.project_scope not in {"개인", "회사"}:
            raise ValueError("프로젝트 구분은 '개인' 또는 '회사'여야 합니다.")
        validate_date_text(self.work_date)
        self.duration_minutes = calculate_duration_minutes(self.start_time, self.end_time)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["duration_minutes"] = self.duration_minutes
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "WorklogEntry":
        return cls(
            project_scope=data.get("project_scope", "회사"),
            work_date=data["work_date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            tool=data["tool"],
            project=data["project"],
            category=data["category"],
            task=data["task"],
            detail_memo=data.get("detail_memo", ""),
        )
