import type { AudioDeviceInfo, Settings } from "../../types/engine";

interface Props {
  settings: Settings | null;
  devices: AudioDeviceInfo[];
  onSave: (s: Settings) => void;
}

export function SettingsPage({ settings, devices, onSave }: Props) {
  if (!settings) return <div>Loading settings...</div>;

  return (
    <div style={{ padding: "2rem" }}>
      <h2 style={{ marginBottom: "1.5rem" }}>Settings</h2>

      <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", gap: "1rem", alignItems: "center" }}>
        <label>Timecode Device</label>
        <select
          value={settings.tc_device ?? ""}
          onChange={(e) =>
            onSave({ ...settings, tc_device: e.target.value || null })
          }
        >
          <option value="">-- Select --</option>
          {devices.map((d) => (
            <option key={d.name} value={d.name}>
              {d.name} ({d.max_input_channels}ch)
            </option>
          ))}
        </select>

        <label>TC Channel</label>
        <input
          type="number"
          min={0}
          value={settings.tc_channel}
          onChange={(e) =>
            onSave({ ...settings, tc_channel: parseInt(e.target.value) || 0 })
          }
          style={{ width: "80px" }}
        />

        <label>Program Device</label>
        <select
          value={settings.pgm_device ?? ""}
          onChange={(e) =>
            onSave({ ...settings, pgm_device: e.target.value || null })
          }
        >
          <option value="">-- Same as TC --</option>
          {devices.map((d) => (
            <option key={d.name} value={d.name}>
              {d.name} ({d.max_input_channels}ch)
            </option>
          ))}
        </select>

        <label>PGM Channel</label>
        <input
          type="number"
          min={0}
          value={settings.pgm_channel}
          onChange={(e) =>
            onSave({ ...settings, pgm_channel: parseInt(e.target.value) || 0 })
          }
          style={{ width: "80px" }}
        />

        <label>Output Folder</label>
        <input
          type="text"
          value={settings.output_folder}
          onChange={(e) =>
            onSave({ ...settings, output_folder: e.target.value })
          }
          style={{ width: "100%" }}
        />

        <label>TrackMaster CSV</label>
        <input
          type="text"
          value={settings.track_master_csv}
          onChange={(e) =>
            onSave({ ...settings, track_master_csv: e.target.value })
          }
          style={{ width: "100%" }}
        />

        <label>Sample Rate</label>
        <select
          value={settings.sample_rate}
          onChange={(e) =>
            onSave({ ...settings, sample_rate: parseInt(e.target.value) })
          }
        >
          <option value={44100}>44100 Hz</option>
          <option value={48000}>48000 Hz</option>
          <option value={96000}>96000 Hz</option>
        </select>

        <label>Timecode FPS</label>
        <select
          value={settings.fps}
          onChange={(e) =>
            onSave({ ...settings, fps: parseInt(e.target.value) })
          }
        >
          <option value={24}>24 fps</option>
          <option value={25}>25 fps</option>
          <option value={30}>30 fps (default)</option>
        </select>
      </div>
    </div>
  );
}
