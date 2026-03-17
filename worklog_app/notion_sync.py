from __future__ import annotations

import json
import traceback
from os import getenv

from dotenv import load_dotenv
from notion_client import Client

from worklog_app.report import build_project_summary_text, build_raw_json_text
from worklog_app.utils import minutes_to_text


load_dotenv()


def split_text_chunks(text: str, chunk_size: int = 1900) -> list[str]:
    """Notion rich_text는 길이 제한이 있어 적당히 잘라서 보낸다."""
    if not text:
        return [""]
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def rich_text_value(text: str) -> list[dict]:
    chunks = split_text_chunks(text)
    return [{"type": "text", "text": {"content": chunk}} for chunk in chunks]


def get_notion_client() -> Client:
    api_key = getenv("NOTION_API_KEY", "").strip()
    if not api_key:
        raise ValueError("NOTION_API_KEY 값이 없습니다. .env 파일을 확인하세요.")
    return Client(auth=api_key)


def get_data_source_id() -> str:
    data_source_id = getenv("NOTION_DATA_SOURCE_ID", "").strip()
    if not data_source_id:
        raise ValueError("NOTION_DATA_SOURCE_ID 값이 없습니다. .env 파일을 확인하세요.")
    return data_source_id


def get_work_items_data_source_id() -> str:
    return getenv("NOTION_WORK_ITEMS_DATA_SOURCE_ID", "").strip()


def build_notion_properties(
    entries: list,
    work_date: str,
    daily_summary: str,
    tomorrow_todo: str,
) -> dict:
    total_minutes = sum(entry.duration_minutes for entry in entries)
    project_summary = build_project_summary_text(entries)
    raw_json_text = build_raw_json_text(entries)

    return {
        "Name": {
            "title": [
                {
                    "type": "text",
                    "text": {"content": f"{work_date} 업무일지"},
                }
            ]
        },
        "Work Date": {"date": {"start": work_date}},
        "Total Minutes": {"number": total_minutes},
        "Total Time Text": {"rich_text": rich_text_value(minutes_to_text(total_minutes))},
        "Project Summary": {"rich_text": rich_text_value(project_summary)},
        "Daily Summary": {"rich_text": rich_text_value(daily_summary or "(미입력)")},
        "Tomorrow TODO": {"rich_text": rich_text_value(tomorrow_todo or "(미입력)")},
        "Raw JSON": {"rich_text": rich_text_value(raw_json_text)},
    }


def build_work_item_properties(entry) -> dict:
    return {
        "Task": {
            "title": [
                {
                    "type": "text",
                    "text": {"content": entry.task},
                }
            ]
        },
        "Work Date": {"date": {"start": entry.work_date}},
        "Duration": {"number": entry.duration_minutes},
        "Category": {"rich_text": rich_text_value(entry.category)},
        "Project": {"rich_text": rich_text_value(entry.project)},
        "Tool": {"rich_text": rich_text_value(entry.tool)},
        "Start Time": {"rich_text": rich_text_value(entry.start_time)},
        "End Time": {"rich_text": rich_text_value(entry.end_time)},
    }


def find_page_by_date(client: Client, data_source_id: str, work_date: str) -> dict | None:
    """같은 날짜 페이지가 있는지 먼저 찾는다.

    Notion 버전에 따라 `databases.query` 또는 `data_sources.query` 중
    하나가 사용될 수 있어 둘 다 시도한다.
    """
    query_filter = {
        "property": "Work Date",
        "date": {"equals": work_date},
    }

    try:
        response = client.databases.query(
            database_id=data_source_id,
            filter=query_filter,
        )
    except Exception:
        if not hasattr(client, "data_sources"):
            raise
        response = client.data_sources.query(
            data_source_id=data_source_id,
            filter=query_filter,
        )

    results = response.get("results", [])
    return results[0] if results else None


def create_page(client: Client, data_source_id: str, properties: dict) -> dict:
    try:
        return client.request(
            path="pages",
            method="POST",
            body={
                "parent": {"database_id": data_source_id},
                "properties": properties,
                "template": {"type": "default"},
            },
        )
    except Exception:
        try:
            if hasattr(client, "data_sources"):
                return client.request(
                    path="pages",
                    method="POST",
                    body={
                        "parent": {"data_source_id": data_source_id},
                        "properties": properties,
                        "template": {"type": "default"},
                    },
                )
        except Exception:
            pass

        try:
            return client.pages.create(parent={"database_id": data_source_id}, properties=properties)
        except Exception:
            if not hasattr(client, "data_sources"):
                raise
            return client.pages.create(parent={"data_source_id": data_source_id}, properties=properties)


def update_page(client: Client, page_id: str, properties: dict) -> dict:
    return client.pages.update(page_id=page_id, properties=properties)


def archive_page(client: Client, page_id: str) -> dict:
    return client.pages.update(page_id=page_id, archived=True)


def log_payload_debug(properties: dict) -> None:
    print("[DEBUG] Notion 속성 매핑 확인")
    print(json.dumps(properties, ensure_ascii=False, indent=2))


def log_work_items_debug(entries: list) -> None:
    print("[DEBUG] Notion 작업 상세 매핑 확인")
    payload = [build_work_item_properties(entry) for entry in entries]
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def find_work_item_pages_by_date(client: Client, data_source_id: str, work_date: str) -> list[dict]:
    query_filter = {
        "property": "Work Date",
        "date": {"equals": work_date},
    }

    try:
        response = client.databases.query(
            database_id=data_source_id,
            filter=query_filter,
            page_size=100,
        )
    except Exception:
        if not hasattr(client, "data_sources"):
            raise
        response = client.data_sources.query(
            data_source_id=data_source_id,
            filter=query_filter,
            page_size=100,
        )

    return response.get("results", [])


def sync_work_items_to_notion(client: Client, entries: list, work_date: str) -> None:
    data_source_id = get_work_items_data_source_id()
    if not data_source_id:
        print("[INFO] NOTION_WORK_ITEMS_DATA_SOURCE_ID 값이 없어 작업 상세 DB 저장은 건너뜁니다.")
        return

    log_work_items_debug(entries)

    existing_pages = find_work_item_pages_by_date(client, data_source_id, work_date)
    for page in existing_pages:
        archive_page(client, page["id"])

    for entry in entries:
        create_page(client, data_source_id, build_work_item_properties(entry))

    print(f"[INFO] 작업 상세 DB를 동기화했습니다. date={work_date}, items={len(entries)}")


def save_day_to_notion(
    entries: list,
    work_date: str,
    daily_summary: str,
    tomorrow_todo: str,
) -> bool:
    try:
        client = get_notion_client()
        data_source_id = get_data_source_id()
        properties = build_notion_properties(entries, work_date, daily_summary, tomorrow_todo)

        log_payload_debug(properties)
        existing_page = find_page_by_date(client, data_source_id, work_date)

        if existing_page:
            update_page(client, existing_page["id"], properties)
            print(f"[INFO] 기존 페이지를 업데이트했습니다. date={work_date}")
        else:
            create_page(client, data_source_id, properties)
            print(f"[INFO] 새 페이지를 생성했습니다. date={work_date}")

        sync_work_items_to_notion(client, entries, work_date)
        return True
    except Exception as error:
        print("[ERROR] Notion 저장 실패")
        print(f"[ERROR] 상세 메시지: {error}")
        print("[ERROR] 어떤 값이 잘못되었는지 확인할 수 있도록 payload를 위에 출력했습니다.")
        print(traceback.format_exc())
        return False
