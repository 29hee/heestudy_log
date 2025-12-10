// 이 모듈이 하는 일: 게임 전역에서 사용하는 상수 값을 정의
export const GRID_WIDTH = 48;
export const GRID_HEIGHT = 32;
export const TICK_MS = 70; // ms per tick
export const TARGET_AREA_RATIO = 0.6; // 60% 채우면 승리

export const KEY_DIRS: Record<string, { x: number; y: number }> = {
  ArrowUp: { x: 0, y: -1 },
  ArrowDown: { x: 0, y: 1 },
  ArrowLeft: { x: -1, y: 0 },
  ArrowRight: { x: 1, y: 0 },
  KeyW: { x: 0, y: -1 },
  KeyS: { x: 0, y: 1 },
  KeyA: { x: -1, y: 0 },
  KeyD: { x: 1, y: 0 },
};
