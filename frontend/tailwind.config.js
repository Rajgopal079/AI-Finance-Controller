/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          app: '#090D16',       /* Deep Obsidian Dark Background */
          surface: '#0F172A',   /* Clean Elevated Surface */
          hover: '#182238',     /* Subtle Interactive Hover */
          card: '#111927'
        },
        border: {
          subtle: '#1E293B',    /* Hairline Hairline Dividers */
          strong: '#334155'     /* Focused Hairlines */
        },
        brand: {
          blue: '#3B82F6',
          purple: '#8B5CF6',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#EF4444'
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
}
