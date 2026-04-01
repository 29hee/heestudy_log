#ifndef TICK_HW_H
#define TICK_HW_H

#include "../core/infra_types.h"

typedef void (*TickHwHandler)(void);

// TickHw를 초기화한다.
InfraStatus TickHw_Init(TickHwHandler handler);
// TickHw_ClearCompareFlag 관련 동작을 수행한다.
void        TickHw_ClearCompareFlag(void);

#endif
