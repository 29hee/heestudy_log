# Developer Guide

GUI 프로젝트를 오랜 시간이 지난 뒤에도 다시 이해하고 수정할 수 있도록 정리한 장기 유지보수 문서입니다.

주의: 이 문서는 현재 코드 구조를 기준으로 작성되었습니다. 문서가 구조 변경을 요구하지 않습니다.

## 1) Project Snapshot

- 목적: UART 상태 데이터를 Tkinter GUI로 실시간 시각화
- 입력 채널: Serial(UART), File(test.txt)
- 핵심 도메인 값: Mode, Button, ADC
- 엔트리포인트: main.py(권장), new.py(호환)
- 앱 조립 지점: app/controller/dashboard_style_mixin.py 의 StyledDashboard

## 2) Architecture At A Glance

```text
Input Source (Serial/File)
         -> I/O Adapter (io/readers.py)
         -> Parser (parser/parsers.py)
         -> State Model (core/config.py)
         -> Controller Mixins (controller/*_mixin.py)
         -> View Renderer (ui/layout_builder.py, ui/gauge_widget.py)
```

아키텍처 원칙:

- io는 데이터 수집만 담당하고 UI를 직접 건드리지 않습니다.
- parser는 문자열 해석만 담당하고 포트 연결/렌더링을 하지 않습니다.
- core는 공통 상수, 임계값, 상태 모델의 단일 소스입니다.
- controller는 연결, 파싱 적용, 런타임 루프를 믹스인으로 분리합니다.
- ui는 표현 계층이며 파싱 규칙이나 포트 제어를 알지 않습니다.

## 3) Directory And File Map (Current)

```text
GUI/
├─ main.py
├─ new.py
├─ test.txt
├─ README.md
├─ simple_dev.md
├─ dev.md
├─ cleaning/
│  ├─ clean_pycache.ps1
│  └─ clean_pycache.sh
└─ app/
   ├─ __init__.py
   ├─ core/
   │  ├─ __init__.py
   │  └─ config.py
   ├─ parser/
   │  ├─ __init__.py
   │  └─ parsers.py
   ├─ io/
   │  ├─ __init__.py
   │  └─ readers.py
   ├─ ui/
   │  ├─ __init__.py
   │  ├─ gauge_widget.py
   │  ├─ layout_builder.py
   │  └─ layout_sections/
   └─ controller/
      ├─ __init__.py
      ├─ dashboard_style_mixin.py
      ├─ dashboard_connection_mixin.py
      ├─ dashboard_parse_mixin.py
      └─ dashboard_runtime_mixin.py
```

## 4) File-Level Responsibilities (Detailed)

### Root Files

| 파일 | 역할 | 비고 |
|---|---|---|
| main.py | 프로그램 기본 실행 진입점 | 신규 실행은 이 파일 기준 |
| new.py | 레거시/호환 실행 진입점 | 과거 실행 스크립트와의 호환성 유지 |
| test.txt | File 모드 입력 시뮬레이션 데이터 | 저장 시 UI 상태 반영 트리거 |
| README.md | 사용자 중심 가이드 | 실행, 사용법, 입력 예시 |
| simple_dev.md | 운영 중심 수정 가이드 | 목적-타겟-모듈 매핑 |
| dev.md | 장기 유지보수 문서 | 본 문서 |

### app/core

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| app/core/config.py | 상수, 임계값, 테마, 상태 모델 DashboardState 정의 | 임계값/기본값 변경 시 전체 동작과 화면 표시 규칙 동시 영향 |

### app/parser

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| app/parser/parsers.py | 입력 라인 정리, 섹션 식별, payload 파싱, ADC 레벨 분류 | 입력 포맷 변경 대응의 1차 수정 지점 |

### app/io

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| app/io/readers.py | SerialReader, FileReader 구현 | 포트 연결 안정성, file polling 반응성에 직접 영향 |

