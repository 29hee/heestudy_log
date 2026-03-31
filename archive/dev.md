# 개발자 가이드 (상세)

이 문서는 S32K 통신 프로젝트의 장기 유지보수 문서입니다.
시간이 지난 뒤에도 구조를 빠르게 복구할 수 있도록 파일 책임과 런타임 흐름을 상세히 정리합니다.

## 1) 프로젝트 식별 정보

- Code root: archive/[final]s32k
- Entry point: main.c
- Runtime API: runtime/runtime.h
- Core pattern: Runtime_Init() then Runtime_Run() cooperative loop
- Current role profile: master coordinator runtime binding

## 2) 디렉터리 트리

```text
[final]s32k/
├─ main.c
├─ app/
│  ├─ app_config.h
│  ├─ app_core.c
│  ├─ app_core.h
│  ├─ app_master.c
│  ├─ app_master.h
│  ├─ app_console.c
│  └─ app_console.h
├─ core/
│  ├─ infra_types.h
│  ├─ infra_queue.c
│  ├─ infra_queue.h
│  ├─ runtime_task.c
│  ├─ runtime_task.h
│  ├─ runtime_tick.c
│  └─ runtime_tick.h
├─ runtime/
│  ├─ runtime.c
│  ├─ runtime.h
│  ├─ runtime_io.c
│  └─ runtime_io.h
├─ services/
│  ├─ uart_service.c
│  ├─ can_module.c
│  ├─ can_service.c
│  ├─ can_proto.c
│  ├─ lin_module.c
│  └─ ...
├─ drivers/
│  ├─ board_hw.c
│  ├─ uart_hw.c
│  ├─ can_hw.c
│  ├─ lin_hw.c
│  ├─ tick_hw.c
│  └─ led_module.c
└─ platform/
   └─ s32k_sdk/
```

## 3) 런타임 생명주기

### 3.1 부팅 경로

1. `main.c`가 `Runtime_Init()`를 호출합니다.
2. `RuntimeIo_BoardInit()`으로 보드 초기화를 수행합니다.
3. `RuntimeTick_Init()`으로 tick 서브시스템을 올립니다.
4. `AppCore_Init()`으로 앱 코어를 초기화합니다.
5. tick hook(`AppCore_OnTickIsr`)를 등록합니다.
6. runtime task table을 구성하고 reset합니다.
7. `Runtime_Run()`으로 무한 super-loop에 진입합니다.

### 3.2 스케줄링 동작

- 스케줄러 구현: `core/runtime_task.c`
- due 실행 함수: `RuntimeTask_RunDue()`
- task table 소유자: `runtime/runtime.c`
- 현재 task 집합:
  - uart
  - lin_fast
  - can
  - lin_poll
  - render
  - heartbeat

task 주기 상수는 `app/app_config.h`에서 관리합니다.

### 3.3 통신 흐름 (핵심)

이 프로젝트는 `uart`, `can`, `lin_fast`, `lin_poll` task를 중심으로 통신을 처리합니다.
통신 관점에서의 end-to-end 흐름은 아래와 같습니다.

```text
[Operator/PC]
  <-> UART(hw/service/console)
  <-> AppCore(command/event 반영)
  <-> CAN service/module
  <-> Remote Node

[Master Node]
  <-> LIN(hw/service)
  <-> AppCore(master policy)
  <-> Console Render(UART 출력)
```

#### UART 경로

```text
UART HW
 -> services/uart_service
 -> app/app_console
 -> app/app_core (AppCore_TaskUart)
```

- 역할: 운영자 입력 수집, 상태/결과 텍스트 출력
- 주기 task: `AppCore_TaskUart`

#### CAN 경로

```text
app_console 명령 큐
 -> AppCore_TaskCan
 -> services/can_module + can_service + can_proto
 -> drivers/can_hw
 -> 원격 노드
 -> (응답/이벤트/텍스트)
 -> AppCore_TaskCan
 -> AppCore_HandleCanIncoming
 -> 화면/결과 반영
```

- 역할: 원격 노드와 명령/응답/이벤트 교환
- 주기 task: `AppCore_TaskCan`

#### LIN 경로

```text
runtime/runtime_io (LIN role/binding)
 -> services/lin_module
 -> drivers/lin_hw
 -> slave 노드 상태 프레임
 -> AppCore_TaskLinFast (fresh status 반영)
 -> AppCore_TaskLinPoll (주기 poll + 로컬 OK 처리)
 -> app_master 정책 처리
```

- 역할: 상태 수집과 승인(OK) 릴레이 흐름 처리
- 주기 task: `AppCore_TaskLinFast`, `AppCore_TaskLinPoll`

#### 통신 Task-파일 매핑

| 통신 목적 | 1차 task/함수 | 1차 파일 | 연계 파일 |
|---|---|---|---|
| UART 입력/렌더 | `AppCore_TaskUart` | `app/app_core.c` | `app/app_console.c`, `services/uart_service.c` |
| CAN 송수신/결과 소비 | `AppCore_TaskCan` | `app/app_core.c` | `services/can_module.c`, `services/can_service.c`, `services/can_proto.c` |
| LIN 최신 상태 반영 | `AppCore_TaskLinFast` | `app/app_core.c` | `services/lin_module.c`, `runtime/runtime_io.c` |
| LIN 주기 poll/OK 처리 | `AppCore_TaskLinPoll` | `app/app_core.c` | `app/app_master.c`, `services/lin_module.c` |

