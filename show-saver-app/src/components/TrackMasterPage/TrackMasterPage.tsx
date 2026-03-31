import type { Track } from "../../types/engine";

interface Props {
  tracks: Track[];
  onLoadCsv: (path: string) => void;
}

export function TrackMasterPage({ tracks, onLoadCsv }: Props) {
  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h2>Track Master</h2>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            onClick={() => {
              const path = prompt("Enter path to TrackMaster CSV:");
              if (path) onLoadCsv(path);
            }}
            style={{ padding: "0.5rem 1rem" }}
          >
            Load CSV
          </button>
        </div>
      </div>

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #444" }}>
            <th style={{ textAlign: "left", padding: "0.5rem" }}>#</th>
            <th style={{ textAlign: "left", padding: "0.5rem" }}>Name</th>
            <th style={{ textAlign: "left", padding: "0.5rem" }}>Timecode</th>
            <th style={{ textAlign: "left", padding: "0.5rem" }}>BPM</th>
            <th style={{ textAlign: "left", padding: "0.5rem" }}>In Show</th>
            <th style={{ textAlign: "left", padding: "0.5rem" }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {tracks.length === 0 ? (
            <tr>
              <td colSpan={6} style={{ padding: "2rem", textAlign: "center", color: "#666" }}>
                No tracks loaded. Load a TrackMaster CSV to get started.
              </td>
            </tr>
          ) : (
            tracks.map((track, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #333" }}>
                <td style={{ padding: "0.5rem" }}>{track.number}</td>
                <td style={{ padding: "0.5rem" }}>{track.name}</td>
                <td style={{ padding: "0.5rem", fontFamily: "monospace" }}>
                  {track.tc_stamp}
                </td>
                <td style={{ padding: "0.5rem" }}>{track.bpm || "—"}</td>
                <td style={{ padding: "0.5rem" }}>
                  {track.in_show ? "Yes" : "No"}
                </td>
                <td style={{ padding: "0.5rem" }}>{track.status || "—"}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
