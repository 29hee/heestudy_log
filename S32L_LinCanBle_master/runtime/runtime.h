// 프로젝트의 최상위 runtime 인터페이스다.
// 상위 코드는 이 함수들만 호출하면 시스템을 초기화하고,
// 무한 cooperative scheduler로 진입할 수 있다.
#ifndef RUNTIME_H
#define RUNTIME_H

#include "../app/app_core.h"
#include "../core/infra_types.h"

// Runtime를 초기화한다.
InfraStatus    Runtime_Init(void);
// Runtime 실행 루프를 시작한다.
void           Runtime_Run(void);
// 현재 runtime이 보유한 AppCore를 조회한다.
const AppCore *Runtime_GetApp(void);

#endif
