import { useState } from "react";
import { MainPage } from "./components/MainPage/MainPage";
import { SettingsPage } from "./components/SettingsPage/SettingsPage";
import { TrackMasterPage } from "./components/TrackMasterPage/TrackMasterPage";
import { useEngine } from "./hooks/useEngine";

type Page = "main" | "settings" | "trackmaster";

function App() {
  const [page, setPage] = useState<Page>("main");
  const engine = useEngine();

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: "#0f0f1a", color: "#e0e0e0" }}>
      {/* Navigation */}
      <nav style={{ display: "flex", gap: "0", borderBottom: "1px solid #333" }}>
        {(["main", "settings", "trackmaster"] as Page[]).map((p) => (
          <button
            key={p}
            onClick={() => setPage(p)}
            style={{
              padding: "0.75rem 1.5rem",
              background: page === p ? "#1a1a3e" : "transparent",
              color: page === p ? "#fff" : "#888",
              border: "none",
              borderBottom: page === p ? "2px solid #4a9eff" : "2px solid transparent",
              cursor: "pointer",
              fontSize: "0.9rem",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            {p === "trackmaster" ? "Track Master" : p}
          </button>
        ))}
      </nav>

      {/* Page content */}
      <div style={{ flex: 1, overflow: "auto" }}>
        {page === "main" && <MainPage status={engine.status} />}
        {page === "settings" && (
          <SettingsPage
            settings={engine.settings}
            devices={engine.devices}
            onSave={engine.saveSettings}
          />
        )}
        {page === "trackmaster" && (
          <TrackMasterPage
            tracks={engine.tracks}
            onLoadCsv={engine.loadTrackMaster}
          />
        )}
      </div>
    </div>
  );
}

export default App;
