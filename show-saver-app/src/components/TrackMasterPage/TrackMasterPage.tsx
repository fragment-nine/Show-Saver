import type { Track } from "../../types/engine";

interface Props {
  tracks: Track[];
  onLoadCsv: (path: string) => void;
  currentSong: string;
}

export function TrackMasterPage({ tracks, onLoadCsv, currentSong }: Props) {
  return (
    <div className="flex flex-col gap-4 p-5 max-w-3xl mx-auto">
      {/* Actions */}
      <div className="flex gap-3">
        <button
          className="btn-blue flex-1"
          onClick={() => {
            const path = prompt("Enter path to TrackMaster CSV:");
            if (path) onLoadCsv(path);
          }}
        >
          Load CSV
        </button>
        <button className="btn-neutral flex-1">Export CSV</button>
      </div>

      {/* Track Table */}
      <div className="panel p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface-raised/50">
              <th className="text-left px-4 py-3 text-xs uppercase tracking-wider text-text-secondary font-medium">#</th>
              <th className="text-left px-4 py-3 text-xs uppercase tracking-wider text-text-secondary font-medium">Name</th>
              <th className="text-left px-4 py-3 text-xs uppercase tracking-wider text-text-secondary font-medium">Timecode</th>
              <th className="text-left px-4 py-3 text-xs uppercase tracking-wider text-text-secondary font-medium">BPM</th>
              <th className="text-center px-4 py-3 text-xs uppercase tracking-wider text-text-secondary font-medium">In Show</th>
              <th className="text-left px-4 py-3 text-xs uppercase tracking-wider text-text-secondary font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {tracks.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-text-secondary">
                  No tracks loaded. Load a TrackMaster CSV to get started.
                </td>
              </tr>
            ) : (
              tracks.map((track, i) => {
                const isCurrent = currentSong === track.name;
                return (
                  <tr
                    key={i}
                    className={`border-b border-border/50 transition-colors ${
                      isCurrent
                        ? "bg-accent/10 border-l-2 border-l-accent"
                        : i % 2 === 0
                          ? "bg-transparent"
                          : "bg-surface-raised/30"
                    }`}
                  >
                    <td className="px-4 py-2.5 text-text-secondary">{track.number}</td>
                    <td className={`px-4 py-2.5 font-medium ${isCurrent ? "text-accent" : ""}`}>
                      {track.name}
                    </td>
                    <td className="px-4 py-2.5 font-mono text-text-secondary">
                      {track.tc_stamp}
                    </td>
                    <td className="px-4 py-2.5 text-text-secondary">{track.bpm || "---"}</td>
                    <td className="px-4 py-2.5 text-center">
                      {track.in_show ? (
                        <span className="inline-block w-2.5 h-2.5 rounded-full bg-green-on shadow-[0_0_4px_rgba(46,204,113,0.5)]" />
                      ) : (
                        <span className="inline-block w-2.5 h-2.5 rounded-full bg-border-bright" />
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-text-secondary">{track.status || "---"}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
