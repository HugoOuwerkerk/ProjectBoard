import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // Build a pure static SPA; Nginx serves / and falls back to index.html
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html', // <- important for /project/[id] etc.
      precompress: false
    }),
    // Disable prerender; we fetch data at runtime from the API
    prerender: { entries: [] }
  }
};

export default config;
