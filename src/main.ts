// 이 모듈이 하는 일: DOM과 순수 게임 모듈을 연결해 단일플레이 루프 실행
import { createInputController } from "./game/Input";
import { Renderer } from "./game/Renderer";
import { computeAreaRatio, createInitialState, stepGame } from "./game/GameCore";
import { Direction } from "./game/GameState";
import { GRID_HEIGHT, GRID_WIDTH, TICK_MS } from "./game/config";
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

  if (gameState.phase === "playing") {
    stateText.textContent = "Playing";
  } else if (gameState.phase === "win") {
    stateText.textContent = "Win!";
  } else {
    stateText.textContent = "Dead";
  }
}

function resetGame() {
  gameState = createInitialState();
  input.setDirection({ x: 0, y: -1 });
  lastTickTime = performance.now();
  updateHud();
  renderer.render(gameState);
}

function loop(now: number) {
  requestAnimationFrame(loop);

  const elapsed = now - lastTickTime;
  if (elapsed >= TICK_MS) {
    lastTickTime = now;
    const dir: Direction = input.getDirection();
    gameState = stepGame(gameState, dir);
    socketStub.emitSnapshot(gameState);
    updateHud();
    renderer.render(gameState);
  }
}

window.addEventListener("resize", () => {
  renderer.resize(canvasCard, GRID_WIDTH, GRID_HEIGHT);
  renderer.render(gameState);
});

resetBtn.addEventListener("click", () => {
  resetGame();
});

renderer.resize(canvasCard, GRID_WIDTH, GRID_HEIGHT);
resetGame();
requestAnimationFrame(loop);

// 서버 authoritative로 옮길 때: socketStub.onSnapshot(state => { gameState = state; renderer.render(gameState); });
