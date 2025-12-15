// 이 모듈이 하는 일: 순수 게임 규칙과 스텝 처리 로직을 정의
import { CellType, Direction, GameState, Player } from "./GameState";
import { GRID_HEIGHT, GRID_WIDTH, TARGET_AREA_RATIO } from "./config";

// 영역/플레이어 초기화는 서버에서도 그대로 재사용할 수 있도록 순수 함수로 유지
export function createGrid(width: number, height: number): CellType[][] {
  return Array.from({ length: height }, () => new Array<CellType>(width).fill(CellType.Empty));
}

export function createInitialState(): GameState {
  // 최초 진입 시에는 모드 선택 화면만 필요하므로 메뉴 상태만 만든다.
  return {
    grid: createGrid(GRID_WIDTH, GRID_HEIGHT),
    players: [],
    mode: null,
    phase: "mode_select",
    tick: 0,
    width: GRID_WIDTH,
    height: GRID_HEIGHT,
  };
}

export function startSoloMode(): GameState {
  const grid = createGrid(GRID_WIDTH, GRID_HEIGHT);
  const players = createSoloPlayers(grid);

  // Solo는 플레이어만 만들고, 실제 게임 시작은 대기 상태에서 키 입력으로 진행한다.
  return {
    grid,
    players,
    mode: "solo",
    phase: "waiting",
    tick: 0,
    width: GRID_WIDTH,
    height: GRID_HEIGHT,
  };
}

export function startPvpMode(): GameState {
  const grid = createGrid(GRID_WIDTH, GRID_HEIGHT);
  const players = createPvpPlayers(grid);

  return {
    grid,
    players,
    mode: "pvp",
    phase: "waiting",
    tick: 0,
    width: GRID_WIDTH,
    height: GRID_HEIGHT,
  };
}

export function createSoloPlayers(grid: CellType[][]): Player[] {
  const zoneSize = 6;
  const startX = Math.floor((GRID_WIDTH - zoneSize) / 2);
  const startY = Math.floor((GRID_HEIGHT - zoneSize) / 2);

  // 가운데 영토만 배치해두고, 플레이어는 오른쪽 변 끝에서 시작해 바로 바깥을 향하게 둔다.
  for (let y = startY; y < startY + zoneSize; y += 1) {
    for (let x = startX; x < startX + zoneSize; x += 1) {
      grid[y][x] = CellType.Player1Territory;
    }
  }

  const player: Player = {
    id: 1,
    x: startX + zoneSize - 1,
    y: startY + Math.floor(zoneSize / 2),
    dirX: 0,
    dirY: 0,
    isAlive: true,
    inTrail: false,
    color: "#f97316",
  };

  return [player];
}

export function createPvpPlayers(grid: CellType[][]): Player[] {
  const zoneSize = 6;
  const centerY = Math.floor((GRID_HEIGHT - zoneSize) / 2);

  // 좌우에 동일한 크기의 시작 영토를 만들어 두어 공정성을 맞춘다.
  for (let y = centerY; y < centerY + zoneSize; y += 1) {
    for (let x = 0; x < zoneSize; x += 1) {
      grid[y][x] = CellType.Player1Territory;
    }
    for (let x = GRID_WIDTH - zoneSize; x < GRID_WIDTH; x += 1) {
      grid[y][x] = CellType.Player2Territory;
    }
  }

  const p1: Player = {
    id: 1,
    x: zoneSize - 1,
    y: centerY + Math.floor(zoneSize / 2),
    dirX: 0,
    dirY: 0,
    isAlive: true,
    inTrail: false,
    color: "#f97316",
  };

  const p2: Player = {
    id: 2,
    x: GRID_WIDTH - zoneSize,
    y: centerY + Math.floor(zoneSize / 2),
    dirX: 0,
    dirY: 0,
    isAlive: true,
    inTrail: false,
    color: "#60a5fa",
  };

  return [p1, p2];
}

export function computeAreaRatio(state: GameState): number {
  // UI는 Player1의 영역 확장을 기준으로 진행 상황을 보여주므로 해당 셀만 센다.
  let owned = 0;
  const total = state.width * state.height;

  for (let y = 0; y < state.height; y += 1) {
    for (let x = 0; x < state.width; x += 1) {
      if (state.grid[y][x] === CellType.Player1Territory) {
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

function getTerritoryCell(playerId: number): CellType {
  return playerId === 1 ? CellType.Player1Territory : CellType.Player2Territory;
}

function getTrailCell(playerId: number): CellType {
  return playerId === 1 ? CellType.Player1Trail : CellType.Player2Trail;
}

// 영역 닫기 시 flood fill로 외부만 표시한 뒤 내부를 해당 플레이어의 영역으로 채운다
export function closeAreaAndFill(state: GameState, playerId: number): void {
  const { width, height, grid } = state;
  const outside = Array.from({ length: height }, () => new Array<boolean>(width).fill(false));
  const queue: Array<{ x: number; y: number }> = [];

  const isWall = (cell: CellType) =>
    cell === CellType.Player1Territory ||
    cell === CellType.Player2Territory ||
    cell === CellType.Player1Trail ||
    cell === CellType.Player2Trail;

  const tryPush = (x: number, y: number) => {
    if (x < 0 || x >= width || y < 0 || y >= height) return;
    if (outside[y][x]) return;
    const cell = grid[y][x];
    if (isWall(cell)) return;
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

  const ownedCell = getTerritoryCell(playerId);
  const trailCell = getTrailCell(playerId);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (grid[y][x] === CellType.Empty && !outside[y][x]) {
        grid[y][x] = ownedCell;
      }
      if (grid[y][x] === trailCell) {
        grid[y][x] = ownedCell;
      }
    }
  }
}

// stepGame은 입력 방향을 받아서 state를 복사한 뒤 변경 사항만 반영한다
export function stepGame(state: GameState, inputDirs: Record<number, Direction>): GameState {
  if (state.phase !== "playing") return state;

  const s = cloneState(state);

  for (const p of s.players) {
    if (!p.isAlive) continue;

    const dir = inputDirs[p.id];
    if (dir && (dir.x !== 0 || dir.y !== 0)) {
      p.dirX = dir.x;
      p.dirY = dir.y;
    }

    const nextX = p.x + p.dirX;
    const nextY = p.y + p.dirY;

    if (nextX < 0 || nextX >= s.width || nextY < 0 || nextY >= s.height) {
      p.isAlive = false;
      s.phase = "dead";
      continue;
    }

    const cell = s.grid[nextY][nextX];

    if (
      p.inTrail &&
      (cell === CellType.Player1Trail || cell === CellType.Player2Trail)
    ) {
      p.isAlive = false;
      s.phase = "dead";
      continue;
    }

    if (!p.inTrail && s.grid[p.y][p.x] === getTerritoryCell(p.id) && cell === CellType.Empty) {
      p.inTrail = true;
    }

    p.x = nextX;
    p.y = nextY;

    if (p.inTrail) {
      if (cell === getTerritoryCell(p.id)) {
        closeAreaAndFill(s, p.id);
        p.inTrail = false;
      } else {
        s.grid[p.y][p.x] = getTrailCell(p.id);
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
