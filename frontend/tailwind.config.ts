import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        buy: "#22c55e",
        sell: "#ef4444",
        hold: "#6b7280",
        dark: {
          bg: "#0f1117",
          card: "#1a1d2e",
          border: "#2d3148",
        },
      },
    },
  },
  plugins: [],
};
export default config;
