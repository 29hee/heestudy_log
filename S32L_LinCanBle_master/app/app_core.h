#ifndef APP_CORE_H
#define APP_CORE_H

#include "../core/infra_types.h"

typedef struct AppCore AppCore;

// AppCore를 초기화한다.
InfraStatus AppCore_Init(AppCore *app);
// AppCore_OnTickIsr 관련 동작을 수행한다.
void        AppCore_OnTickIsr(void *context);
// AppCore_TaskHeartbeat 관련 동작을 수행한다.
void        AppCore_TaskHeartbeat(AppCore *app, uint32_t now_ms);
// AppCore_TaskUart 관련 동작을 수행한다.
void        AppCore_TaskUart(AppCore *app, uint32_t now_ms);
// AppCore의 CAN 경로를 한 번 진행한다.
void        AppCore_TaskCan(AppCore *app, uint32_t now_ms);
// AppCore의 LIN fast 경로를 한 번 진행한다.
void        AppCore_TaskLinFast(AppCore *app, uint32_t now_ms);
// AppCore의 LIN poll 경로를 한 번 진행한다.
void        AppCore_TaskLinPoll(AppCore *app, uint32_t now_ms);
// AppCore 화면 갱신을 수행한다.
void        AppCore_TaskRender(AppCore *app, uint32_t now_ms);

#endif
