import type { AudioDeviceInfo, Settings } from "../../types/engine";

interface Props {
  settings: Settings | null;
  devices: AudioDeviceInfo[];
  onSave: (s: Settings) => void;
  onRefreshDevices: () => void;
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="panel">
      <div className="panel-label">{label}</div>
      <div className="flex flex-col gap-3">{children}</div>
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-4">
      <label className="text-sm text-text-secondary w-40 shrink-0">{label}</label>
      <div className="flex-1">{children}</div>
    </div>
  );
}

export function SettingsPage({ settings, devices, onSave, onRefreshDevices }: Props) {
  if (!settings) {
    return <div className="p-6 text-text-secondary">Loading settings...</div>;
  }

  return (
    <div className="flex flex-col gap-4 p-5 max-w-2xl mx-auto">
      {/* Refresh Button */}
      <button onClick={onRefreshDevices} className="btn-blue w-full py-2.5">
        Refresh Audio Devices
      </button>

      {/* Audio Devices */}
      <Section label="Audio Devices">
        <Field label="Timecode Device">
          <select
            className="w-full"
            value={settings.tc_device ?? ""}
            onChange={(e) => onSave({ ...settings, tc_device: e.target.value || null })}
          >
            <option value="">-- Select --</option>
            {devices.map((d) => (
              <option key={d.name} value={d.name}>
                {d.name} ({d.max_input_channels}ch)
              </option>
            ))}
          </select>
        </Field>

        <Field label="TC Channel">
          <input
            type="number"
            min={0}
            className="w-24"
            value={settings.tc_channel}
            onChange={(e) => onSave({ ...settings, tc_channel: parseInt(e.target.value) || 0 })}
          />
        </Field>

        <Field label="Program Device">
          <select
            className="w-full"
            value={settings.pgm_device ?? ""}
            onChange={(e) => onSave({ ...settings, pgm_device: e.target.value || null })}
          >
            <option value="">-- Same as TC --</option>
            {devices.map((d) => (
              <option key={d.name} value={d.name}>
                {d.name} ({d.max_input_channels}ch)
              </option>
            ))}
          </select>
        </Field>

        <Field label="PGM Channel">
          <input
            type="number"
            min={0}
            className="w-24"
            value={settings.pgm_channel}
            onChange={(e) => onSave({ ...settings, pgm_channel: parseInt(e.target.value) || 0 })}
          />
        </Field>
      </Section>

      {/* Output Paths */}
      <Section label="Output Paths">
        <Field label="Output Folder">
          <input
            type="text"
            className="w-full"
            value={settings.output_folder}
            onChange={(e) => onSave({ ...settings, output_folder: e.target.value })}
            placeholder="/path/to/recordings"
          />
        </Field>

        <Field label="TrackMaster CSV">
          <input
            type="text"
            className="w-full"
            value={settings.track_master_csv}
            onChange={(e) => onSave({ ...settings, track_master_csv: e.target.value })}
            placeholder="/path/to/trackmaster.csv"
          />
        </Field>
      </Section>

      {/* Recording Options */}
      <Section label="Recording Options">
        <Field label="Sample Rate">
          <select
            className="w-full"
            value={settings.sample_rate}
            onChange={(e) => onSave({ ...settings, sample_rate: parseInt(e.target.value) })}
          >
            <option value={44100}>44,100 Hz</option>
            <option value={48000}>48,000 Hz</option>
            <option value={96000}>96,000 Hz</option>
          </select>
        </Field>

        <Field label="Timecode FPS">
          <select
            className="w-full"
            value={settings.fps}
            onChange={(e) => onSave({ ...settings, fps: parseInt(e.target.value) })}
          >
            <option value={24}>24 fps</option>
            <option value={25}>25 fps</option>
            <option value={30}>30 fps</option>
          </select>
        </Field>
      </Section>
    </div>
  );
}
