/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0a',
        surface: '#141414',
        'surface-light': '#1f1f1f',
        border: '#2a2a2a',
        'text-primary': '#ffffff',
        'text-secondary': '#a1a1a1',
        'text-muted': '#6b6b6b',
        accent: '#525252',
      },
    },
  },
  plugins: [],
}
