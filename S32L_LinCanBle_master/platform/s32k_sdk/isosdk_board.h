#ifndef ISOSDK_BOARD_H
#define ISOSDK_BOARD_H

#include <stdint.h>

// IsoSdk_Board를 초기화한다.
uint8_t  IsoSdk_BoardInit(void);
// IsoSdk_Board LIN transceiver를 활성화한다.
void     IsoSdk_BoardEnableLinTransceiver(void);
void    *IsoSdk_BoardGetRgbLedPort(void);
// IsoSdk_BoardGetRgbLedRedPin 관련 동작을 수행한다.
uint32_t IsoSdk_BoardGetRgbLedRedPin(void);
// IsoSdk_BoardGetRgbLedGreenPin 관련 동작을 수행한다.
uint32_t IsoSdk_BoardGetRgbLedGreenPin(void);
// IsoSdk_BoardGetRgbLedActiveOnLevel 관련 동작을 수행한다.
uint8_t  IsoSdk_BoardGetRgbLedActiveOnLevel(void);
// IsoSdk_Board slave1 버튼 입력을 읽는다.
uint8_t  IsoSdk_BoardReadSlave1ButtonPressed(void);
// IsoSdk_GpioWritePin 관련 동작을 수행한다.
void     IsoSdk_GpioWritePin(void *gpio_port, uint32_t pin, uint8_t level);
// IsoSdk_GpioSetPinsDirectionMask 관련 동작을 수행한다.
void     IsoSdk_GpioSetPinsDirectionMask(void *gpio_port, uint32_t pin_mask);

#endif
