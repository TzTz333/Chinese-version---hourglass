const { withSentryConfig } = require("@sentry/nextjs");
const path = require("path");


const nextConfig = {
  reactStrictMode: false,
  swcMinify: true,
  //配置图片优化
  images: {
    domains: [
        "vinci-web.s3.amazonaws.com",
        "planefs-staging.s3.ap-south-1.amazonaws.com",
        "planefs.s3.amazonaws.com",
        "images.unsplash.com",
        "localhost:8080",
    ],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/api/users/file-assets',
      },
    ],
  },
  output: "standalone",
  experimental: {
    // this includes files from the monorepo base two directories up
    outputFileTracingRoot: path.join(__dirname, "../../"),
  },
};

if (parseInt(process.env.NEXT_PUBLIC_ENABLE_SENTRY || "0")) {
  module.exports = withSentryConfig(nextConfig, { silent: true }, { hideSourceMaps: true });
} else {
  module.exports = nextConfig;
}
