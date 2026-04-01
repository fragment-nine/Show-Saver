import { useState } from "react";
import { MainPage } from "./components/MainPage/MainPage";
import { SettingsPage } from "./components/SettingsPage/SettingsPage";
import { TrackMasterPage } from "./components/TrackMasterPage/TrackMasterPage";
import { useEngine } from "./hooks/useEngine";

type Page = "main" | "settings" | "trackmaster";

const tabs: { key: Page; label: string }[] = [
  { key: "main", label: "Main" },
  { key: "settings", label: "Settings" },
  { key: "trackmaster", label: "Track Master" },
];

function App() {
  const [page, setPage] = useState<Page>("main");
  const engine = useEngine();

  return (
    <div className="flex flex-col h-screen bg-bg text-text-primary">
      {/* Tab Navigation */}
      <nav className="flex border-b border-border bg-surface shrink-0">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setPage(tab.key)}
            className={`px-6 py-3 text-sm font-medium uppercase tracking-wider border-b-2 transition-colors duration-150 ${
              page === tab.key
                ? "text-accent border-accent bg-surface-raised"
                : "text-text-secondary border-transparent hover:text-text-primary hover:bg-surface-raised/50"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Page Content */}
      <div className="flex-1 overflow-auto">
        {page === "main" && (
          <MainPage
            status={engine.status}
            settings={engine.settings}
            onSaveSettings={engine.saveSettings}
          />
        )}
        {page === "settings" && (
          <SettingsPage
            settings={engine.settings}
            devices={engine.devices}
            onSave={engine.saveSettings}
            onRefreshDevices={engine.refreshDevices}
          />
        )}
        {page === "trackmaster" && (
          <TrackMasterPage
            tracks={engine.tracks}
            onLoadCsv={engine.loadTrackMaster}
            currentSong={engine.status?.current_song ?? ""}
          />
        )}
      </div>
    </div>
  );
}

export default App;
