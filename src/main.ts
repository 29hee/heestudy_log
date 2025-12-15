// 이 모듈이 하는 일: DOM과 순수 게임 모듈을 연결해 단일플레이 루프 실행
import { createInputController } from "./game/Input";
import { Renderer } from "./game/Renderer";
import {
  computeAreaRatio,
  createInitialState,
  startPvpMode,
  startSoloMode,
  stepGame,
} from "./game/GameCore";
import { GRID_HEIGHT, GRID_WIDTH, KEY_DIRS_P1, KEY_DIRS_P2, TICK_MS } from "./game/config";
import { ClientSocketStub } from "./net/ClientSocketStub";

const canvas = document.getElementById("gameCanvas") as HTMLCanvasElement;
const areaText = document.getElementById("areaText") as HTMLElement;
const bestText = document.getElementById("bestText") as HTMLElement;
const stateText = document.getElementById("stateText") as HTMLElement;
const resetBtn = document.getElementById("resetBtn") as HTMLButtonElement;
const canvasCard = document.querySelector(".canvas-card") as HTMLElement;

const renderer = new Renderer(canvas);
const input = createInputController(window);
const socketStub = new ClientSocketStub();

let bestAreaRatio = 0;
let gameState = createInitialState();
let lastTickTime = performance.now();

function updateHud() {
  const areaRatio = computeAreaRatio(gameState);
  const areaPercent = Math.round(areaRatio * 100);
  bestAreaRatio = Math.max(bestAreaRatio, areaRatio);

  areaText.textContent = `${areaPercent}%`;
  bestText.textContent = `${Math.round(bestAreaRatio * 100)}%`;

  if (gameState.phase === "mode_select") {
    stateText.textContent = "Mode Select";
  } else if (gameState.phase === "waiting") {
    stateText.textContent = "Waiting";
  } else if (gameState.phase === "playing") {
    stateText.textContent = "Playing";
  } else if (gameState.phase === "win") {
    stateText.textContent = "Win!";
  } else {
    stateText.textContent = "Dead";
  }
}

function resetGame() {
  gameState = createInitialState();
  input.reset();
  lastTickTime = performance.now();
  updateHud();
  renderer.render(gameState);
}

function isMovementKey(code: string): boolean {
  return Boolean(KEY_DIRS_P1[code] || KEY_DIRS_P2[code]);
}

function loop(now: number) {
  requestAnimationFrame(loop);

  // 플레이 중이 아니면 HUD/렌더만 유지한다.
  if (gameState.phase !== "playing") {
    renderer.render(gameState);
    return;
  }

  const elapsed = now - lastTickTime;
  if (elapsed >= TICK_MS) {
    lastTickTime = now;
    const dirs = input.getDirections();
    gameState = stepGame(gameState, dirs);
    socketStub.emitSnapshot(gameState);
    updateHud();
    renderer.render(gameState);
  }
}

window.addEventListener("resize", () => {
  renderer.resize(canvasCard, GRID_WIDTH, GRID_HEIGHT);
  renderer.render(gameState);
});

window.addEventListener("keydown", (e) => {
  if (gameState.phase === "mode_select") {
    if (e.code === "Digit1") {
      gameState = startSoloMode();
    } else if (e.code === "Digit2") {
      gameState = startPvpMode();
    } else {
      return;
    }

    // 새 모드로 진입하면 입력 큐와 HUD를 초기화해 남은 상태가 끌려오지 않도록 한다.
    input.reset();
    lastTickTime = performance.now();
    updateHud();
    renderer.render(gameState);
    return;
  }

  if (gameState.phase === "waiting" && isMovementKey(e.code)) {
    gameState = { ...gameState, phase: "playing" };
    updateHud();
    renderer.render(gameState);
  }
});

resetBtn.addEventListener("click", () => {
  resetGame();
});

renderer.resize(canvasCard, GRID_WIDTH, GRID_HEIGHT);
resetGame();
requestAnimationFrame(loop);

// 서버 authoritative로 옮길 때: socketStub.onSnapshot(state => { gameState = state; renderer.render(gameState); });