### app/ui

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| app/ui/layout_builder.py | Tk 위젯 생성/배치, 화면 골격 구성 | 레이아웃/반응형/배치 영향 |
| app/ui/gauge_widget.py | ADC 게이지 렌더링 | 시각 표현/가독성 영향 |
| app/ui/layout_sections/* | 레이아웃 섹션 분리 구성 | 화면 일부 영역 커스터마이징 영향 |

### app/controller (Mixin Composition)

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| app/controller/dashboard_style_mixin.py | StyledDashboard 조립, 폰트/스타일, UI bootstrap | 앱 초기 구성과 스타일 영향 |
| app/controller/dashboard_connection_mixin.py | 포트 탐색, connect/disconnect, IO 콜백 | 연결 정책/오류 대응 영향 |
| app/controller/dashboard_parse_mixin.py | parse 결과를 상태에 적용하는 규칙 | 상태 반영 규칙 영향 |
| app/controller/dashboard_runtime_mixin.py | update loop, blink, resize, on_close | 런타임 갱신/창 생명주기 영향 |

## 5) Runtime Lifecycle (Step-by-Step)

### Startup

1. main.py 또는 new.py에서 StyledDashboard를 생성합니다.
2. dashboard_style_mixin.py 에서 state, reader, ui를 초기화합니다.
3. refresh_ports, update_gui, schedule_blink_tick이 시작됩니다.

### Running

1. readers.py가 Serial 또는 File 라인을 전달합니다.
2. dashboard_parse_mixin.py가 parsers.py를 이용해 라인을 해석합니다.
3. state가 갱신되고 dashboard_runtime_mixin.py가 UI를 주기적으로 업데이트합니다.

### Shutdown / Mode Switch

1. file mode 종료 또는 serial disconnect를 수행합니다.
2. running 플래그를 내리고 리더를 정리합니다.
3. window close 시 on_close에서 안전 종료합니다.

## 6) Input Contract (Stable Reference)

| Category | Supported Values |
|---|---|
| Mode | normal, emergency |
| Button | approved, denied, ok, waiting |
| ADC | safe, warning, danger, emergency, lock=0, lock=1, numeric value |

유지보수 규칙:

- 새로운 입력 토큰을 추가하면 먼저 parsers.py 규칙을 확장합니다.
- 파싱 결과 의미가 바뀌면 config.py 임계값과 parse apply 규칙을 함께 검토합니다.
- 화면 표시 규칙 변경은 runtime mixin과 gauge_widget.py를 함께 확인합니다.

## 7) Change Guide (Where To Edit First)

| 변경 요구 | 1차 수정 파일 | 2차 확인 파일 |
|---|---|---|
| 새 입력 포맷 추가 | app/parser/parsers.py | app/controller/dashboard_parse_mixin.py |
| ADC 레벨 기준 변경 | app/core/config.py | app/parser/parsers.py, app/ui/gauge_widget.py |
| Serial 연결 정책 변경 | app/controller/dashboard_connection_mixin.py | app/io/readers.py |
| File polling 정책 변경 | app/io/readers.py | app/controller/dashboard_connection_mixin.py |
| 레이아웃 개편 | app/ui/layout_builder.py | app/ui/layout_sections, app/controller/dashboard_style_mixin.py |
| 게이지 스타일 변경 | app/ui/gauge_widget.py | app/controller/dashboard_runtime_mixin.py |
| 상태 반영 로직 변경 | app/controller/dashboard_parse_mixin.py | app/controller/dashboard_runtime_mixin.py |
| 창/루프 동작 변경 | app/controller/dashboard_runtime_mixin.py | app/controller/dashboard_style_mixin.py |

## 8) Dependency Rules (Do/Do Not)

Do:

- controller가 io, parser, core, ui를 조합하도록 유지합니다.
- parse 규칙은 parser에, 임계값/상태 정의는 core에 모읍니다.

Do Not:

- ui에서 시리얼 포트를 직접 열지 않습니다.
- io에서 Tk 위젯을 직접 수정하지 않습니다.
- parser에서 UI 객체에 접근하지 않습니다.

## 9) Cache Notes

- __pycache__ 및 .pyc는 캐시 산출물이므로 삭제 가능합니다.

### Cache Cleaning

```pwsh
./cleaning/clean_pycache.ps1 -WhatIf
./cleaning/clean_pycache.ps1
```

권한 오류 발생 시:

```pwsh
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
Unblock-File -Path .\cleaning\clean_pycache.ps1
```
