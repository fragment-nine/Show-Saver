import { useEffect, useRef } from "react";
import type { AudioLevels } from "../../types/engine";

interface Props {
  levels: AudioLevels | null;
  label: string;
}

export function VuMeter({ levels, label }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const w = canvas.width;
    const h = canvas.height;

    const rms = Math.max(0, Math.min(1, (levels?.rms ?? 0) * 2));
    const peak = Math.max(0, Math.min(1, (levels?.peak ?? 0) * 2));

    // Clear
    ctx.fillStyle = "#10102a";
    ctx.fillRect(0, 0, w, h);

    // Segmented meter
    const segments = 40;
    const segW = (w - 40) / segments;
    const gap = 1;
    const barY = 6;
    const barH = h - 12;
    const rmsSegs = Math.floor(rms * segments);
    const peakSeg = Math.floor(peak * segments);

    for (let i = 0; i < segments; i++) {
      const x = 30 + i * segW;
      const ratio = i / segments;

      if (i < rmsSegs) {
        if (ratio < 0.6) ctx.fillStyle = "#2ecc71";
        else if (ratio < 0.8) ctx.fillStyle = "#f39c12";
        else ctx.fillStyle = "#e74c3c";
      } else {
        ctx.fillStyle = "#1a1a35";
      }

      ctx.fillRect(x, barY, segW - gap, barH);
    }

    // Peak indicator
    if (peakSeg > 0 && peakSeg < segments) {
      const peakX = 30 + peakSeg * segW;
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(peakX, barY, 2, barH);
    }

    // Label
    ctx.fillStyle = "#8888aa";
    ctx.font = "bold 11px Inter, sans-serif";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText(label, 4, h / 2);
  }, [levels, label]);

  return (
    <canvas
      ref={canvasRef}
      width={400}
      height={28}
      className="w-full h-7 rounded"
    />
  );
}
