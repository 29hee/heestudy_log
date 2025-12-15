// 이 모듈이 하는 일: 게임 전역에서 사용하는 상수 값을 정의
export const GRID_WIDTH = 48;
export const GRID_HEIGHT = 32;
export const TICK_MS = 70; // ms per tick
export const TARGET_AREA_RATIO = 0.6; // 60% 채우면 승리

// WASD를 Player 1에, 방향키를 Player 2에 전담시켜
// 입력이 동시에 들어와도 서로의 방향 상태를 덮어쓰지 않게 한다.
export const KEY_DIRS_P1: Record<string, { x: number; y: number }> = {
  KeyW: { x: 0, y: -1 },
  KeyS: { x: 0, y: 1 },
  KeyA: { x: -1, y: 0 },
  KeyD: { x: 1, y: 0 },
};

export const KEY_DIRS_P2: Record<string, { x: number; y: number }> = {
  ArrowUp: { x: 0, y: -1 },
  ArrowDown: { x: 0, y: 1 },
  ArrowLeft: { x: -1, y: 0 },
  ArrowRight: { x: 1, y: 0 },
};
