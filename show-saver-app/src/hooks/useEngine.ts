import { invoke } from "@tauri-apps/api/core";
import { useCallback, useEffect, useRef, useState } from "react";
import type {
  AudioDeviceInfo,
  EngineStatus,
  Settings,
  Track,
} from "../types/engine";

/** Hook for interacting with the Rust audio engine via Tauri IPC. */
export function useEngine() {
  const [status, setStatus] = useState<EngineStatus | null>(null);
  const [devices, setDevices] = useState<AudioDeviceInfo[]>([]);
  const [tracks, setTracks] = useState<Track[]>([]);
  const [settings, setSettings] = useState<Settings | null>(null);
  const pollRef = useRef<number | null>(null);

  // Poll engine status at ~30Hz
  useEffect(() => {
    const poll = () => {
      invoke<EngineStatus>("get_status")
        .then(setStatus)
        .catch(console.error);
      pollRef.current = requestAnimationFrame(poll);
    };
    pollRef.current = requestAnimationFrame(poll);
    return () => {
      if (pollRef.current) cancelAnimationFrame(pollRef.current);
    };
  }, []);

  const refreshDevices = useCallback(async () => {
    const devs = await invoke<AudioDeviceInfo[]>("get_audio_devices");
    setDevices(devs);
  }, []);

  const loadTrackMaster = useCallback(async (path: string) => {
    const loaded = await invoke<Track[]>("load_track_master", { path });
    setTracks(loaded);
  }, []);

  const loadSettings = useCallback(async () => {
    const s = await invoke<Settings>("get_settings");
    setSettings(s);
  }, []);

  const saveSettings = useCallback(async (s: Settings) => {
    await invoke("update_settings", { settings: s });
    setSettings(s);
  }, []);

  // Load settings and devices on mount
  useEffect(() => {
    loadSettings();
    refreshDevices();
  }, [loadSettings, refreshDevices]);

  return {
    status,
    devices,
    tracks,
    settings,
    refreshDevices,
    loadTrackMaster,
    loadSettings,
    saveSettings,
    setTracks,
  };
}
