import test from "node:test";
import assert from "node:assert/strict";

import {
  classifyFile,
  docIconFor,
  formatBytes,
  MAX_ATTACHMENT_BYTES,
} from "../lib/doc-attachments";

function makeFile(name: string, type = "", size = 0): File {
  // File constructor available in modern Node runtimes.
  return new File([new Uint8Array(size)], name, { type });
}

// classifyFile ---------------------------------------------------------------

test("classifyFile: image via MIME", () => {
  assert.equal(classifyFile(makeFile("x.png", "image/png")), "image");
  assert.equal(classifyFile(makeFile("x.jpg", "image/jpeg")), "image");
});

test("classifyFile: doc via MIME", () => {
  assert.equal(
    classifyFile(makeFile("a.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
    "doc",
  );
  assert.equal(classifyFile(makeFile("b.pdf", "application/pdf")), "doc");
});

test("classifyFile: doc via extension fallback when MIME empty", () => {
  assert.equal(classifyFile(makeFile("report.pptx")), "doc");
  assert.equal(classifyFile(makeFile("REPORT.XLSX")), "doc");
});

test("classifyFile: rejects unsupported", () => {
  assert.equal(classifyFile(makeFile("a.zip", "application/zip")), null);
  assert.equal(classifyFile(makeFile("a.txt", "text/plain")), null);
  assert.equal(classifyFile(makeFile("noext")), null);
});

// formatBytes ----------------------------------------------------------------

test("formatBytes: B / KB / MB", () => {
  assert.equal(formatBytes(0), "0 B");
  assert.equal(formatBytes(512), "512 B");
  assert.equal(formatBytes(1024), "1.0 KB");
  assert.equal(formatBytes(1024 * 1024), "1.0 MB");
  assert.equal(formatBytes(5 * 1024 * 1024), "5.0 MB");
});

test("formatBytes: negative / NaN returns empty string", () => {
  assert.equal(formatBytes(-1), "");
  assert.equal(formatBytes(Number.NaN), "");
});

// docIconFor -----------------------------------------------------------------

test("docIconFor: labels by extension", () => {
  assert.equal(docIconFor("report.pdf").label, "PDF");
  assert.equal(docIconFor("report.docx").label, "DOCX");
  assert.equal(docIconFor("report.xlsx").label, "XLSX");
  assert.equal(docIconFor("report.pptx").label, "PPTX");
});

test("docIconFor: fallback for unknown extension", () => {
  assert.equal(docIconFor("mystery.bin").label, "BIN");
  assert.equal(docIconFor("noext").label, "FILE");
});

// Limits sanity check -------------------------------------------------------

test("MAX_ATTACHMENT_BYTES is 10 MB", () => {
  assert.equal(MAX_ATTACHMENT_BYTES, 10 * 1024 * 1024);
});
