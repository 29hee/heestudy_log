# Simple Dev Guide (운영 버전)

이 문서는 유지보수 시 "무엇을 고칠 때 어느 파일부터 열어야 하는지"를 빠르게 찾기 위한 가이드입니다.

## 1) 한 장 구조 요약

```text
drivers/platform
 -> services
 -> app
 -> runtime
 -> main

runtime loop
 -> core/runtime_task 스케줄러
 -> app task 실행(uart, lin_fast, can, lin_poll, render, heartbeat)
```

## 2) 수정 맵 (목적 - 타겟 파일 - 담당 모듈)

| 수정 목적 | 타겟 파일 | 담당 모듈 |
|---|---|---|
| 부팅/초기화 순서 변경 | `[final]s32k/main.c`, `[final]s32k/runtime/runtime.c` | runtime |
| task 주기/순서 변경 | `[final]s32k/app/app_config.h`, `[final]s32k/runtime/runtime.c` | app + runtime |
| 앱 동작 로직 변경 | `[final]s32k/app/app_core.c` | app |
| UART 서비스 동작 변경 | `[final]s32k/services/uart_service.c` | services |
| CAN 프로토콜/서비스 변경 | `[final]s32k/services/can_proto.c`, `[final]s32k/services/can_service.c` | services |
| LIN 역할/바인딩 설정 변경 | `[final]s32k/runtime/runtime_io.c` | runtime |
| LIN 상태머신/서비스 변경 | `[final]s32k/services/lin_module.c` | services |
| 보드/주변장치 제어 변경 | `[final]s32k/drivers/board_hw.c`, `[final]s32k/drivers/*_hw.c` | drivers |
| 스케줄러 규칙 변경 | `[final]s32k/core/runtime_task.c` | core |
| 공통 큐/타입 유틸리티 변경 | `[final]s32k/core/infra_queue.c`, `[final]s32k/core/infra_types.h` | core |

## 3) 장애별 1차 확인

| 증상 | 1차 확인 파일 | 담당 모듈 |
|---|---|---|
| 초기화 실패 후 멈춤 | `[final]s32k/runtime/runtime.c` | runtime |
| 주기 task 미실행 | `[final]s32k/core/runtime_task.c`, `[final]s32k/runtime/runtime.c` | core + runtime |
| UART 결과 불일치 | `[final]s32k/services/uart_service.c`, `[final]s32k/app/app_console.c` | services + app |
| CAN 처리 이상 | `[final]s32k/services/can_module.c`, `[final]s32k/services/can_service.c` | services |
| LIN timeout/error | `[final]s32k/services/lin_module.c`, `[final]s32k/runtime/runtime_io.c` | services + runtime |
| 하드웨어 초기화/제어 이상 | `[final]s32k/drivers/board_hw.c`, `[final]s32k/drivers/*_hw.c` | drivers |

## 4) 유지보수 가드레일

- `main.c`는 얇게 유지하고 앱 정책 로직을 넣지 않습니다.
- 하드웨어 직접 제어는 `drivers`에 모으고 상위 계층으로 퍼뜨리지 않습니다.
- 프로토콜 파싱/서비스 로직은 `services`에 유지합니다.
- task 스케줄 소유권은 `runtime/core`에 유지합니다.

## 5) 문서 역할 분리

- `README.md`: 프로젝트 개요와 위치 안내
- `simple_dev.md`: 빠른 수정 판단용 맵
- `dev.md`: 상세 아키텍처와 파일 책임
