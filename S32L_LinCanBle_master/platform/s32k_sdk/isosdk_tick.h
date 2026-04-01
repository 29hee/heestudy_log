#ifndef ISOSDK_TICK_H
#define ISOSDK_TICK_H

#include <stdint.h>

typedef void (*IsoSdkTickHandler)(void);

// IsoSdk_Tick를 초기화한다.
uint8_t IsoSdk_TickInit(IsoSdkTickHandler handler);
// IsoSdk_TickClearCompareFlag 관련 동작을 수행한다.
void    IsoSdk_TickClearCompareFlag(void);

#endif
