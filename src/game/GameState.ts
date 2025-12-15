// 이 모듈이 하는 일: 게임 상태, 셀 타입, 플레이어 등의 데이터 모델을 정의

export enum CellType {
  Empty = 0,
  Player1Territory = 1,
  Player2Territory = 2,
  Player1Trail = 3,
  Player2Trail = 4,
}

export interface Player {
  id: number;
  x: number;
  y: number;
  dirX: number;
  dirY: number;
  isAlive: boolean;
  inTrail: boolean;
  color: string;
}

export interface GameState {
  grid: CellType[][];
  players: Player[];
  mode: "solo" | "pvp" | null;
  phase: "mode_select" | "waiting" | "playing" | "win" | "dead";
  tick: number;
  width: number;
  height: number;
}

export interface Direction {
  x: number;
  y: number;
}
