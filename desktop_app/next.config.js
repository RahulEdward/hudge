/** @type {import('next').NextConfig} */
const nextConfig = {
  output: process.env.ELECTRON_BUILD ? 'export' : undefined,
  distDir: process.env.ELECTRON_BUILD ? 'build' : '.next',
  images: { unoptimized: true },
  trailingSlash: true,
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
