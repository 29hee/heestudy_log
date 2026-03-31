# Developer Guide

GUI 프로젝트를 오랜 시간이 지난 뒤에도 다시 이해하고 수정할 수 있도록 정리한 장기 유지보수 문서입니다.

## 1) Project Snapshot

- 목적: UART 상태 데이터를 Tkinter GUI로 실시간 시각화
- 입력 채널: Serial(UART), File(`test.txt`)
- 핵심 도메인 값: `Mode`, `Button`, `ADC`
- 엔트리포인트: `main.py`(권장), `new.py`(호환)
- 메인 오케스트레이터: `app/controller/dashboard_controller.py`

## 2) Architecture At A Glance

```text
Input Source (Serial/File)
         -> I/O Adapter (io)
         -> Parser (parser)
         -> State Model (core)
         -> Application Orchestrator (controller)
         -> View Renderer (ui)
```

아키텍처 원칙:

- `io`는 데이터 수집만 담당하고 UI를 직접 건드리지 않습니다.
- `parser`는 문자열 해석만 담당하고 입출력 연결/렌더링을 하지 않습니다.
- `core`는 공통 상수/임계값/상태 모델의 단일 소스입니다.
- `controller`는 상태 전이와 UI 반영의 단일 진입점입니다.
- `ui`는 표현 계층이며 파싱 규칙이나 포트 제어를 알지 않습니다.

## 3) Directory And File Map

```text
GUI/
├─ main.py
├─ new.py
├─ test.txt
├─ _tree.txt
├─ README.md
├─ dev.md
├─ DEW_new.md
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
        │  ├─ file_reader.py
        │  └─ serial_reader.py
        ├─ ui/
        │  ├─ __init__.py
        │  ├─ gauge_widget.py
        │  └─ layout_builder.py
        └─ controller/
                ├─ __init__.py
                └─ dashboard_controller.py
```

## 4) File-Level Responsibilities (Detailed)

### Root Files

| 파일 | 역할 | 비고 |
|---|---|---|
| `main.py` | 프로그램 기본 실행 진입점 | 신규 실행은 이 파일 기준 |
| `new.py` | 레거시/호환 실행 진입점 | 과거 실행 스크립트와의 호환성 유지 |
| `test.txt` | File 모드 입력 시뮬레이션 데이터 | 저장 시 UI 상태 반영 트리거 |
| `README.md` | 사용자 중심 가이드 | 실행/입력 형식/간단 구조 |
| `dev.md` | 개발자 장기 유지보수 문서 | 본 문서 |
| `DEW_new.md` | 문서 이동 안내 파일 | `dev.md`로 리다이렉트 |
| `_tree.txt` | 트리/메모 보조 파일 | 런타임 직접 사용 아님 |

### `app/core`

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| `app/core/config.py` | 상수, 임계값, 테마, 상태 모델(`DashboardState`) 정의 | 임계값/기본값 변경 시 전체 동작과 화면 표시 규칙 동시 영향 |

### `app/parser`

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| `app/parser/parsers.py` | 입력 라인 정리, 섹션 식별, payload 파싱, ADC 레벨 분류 | 입력 포맷 변경 대응의 1차 수정 지점 |

### `app/io`

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| `app/io/serial_reader.py` | 시리얼 포트 연결/읽기 스레드, 라인 콜백 전달 | 포트 안정성, 연결/해제 UX에 직접 영향 |
| `app/io/file_reader.py` | 파일 변경 감지 및 라인 콜백 전달 | File 모드 반영 지연/빈도와 관련 |

### `app/ui`

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| `app/ui/layout_builder.py` | Tk 위젯 생성/배치, 화면 골격 구성 | 레이아웃/반응형/시각 배치 영향 |
| `app/ui/gauge_widget.py` | ADC 게이지 렌더링(바, 눈금, 마커, 라벨) | 시각 표현/가독성 영향 |

### `app/controller`

| 파일 | 역할 | 변경 시 영향 |
|---|---|---|
| `app/controller/dashboard_controller.py` | 상태 보관, 입력 처리 파이프라인 연결, UI 갱신 오케스트레이션 | 앱의 실제 동작 규칙 전반 영향 |

## 5) Runtime Lifecycle (Step-by-Step)

