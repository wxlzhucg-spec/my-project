const path = require('path')

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    path.join(__dirname, 'App.vue'),
    path.join(__dirname, 'pages/**/*.{vue,js,ts}'),
    path.join(__dirname, 'components/**/*.{vue,js,ts}')
  ],
  corePlugins: {
    preflight: false
  },
  separator: process.env.UNI_PLATFORM && process.env.UNI_PLATFORM.indexOf('mp-') === 0 ? '__' : ':',
  theme: {
    extend: {}
  },
  plugins: []
}
