## Install dependencies

```bash
# Create a Vue 3 project with Vite
npm create vite@latest my-app -- --template vue
cd my-app
npm install

# Add Vuetify and other plugins
npm install vuetify@^3 vue-router@4 pinia vue-i18n@9
# Vuetify plugin + Sass for preprocessing
npm install -D @vuetify/vite-plugin sass
```

The Vuetify plugin will automatically import component styles when `autoImport` is enabled in `vite.config.ts`.