### Startup

1. `main.py` 또는 `new.py`에서 앱 인스턴스를 생성합니다.
2. 컨트롤러가 초기 상태(`DashboardState`)와 UI 레이아웃을 준비합니다.
3. 사용자 모드 선택(Serial/File)에 따라 입력 리더를 초기화합니다.

### Running (Serial/File 공통)

1. I/O 레이어가 텍스트 라인을 읽습니다.
2. `parsers.py`가 라인을 정규화하고 의미 있는 값으로 해석합니다.
3. 컨트롤러가 해석 결과를 상태 모델에 반영합니다.
4. 상태 변경 사항을 UI 위젯에 전달하여 렌더링합니다.

### Shutdown / Mode Switch

1. 기존 리더 스레드/연결을 안전하게 종료합니다.
2. 필요한 상태를 초기화하거나 유지 정책에 따라 보존합니다.
3. 새 모드 리더를 연결하고 파이프라인을 재시작합니다.

## 6) Input Contract (Stable Reference)

| Category | Supported Values |
|---|---|
| `Mode` | `normal`, `emergency` |
| `Button` | `approved`, `denied`, `ok`, `waiting` |
| `ADC` | `safe`, `warning`, `danger`, `emergency`, `lock=0`, `lock=1`, numeric value |

유지보수 규칙:

- 새로운 입력 토큰을 추가하면 먼저 `parsers.py`에서 해석 규칙을 확장합니다.
- 파싱 결과의 의미가 바뀌면 `config.py` 임계값/상태 모델과 함께 검토합니다.
- 화면 표시 규칙 변경은 `dashboard_controller.py`와 `gauge_widget.py`를 함께 확인합니다.

## 7) Change Guide (Where To Edit First)

| 변경 요구 | 1차 수정 파일 | 2차 확인 파일 |
|---|---|---|
| 새 입력 포맷 추가 | `app/parser/parsers.py` | `app/controller/dashboard_controller.py` |
| ADC 레벨 기준 변경 | `app/core/config.py` | `app/parser/parsers.py`, `app/ui/gauge_widget.py` |
| Serial 연결 정책 변경 | `app/io/serial_reader.py` | `app/controller/dashboard_controller.py` |
| File polling 정책 변경 | `app/io/file_reader.py` | `app/controller/dashboard_controller.py` |
| 레이아웃 개편 | `app/ui/layout_builder.py` | `app/controller/dashboard_controller.py` |
| 게이지 스타일 변경 | `app/ui/gauge_widget.py` | `app/core/config.py` |
| 상태 전이 로직 변경 | `app/controller/dashboard_controller.py` | `app/core/config.py`, `app/parser/parsers.py` |

## 8) Dependency Rules (Do/Do Not)

Do:

- `controller`가 `io`, `parser`, `core`, `ui`를 조합하도록 유지합니다.
- 파싱 로직은 `parser`에, 임계값과 상태 정의는 `core`에 모읍니다.

Do Not:

- `ui`에서 시리얼 포트를 직접 열지 않습니다.
- `io`에서 Tk 위젯을 직접 수정하지 않습니다.
- `parser`에서 UI 객체에 접근하지 않습니다.

## 9) Legacy and Cache Notes

- `__pycache__` 및 `.pyc`는 캐시 산출물이므로 삭제 가능합니다.
- 과거 구조 흔적으로 `constants`, `theme`, `state`, `payload_parser`, `sections_parser` 관련 `.pyc`가 남아 있을 수 있습니다.
- 실제 소스 기준은 `config.py`, `parsers.py`입니다.

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

## 10) Portfolio Value Points

- 계층 분리 아키텍처(`io -> parser -> core/state -> controller -> ui`)를 명확히 유지
- 입력 소스(Serial/File) 교체에 유연한 어댑터 구조
- 변경 요구별 수정 시작점을 문서화해 유지보수 비용 최소화

## 11) Recommended Next Improvements

- 파서 단위 테스트 추가(입력 케이스 회귀 방지)
- 상태 전이 로깅 추가(디버깅 추적성 향상)
- 시리얼 재연결/타임아웃 정책 표준화
- 모드 전환 시 상태 보존 정책 명문화
