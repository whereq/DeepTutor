/** @type {import('next').NextConfig} */

const fs = require("fs");
const path = require("path");

function readJsonFile(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return {};
  }
}

function firstNonEmpty(...values) {
  for (const value of values) {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      return String(value).trim();
    }
  }
  return "";
}

function normalizeBoolean(value) {
  if (value === "__NEXT_PUBLIC_AUTH_ENABLED_PLACEHOLDER__") {
    return value;
  }
  return ["1", "true", "yes", "on"].includes(String(value).trim().toLowerCase())
    ? "true"
    : "false";
}

const SETTINGS_DIR = path.resolve(__dirname, "..", "data", "user", "settings");
const SYSTEM_SETTINGS = readJsonFile(path.join(SETTINGS_DIR, "system.json"));
const AUTH_SETTINGS = readJsonFile(path.join(SETTINGS_DIR, "auth.json"));
const BACKEND_PORT = firstNonEmpty(
  process.env.BACKEND_PORT,
  SYSTEM_SETTINGS.backend_port,
  "8001",
);

// Use data/user/settings as the frontend source of truth. Environment values
// remain explicit deployment overrides for Docker/CI.
const NEXT_PUBLIC_API_BASE = firstNonEmpty(
  process.env.NEXT_PUBLIC_API_BASE_EXTERNAL,
  SYSTEM_SETTINGS.next_public_api_base_external,
  process.env.NEXT_PUBLIC_API_BASE,
  SYSTEM_SETTINGS.next_public_api_base,
  `http://localhost:${BACKEND_PORT}`,
);

const NEXT_PUBLIC_AUTH_ENABLED = normalizeBoolean(
  firstNonEmpty(
    process.env.NEXT_PUBLIC_AUTH_ENABLED,
    process.env.AUTH_ENABLED,
    AUTH_SETTINGS.enabled,
    "false",
  ),
);

process.env.NEXT_PUBLIC_API_BASE = NEXT_PUBLIC_API_BASE;
process.env.NEXT_PUBLIC_AUTH_ENABLED = NEXT_PUBLIC_AUTH_ENABLED;

// Resolve the build-time application version. Priority:
//   1. Explicit APP_VERSION env (set by CI from the release tag)
//   2. `git describe --tags` when building from a checkout (local dev)
//   3. Empty string → frontend treats it as "unknown" and shows the
//      latest GitHub release as a neutral fallback.
const APP_VERSION = (() => {
  if (process.env.APP_VERSION) return process.env.APP_VERSION;
  try {
    const { execSync } = require("child_process");
    return execSync("git describe --tags --always --dirty=-dev", {
      stdio: ["ignore", "pipe", "ignore"],
    })
      .toString()
      .trim();
  } catch {
    return "";
  }
})();

const nextConfig = {
  // Expose the build-time version to the browser so the sidebar badge
  // can compare it against GitHub's latest release.
  env: {
    NEXT_PUBLIC_APP_VERSION: APP_VERSION,
    NEXT_PUBLIC_API_BASE,
    NEXT_PUBLIC_AUTH_ENABLED,
  },

  // Standalone output: self-contained server.js + minimal node_modules
  // This eliminates the need to copy the full node_modules into Docker production images
  output: "standalone",

  // Move dev indicator to bottom-right corner
  devIndicators: {
    position: "bottom-right",
  },

  // Transpile mermaid and related packages for proper ESM handling
  transpilePackages: ["mermaid"],

  // Turbopack configuration (used when running `npm run dev:turbo`)
  turbopack: {
    resolveAlias: {
      // Fix for mermaid's cytoscape dependency - use CJS version
      cytoscape: "cytoscape/dist/cytoscape.cjs.js",
    },
  },

  // Webpack configuration (used for production builds - next build)
  webpack: (config) => {
    const path = require("path");
    config.resolve.alias = {
      ...config.resolve.alias,
      cytoscape: path.resolve(
        __dirname,
        "node_modules/cytoscape/dist/cytoscape.cjs.js",
      ),
    };
    return config;
  },
};

module.exports = nextConfig;
