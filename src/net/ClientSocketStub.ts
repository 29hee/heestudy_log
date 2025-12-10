// 이 모듈이 하는 일: WebSocket 연동을 위한 클라이언트 스텁 인터페이스 정의
import { Direction, GameState } from "../game/GameState";

export type ClientRole = "player" | "spectator";

// 실제 서버 연결 없이 인터페이스만 제공하는 더미 구현
export class ClientSocketStub {
  private snapshotHandler: ((state: GameState) => void) | null = null;

  connect(role: ClientRole): void {
    console.info(`Stub connect invoked with role=${role}`);
  }

  sendInput(dir: Direction): void {
    console.info("Stub sendInput", dir);
  }

  onSnapshot(callback: (state: GameState) => void): void {
    this.snapshotHandler = callback;
  }

  // 로컬 싱글플레이에서 서버 스냅샷이 없으므로 필요 시 외부에서 호출 가능
  emitSnapshot(state: GameState): void {
    if (this.snapshotHandler) {
      this.snapshotHandler(state);
    }
  }
}
