from __future__ import annotations

from datetime import datetime


def get_today_date_str() -> str:
    return datetime.today().strftime("%Y-%m-%d")


def validate_date_text(value: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("날짜 형식은 YYYY-MM-DD 이어야 합니다.") from error


def validate_time_text(value: str) -> None:
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError as error:
        raise ValueError("시간 형식은 HH:MM 이어야 합니다. 예: 09:30") from error


def calculate_duration_minutes(start_time: str, end_time: str) -> int:
    validate_time_text(start_time)
    validate_time_text(end_time)

    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")

    minutes = int((end - start).total_seconds() // 60)
    if minutes <= 0:
        raise ValueError("종료 시간은 시작 시간보다 늦어야 합니다.")
    return minutes


def minutes_to_text(minutes: int) -> str:
    hours = minutes // 60
    remain = minutes % 60
    if hours and remain:
        return f"{hours}시간 {remain}분"
    if hours:
        return f"{hours}시간"
    return f"{remain}분"


def ask_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("값을 비워둘 수 없습니다.")


def ask_project_scope() -> str:
    while True:
        print("프로젝트 구분 선택:")
        print("1) 회사 프로젝트")
        print("2) 개인 프로젝트")
        choice = input("선택 [1]: ").strip() or "1"
        if choice == "1":
            return "회사"
        if choice == "2":
            return "개인"
        print("1 또는 2를 입력하세요.")


def ask_date(label: str, default: str | None = None) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        value = input(f"{label}{suffix}: ").strip()
        if not value and default:
            value = default
        try:
            validate_date_text(value)
            return value
        except ValueError as error:
            print(error)


def ask_time(label: str) -> str:
    while True:
        value = input(f"{label} (HH:MM): ").strip()
        try:
            validate_time_text(value)
            return value
        except ValueError as error:
            print(error)


def format_entry_line(entry) -> str:
    memo_text = f" / 메모: {entry.detail_memo}" if entry.detail_memo else ""
    return (
        f"{entry.start_time}~{entry.end_time} "
        f"({minutes_to_text(entry.duration_minutes)}) | "
        f"{entry.project_scope} | {entry.project} | {entry.category} | {entry.task} | {entry.tool}{memo_text}"
    )
