import test from "node:test";
import assert from "node:assert/strict";

// Must be set before importing the module under test, since API_BASE_URL is
// read at module-load time and the module throws if it's missing.
process.env.NEXT_PUBLIC_API_BASE = "http://localhost:8001/api";

const { resolveBase, apiUrl, wsUrl } = await import("../lib/api.ts");

function setWindow(hostname: string | undefined): void {
  if (hostname === undefined) {
    delete (globalThis as { window?: unknown }).window;
    return;
  }
  (globalThis as { window?: unknown }).window = {
    location: { hostname },
  } as unknown;
}

test("resolveBase returns the build-time base in SSR (no window)", () => {
  setWindow(undefined);
  assert.equal(resolveBase(), "http://localhost:8001/api");
});

test("resolveBase returns base unchanged when client is also on localhost", () => {
  setWindow("localhost");
  assert.equal(resolveBase(), "http://localhost:8001/api");
});

test("resolveBase rewrites loopback hostname to remote LAN host and preserves path", () => {
  setWindow("192.168.1.10");
  assert.equal(resolveBase(), "http://192.168.1.10:8001/api");
});

test("resolveBase treats IPv6 loopback as loopback (no swap when client is also ::1)", () => {
  setWindow("::1");
  assert.equal(resolveBase(), "http://localhost:8001/api");
});

test("apiUrl composes correctly after rewrite, without losing the base path", () => {
  setWindow("10.0.0.5");
  assert.equal(
    apiUrl("/api/v1/knowledge/list"),
    "http://10.0.0.5:8001/api/api/v1/knowledge/list",
  );
});

test("wsUrl converts http to ws and respects rewritten host", () => {
  setWindow("10.0.0.5");
  assert.equal(wsUrl("/api/v1/ws"), "ws://10.0.0.5:8001/api/api/v1/ws");
});

test("wsUrl keeps original loopback when client is also loopback", () => {
  setWindow("127.0.0.1");
  assert.equal(wsUrl("/api/v1/ws"), "ws://localhost:8001/api/api/v1/ws");
});
