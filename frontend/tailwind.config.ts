import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#0f1419",
          raised: "#161b22",
          overlay: "#1c2128",
        },
        border: {
          DEFAULT: "#30363d",
          muted: "#21262d",
        },
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
      boxShadow: {
        glow: "0 0 40px -10px var(--accent-glow)",
      },
    },
  },
  plugins: [],
};

export default config;
