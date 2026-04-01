import type { EngineStatus, Settings } from "../../types/engine";
import { TimecodeDisplay } from "./TimecodeDisplay";
import { VuMeter } from "./VuMeter";
import { EnableToggles } from "./EnableToggles";

interface Props {
  status: EngineStatus | null;
  settings: Settings | null;
  onSaveSettings: (s: Settings) => void;
}

export function MainPage({ status, settings, onSaveSettings }: Props) {
  return (
    <div className="flex flex-col gap-4 p-5 max-w-2xl mx-auto">
      {/* Enable Toggles */}
      {settings && <EnableToggles settings={settings} onSave={onSaveSettings} />}

      {/* Manual Start / Stop */}
      <div className="grid grid-cols-2 gap-3">
        <button className="btn-green py-3 text-base">
          Manual Start
        </button>
        <button className="btn-red py-3 text-base">
          Manual Stop
        </button>
      </div>

      {/* Audio Levels */}
      <div className="panel">
        <div className="panel-label">Audio Levels</div>
        <div className="flex flex-col gap-1.5">
          <VuMeter levels={status?.pgm_levels ?? null} label="PGM" />
          <VuMeter levels={status?.tc_levels ?? null} label="TC" />
        </div>
      </div>

      {/* Timecode Display */}
      <TimecodeDisplay
        timecode={status?.timecode ?? null}
        songName={status?.current_song ?? ""}
        isRecording={status?.is_recording ?? false}
        state={status?.state ?? "idle"}
      />
    </div>
  );
}
