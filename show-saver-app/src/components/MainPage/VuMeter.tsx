import { useEffect, useRef } from "react";
import type { AudioLevels } from "../../types/engine";

interface Props {
  levels: AudioLevels | null;
  label: string;
  width?: number;
  height?: number;
}

export function VuMeter({ levels, label, width = 40, height = 200 }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rms = levels?.rms ?? 0;
    const peak = levels?.peak ?? 0;

    // Convert to dB-like scale (0 to 1 range)
    const rmsDb = Math.max(0, Math.min(1, rms * 2));
    const peakDb = Math.max(0, Math.min(1, peak * 2));

    // Clear
    ctx.fillStyle = "#1a1a2e";
    ctx.fillRect(0, 0, width, height);

    // RMS bar (green -> yellow -> red)
    const rmsHeight = rmsDb * height;
    const gradient = ctx.createLinearGradient(0, height, 0, 0);
    gradient.addColorStop(0, "#00ff00");
    gradient.addColorStop(0.6, "#00ff00");
    gradient.addColorStop(0.8, "#ffff00");
    gradient.addColorStop(1.0, "#ff0000");

    ctx.fillStyle = gradient;
    ctx.fillRect(4, height - rmsHeight, width - 8, rmsHeight);

    // Peak indicator (thin line)
    const peakY = height - peakDb * height;
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(2, peakY - 1, width - 4, 2);

    // Label
    ctx.fillStyle = "#888";
    ctx.font = "10px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(label, width / 2, height - 4);
  }, [levels, width, height, label]);

  return <canvas ref={canvasRef} width={width} height={height} />;
}
