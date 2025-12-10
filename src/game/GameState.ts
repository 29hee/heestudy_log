// 이 모듈이 하는 일: 게임 상태, 셀 타입, 플레이어 등의 데이터 모델을 정의

export enum CellType {
  Empty = 0,
  Owned = 1,
  Trail = 2,
}

export interface Player {
  id: number;
  x: number;
  y: number;
  dirX: number;
  dirY: number;
  isAlive: boolean;
  inTrail: boolean;
}

export interface GameState {
  grid: CellType[][];
  players: Player[];
  phase: "playing" | "win" | "dead";
  tick: number;
  width: number;
  height: number;
}

export interface Direction {
  x: number;
  y: number;
}
