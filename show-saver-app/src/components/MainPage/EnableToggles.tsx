import type { Settings } from "../../types/engine";

interface Props {
  settings: Settings;
  onSave: (s: Settings) => void;
}

function Toggle({
  label,
  enabled,
  onChange,
}: {
  label: string;
  enabled: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <button
      onClick={() => onChange(!enabled)}
      className={`flex items-center gap-3 px-4 py-2.5 rounded-md border transition-all duration-150 ${
        enabled
          ? "bg-green-on/15 border-green-on/40 text-green-on"
          : "bg-surface-raised border-border text-text-secondary hover:border-border-bright"
      }`}
    >
      <span
        className={`w-2.5 h-2.5 rounded-full transition-colors ${
          enabled ? "bg-green-on shadow-[0_0_6px_rgba(46,204,113,0.6)]" : "bg-border-bright"
        }`}
      />
      <span className="text-sm font-medium">{label}</span>
    </button>
  );
}

export function EnableToggles({ settings, onSave }: Props) {
  return (
    <div className="panel">
      <div className="panel-label">Recording Outputs</div>
      <div className="grid grid-cols-2 gap-2">
        <Toggle
          label="Enable PGM"
          enabled={settings.enable_pgm}
          onChange={(v) => onSave({ ...settings, enable_pgm: v })}
        />
        <Toggle
          label="Enable TC"
          enabled={settings.enable_tc}
          onChange={(v) => onSave({ ...settings, enable_tc: v })}
        />
        <Toggle
          label="Enable Long PGM"
          enabled={settings.enable_pgm_long}
          onChange={(v) => onSave({ ...settings, enable_pgm_long: v })}
        />
        <Toggle
          label="Enable Long TC"
          enabled={settings.enable_tc_long}
          onChange={(v) => onSave({ ...settings, enable_tc_long: v })}
        />
      </div>
    </div>
  );
}
