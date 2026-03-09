/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './ui/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './electron_main/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0f',
        surface: '#12121a',
        border: '#1e1e2e',
        profit: '#10b981',    // emerald-500
        loss: '#f43f5e',      // rose-500
        accent: '#6366f1',    // indigo-500
        muted: '#6b7280',
        primary: {
          DEFAULT: '#6366f1',
          foreground: '#ffffff',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
