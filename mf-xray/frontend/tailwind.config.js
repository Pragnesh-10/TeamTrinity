/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0f1e',
        surface: '#111827',
        border: '#1f2937',
        teal: '#00d4aa',
        amber: '#f59e0b',
        red: '#ef4444',
      },
      fontFamily: {
        mono: ['"DM Mono"', '"JetBrains Mono"', 'monospace'],
        sans: ['Inter', '"DM Sans"', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
