/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Civic Green
        'civic-dark': '#0F6E56',
        'civic': '#1D9E75',
        'civic-light': '#E8F5F0',
        // Trust Blue
        'trust-dark': '#185FA5',
        'trust': '#378ADD',
        'trust-light': '#E3F2FD',
        // Safety Orange
        'safety-dark': '#D85A30',
        'safety': '#EB6834',
        'safety-light': '#FFF3F0',
        // Neutral & Dark
        'neutral': '#5F5E5A',
        'charcoal': '#2C2C2A',
      },
      spacing: {
        '80': '80px',
        '40': '40px',
      },
      transitionDuration: {
        '300': '300ms',
        '200': '200ms',
      },
      screens: {
        'xs': '320px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  },
  plugins: [],
}
