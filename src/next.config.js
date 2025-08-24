/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode for better development experience
  reactStrictMode: true,
  
  // Enable SWC minification for faster builds
  swcMinify: true,
  
  // Configure experimental features
  experimental: {
    // Enable app directory features
    appDir: true,
    // Enable server components
    serverComponentsExternalPackages: ['swisseph'],
  },
  
  // Configure images
  images: {
    // Allow external images from Google Maps API
    domains: [
      'maps.googleapis.com',
      'maps.gstatic.com',
      'lh3.googleusercontent.com',
    ],
    // Configure image formats
    formats: ['image/webp', 'image/avif'],
  },
  
  // Configure environment variables
  env: {
    // Make API URL available to client
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://jyotish-api-ndcfqrjivq-uc.a.run.app',
    NEXT_PUBLIC_GOOGLE_MAPS_API_KEY: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY,
  },
  
  // Configure headers for security and CORS
  async headers() {
    return [
      {
        // Apply headers to all routes
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
        ],
      },
      {
        // Apply specific headers to API routes
        source: '/api/(.*)',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization, X-API-Key',
          },
        ],
      },
    ];
  },
  
  // Configure redirects
  async redirects() {
    return [
      {
        source: '/',
        destination: '/calendario',
        permanent: false,
      },
    ];
  },
  
  // Configure webpack for optimizations
  webpack: (config, { dev, isServer }) => {
    // Optimize bundle size
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            enforce: true,
          },
        },
      };
    }
    
    // Handle SVG files
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });
    
    return config;
  },
  
  // Configure TypeScript
  typescript: {
    // Don't fail build on TypeScript errors in production
    ignoreBuildErrors: process.env.NODE_ENV === 'production',
  },
  
  // Configure ESLint
  eslint: {
    // Don't fail build on ESLint errors in production
    ignoreDuringBuilds: process.env.NODE_ENV === 'production',
  },
  
  // Configure output
  output: 'standalone',
  
  // Configure trailing slash
  trailingSlash: false,
  
  // Configure powered by header
  poweredByHeader: false,
  
  // Configure compression
  compress: true,
  
  // Configure source maps
  productionBrowserSourceMaps: false,
  
  // Configure i18n (if needed in the future)
  // i18n: {
  //   locales: ['es', 'en'],
  //   defaultLocale: 'es',
  // },
};

module.exports = nextConfig;
