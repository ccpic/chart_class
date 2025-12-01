/**
 * Next.js configuration for serving the app under a sub-path `/chart_class2`.
 * This ensures generated asset URLs include the prefix so Apache reverse-proxy
 * can forward them correctly (recommended long-term fix).
 */
/** @type {import('next').NextConfig} */
const nextConfig = {
  basePath: '/chart_class2',
  assetPrefix: '/chart_class2',
  // Keep other settings as default. If you use `output: 'standalone'` in
  // another config, start the server with `node .next/standalone/server.js`.
  output: 'standalone',
};

module.exports = nextConfig;
