// LIN sensor slave 전용 runtime 구현 파일이다.
// 센서 노드가 실제로 쓰는 task만 등록하여,
// CAN, UART, render 같은 다른 노드용 스케줄 항목을 제거한다.
#include "runtime.h"

#include "../app/app_config.h"
#include "../app/app_core_internal.h"
#include "../core/runtime_task.h"
#include "../core/runtime_tick.h"
#include "runtime_io.h"

typedef struct
{
    uint8_t          initialized;
    InfraStatus      init_status;
    AppCore          app;
    RuntimeTaskEntry tasks[4];
} RuntimeContext;

static RuntimeContext g_runtime;

// AppCore heartbeat task를 runtime task 서명으로 감싼다.
static void Runtime_TaskHeartbeat(void *context, uint32_t now_ms)
{
    AppCore_TaskHeartbeat((AppCore *)context, now_ms);
}

// AppCore LIN fast task를 runtime scheduler에 연결한다.
static void Runtime_TaskLinFast(void *context, uint32_t now_ms)
{
    AppCore_TaskLinFast((AppCore *)context, now_ms);
}

// AppCore LED task를 runtime scheduler에 연결한다.
static void Runtime_TaskLed(void *context, uint32_t now_ms)
{
    AppCore_TaskLed((AppCore *)context, now_ms);
}

// AppCore ADC task를 runtime scheduler에 연결한다.
static void Runtime_TaskAdc(void *context, uint32_t now_ms)
{
    AppCore_TaskAdc((AppCore *)context, now_ms);
}

// sensor slave 역할에서 실제로 돌릴 cooperative task table을 구성한다.
// 주기와 순서는 이 함수 하나만 보면 정리되게 두었다.
static void Runtime_BuildTaskTable(RuntimeContext *runtime)
{
    runtime->tasks[0].name        = "lin_fast";
    runtime->tasks[0].period_ms   = APP_TASK_LIN_FAST_MS;
    runtime->tasks[0].last_run_ms = 0U;
    runtime->tasks[0].task_fn     = Runtime_TaskLinFast;
    runtime->tasks[0].context     = &runtime->app;

    runtime->tasks[1].name        = "adc";
    runtime->tasks[1].period_ms   = APP_TASK_ADC_MS;
    runtime->tasks[1].last_run_ms = 0U;
    runtime->tasks[1].task_fn     = Runtime_TaskAdc;
    runtime->tasks[1].context     = &runtime->app;

    runtime->tasks[2].name        = "led";
    runtime->tasks[2].period_ms   = APP_TASK_LED_MS;
    runtime->tasks[2].last_run_ms = 0U;
    runtime->tasks[2].task_fn     = Runtime_TaskLed;
    runtime->tasks[2].context     = &runtime->app;

    runtime->tasks[3].name        = "heartbeat";
    runtime->tasks[3].period_ms   = APP_TASK_HEARTBEAT_MS;
    runtime->tasks[3].last_run_ms = 0U;
    runtime->tasks[3].task_fn     = Runtime_TaskHeartbeat;
    runtime->tasks[3].context     = &runtime->app;
}

// 초기화 실패 시 빠져나오지 않는 fault loop다.
static void Runtime_FaultLoop(void)
{
    for (;;)
    {
    }
}

// runtime, 보드, tick, app, ISR hook를 차례대로 준비한다.
// 어느 한 단계라도 실패하면 이후 run 단계로 가지 않게 막는다.
// 주의: hook 등록을 AppCore 초기화 뒤에 두어, 미초기화 LIN 모듈에 ISR이 먼저 들어가는 일을 피한다.
InfraStatus Runtime_Init(void)
{
    InfraStatus status;
    uint32_t    start_ms;

    g_runtime.initialized = 0U;
    g_runtime.init_status = INFRA_STATUS_NOT_READY;

    // 1) 보드와 외부 트랜시버를 먼저 올린다.
    status = RuntimeIo_BoardInit();
    if (status != INFRA_STATUS_OK)
    {
        g_runtime.init_status = status;
        return status;
    }

    // 2) 전체 task가 공유할 시간 기준을 만든다.
    status = RuntimeTick_Init();
    if (status != INFRA_STATUS_OK)
    {
        g_runtime.init_status = status;
        return status;
    }

    // 3) application 조립을 끝낸 뒤에만 ISR hook를 등록한다.
    status = AppCore_Init(&g_runtime.app);
    if (status != INFRA_STATUS_OK)
    {
        g_runtime.init_status = status;
        return status;
    }

    RuntimeTick_ClearHooks();
    // 4) LIN timeout service로 이어지는 짧은 ISR hook를 연결한다.
    status = RuntimeTick_RegisterHook(AppCore_OnTickIsr, &g_runtime.app);
    if (status != INFRA_STATUS_OK)
    {
        g_runtime.init_status = status;
        return status;
    }

    // 5) 역할별 task table을 만들고 같은 start tick으로 정렬한다.
    Runtime_BuildTaskTable(&g_runtime);
    start_ms = RuntimeTick_GetMs();
    RuntimeTask_ResetTable(g_runtime.tasks,
                           INFRA_ARRAY_COUNT(g_runtime.tasks),
                           start_ms);

    g_runtime.initialized = 1U;
    g_runtime.init_status = INFRA_STATUS_OK;
    return INFRA_STATUS_OK;
}

// sensor slave용 super-loop를 계속 돌린다.
void Runtime_Run(void)
{
    if ((g_runtime.initialized == 0U) || (g_runtime.init_status != INFRA_STATUS_OK))
    {
        Runtime_FaultLoop();
    }

    for (;;)
    {
        RuntimeTask_RunDue(g_runtime.tasks,
                           INFRA_ARRAY_COUNT(g_runtime.tasks),
                           RuntimeTick_GetMs());
    }
}

// 현재 runtime이 들고 있는 AppCore를 조회한다.
const AppCore *Runtime_GetApp(void)
{
    return &g_runtime.app;
}

// 참고:
// fault loop가 아주 단순해서 bring-up 중 실패 원인을 현장에서 바로 알기는 어렵다.
// 나중에는 마지막 init 실패 코드를 LED나 간단한 상태 변수로 남기는 정도만 더해도 도움이 된다.
