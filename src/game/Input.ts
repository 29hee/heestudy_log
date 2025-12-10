// 이 모듈이 하는 일: 키보드 입력을 수집하여 현재 방향 상태를 제공
import { Direction } from "./GameState";
import { KEY_DIRS } from "./config";

export interface InputController {
  getDirection(): Direction;
  setDirection(dir: Direction): void;
  dispose(): void;
}

export function createInputController(target: Window | HTMLElement): InputController {
  let currentDir: Direction = { x: 0, y: -1 };

  const handleKeyDown = (e: KeyboardEvent) => {
    const dir = KEY_DIRS[e.code];
    if (!dir) return;
    e.preventDefault();
    currentDir = dir;
  };

  target.addEventListener("keydown", handleKeyDown as EventListener);

  return {
    getDirection: () => currentDir,
    setDirection: (dir: Direction) => {
      currentDir = dir;
    },
    dispose: () => {
      target.removeEventListener("keydown", handleKeyDown as EventListener);
    },
  };
}
