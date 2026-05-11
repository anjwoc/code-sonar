#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

function isNumberPair(value) {
  return Array.isArray(value) && value.length === 2 && value.every((n) => typeof n === "number");
}

function isOrthogonal(points) {
  if (!Array.isArray(points) || points.length < 2) return false;
  for (let i = 1; i < points.length; i += 1) {
    const prev = points[i - 1];
    const next = points[i];
    if (!isNumberPair(prev) || !isNumberPair(next)) return false;
    const dx = next[0] - prev[0];
    const dy = next[1] - prev[1];
    if (dx !== 0 && dy !== 0) return false;
  }
  return true;
}

function normalizeArrow(element) {
  if (!element || element.type !== "arrow") return false;

  let changed = false;

  if (element.elbowed !== true) {
    element.elbowed = true;
    changed = true;
  }

  if (element.roundness !== null) {
    element.roundness = null;
    changed = true;
  }

  if (typeof element.roughness === "number" && element.roughness > 1) {
    element.roughness = 1;
    changed = true;
  }

  const points = element.points;
  if (Array.isArray(points) && points.length >= 2 && !isOrthogonal(points)) {
    const first = points[0];
    const last = points[points.length - 1];
    if (isNumberPair(first) && isNumberPair(last)) {
      element.points = [
        first,
        [last[0], first[1]],
        last,
      ];
      changed = true;
    }
  }

  if (changed) {
    element.version = typeof element.version === "number" ? element.version + 1 : 1;
  }

  return changed;
}

function normalizeFile(filePath) {
  const raw = fs.readFileSync(filePath, "utf8");
  const doc = JSON.parse(raw);
  if (!Array.isArray(doc.elements)) {
    throw new Error(`${filePath} does not contain an elements array`);
  }

  let changed = 0;
  for (const element of doc.elements) {
    if (normalizeArrow(element)) changed += 1;
  }

  if (changed > 0) {
    fs.writeFileSync(filePath, `${JSON.stringify(doc, null, "\t")}\n`);
  }

  return changed;
}

const files = process.argv.slice(2);
if (files.length === 0) {
  console.error("Usage: normalize-excalidraw-arrows.js <file.excalidraw> [...]");
  process.exit(1);
}

let total = 0;
for (const file of files) {
  const filePath = path.resolve(file);
  const changed = normalizeFile(filePath);
  total += changed;
  console.log(`${filePath}: normalized ${changed} arrow(s)`);
}

console.log(`normalized ${total} arrow(s) total`);
