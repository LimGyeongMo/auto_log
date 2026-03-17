# Worklog CLI

Python으로 실행하는 로컬 업무기록 CLI 프로그램입니다.

하루 동안 한 작업을 JSON 파일에 저장하고, 날짜별 조회와 일일 보고서 생성을 지원합니다.
원하면 Notion 데이터베이스에도 하루 단위 페이지로 저장할 수 있습니다.
작업은 `회사 프로젝트`와 `개인 프로젝트`로 구분해서 저장할 수 있습니다.

## 파일 구조

```text
worklog-cli/
├─ main.py
├─ project_registry.json
├─ requirements.txt
├─ .env.example
├─ README.md
├─ sample_data/
│  └─ worklog.sample.json
└─ worklog_app/
   ├─ __init__.py
   ├─ models.py
   ├─ utils.py
   ├─ storage.py
   ├─ report.py
   └─ notion_sync.py
```

## 설치

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 실행

```bash
python main.py
```

기본 저장 파일은 실행 위치 기준 `worklog.json` 입니다.

프로젝트 경로 보관 파일은 `project_registry.json` 입니다.

메뉴 없이 바로 Notion 저장만 실행하려면 아래처럼 사용할 수 있습니다.

```bash
python main.py notion-save --date 2026-03-16
```

날짜를 생략하면 오늘 날짜를 사용합니다.

```bash
python main.py notion-save
```

## 현재 운영 상태

현재 프로젝트는 아래 기준으로 동작합니다.

- 로컬 작업 기록 파일: `worklog.json`
- 프로젝트 경로 등록 파일: `project_registry.json`
- Notion 연동 환경 변수 파일: `.env`
- Notion 연동 상세 가이드: `NOTION_SETUP.md`

현재 등록된 개인 프로젝트:

- `C:\Users\ISDATA\Desktop\test2`
- `C:\Users\ISDATA\Desktop\test`

현재 데이터 저장 방식:

- 하루 작업은 `worklog.json`에 JSON으로 저장
- Notion에는 날짜별 페이지 1개로 저장
- 같은 날짜 페이지가 있으면 새로 만들지 않고 업데이트
- 프로젝트는 `회사`와 `개인`으로 구분해서 저장
- Notion에는 현재 `[회사] 프로젝트명`, `[개인] 프로젝트명` 형태로 요약 텍스트에 반영

빠른 저장 명령:

```bash
python main.py notion-save
```

`notion-save`는 항상 오늘 날짜 기준으로만 저장합니다.

Codex 없이 터미널에서 바로 저장하려면 아래 스크립트를 사용할 수 있습니다.

Windows `cmd`:

```bash
save-log.bat
```

Git Bash / bash:

```bash
./save-log.sh
```

대화 기준 호출 문구:

- 앞으로 Notion 저장 실행 요청은 `save log` 로 사용합니다.
- `save log` 요청 시 등록된 프로젝트들의 오늘 Git 커밋/변경 파일을 먼저 수집해 `worklog.json` 초안을 갱신한 뒤 오늘 날짜 페이지를 생성하거나 업데이트합니다.
- 날짜는 항상 오늘 날짜를 사용합니다.

셸에서 직접 실행할 때도 같은 의미로 `save-log.bat` 또는 `save-log.sh`를 사용하면 됩니다.

## 메뉴

1. 작업 입력
2. 오늘 작업 보기
3. 날짜별 작업 보기
4. 일일 보고서 생성
5. Notion에 저장
6. 종료

## 입력 데이터

- 날짜
- 프로젝트 구분(회사 / 개인)
- 시작 시간
- 종료 시간
- 사용 툴
- 프로젝트명
- 작업 카테고리
- 작업 내용
- 상세 메모

시간은 `09:00`, `18:30` 형식으로 입력합니다.
프로젝트 구분은 입력 시 `회사 프로젝트` 또는 `개인 프로젝트`를 선택합니다.

## 프로젝트 경로 관리

향후 Git 로그 수집이나 변경 파일 자동 조회를 붙이기 위해 프로젝트 경로는 `project_registry.json` 에 보관할 수 있습니다.

현재 등록된 개인 프로젝트:

- `C:\Users\ISDATA\Desktop\test2`
- `C:\Users\ISDATA\Desktop\test`

현재 버전에서는 이 파일을 `save-log.bat`, `save-log.sh`, `python main.py notion-save` 실행 시 자동 조회에 사용합니다.

## Git 자동 수집

`save-log.bat`, `save-log.sh`, `python main.py notion-save`, 메뉴의 `5) Notion에 저장`은 아래 순서로 동작합니다.

- `project_registry.json` 에 등록된 프로젝트 경로를 순회합니다.
- Git 저장소인 프로젝트만 대상으로 오늘 커밋과 현재 변경 파일을 읽습니다.
- 수집 결과를 `Git 자동 수집` 카테고리의 작업으로 `worklog.json`에 저장합니다.
- 같은 날짜의 기존 자동 수집 엔트리는 새 수집 결과로 교체합니다.
- 그 뒤 오늘 날짜 작업 데이터를 기준으로 Notion 저장을 진행합니다.

## Notion 연동 준비

### 1. 통합(Integration) 생성

1. Notion Developers 페이지에서 새 integration을 만듭니다.
2. 생성 후 API 키를 복사합니다.

### 2. 데이터베이스 생성

Notion에서 데이터베이스를 만들고 아래 속성명을 정확히 맞춥니다.

- `Name` : Title
- `Work Date` : Date
- `Total Minutes` : Number
- `Total Time Text` : Rich text
- `Project Summary` : Rich text
- `Daily Summary` : Rich text
- `Tomorrow TODO` : Rich text
- `Raw JSON` : Rich text

### 3. 데이터베이스 공유

만든 integration에 해당 데이터베이스를 공유해야 API로 접근할 수 있습니다.

### 4. 환경 변수 설정

`.env.example`을 복사해서 `.env`를 만든 뒤 값을 입력합니다.

```env
NOTION_API_KEY=secret_xxx
NOTION_DATA_SOURCE_ID=xxxxxxxxxxxxxxxx
```

자세한 연결 절차는 [NOTION_SETUP.md](C:\Users\ISDATA\Desktop\test2\NOTION_SETUP.md) 문서를 참고하면 됩니다.

## Notion 저장 방식

- 날짜별로 페이지 1개를 사용합니다.
- 같은 날짜 페이지가 있으면 검색 후 업데이트합니다.
- 없으면 새 페이지를 생성하며, 가능하면 Notion 데이터베이스의 기본 템플릿을 사용합니다.
- 저장 전에 콘솔에 미리보기를 먼저 출력합니다.
- `회사/개인` 구분은 프로젝트 요약 텍스트와 원본 JSON에 함께 저장됩니다.

## 확장 포인트

구조를 단순하게 두었지만 아래 기능을 나중에 붙이기 쉽게 분리했습니다.

- GUI(Tkinter, PySide)
- Excel 저장
- Markdown 저장
- Git 로그 연동
- 에디터 로그 자동 수집

## 샘플 데이터

`sample_data/worklog.sample.json` 파일을 참고하면 저장 구조를 바로 이해할 수 있습니다.

## 유지보수 원칙

- 로직, CLI 흐름, 저장 형식, Notion 연동 방식이 바뀌면 `README.md`도 함께 수정합니다.
- 새 기능이 추가되면 실행 방법과 입력/출력 예시도 같이 갱신하는 것을 기본 원칙으로 합니다.
- 대화에서 사용하는 주요 실행 표현이 바뀌면 `README.md`에 반영합니다.
