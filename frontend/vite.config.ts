/**
 * Vite configuration for the DMS frontend.
 *
 * Key settings:
 *  - The React plugin enables JSX transforms and Fast Refresh.
 *  - The server proxy rewrites /api/* requests to the Django backend so the
 *    browser never has to deal with CORS during development.
 *    In production the reverse proxy (nginx) handles this routing.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  server: {
    // Bind to all interfaces so the Vite dev server is reachable from
    // outside the Docker container (e.g. the host browser at localhost:5173).
    host: '0.0.0.0',
    port: 5173,

    proxy: {
      // Any request starting with /api is forwarded to Django.
      // This avoids cross-origin issues during local development.
      '/api': {
        target: 'http://backend:8000', // Docker Compose service name
        changeOrigin: true,
      },
    },
  },
});
