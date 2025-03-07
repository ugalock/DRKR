import { defineConfig } from 'vite'
import wasm from "vite-plugin-wasm";
import topLevelAwait from "vite-plugin-top-level-await";
import react from '@vitejs/plugin-react'
import compression from 'vite-plugin-compression';
// import { visualizer } from 'rollup-plugin-visualizer';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(), 
    wasm(), 
    topLevelAwait(),
    compression({
      algorithm: 'brotliCompress',
      threshold: 10240, // Only compress files larger than 10KB
    }),
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
      filter: /\.(wasm)$/i,
      compressionOptions: {
        level: 11, // highest compression level for Brotli
      },
      threshold: 10240, // compress all WASM files regardless of size
      deleteOriginFile: false, // keep the original file
    }),
    // visualizer({
    //   open: true, // Open analyzer in browser
    //   gzipSize: true,
    //   brotliSize: true,
    // }),
  ],
  server: {
    port: 3000,
    host: true,
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Split large vendor libraries into separate chunks
          'vendor-mui': ['@mui/material', '@mui/icons-material'],
          'vendor-auth': ['@auth0/auth0-react',],
          // Add more as needed based on your dependencies
        }
      }
    },
    // Only load the WASM file when it's actually needed
    assetsInlineLimit: 0, // Don't inline any assets
  },
})
