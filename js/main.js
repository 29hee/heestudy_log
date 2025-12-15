const GRID_WIDTH = 96;
const GRID_HEIGHT = 64;
const TICK_MS = 70;
const TARGET_AREA_RATIO = 0.6;

const CELL = {
  EMPTY: 0,
  P1_TERRITORY: 1,
  P2_TERRITORY: 2,
  P1_TRAIL: 3,
  P2_TRAIL: 4,
};

const KEY_DIRS_P1 = {
  KeyW: { x: 0, y: -1 },
  KeyS: { x: 0, y: 1 },
  KeyA: { x: -1, y: 0 },
  KeyD: { x: 1, y: 0 },
};

const KEY_DIRS_P2 = {
  ArrowUp: { x: 0, y: -1 },
  ArrowDown: { x: 0, y: 1 },
  ArrowLeft: { x: -1, y: 0 },
  ArrowRight: { x: 1, y: 0 },
};

const PLAYER_CELL = {
  1: { territory: CELL.P1_TERRITORY, trail: CELL.P1_TRAIL, color: "#f97316" },
  2: { territory: CELL.P2_TERRITORY, trail: CELL.P2_TRAIL, color: "#60a5fa" },
};

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const areaText = document.getElementById("areaText");
const bestText = document.getElementById("bestText");
const stateText = document.getElementById("stateText");
const resetBtn = document.getElementById("resetBtn");

let bestAreaRatio = 0;
let gameState = null;
let lastTickTime = 0;

const pendingDirs = {
  1: { x: 0, y: 0 },
  2: { x: 0, y: 0 },
};

function createGrid(w, h) {
  const g = new Array(h);
  for (let y = 0; y < h; y++) {
    g[y] = new Array(w).fill(CELL.EMPTY);
  }
  return g;
}

function createInitialState() {
  return {
    grid: createGrid(GRID_WIDTH, GRID_HEIGHT),
    players: [],
    phase: "mode_select",
    mode: null,
    tick: 0,
    width: GRID_WIDTH,
    height: GRID_HEIGHT,
  };
}

function resetPendingDirs() {
  pendingDirs[1] = { x: 0, y: 0 };
  pendingDirs[2] = { x: 0, y: 0 };
}

function startSoloMode() {
  resetPendingDirs();
  // Recreate the board so stale trails or territory from other modes never leak into solo runs.
  gameState = {
    ...gameState,
    grid: createGrid(GRID_WIDTH, GRID_HEIGHT),
    players: createSoloPlayers(),
    mode: "solo",
    phase: "waiting",
    tick: 0,
  };
  updateHud(gameState);
  render(gameState);
}

function createSoloPlayers() {
  const grid = gameState.grid;
  const zoneSize = 6;
  const startX = Math.floor((GRID_WIDTH - zoneSize) / 2);
  const startY = Math.floor((GRID_HEIGHT - zoneSize) / 2);

  for (let y = startY; y < startY + zoneSize; y++) {
    for (let x = startX; x < startX + zoneSize; x++) {
      grid[y][x] = CELL.P1_TERRITORY;
    }
  }

  const player = {
    id: 1,
    x: startX + zoneSize - 1,
    y: startY + Math.floor(zoneSize / 2),
    dirX: 0,
    dirY: 0,
    isAlive: true,
    inTrail: false,
    color: PLAYER_CELL[1].color,
  };

  return [player];
}

function startPvpMode() {
  resetPendingDirs();
  // Always clear to a fresh grid before spawning both players, otherwise captured land from solo play would persist.
  gameState = {
    ...gameState,
    grid: createGrid(GRID_WIDTH, GRID_HEIGHT),
    players: createPvpPlayers(),
    mode: "pvp",
    phase: "waiting",
    tick: 0,
  };
  updateHud(gameState);
  render(gameState);
}

function createPvpPlayers() {
  const grid = gameState.grid;
  const zoneSize = 6;
  const centerY = Math.floor((GRID_HEIGHT - zoneSize) / 2);

  for (let y = centerY; y < centerY + zoneSize; y++) {
    for (let x = 0; x < zoneSize; x++) {
      grid[y][x] = CELL.P1_TERRITORY;
    }
  }

  for (let y = centerY; y < centerY + zoneSize; y++) {
    for (let x = GRID_WIDTH - zoneSize; x < GRID_WIDTH; x++) {
      grid[y][x] = CELL.P2_TERRITORY;
    }
  }

  const p1 = {
    id: 1,
    x: zoneSize - 1,
    y: centerY + Math.floor(zoneSize / 2),
    dirX: 0,
    dirY: 0,
    isAlive: true,
    inTrail: false,
    color: PLAYER_CELL[1].color,
  };

  const p2 = {
    id: 2,
    x: GRID_WIDTH - zoneSize,
    y: centerY + Math.floor(zoneSize / 2),
    dirX: 0,
    dirY: 0,
    isAlive: true,
    inTrail: false,
    color: PLAYER_CELL[2].color,
  };

  return [p1, p2];
}

