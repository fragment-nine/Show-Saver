import type { Timecode } from "../../types/engine";
import { formatTimecode } from "../../types/engine";

interface Props {
  timecode: Timecode | null;
  songName: string;
  isRecording: boolean;
}

export function TimecodeDisplay({ timecode, songName, isRecording }: Props) {
  const tc = timecode ? formatTimecode(timecode) : "--:--:--:--";

  return (
    <div className="tc-display">
      <div className="tc-value" style={{ fontFamily: "monospace", fontSize: "3rem", fontWeight: "bold" }}>
        {tc}
      </div>
      <div className="tc-song" style={{ fontSize: "1.2rem", marginTop: "0.5rem" }}>
        {songName || "---"}
      </div>
      {isRecording && (
        <div className="tc-recording" style={{ color: "red", fontWeight: "bold", marginTop: "0.25rem" }}>
          ● RECORDING
        </div>
      )}
    </div>
  );
}
