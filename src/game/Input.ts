// 이 모듈이 하는 일: 키보드 입력을 수집하여 현재 방향 상태를 제공
import { Direction } from "./GameState";
import { KEY_DIRS_P1, KEY_DIRS_P2 } from "./config";

export interface InputController {
  getDirections(): Record<number, Direction>;
  reset(): void;
  dispose(): void;
}

export function createInputController(target: Window | HTMLElement): InputController {
  // 플레이어마다 방향 상태를 따로 보관해 두어
  // 2인 모드에서 동시에 입력해도 서로 덮어쓰지 않는다.
  const currentDirs: Record<number, Direction> = {
    1: { x: 0, y: 0 },
    2: { x: 0, y: 0 },
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (KEY_DIRS_P1[e.code]) {
      e.preventDefault();
      currentDirs[1] = KEY_DIRS_P1[e.code];
      return;
    }
    if (KEY_DIRS_P2[e.code]) {
      e.preventDefault();
      currentDirs[2] = KEY_DIRS_P2[e.code];
    }
  };

  target.addEventListener("keydown", handleKeyDown as EventListener);

  return {
    getDirections: () => ({ ...currentDirs }),
    reset: () => {
      currentDirs[1] = { x: 0, y: 0 };
      currentDirs[2] = { x: 0, y: 0 };
    },
    dispose: () => {
      target.removeEventListener("keydown", handleKeyDown as EventListener);
    },
  };
}
