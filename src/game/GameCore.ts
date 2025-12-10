// 이 모듈이 하는 일: 순수 게임 규칙과 스텝 처리 로직을 정의
import { CellType, Direction, GameState, Player } from "./GameState";
import { GRID_HEIGHT, GRID_WIDTH, TARGET_AREA_RATIO } from "./config";

// 영역/플레이어 초기화는 서버에서도 그대로 재사용할 수 있도록 순수 함수로 유지
export function createGrid(width: number, height: number): CellType[][] {
  return Array.from({ length: height }, () => new Array<CellType>(width).fill(CellType.Empty));
}

export function createInitialState(): GameState {
  const grid = createGrid(GRID_WIDTH, GRID_HEIGHT);
  const startY = GRID_HEIGHT - 4;

  for (let y = startY; y < GRID_HEIGHT; y += 1) {
    for (let x = 0; x < GRID_WIDTH; x += 1) {
      grid[y][x] = CellType.Owned;
    }
  }

  const player: Player = {
    id: 1,
    x: Math.floor(GRID_WIDTH / 2),
    y: startY - 1,
    dirX: 0,
    dirY: -1,
    isAlive: true,
    inTrail: false,
  };

  return {
    grid,
    players: [player],
    phase: "playing",
    tick: 0,
    width: GRID_WIDTH,
    height: GRID_HEIGHT,
  };
}

export function computeAreaRatio(state: GameState): number {
  let owned = 0;
  const total = state.width * state.height;

  for (let y = 0; y < state.height; y += 1) {
    for (let x = 0; x < state.width; x += 1) {
      if (state.grid[y][x] === CellType.Owned) {
        owned += 1;
      }
    }
  }

  return owned / total;
}

function cloneState(state: GameState): GameState {
  return {
    ...state,
    grid: state.grid.map((row) => [...row]),
    players: state.players.map((p) => ({ ...p })),
  };
}

// 영역 닫기 시 flood fill로 외부만 표시한 뒤 내부를 Owned로 채운다
export function closeAreaAndFill(state: GameState): void {
  const { width, height, grid } = state;
  const outside = Array.from({ length: height }, () => new Array<boolean>(width).fill(false));
  const queue: Array<{ x: number; y: number }> = [];

  const tryPush = (x: number, y: number) => {
    if (x < 0 || x >= width || y < 0 || y >= height) return;
    if (outside[y][x]) return;
    const cell = grid[y][x];
    if (cell === CellType.Owned || cell === CellType.Trail) return;
    outside[y][x] = true;
    queue.push({ x, y });
  };

  for (let x = 0; x < width; x += 1) {
    tryPush(x, 0);
    tryPush(x, height - 1);
  }
  for (let y = 0; y < height; y += 1) {
    tryPush(0, y);
    tryPush(width - 1, y);
  }

  while (queue.length > 0) {
    const { x, y } = queue.shift() as { x: number; y: number };
    tryPush(x + 1, y);
    tryPush(x - 1, y);
    tryPush(x, y + 1);
    tryPush(x, y - 1);
  }

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (grid[y][x] === CellType.Empty && !outside[y][x]) {
        grid[y][x] = CellType.Owned;
      }
      if (grid[y][x] === CellType.Trail) {
        grid[y][x] = CellType.Owned;
      }
    }
  }
}

// stepGame은 입력 방향을 받아서 state를 복사한 뒤 변경 사항만 반영한다
export function stepGame(state: GameState, inputDir: Direction): GameState {
  if (state.phase !== "playing") return state;

  const s = cloneState(state);

  for (const p of s.players) {
    if (!p.isAlive) continue;

    if (inputDir.x !== 0 || inputDir.y !== 0) {
      p.dirX = inputDir.x;
      p.dirY = inputDir.y;
    }

    const nextX = p.x + p.dirX;
    const nextY = p.y + p.dirY;

    if (nextX < 0 || nextX >= s.width || nextY < 0 || nextY >= s.height) {
      p.isAlive = false;
      s.phase = "dead";
      continue;
    }

    const cell = s.grid[nextY][nextX];

    if (p.inTrail && cell === CellType.Trail) {
      p.isAlive = false;
      s.phase = "dead";
      continue;
    }

    if (!p.inTrail && s.grid[p.y][p.x] === CellType.Owned && cell === CellType.Empty) {
      p.inTrail = true;
    }

    p.x = nextX;
    p.y = nextY;

    if (p.inTrail) {
      if (cell === CellType.Owned) {
        closeAreaAndFill(s);
        p.inTrail = false;
      } else {
        s.grid[p.y][p.x] = CellType.Trail;
      }
    }
  }

  s.tick += 1;

  const ratio = computeAreaRatio(s);
  if (ratio >= TARGET_AREA_RATIO && s.phase === "playing") {
    s.phase = "win";
  }

  return s;
}