function computeAreaRatio(state) {
  const { width, height, grid } = state;
  const codes = PLAYER_CELL[1];
  let owned = 0;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const cell = grid[y][x];
      if (cell === codes.territory || cell === codes.trail) {
        owned++;
      }
    }
  }

  return owned / (width * height);
}

function handleModeSelection(code) {
  if (code === "Digit1") {
    startSoloMode();
    return true;
  }
  if (code === "Digit2") {
    startPvpMode();
    return true;
  }
  return false;
}

function applyDirectionFromKey(code) {
  let applied = false;
  const dirP1 = KEY_DIRS_P1[code];
  if (dirP1) {
    pendingDirs[1] = dirP1;
    applied = true;
  }
  const dirP2 = KEY_DIRS_P2[code];
  if (dirP2) {
    pendingDirs[2] = dirP2;
    applied = true;
  }
  return applied;
}

window.addEventListener("keydown", (e) => {
  if (!gameState) return;

  if (gameState.phase === "mode_select") {
    if (handleModeSelection(e.code)) return;
  }

  if (!gameState.players.length) return;

  const applied = applyDirectionFromKey(e.code);

  if (applied && gameState.phase === "waiting") {
    // First movement input transitions the game into active play.
    gameState.phase = "playing";
    lastTickTime = performance.now();
  }
});

function stepGame(state) {
  if (state.phase !== "playing") return state;

  for (const player of state.players) {
    if (!player.isAlive) continue;

    const dir = pendingDirs[player.id];
    if (dir) {
      player.dirX = dir.x;
      player.dirY = dir.y;
    }

    if (player.dirX === 0 && player.dirY === 0) continue;

    const nextX = player.x + player.dirX;
    const nextY = player.y + player.dirY;

    if (nextX < 0 || nextX >= state.width || nextY < 0 || nextY >= state.height) {
      player.isAlive = false;
      state.phase = "dead";
      continue;
    }

    const cell = state.grid[nextY][nextX];
    const codes = PLAYER_CELL[player.id];
    const enemyTerritory =
      player.id === 1 ? CELL.P2_TERRITORY : CELL.P1_TERRITORY;
    const enemyTrail = player.id === 1 ? CELL.P2_TRAIL : CELL.P1_TRAIL;

    if (cell === enemyTerritory || cell === enemyTrail) {
      player.isAlive = false;
      state.phase = "dead";
      continue;
    }

    const isTrailCell = cell === CELL.P1_TRAIL || cell === CELL.P2_TRAIL;
    if (player.inTrail && isTrailCell) {
      player.isAlive = false;
      state.phase = "dead";
      continue;
    }

    const leavingOwnLand =
      !player.inTrail &&
      state.grid[player.y][player.x] === codes.territory &&
      cell === CELL.EMPTY;

    if (leavingOwnLand) {
      player.inTrail = true;
    }

    player.x = nextX;
    player.y = nextY;

    if (player.inTrail) {
      if (cell === codes.territory) {
        closeAreaAndFill(state.grid, codes);
        player.inTrail = false;
      } else if (cell === CELL.EMPTY) {
        state.grid[player.y][player.x] = codes.trail;
      }
    }
  }

  state.tick += 1;

  const ratio = computeAreaRatio(state);
  if (ratio >= TARGET_AREA_RATIO && state.phase === "playing") {
    state.phase = "win";
  }

  return state;
}

function closeAreaAndFill(grid, codes) {
  const height = grid.length;
  const width = grid[0].length;
  const outside = Array.from({ length: height }, () => new Array(width).fill(false));
  const q = [];

  // Treat any non-empty cell as a wall so captures never overwrite opponent territory or existing trails.
  const tryPush = (x, y) => {
    if (x < 0 || x >= width || y < 0 || y >= height) return;
    if (outside[y][x]) return;
    if (grid[y][x] !== CELL.EMPTY) return;
    outside[y][x] = true;
    q.push({ x, y });
  };

  for (let x = 0; x < width; x++) {
    tryPush(x, 0);
    tryPush(x, height - 1);
  }
  for (let y = 0; y < height; y++) {
    tryPush(0, y);
    tryPush(width - 1, y);
  }

  while (q.length) {
    const { x, y } = q.pop();
    tryPush(x + 1, y);
    tryPush(x - 1, y);
    tryPush(x, y + 1);
    tryPush(x, y - 1);
  }

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (!outside[y][x] && grid[y][x] === CELL.EMPTY) {
        grid[y][x] = codes.territory;
      }
      if (grid[y][x] === codes.trail) {
        grid[y][x] = codes.territory;
      }
    }
  }
}

