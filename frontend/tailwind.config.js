// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}", // 掃描 src 目錄下的 .vue, .js 等文件
  ],
  theme: {
    extend: {
      fontFamily: {
        // 定義一個名為 'NotoSansTC' 的字體家族
        // 'sans-serif' 作為備用字體，以防 NotoSansTC 未載入
        'NotoSansTC': ['NotoSansTC', 'sans-serif'],
      }
    },
  },
  plugins: [],
}