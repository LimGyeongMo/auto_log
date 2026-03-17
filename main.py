import argparse

from worklog_app.models import WorklogEntry
from worklog_app.notion_sync import save_day_to_notion
from worklog_app.report import (
    build_daily_summary_lines,
    generate_report_text,
    summarize_by_project,
)
from worklog_app.storage import WorklogStorage
from worklog_app.utils import (
    ask_date,
    ask_non_empty,
    ask_project_scope,
    ask_time,
    format_entry_line,
    get_today_date_str,
    minutes_to_text,
)


def print_menu() -> None:
    print("\n==== 업무기록 프로그램 ====")
    print("1) 작업 입력")
    print("2) 오늘 작업 보기")
    print("3) 날짜별 작업 보기")
    print("4) 일일 보고서 생성")
    print("5) Notion에 저장")
    print("6) 종료")


def input_work_entry(storage: WorklogStorage) -> None:
    print("\n[작업 입력]")

    project_scope = ask_project_scope()
    work_date = ask_date("날짜", default=get_today_date_str())
    start_time = ask_time("시작 시간")
    end_time = ask_time("종료 시간")
    tool = ask_non_empty("사용 툴 (Android Studio / VS Code / 기타): ")
    project = ask_non_empty("프로젝트명: ")
    category = ask_non_empty("작업 카테고리: ")
    task = ask_non_empty("작업 내용: ")
    detail_memo = input("상세 메모: ").strip()

    try:
        entry = WorklogEntry(
            project_scope=project_scope,
            work_date=work_date,
            start_time=start_time,
            end_time=end_time,
            tool=tool,
            project=project,
            category=category,
            task=task,
            detail_memo=detail_memo,
        )
    except ValueError as error:
        print(f"입력 오류: {error}")
        return

    storage.add_entry(entry)
    print(f"저장 완료: {project_scope} / {project} / {task} / {minutes_to_text(entry.duration_minutes)}")


def show_entries_for_date(storage: WorklogStorage, work_date: str) -> None:
    entries = storage.get_entries_by_date(work_date)
    if not entries:
        print(f"\n{work_date} 데이터가 없습니다.")
        return

    print(f"\n[{work_date} 작업 목록]")
    for index, entry in enumerate(entries, start=1):
        print(f"{index}. {format_entry_line(entry)}")

    total_minutes = sum(entry.duration_minutes for entry in entries)
    print(f"\n총 작업 시간: {minutes_to_text(total_minutes)}")

    project_totals = summarize_by_project(entries)
    print("\n[프로젝트별 합산]")
    for project, data in project_totals.items():
        print(f"- {project}: {minutes_to_text(data['minutes'])}")


def create_daily_report(storage: WorklogStorage, work_date: str) -> str | None:
    entries = storage.get_entries_by_date(work_date)
    if not entries:
        print(f"\n{work_date} 데이터가 없습니다.")
        return None

    print(f"\n[{work_date} 업무 요약 입력]")
    daily_summary = input("오늘 작업 요약: ").strip()
    tomorrow_todo = input("내일 이어서 할 일: ").strip()

    report_text = generate_report_text(entries, work_date, daily_summary, tomorrow_todo)
    print("\n===== 일일 보고서 =====")
    print(report_text)
    return report_text


def save_to_notion(storage: WorklogStorage) -> None:
    print("\n[Notion 저장]")
    work_date = ask_date("저장할 날짜", default=get_today_date_str())
    entries = storage.get_entries_by_date(work_date)
    if not entries:
        print(f"{work_date} 데이터가 없습니다.")
        return

    daily_summary = input("오늘 작업 요약: ").strip()
    tomorrow_todo = input("내일 이어서 할 일: ").strip()

    preview_lines = build_daily_summary_lines(entries, work_date, daily_summary, tomorrow_todo)
    print("\n===== Notion 전송 미리보기 =====")
    print("\n".join(preview_lines))

    answer = input("\nNotion에 저장할까요? (y/n): ").strip().lower()
    if answer != "y":
        print("저장을 취소했습니다.")
        return

    success = save_day_to_notion(entries, work_date, daily_summary, tomorrow_todo)
    if success:
        print("Notion 저장이 완료되었습니다.")
    else:
        print("Notion 저장에 실패했습니다. 위 로그를 확인하세요.")


def save_to_notion_direct(storage: WorklogStorage, work_date: str) -> None:
    """메뉴를 거치지 않고 바로 Notion 저장을 실행한다."""
    entries = storage.get_entries_by_date(work_date)
    if not entries:
        print(f"{work_date} 데이터가 없습니다.")
        return

    print(f"\n[{work_date} Notion 바로 저장]")
    daily_summary = input("오늘 작업 요약: ").strip()
    tomorrow_todo = input("내일 이어서 할 일: ").strip()

    preview_lines = build_daily_summary_lines(entries, work_date, daily_summary, tomorrow_todo)
    print("\n===== Notion 전송 미리보기 =====")
    print("\n".join(preview_lines))

    answer = input("\n바로 Notion에 저장할까요? (y/n): ").strip().lower()
    if answer != "y":
        print("저장을 취소했습니다.")
        return

    success = save_day_to_notion(entries, work_date, daily_summary, tomorrow_todo)
    if success:
        print("Notion 저장이 완료되었습니다.")
    else:
        print("Notion 저장에 실패했습니다. 위 로그를 확인하세요.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="로컬 업무기록 CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("notion-save", help="메뉴 없이 오늘 날짜로 바로 Notion 저장")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    storage = WorklogStorage("worklog.json")

    if args.command == "notion-save":
        save_to_notion_direct(storage, get_today_date_str())
        return

    while True:
        print_menu()
        choice = input("메뉴 선택: ").strip()

        if choice == "1":
            input_work_entry(storage)
        elif choice == "2":
            show_entries_for_date(storage, get_today_date_str())
        elif choice == "3":
            work_date = ask_date("조회할 날짜", default=get_today_date_str())
            show_entries_for_date(storage, work_date)
        elif choice == "4":
            work_date = ask_date("보고서 날짜", default=get_today_date_str())
            create_daily_report(storage, work_date)
        elif choice == "5":
            save_to_notion(storage)
        elif choice == "6":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 메뉴입니다. 1~6 중에서 선택하세요.")


if __name__ == "__main__":
    main()