function resizeCanvas() {
  const container = canvas.parentElement;
  const { clientWidth, clientHeight } = container;

  const aspectGrid = GRID_WIDTH / GRID_HEIGHT;
  const aspectContainer = clientWidth / clientHeight;

  let drawW;
  let drawH;
  if (aspectContainer > aspectGrid) {
    drawH = clientHeight;
    drawW = drawH * aspectGrid;
  } else {
    drawW = clientWidth;
    drawH = drawW / aspectGrid;
  }

  canvas.width = drawW * window.devicePixelRatio;
  canvas.height = drawH * window.devicePixelRatio;
  canvas.style.width = `${drawW}px`;
  canvas.style.height = `${drawH}px`;

  ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
}

function render(state) {
  if (!ctx || !state) return;

  const w = canvas.width / window.devicePixelRatio;
  const h = canvas.height / window.devicePixelRatio;
  const cellW = w / state.width;
  const cellH = h / state.height;

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#020617";
  ctx.fillRect(0, 0, w, h);

  ctx.strokeStyle = "rgba(15,23,42,0.6)";
  ctx.lineWidth = 0.5;
  for (let x = 0; x <= state.width; x++) {
    ctx.beginPath();
    ctx.moveTo(x * cellW, 0);
    ctx.lineTo(x * cellW, h);
    ctx.stroke();
  }
  for (let y = 0; y <= state.height; y++) {
    ctx.beginPath();
    ctx.moveTo(0, y * cellH);
    ctx.lineTo(w, y * cellH);
    ctx.stroke();
  }

  for (let y = 0; y < state.height; y++) {
    for (let x = 0; x < state.width; x++) {
      const cell = state.grid[y][x];
      if (cell === CELL.P1_TERRITORY) {
        ctx.fillStyle = "rgba(93, 242, 200, 0.85)";
        ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
      } else if (cell === CELL.P2_TERRITORY) {
        ctx.fillStyle = "rgba(96, 165, 250, 0.8)";
        ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
      } else if (cell === CELL.P1_TRAIL) {
        ctx.fillStyle = "rgba(250, 204, 21, 0.9)";
        ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
      } else if (cell === CELL.P2_TRAIL) {
        ctx.fillStyle = "rgba(34, 211, 238, 0.9)";
        ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
      }
    }
  }

  if (Array.isArray(state.players)) {
    for (const p of state.players) {
      if (!p.isAlive) continue;
      ctx.fillStyle = p.color || "#f97316";
      const px = p.x * cellW;
      const py = p.y * cellH;
      ctx.beginPath();
      ctx.roundRect(px + 2, py + 2, cellW - 4, cellH - 4, 4);
      ctx.fill();
    }
  }

  if (state.phase === "waiting" && state.players.length) {
    ctx.fillStyle = "rgba(255,255,255,0.9)";
    ctx.font = "bold 32px system-ui";
    ctx.textAlign = "center";
    ctx.fillText("Press move to start", w / 2, h / 2);
  }

  if (state.phase === "mode_select") {
    ctx.fillStyle = "rgba(0,0,0,0.6)";
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 32px system-ui";
    ctx.textAlign = "center";
    ctx.fillText("SELECT MODE", w / 2, h / 2 - 40);
    ctx.font = "20px system-ui";
    ctx.fillText("1 - SOLO", w / 2, h / 2 + 10);
    ctx.fillText("2 - LOCAL PVP", w / 2, h / 2 + 40);
  }
}

function updateHud(state) {
  const areaRatio = computeAreaRatio(state);
  const areaPercent = Math.round(areaRatio * 100);
  bestAreaRatio = Math.max(bestAreaRatio, areaRatio);

  areaText.textContent = `${areaPercent}%`;
  bestText.textContent = `${Math.round(bestAreaRatio * 100)}%`;

  if (state.phase === "playing") {
    stateText.textContent = "Playing";
  } else if (state.phase === "win") {
    stateText.textContent = "Win!";
  } else if (state.phase === "dead") {
    stateText.textContent = "Dead";
  } else if (state.phase === "waiting") {
    stateText.textContent = "Ready";
  } else {
    stateText.textContent = "Select mode";
  }
}

function resetGame() {
  // Reset back to menu-only state so mode selectors own player creation.
  gameState = createInitialState();
  resetPendingDirs();
  lastTickTime = performance.now();
  updateHud(gameState);
  render(gameState);
}

function loop(now) {
  requestAnimationFrame(loop);
  if (!gameState) return;

  if (gameState.phase !== "playing") {
    render(gameState);
    return;
  }

  const elapsed = now - lastTickTime;
  if (elapsed < TICK_MS) return;

  lastTickTime = now;
  gameState = stepGame(gameState);
  updateHud(gameState);
  render(gameState);
}

window.addEventListener("resize", () => {
  resizeCanvas();
  if (gameState) render(gameState);
});

resetBtn.addEventListener("click", () => {
  resetGame();
});

resizeCanvas();
resetGame();
requestAnimationFrame(loop);
