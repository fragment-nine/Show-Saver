import type { Timecode } from "../../types/engine";
import { formatTimecode } from "../../types/engine";

interface Props {
  timecode: Timecode | null;
  songName: string;
  isRecording: boolean;
  state: string;
}

export function TimecodeDisplay({ timecode, songName, isRecording, state }: Props) {
  const tc = timecode ? formatTimecode(timecode) : "--:--:--:--";

  const stateColor =
    state === "recording"
      ? "text-red-rec"
      : state === "armed"
        ? "text-amber"
        : "text-text-secondary";

  return (
    <div className="panel relative">
      <span className="absolute top-3 right-4 text-xs uppercase tracking-widest text-text-secondary">
        timecode
      </span>

      <div className="font-mono text-[4rem] leading-none font-bold tracking-wider text-text-primary mt-2">
        {tc}
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="text-lg font-medium text-accent truncate max-w-[70%]">
          {songName || "---"}
        </div>
        <div className={`flex items-center gap-2 text-sm font-medium uppercase ${stateColor}`}>
          {isRecording && (
            <span className="w-2.5 h-2.5 rounded-full bg-red-rec animate-pulse shadow-[0_0_8px_rgba(231,76,60,0.8)]" />
          )}
          {state}
        </div>
      </div>
    </div>
  );
}
