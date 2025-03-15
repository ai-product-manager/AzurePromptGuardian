/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          primary: {
            DEFAULT: '#0070f3',
            50: '#e6f1fe',
            100: '#cce3fd',
            200: '#99c7fb',
            300: '#66aaf9',
            400: '#338ef7',
            500: '#0070f3',
            600: '#005ac2',
            700: '#004392',
            800: '#002d61',
            900: '#001631',
          }
        }
      },
    },
    plugins: [],
  }