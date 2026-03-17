from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from worklog_app.models import WorklogEntry


AUTO_SOURCE = "git-auto"


@dataclass
class RegisteredProject:
    name: str
    path: Path
    project_scope: str


def load_registered_projects(registry_path: str) -> list[RegisteredProject]:
    path = Path(registry_path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    projects: list[RegisteredProject] = []
    for item in data.get("personal_projects", []):
        projects.append(
            RegisteredProject(
                name=item["name"],
                path=Path(item["path"]),
                project_scope="개인",
            )
        )

    for item in data.get("company_projects", []):
        projects.append(
            RegisteredProject(
                name=item["name"],
                path=Path(item["path"]),
                project_scope="회사",
            )
        )

    return projects


def run_git_command(project_path: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def is_git_repository(project_path: Path) -> bool:
    result = run_git_command(project_path, ["rev-parse", "--is-inside-work-tree"])
    return result.returncode == 0 and result.stdout.strip() == "true"


def collect_today_commits(project_path: Path, work_date: str) -> list[tuple[str, str]]:
    result = run_git_command(
        project_path,
        [
            "log",
            "--since",
            f"{work_date} 00:00:00",
            "--until",
            f"{work_date} 23:59:59",
            "--pretty=format:%ad|%s",
            "--date=format:%H:%M",
        ],
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    commits: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if "|" not in line:
            continue
        time_text, subject = line.split("|", 1)
        commits.append((time_text.strip(), subject.strip()))
    return commits


def collect_changed_files(project_path: Path) -> list[str]:
    result = run_git_command(project_path, ["status", "--short"])
    if result.returncode != 0 or not result.stdout.strip():
        return []

    changed_files: list[str] = []
    for line in result.stdout.splitlines():
        file_path = line[3:] if len(line) > 3 else line
        changed_files.append(file_path.strip())
    return changed_files


def build_time_range(commits: list[tuple[str, str]], has_changes: bool) -> tuple[str, str]:
    if commits:
        start_time = commits[-1][0]
        end_time = commits[0][0]
        if start_time == end_time:
            return start_time, add_minutes(start_time, 30)
        return start_time, end_time

    if has_changes:
        return "09:00", "09:30"

    return "09:00", "09:30"


def add_minutes(time_text: str, minutes: int) -> str:
    time_value = datetime.strptime(time_text, "%H:%M")
    return (time_value + timedelta(minutes=minutes)).strftime("%H:%M")


def build_task_text(commits: list[tuple[str, str]], changed_files: list[str]) -> tuple[str, str]:
    task_parts: list[str] = []
    detail_lines: list[str] = []

    if commits:
        task_parts.append(f"오늘 커밋 {len(commits)}건")
        task_parts.extend(subject for _, subject in commits[:2])
        detail_lines.append("커밋:")
        detail_lines.extend(f"- {time_text} {subject}" for time_text, subject in commits)

    if changed_files:
        task_parts.append(f"변경 파일 {len(changed_files)}개")
        detail_lines.append("변경 파일:")
        detail_lines.extend(f"- {file_path}" for file_path in changed_files[:10])
        if len(changed_files) > 10:
            detail_lines.append(f"- 외 {len(changed_files) - 10}개")

    return " / ".join(task_parts), "\n".join(detail_lines)


def collect_auto_entries(work_date: str, registry_path: str) -> list[WorklogEntry]:
    entries: list[WorklogEntry] = []

    for project in load_registered_projects(registry_path):
        if not project.path.exists() or not is_git_repository(project.path):
            continue

        commits = collect_today_commits(project.path, work_date)
        changed_files = collect_changed_files(project.path)
        if not commits and not changed_files:
            continue

        start_time, end_time = build_time_range(commits, bool(changed_files))
        task_text, detail_text = build_task_text(commits, changed_files)
        entries.append(
            WorklogEntry(
                project_scope=project.project_scope,
                work_date=work_date,
                start_time=start_time,
                end_time=end_time,
                tool="Git",
                project=project.name,
                category="Git 자동 수집",
                task=task_text,
                detail_memo=detail_text,
                source=AUTO_SOURCE,
            )
        )

    return entries
