import type { EngineStatus } from "../../types/engine";
import { TimecodeDisplay } from "./TimecodeDisplay";
import { VuMeter } from "./VuMeter";

interface Props {
  status: EngineStatus | null;
}

export function MainPage({ status }: Props) {
  return (
    <div style={{ display: "flex", gap: "2rem", padding: "2rem", alignItems: "flex-start" }}>
      <div style={{ flex: 1 }}>
        <TimecodeDisplay
          timecode={status?.timecode ?? null}
          songName={status?.current_song ?? ""}
          isRecording={status?.is_recording ?? false}
        />

        <div style={{ marginTop: "2rem", display: "flex", gap: "1rem" }}>
          <button style={{ padding: "0.75rem 2rem", fontSize: "1rem", background: "#2d5a27", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
            ARM
          </button>
          <button style={{ padding: "0.75rem 2rem", fontSize: "1rem", background: "#1a4a8a", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
            MANUAL START
          </button>
          <button style={{ padding: "0.75rem 2rem", fontSize: "1rem", background: "#8a1a1a", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
            STOP
          </button>
        </div>

        <div style={{ marginTop: "2rem", color: "#aaa", fontSize: "0.9rem" }}>
          <div>State: {status?.state ?? "idle"}</div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "0.5rem" }}>
        <VuMeter levels={status?.tc_levels ?? null} label="TC" />
        <VuMeter levels={status?.pgm_levels ?? null} label="PGM" />
      </div>
    </div>
  );
}
