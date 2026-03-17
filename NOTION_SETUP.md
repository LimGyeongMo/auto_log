# Notion 연동 가이드

이 문서는 `worklog` CLI 프로그램을 개인 Notion 데이터베이스와 연결하는 방법을 설명합니다.

## 1. Notion Integration 만들기

1. Notion Developers 페이지에 접속합니다.
2. 새 integration을 생성합니다.
3. 생성 후 발급된 API 키를 복사합니다.

이 값은 나중에 `.env` 파일의 `NOTION_API_KEY`에 넣습니다.

## 2. Notion 데이터베이스 만들기

Notion에서 요약용 데이터베이스를 만들고 아래 속성명을 정확히 맞춥니다.

- `Name` : Title
- `Work Date` : Date
- `Total Minutes` : Number
- `Total Time Text` : Rich text
- `Project Summary` : Rich text
- `Daily Summary` : Rich text
- `Tomorrow TODO` : Rich text
- `Raw JSON` : Rich text

속성명이 다르면 현재 코드와 매핑되지 않아 저장에 실패할 수 있습니다.

작업 상세를 별도 DB에 저장하려면 두 번째 데이터베이스를 추가로 만들 수 있습니다.

- `Task` : Title
- `Work Date` : Date
- `Duration` : Number
- `Category` : Rich text
- `Project` : Rich text
- `Tool` : Rich text
- `Start Time` : Rich text
- `End Time` : Rich text

이 두 번째 DB는 선택 사항이며, `.env`에 `NOTION_WORK_ITEMS_DATA_SOURCE_ID`를 넣었을 때만 사용합니다.

## 3. 데이터베이스를 Integration에 공유하기

이 단계가 빠지면 API 호출이 실패합니다.

1. Notion에서 만든 데이터베이스 페이지를 엽니다.
2. 우측 상단의 공유 메뉴를 엽니다.
3. 방금 만든 integration을 초대하거나 연결합니다.

## 4. 데이터베이스 ID 확인하기

데이터베이스 페이지 URL에서 ID를 확인할 수 있습니다.

예시:

```text
https://www.notion.so/workspace/abcde12345f67890abcde12345f67890?v=...
```

위 URL이라면 아래 값이 데이터베이스 ID 후보입니다.

```text
abcde12345f67890abcde12345f67890
```

요약 DB의 ID는 `.env` 파일의 `NOTION_DATA_SOURCE_ID`에 넣습니다.

작업 상세 DB를 만들었다면 그 ID는 `.env` 파일의 `NOTION_WORK_ITEMS_DATA_SOURCE_ID`에 넣습니다.

## 5. .env 파일 만들기

프로젝트 루트에서 `.env.example`을 참고해 `.env` 파일을 만듭니다.

예시:

```env
NOTION_API_KEY=secret_xxx
NOTION_DATA_SOURCE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_WORK_ITEMS_DATA_SOURCE_ID=yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

## 6. 패키지 설치 및 실행

```bash
pip install -r requirements.txt
python main.py
```

메뉴에서 `5) Notion에 저장`을 선택하면 됩니다.

## 7. 저장 방식

- 하루 단위로 Notion 페이지 1개를 사용합니다.
- 같은 날짜 페이지가 있으면 먼저 검색한 뒤 업데이트합니다.
- 없으면 새 페이지를 생성합니다.
- 전송 전에 콘솔에서 미리보기를 보여줍니다.
- `NOTION_WORK_ITEMS_DATA_SOURCE_ID`가 있으면 같은 날짜의 작업 상세 row도 별도 DB에 동기화합니다.

## 8. 자주 발생하는 오류

### 1) `.env` 값이 비어 있는 경우

- `NOTION_API_KEY` 누락
- `NOTION_DATA_SOURCE_ID` 누락
- 선택 사항: `NOTION_WORK_ITEMS_DATA_SOURCE_ID`가 없으면 작업 상세 DB 저장은 건너뜁니다.

### 2) 속성명이 다른 경우

코드는 아래 이름을 기준으로 저장합니다.

- `Name`
- `Work Date`
- `Total Minutes`
- `Total Time Text`
- `Project Summary`
- `Daily Summary`
- `Tomorrow TODO`
- `Raw JSON`

작업 상세 DB를 사용할 경우 아래 이름도 맞아야 합니다.

- `Task`
- `Work Date`
- `Duration`
- `Category`
- `Project`
- `Tool`
- `Start Time`
- `End Time`

### 3) Integration 공유를 안 한 경우

데이터베이스를 integration에 공유하지 않으면 권한 오류가 발생할 수 있습니다.

## 9. 현재 코드에서 관련 파일

- [main.py](C:\Users\ISDATA\Desktop\test2\main.py)
- [worklog_app/notion_sync.py](C:\Users\ISDATA\Desktop\test2\worklog_app\notion_sync.py)
- [.env.example](C:\Users\ISDATA\Desktop\test2\.env.example)
