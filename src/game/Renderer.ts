// 이 모듈이 하는 일: GameState를 받아 캔버스에 그리기만 담당
import { GameState, CellType } from "./GameState";

export class Renderer {
  private readonly canvas: HTMLCanvasElement;
  private readonly ctx: CanvasRenderingContext2D | null;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
  }

  resize(container: HTMLElement, gridWidth: number, gridHeight: number): void {
    const { clientWidth, clientHeight } = container;
    const aspectGrid = gridWidth / gridHeight;
    const aspectContainer = clientWidth / clientHeight;

    let drawW: number;
    let drawH: number;
    if (aspectContainer > aspectGrid) {
      drawH = clientHeight;
      drawW = drawH * aspectGrid;
    } else {
      drawW = clientWidth;
      drawH = drawW / aspectGrid;
    }

    this.canvas.width = drawW * window.devicePixelRatio;
    this.canvas.height = drawH * window.devicePixelRatio;
    this.canvas.style.width = `${drawW}px`;
    this.canvas.style.height = `${drawH}px`;

    if (this.ctx) {
      this.ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
    }
  }

  render(state: GameState): void {
    if (!this.ctx) return;

    const w = this.canvas.width / window.devicePixelRatio;
    const h = this.canvas.height / window.devicePixelRatio;
    const cellW = w / state.width;
    const cellH = h / state.height;

    this.ctx.clearRect(0, 0, w, h);
    this.ctx.fillStyle = "#020617";
    this.ctx.fillRect(0, 0, w, h);

    this.ctx.strokeStyle = "rgba(15,23,42,0.6)";
    this.ctx.lineWidth = 0.5;
    for (let x = 0; x <= state.width; x += 1) {
      this.ctx.beginPath();
      this.ctx.moveTo(x * cellW, 0);
      this.ctx.lineTo(x * cellW, h);
      this.ctx.stroke();
    }
    for (let y = 0; y <= state.height; y += 1) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y * cellH);
      this.ctx.lineTo(w, y * cellH);
      this.ctx.stroke();
    }

    for (let y = 0; y < state.height; y += 1) {
      for (let x = 0; x < state.width; x += 1) {
        const cell = state.grid[y][x];
        if (cell === CellType.Owned) {
          this.ctx.fillStyle = "rgba(93, 242, 200, 0.85)";
          this.ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
        } else if (cell === CellType.Trail) {
          this.ctx.fillStyle = "rgba(250, 204, 21, 0.9)";
          this.ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
        }
      }
    }

    for (const p of state.players) {
      if (!p.isAlive) continue;
      this.ctx.fillStyle = "#f97316";
      const px = p.x * cellW;
      const py = p.y * cellH;
      this.ctx.beginPath();
      this.ctx.roundRect(px + 2, py + 2, cellW - 4, cellH - 4, 4);
      this.ctx.fill();
    }
  }
}
