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
    },
  },
  plugins: [],
};

export default config;
