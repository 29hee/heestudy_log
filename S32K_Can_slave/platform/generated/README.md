# Generated Inputs

이 폴더는 보드별 독립 빌드 시 IDE 또는 Config Tools가 생성한 파일을 두는 자리입니다.

필수 항목:
- `sdk_project_config.h`
- 필요하다면 그와 함께 생성되는 `sdk_project_config.c` 또는 peripheral config source

추가로 NXP SDK 기본 패키지에서 아래 헤더들이 include path에 들어와야 합니다.
- `status.h`
- `device_registers.h`
- `osif.h`
- `callbacks.h`

현재 `re_3_prune`는 소스 구조 정리본이며, 위 생성 파일과 SDK 기본 헤더는 저장소에 포함되어 있지 않습니다.
