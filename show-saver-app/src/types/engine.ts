/** Timecode value from the Rust backend. */
export interface Timecode {
  hours: number;
  minutes: number;
  seconds: number;
  frames: number;
}

/** Audio level data for VU meters. */
export interface AudioLevels {
  rms: number;
  peak: number;
}

/** Audio device info from cpal. */
export interface AudioDeviceInfo {
  name: string;
  max_input_channels: number;
  default_sample_rate: number;
}

/** A track/song from the TrackMaster CSV. */
export interface Track {
  number: number;
  name: string;
  tc_stamp: string;
  tc_seconds: number;
  show_order: number;
  in_show: boolean;
  status: string;
  file_folder_name: string;
  bpm: string;
}

/** Application settings. */
export interface Settings {
  tc_device: string | null;
  tc_channel: number;
  pgm_device: string | null;
  pgm_channel: number;
  output_folder: string;
  track_master_csv: string;
  sample_rate: number;
  fps: number;
  auto_arm: boolean;
  enable_tc: boolean;
  enable_pgm: boolean;
  enable_tc_long: boolean;
  enable_pgm_long: boolean;
}

/** Engine status returned by get_status. */
export interface EngineStatus {
  timecode: Timecode;
  tc_levels: AudioLevels;
  pgm_levels: AudioLevels;
  current_song: string;
  is_recording: boolean;
  state: string;
}

/** Format a Timecode to HH:MM:SS:FF display string. */
export function formatTimecode(tc: Timecode): string {
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${pad(tc.hours)}:${pad(tc.minutes)}:${pad(tc.seconds)}:${pad(tc.frames)}`;
}
