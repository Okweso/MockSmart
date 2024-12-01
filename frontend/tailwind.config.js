/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {clipPath: {
      diagonal: 'polygon(0 0, 100% 0, 100% 100%)',
    },},
  },
  plugins: [],
}

