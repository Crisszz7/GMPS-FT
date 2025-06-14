// tailwind.config.js
export default {
    content: [
      './index.html',
      './src/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
      extend: {
        backgroundImage: {
          flower: "url('/src/assets/imgs/background-login.jpg')",
        },
      },
    },
    plugins: [],
  }
  