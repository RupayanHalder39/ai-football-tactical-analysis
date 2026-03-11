import type { Config } from 'tailwindcss';

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"] as Config["content"],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config;
