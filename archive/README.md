# 통신 프로젝트 README

이 폴더는 GUI 프로젝트와 연계된 S32K 통신 펌웨어 구현 보관본입니다.
실제 소스 루트는 `[final]s32k`입니다.

## 1) 프로젝트 범위

- 타겟 플랫폼: S32K
- 실행 모델: cooperative super-loop scheduler
- 현재 역할 프로파일: master coordinator
- 시작점: `[final]s32k/main.c`

## 2) 소스 위치

```text
archive/
└─ [final]s32k/
   ├─ main.c
   ├─ app/
   ├─ core/
   ├─ runtime/
   ├─ services/
   ├─ drivers/
   └─ platform/
```

## 3) 런타임 흐름 (요약)

```text
main.c
 -> Runtime_Init()
 -> Runtime_Run()
 -> RuntimeTask_RunDue() 반복 실행
```

task 구성과 실행 순서는 `[final]s32k/runtime/runtime.c`에서 관리합니다.

## 4) 모듈 요약

- `app`: 역할별 앱 로직, 콘솔 표시, task payload
- `core`: 공통 타입/큐/스케줄러/틱 유틸리티
- `runtime`: 초기화 순서, task table 구성, 실행 루프
- `services`: UART/CAN/LIN 서비스 및 프로토콜 처리
- `drivers`: 보드/주변장치 하드웨어 제어 래퍼
- `platform`: SDK 및 플랫폼 의존 자산

## 5) 빌드/플래시

빌드 및 플래시 절차는 현재 사용 중인 S32K IDE/툴체인 프로젝트 설정을 따릅니다.
이미 `[final]s32k`를 대상으로 구성된 기존 파이프라인을 사용하세요.

## 6) 문서 안내

- 빠른 운영/수정 가이드: `simple_dev.md`
- 상세 아키텍처/파일 책임 가이드: `dev.md`


# 필요 한 콘텐츠
시스템 블록 다이어그램
내용: PC GUI, Master(S32K), Slave 노드, UART/CAN/LIN 연결선
목적: 전체 통신 토폴로지 한눈에 파악
런타임 Task 타임라인
내용: uart / lin_fast / can / lin_poll / render / heartbeat 주기 축(time axis)
목적: 스케줄 충돌, 지연 원인 설명
CAN 프레임 예시 표
내용: command/event/text/response별 ID, payload 의미, source/target
목적: 디버깅 시 패킷 해석 속도 향상
LIN 상태 전이도
내용: normal, warning, danger, emergency, lock 상태 전이 조건
목적: 정책 로직 이해와 변경 영향 분석
부팅 시퀀스 다이어그램
내용: main -> Runtime_Init -> BoardInit -> TickInit -> AppInit -> Hook -> Run
목적: 초기화 실패 지점 추적
장애 트러블슈팅 플로우차트
내용: “증상 -> 1차 확인 파일 -> 2차 확인 파일” 의사결정 트리
목적: 현장 대응 속도 향상