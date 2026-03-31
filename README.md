# MCU UART Monitoring Dashboards

UART 데이터를 실시간으로 시각화하는 Tkinter 기반 GUI입니다.  
Serial / File 모드를 지원하며 ADC, Button, Mode 상태를 직관적으로 확인할 수 있습니다.
## 🚀 TL;DR

- UART 데이터를 실시간으로 시각화하는 Tkinter 기반 GUI
- Serial / File 모드 지원
- ADC / Button / Mode 상태 모니터링 가능

## 1) ⚙️ 실행 방법

> OS: Windows

```bash
cd GUI
python main.py
```
* 실행 진입점: `main.py`
* 호환 진입점: `new.py`


## 2) 🧭 Usage

### Mode 선택
1. 프로그램을 실행합니다
2. 창 크기를 원하는 대로 조절합니다
3. Dropdown에서 모드를 선택합니다 (`Serial` / `File`)
   * Serial: 실제 UART 연결
   * File: test.txt 기반 시뮬레이션
---

### Serial 모드

1. 포트 선택
2. `Connect` 클릭
3. 데이터 실시간 확인
4. 옵션:
   * refresh ports → 포트 재조회
   * disconnect → 연결 해제
---

### File 모드
1. `test.txt` 수정
2. 저장
3. GUI 자동 반영
	### 📥 Input Format
	```BASH
   # Example:
	[Status]
	Mode : normal
	Button : approved
	ADC : 4095 (emergency, lock=0)
	```
   - 지원 값
   * Mode: `normal`, `emergency`
   * Button: `approved`, `denied`, `waiting`, `ok`
   * ADC:
     * `숫자`
     * `safe`, `warning`, `waiting`, `emergency`
     * `lock=0`, `lock=1`


## 3) 📁 Structure (simple)

```text
GUI/
├─ main.py
├─ new.py
├─ test.txt
├─ README.md
├─ dev.md
├─ cleaning/
│  ├─ clean_pycache.ps1
│  └─ clean_pycache.sh
└─ app/
  ├─ core/
  ├─ parser/
  ├─ io/
  ├─ ui/
  └─ controller/
```

## 4) 🧹 Cache Cleaning

```pwsh
# PowerShell
./cleaning/clean_pycache.ps1 -WhatIf   # 삭제 없이 대상만 확인
./cleaning/clean_pycache.ps1           # 실제 삭제
```

권한 오류가 날 경우:

```pwsh
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
Unblock-File -Path .\cleaning\clean_pycache.ps1
```

## 5) 개발자 문서

상세한 파일 구조, 파일별 역할, 유지보수 로드맵은 `simple_dev.md`를 참고해주세요.