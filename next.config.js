/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ["localhost"],
    remotePatterns: [
      {
        // https://icons8.com/icon/z3YMXqHDYl9X/brain
        protocol: "https",
        hostname: "img.icons8.com",
        port: "",
      }
    ],
  },
  rewrites: async () => {
    return [
      {
        source: "/api/:path*",
        destination: process.env.NODE_ENV === 'production'
          ? 'https://tinygen-g3ra.onrender.com/api/:path*' // Replace with your production URL
          : 'http://127.0.0.1:8000/api/:path*', // Proxy to Backend in development
      },
    ];
  },
  async redirects() {
    return [
      {
        source: '/chrome',
        destination: 'https://chrome.google.com/webstore/detail/sniptube-elevate-your-you/fidajdajcfpjlbmgmpbcobkofibhkimk',
        permanent: false,
        basePath: false
      },
      {
        source: '/firefox',
        destination: 'https://addons.mozilla.org/en-US/firefox/addon/sniptube/',
        permanent: false,
        basePath: false
      },
      {
        source: '/edge',
        destination: 'https://microsoftedge.microsoft.com/addons/detail/sniptube-elevate-your-y/hibkflieoofejdponchkigjjklebinia',
        permanent: false,
        basePath: false
      },
      {
        source: '/safari',
        destination: 'https://github.com/psycho-baller/snipTube/blob/main/docs/safari.md',
        permanent: false,
        basePath: false
      },
    ]
  },
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          { key: "Access-Control-Allow-Credentials", value: "true" },
          { key: "Access-Control-Allow-Origin", value: process.env.NODE_ENV === 'production' ? "chrome-extension://jciifdnfancohlpbnechegapliahanid" : "chrome-extension://okiflhgmoemcbijlcfhihgddnomeigle" },
          { key: "Access-Control-Allow-Methods", value: "GET, POST, OPTIONS" },
          { key: "Access-Control-Allow-Headers", value: "Content-Type" },
        ]
      }
    ]
  }
};

module.exports = nextConfig;
