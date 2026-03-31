# Simple Dev Guide 

"수정이 필요할 때 어디를 먼저 열어야 하는지"를 빠르게 찾기 위한 문서.  
실행 방법, 사용자 사용법, 입력 예시는 `README.md` 기준.  
더 많은 정보와 상세 구조는 `dev.md` 확인.

## 1) 구조 한 장 요약

```text
io/readers.py (입력 수집)
 -> parser/parsers.py (문자열 해석)
 -> core/config.py (상태/임계값 정의)
 -> controller/*_mixin.py (상태 반영/흐름 제어)
 -> ui/* (화면 렌더링)
```

| 모듈 | 대표 파일 | 담당 범위 |
|---|---|---|
| io | app/io/readers.py | Serial/File 입력 수집, 콜백 전달 |
| parser | app/parser/parsers.py | 입력 라인 파싱, 토큰 해석, 레벨 분류 |
| core | app/core/config.py | 기본값, 임계값, 상태 모델 정의 |
| controller | app/controller/dashboard_style_mixin.py, app/controller/dashboard_connection_mixin.py, app/controller/dashboard_parse_mixin.py, app/controller/dashboard_runtime_mixin.py | 조립, 연결, 파싱 적용, 런타임 루프 제어 |
| ui | app/ui/layout_builder.py, app/ui/gauge_widget.py, app/ui/layout_sections | 위젯 배치, 시각 표현 |

## 2) Modify Map (목적-타겟파일-담당모듈)

| 수정 목적 | 타겟 파일 | 담당 모듈 |
|---|---|---|
| 입력 문자열 규칙 변경 | app/parser/parsers.py | parser |
| ADC 임계값/기본 상태 변경 | app/core/config.py | core |
| Serial 연결/해제 정책 변경 | app/controller/dashboard_connection_mixin.py | controller |
| File polling 주기/감지 정책 변경 | app/io/readers.py | io |
| 상태 반영 순서/전이 로직 변경 | app/controller/dashboard_parse_mixin.py | controller |
| UI 레이아웃/컴포넌트 배치 변경 | app/ui/layout_builder.py | ui |
| 레이아웃 섹션 세부 배치 변경 | app/ui/layout_sections | ui |
| ADC 게이지 스타일/눈금/마커 변경 | app/ui/gauge_widget.py | ui |
| 창 리사이즈/주기 업데이트 동작 변경 | app/controller/dashboard_runtime_mixin.py | controller |
| 실행 진입 방식 변경 | main.py, new.py, app/__init__.py | entrypoint |

## 3) 장애 유형별 대응

| 증상 | 1차 타겟 파일 | 담당 모듈 |
|---|---|---|
| 포트 연결 실패/끊김 | app/controller/dashboard_connection_mixin.py | controller |
| 파일 수정 후 반영 지연/미반영 | app/io/readers.py | io |
| 값 파싱 실패, 예상과 다른 상태 표시 | app/parser/parsers.py | parser |
| 게이지/색상 표시 이상 | app/ui/gauge_widget.py | ui |
| 전체 동작 순서 꼬임, 상태 반영 누락 | app/controller/dashboard_parse_mixin.py | controller |

## 4) 수정 시 의존 규칙

- parser 수정 시 dashboard_parse_mixin.py 반영 경로를 반드시 함께 확인.
- core 임계값 수정 시 parser 분류 기준과 gauge_widget.py 표시 결과를 함께 확인.
- readers.py 수정 시 ui를 직접 호출하지 않고 controller 경유 구조를 유지.
- ui 수정 시 입력/파싱 규칙을 침범하지 않고 표현 책임만 유지.

## 5) 중복 없는 문서 분리 원칙

- README.md: 실행/사용법/입력 예시(사용자 관점)
- simple_dev.md: 수정 목적별 타겟 파일 탐색(운영 관점)
- dev.md: 상세 아키텍처/생명주기/장기 유지보수 기준(개발 관점)
