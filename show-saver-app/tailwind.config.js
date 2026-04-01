/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0d0d1a",
        surface: "#141428",
        "surface-raised": "#1a1a35",
        "surface-input": "#10102a",
        border: "#2a2a45",
        "border-bright": "#3a3a5a",
        accent: "#4a9eff",
        "text-primary": "#e0e0e8",
        "text-secondary": "#8888aa",
        "green-on": "#2ecc71",
        "red-rec": "#e74c3c",
        amber: "#f39c12",
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"SF Mono"', '"Fira Code"', "monospace"],
      },
    },
  },
  plugins: [],
};