## 4) 모듈/파일 책임 상세

### 4.1 main 계층

| 파일 | 책임 | 메모 |
|---|---|---|
| `main.c` | 프로그램 시작 후 runtime으로 위임 | 최대한 얇게 유지 |

### 4.2 runtime 계층

| 파일 | 책임 | 메모 |
|---|---|---|
| `runtime/runtime.h` | 상위에서 호출하는 runtime API 제공 | 통합 진입면 |
| `runtime/runtime.c` | 초기화 순서, task table 구성, 실행 루프 | 스케줄 배선 소유 |
| `runtime/runtime_io.h` | 역할별 보드/통신 바인딩 인터페이스 | 프로젝트 종속부 추상화 |
| `runtime/runtime_io.c` | master LIN 설정/이벤트 브리지 조립 | hw 이벤트를 service 이벤트로 변환 |

### 4.3 app 계층

| 파일 | 책임 | 메모 |
|---|---|---|
| `app/app_config.h` | task 주기, 노드/콘솔 상수 정의 | 타이밍 단일 소스 |
| `app/app_core.h` | AppCore 공개 API | runtime이 호출 |
| `app/app_core.c` | 앱 동작 오케스트레이션 | runtime task가 직접 호출 |
| `app/app_master.c` | master 역할 정책 로직 | 역할별 분리 |
| `app/app_console.c` | 콘솔 출력/입력 처리 | 프로파일별 출력 형태 |

### 4.4 core 계층

| 파일 | 책임 | 메모 |
|---|---|---|
| `core/infra_types.h` | 공통 상태/시간/유틸 타입 | 전체 공용 기반 |
| `core/infra_queue.c` | 경량 큐 유틸리티 | app/services에서 사용 |
| `core/runtime_task.c` | cooperative due 판정/호출 | 정책 로직 금지 |
| `core/runtime_tick.c` | tick 추상화와 hook 관리 | ISR 연계 기반 |

### 4.5 services 계층

| 파일군 | 책임 | 메모 |
|---|---|---|
| `uart_service.*` | UART 서비스 레벨 처리 | `uart_hw` 상위 계층 |
| `can_module.*`, `can_service.*`, `can_proto.*` | CAN 프레임/프로토콜/서비스 처리 | 계층 관심사 분리 유지 |
| `lin_module.*` | LIN 상태 전이, 이벤트 처리 | runtime_io 바인딩과 연결 |

### 4.6 drivers/platform 계층

| 파일군 | 책임 | 메모 |
|---|---|---|
| `drivers/*_hw.*` | 하드웨어 직접 제어 래퍼 | 레지스터 접근 집중 |
| `drivers/board_hw.*` | 보드 공통 초기화/트랜시버 제어 | runtime init 의존점 |
| `platform/s32k_sdk` | 벤더 SDK 자산 | 외부 의존 경계 |

## 5) 의존 규칙과 소유권

반드시 지킬 것:

- runtime이 초기화 순서와 task table 구성을 소유합니다.
- app이 비즈니스 동작과 task payload를 소유합니다.
- services가 UART/CAN/LIN 프로토콜/서비스를 소유합니다.
- drivers가 하드웨어 직접 제어를 소유합니다.
- core가 스케줄러/틱/공통 유틸을 소유합니다.

피해야 할 것:

- `main.c`에 정책 로직 추가
- app에서 driver 우회한 직접 하드웨어 호출
- app/services 간 중복 파싱 로직 생성
- runtime/core 밖으로 스케줄 규칙 분산

## 6) 변경 영향 맵

| 변경 목적 | 1차 파일 | 2차 확인 파일 |
|---|---|---|
| task 주기 변경 | `app/app_config.h` | `runtime/runtime.c` 실행 순서 |
| 신규 runtime task 추가 | `runtime/runtime.c` | `app/app_core.h`, `app/app_core.c` |
| LIN 역할 동작 변경 | `services/lin_module.c` | `runtime/runtime_io.c` 바인딩 |
| CAN payload/proto 변경 | `services/can_proto.c` | `services/can_service.c`, app 처리부 |
| 콘솔 출력 포맷 변경 | `app/app_console.c`, `app/app_config.h` | `services/uart_service.c` |
| init 순서 변경 | `runtime/runtime.c` | `drivers/board_hw.c`, `core/runtime_tick.c` |
| 스케줄/틱 규칙 변경 | `core/runtime_task.c`, `core/runtime_tick.c` | `runtime/runtime.c` 루프 가정 |

## 7) 운영 디버그 체크리스트

1. 부팅 직후 멈춤이면 `runtime/runtime.c`의 `Runtime_Init()` 실패 분기부터 확인
2. 주기 동작 누락이면 `app/app_config.h` 주기값과 `core/runtime_task.c` due 판정 확인
3. 통신 결과 이상이면 app보다 services 계층부터 확인
4. 하드웨어 반응 이상이면 `drivers/board_hw.c` 및 해당 `*_hw.c` 초기화 확인

## 8) 향후 개선 메모

- 현재 fault loop는 관측성이 낮아 원인 추적이 어렵습니다.
- init 실패 코드를 UART/LED로 노출하면 현장 디버깅 비용을 줄일 수 있습니다.

## 9) 관련 문서

- `archive/README.md`: 프로젝트 개요
- `archive/simple_dev.md`: 빠른 수정 맵
