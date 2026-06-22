/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        app: '#F7F8FA',
        accent: {
          DEFAULT: '#2563EB',
          hover: '#1D4ED8',
          light: '#EFF6FF',
        },
      },
    },
  },
  plugins: [],
}
