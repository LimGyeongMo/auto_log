from __future__ import annotations

import json

from worklog_app.utils import minutes_to_text


def summarize_by_project(entries: list) -> dict[str, dict]:
    project_map: dict[str, dict] = {}

    for entry in entries:
        project_key = f"[{entry.project_scope}] {entry.project}"
        if project_key not in project_map:
            project_map[project_key] = {"minutes": 0, "tasks": []}

        project_map[project_key]["minutes"] += entry.duration_minutes
        project_map[project_key]["tasks"].append(entry.task)

    return project_map


def build_project_summary_text(entries: list) -> str:
    project_map = summarize_by_project(entries)
    lines: list[str] = []

    for project, data in project_map.items():
        task_text = ", ".join(data["tasks"])
        lines.append(f"{project} ({minutes_to_text(data['minutes'])}) - {task_text}")

    return "\n".join(lines)


def build_daily_summary_lines(
    entries: list,
    work_date: str,
    daily_summary: str,
    tomorrow_todo: str,
) -> list[str]:
    total_minutes = sum(entry.duration_minutes for entry in entries)
    project_map = summarize_by_project(entries)

    lines = [f"[{work_date} 업무 정리]", "", f"총 작업 시간: {minutes_to_text(total_minutes)}", ""]

    for index, (project, data) in enumerate(project_map.items(), start=1):
        lines.append(f"{index}. {project}")
        lines.append(f"- 작업 시간: {minutes_to_text(data['minutes'])}")
        lines.append("- 수행 업무:")
        for task in data["tasks"]:
            lines.append(f"  - {task}")
        lines.append("")

    lines.append(f"오늘 작업 요약: {daily_summary or '(미입력)'}")
    lines.append(f"내일 이어서 할 일: {tomorrow_todo or '(미입력)'}")
    return lines


def generate_report_text(
    entries: list,
    work_date: str,
    daily_summary: str,
    tomorrow_todo: str,
) -> str:
    return "\n".join(build_daily_summary_lines(entries, work_date, daily_summary, tomorrow_todo))


def build_raw_json_text(entries: list) -> str:
    return json.dumps([entry.to_dict() for entry in entries], ensure_ascii=False, indent=2)
