#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const SOURCE = "code-sonar:render-excalidraw-from-mermaid";
const UPDATED = Date.now();

const CLASS_STYLE = {
  external: { stroke: "#fb923c", fill: "#ffedd5", text: "#111827" },
  app: { stroke: "#93c5fd", fill: "#dbeafe", text: "#111827" },
  core: { stroke: "#22d3ee", fill: "#cffafe", text: "#111827" },
  event: { stroke: "#4ade80", fill: "#dcfce7", text: "#111827" },
  batch: { stroke: "#fbbf24", fill: "#fef3c7", text: "#111827" },
  storage: { stroke: "#fb923c", fill: "#ffedd5", text: "#111827" },
};

const LAYER_STYLE = {
  ADMIN_LAYER: { stroke: "#cbd5e1", fill: "#f8fafc" },
  FE_LAYER: { stroke: "#bfdbfe", fill: "#eff6ff" },
  GW_LAYER: { stroke: "#ddd6fe", fill: "#f5f3ff" },
  BE_LAYER: { stroke: "#a5f3fc", fill: "#ecfeff" },
  EVENT_LAYER: { stroke: "#bbf7d0", fill: "#f0fdf4" },
  BATCH_LAYER: { stroke: "#fde68a", fill: "#fffbeb" },
  STORAGE_LAYER: { stroke: "#fed7aa", fill: "#fff7ed" },
};

const EDGE_STYLE = {
  neutral: { key: "neutral", stroke: "#334155", labelText: "#1f2937", labelFill: "#f8fafc", strokeWidth: 1.1, railOffset: 0 },
  feign: { key: "feign", stroke: "#475569", labelText: "#334155", labelFill: "#f8fafc", strokeWidth: 1.1, railOffset: 0 },
  webclient: { key: "webclient", stroke: "#0e7490", labelText: "#0e7490", labelFill: "#ecfeff", strokeWidth: 1.3, railOffset: 0 },
  http: { key: "http", stroke: "#0f766e", labelText: "#0f766e", labelFill: "#f0fdfa", strokeWidth: 1.3, railOffset: 0 },
  kafka: { key: "kafka", stroke: "#15803d", labelText: "#166534", labelFill: "#f0fdf4", strokeWidth: 1.3, railOffset: 0 },
  jpa: { key: "jpa", stroke: "#1d4ed8", labelText: "#1d4ed8", labelFill: "#eff6ff", strokeWidth: 1.6, railOffset: -18 },
  redis: { key: "redis", stroke: "#be123c", labelText: "#be123c", labelFill: "#fff1f2", strokeWidth: 1.6, railOffset: 18 },
  springData: { key: "springData", stroke: "#6d28d9", labelText: "#6d28d9", labelFill: "#f5f3ff", strokeWidth: 1.6, railOffset: -6 },
  elastic: { key: "elastic", stroke: "#b45309", labelText: "#b45309", labelFill: "#fffbeb", strokeWidth: 1.6, railOffset: 6 },
};

const LAYOUT_RULES = {
  framePaddingX: 48,
  framePaddingTop: 56,
  framePaddingBottom: 44,
  nodeGapX: 40,
  nodeGapY: 36,
  centerTolerance: 4,
  frameMarginToleranceX: 20,
  frameMarginToleranceY: 24,
};

const LAYOUT = {
  EXT: { x: 40, y: 410, w: 240, h: 110 },
  ADMIN_LAYER: { x: 340, y: 70, w: 600, h: 168 },
  FE_LAYER: { x: 340, y: 290, w: 600, h: 298 },
  GW_LAYER: { x: 340, y: 628, w: 600, h: 174 },
  BE_LAYER: { x: 1010, y: 164, w: 920, h: 506 },
  EVENT_LAYER: { x: 1010, y: 720, w: 920, h: 200 },
  BATCH_LAYER: { x: 1010, y: 970, w: 620, h: 174 },
  STORAGE_LAYER: { x: 2080, y: 92, w: 360, h: 820 },
};

const NODE_LAYOUT = {
  AW: { w: 218, h: 58 },
  AA: { w: 218, h: 58 },
  GATE: { w: 260, h: 74 },
  WEB: { w: 260, h: 74 },
  GW: { w: 430, h: 74 },
  AGG: { w: 300, h: 78 },
  API: { w: 300, h: 78 },
  PBK: { w: 300, h: 78 },
  IP: { w: 190, h: 64 },
  KAFKA: { w: 220, h: 74 },
  CONSUMERS: { w: 320, h: 96 },
  BATCH: { w: 440, h: 74 },
  ES: { w: 250, h: 66 },
  ORA: { w: 250, h: 74 },
  MONGO: { w: 250, h: 66 },
  REDIS: { w: 250, h: 66 },
};

const INBOUND_RAIL_X = LAYOUT.BE_LAYER.x - 42;
const STORAGE_RAIL_X = LAYOUT.STORAGE_LAYER.x - 58;

function usage() {
  console.error("Usage: render-excalidraw-from-mermaid.js --input <index.md> --output <file.excalidraw> [--validate-only]");
  process.exit(1);
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--input") args.input = argv[++i];
    else if (arg === "--output") args.output = argv[++i];
    else if (arg === "--validate-only") args.validateOnly = true;
    else usage();
  }
  if (!args.input && !args.validateOnly) usage();
  if (!args.output) usage();
  return args;
}

function extractMermaid(markdown) {
  const match = markdown.match(/```mermaid\s*([\s\S]*?)```/);
  if (!match) throw new Error("No mermaid fenced block found");
  return match[1];
}

function cleanLabel(label) {
  return label
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/\\n/g, "\n")
    .replace(/[ \t]*\/[ \t]*/g, " / ")
    .split("\n")
    .map((line) => line.trim())
    .join("\n")
    .trim();
}

function parseNodeDeclaration(line) {
  const quoted = line.match(/^([A-Za-z0-9_]+)\s*\["([\s\S]+)"\]\s*$/);
  if (quoted) return { id: quoted[1], label: cleanLabel(quoted[2]), shape: "rectangle" };
  const db = line.match(/^([A-Za-z0-9_]+)\s*\[\("([\s\S]+)"\)\]\s*$/);
  if (db) return { id: db[1], label: cleanLabel(db[2]), shape: "storage" };
  return null;
}

function parseMermaid(mermaid) {
  const lines = mermaid.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const nodes = new Map();
  const edges = [];
  const subgraphs = new Map();
  const nodeToSubgraph = new Map();
  const classByNode = new Map();
  const stack = [];

  for (const line of lines) {
    if (line.startsWith("%%") || line.startsWith("flowchart") || line.startsWith("classDef") || line.startsWith("style")) continue;
    const subgraph = line.match(/^subgraph\s+([A-Za-z0-9_]+)\["(.+)"\]\s*$/);
    if (subgraph) {
      subgraphs.set(subgraph[1], { id: subgraph[1], label: cleanLabel(subgraph[2]), nodes: [] });
      stack.push(subgraph[1]);
      continue;
    }
    if (line === "end") {
      stack.pop();
      continue;
    }
    if (line.startsWith("direction")) continue;

    const edge = line.match(/^([A-Za-z0-9_]+)\s*-->\|([^|]+)\|\s*([A-Za-z0-9_]+)\s*$/);
    if (edge) {
      edges.push({ from: edge[1], to: edge[3], label: edge[2].trim() });
      continue;
    }

    const classLine = line.match(/^class\s+(.+?)\s+([A-Za-z0-9_-]+)\s*$/);
    if (classLine) {
      for (const id of classLine[1].split(",").map((v) => v.trim()).filter(Boolean)) {
        classByNode.set(id, classLine[2]);
      }
      continue;
    }

    const node = parseNodeDeclaration(line);
    if (node) {
      nodes.set(node.id, node);
      const parent = stack[stack.length - 1] || null;
      if (parent) {
        nodeToSubgraph.set(node.id, parent);
        subgraphs.get(parent)?.nodes.push(node.id);
      }
    }
  }

  for (const [id, node] of nodes) {
    node.className = classByNode.get(id) || inferClass(id, nodeToSubgraph.get(id));
    node.subgraph = nodeToSubgraph.get(id) || null;
  }

  return { nodes, edges, subgraphs };
}

function inferClass(nodeId, subgraphId) {
  if (nodeId === "EXT") return "external";
  if (subgraphId === "BE_LAYER") return "core";
  if (subgraphId === "EVENT_LAYER") return "event";
  if (subgraphId === "BATCH_LAYER") return "batch";
  if (subgraphId === "STORAGE_LAYER") return "storage";
  return "app";
}

function makeId(prefix, raw) {
  return `${prefix}_${String(raw).toLowerCase().replace(/[^a-z0-9_]+/g, "_")}`;
}

function makeIndexGenerator() {
  let i = 0;
  return () => `a${(i++).toString(36)}`;
}

function seedFor(value) {
  let hash = 2166136261;
  for (const char of String(value)) {
    hash ^= char.charCodeAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return Math.abs(hash) || 1;
}

function baseElement(id, type, x, y, width, height, index) {
  const seed = seedFor(`${type}:${id}`);
  return {
    id,
    type,
    x,
    y,
    width,
    height,
    angle: 0,
    strokeColor: "#3f3f46",
    backgroundColor: "transparent",
    fillStyle: "solid",
    strokeWidth: 1,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 100,
    groupIds: [],
    frameId: null,
    roundness: null,
    seed,
    version: 1,
    versionNonce: seed + 1,
    isDeleted: false,
    boundElements: [],
    updated: UPDATED,
    link: null,
    locked: false,
    index,
    hasTextLink: false,
  };
}

function frameElement(id, label, box, style, nextIndex) {
  return {
    ...baseElement(id, "frame", box.x, box.y, box.w, box.h, nextIndex()),
    strokeColor: style.stroke,
    backgroundColor: style.fill,
    opacity: 36,
    name: "",
    customData: {
      frameColor: {
        stroke: style.stroke,
        fill: style.fill,
        nameColor: "transparent",
      },
      label,
    },
  };
}

function rectElement(id, box, style, frameId, nextIndex, textId = null) {
  const boundElements = textId ? [{ type: "text", id: textId }] : [];
  return {
    ...baseElement(id, "rectangle", box.x, box.y, box.w, box.h, nextIndex()),
    strokeColor: style.stroke,
    backgroundColor: style.fill,
    strokeWidth: style.strokeWidth || 1,
    frameId,
    boundElements,
    roundness: { type: 3 },
  };
}

function textMetrics(text, fontSize) {
  const lines = String(text).split("\n");
  const longest = lines.reduce((max, line) => Math.max(max, line.length), 0);
  return {
    width: Math.max(24, longest * fontSize * 0.58),
    height: lines.length * fontSize * 1.25,
  };
}

function fittedNodeBox(layout, label, fontSize) {
  const metrics = textMetrics(label, fontSize);
  return {
    ...layout,
    w: Math.max(layout.w, Math.ceil(metrics.width + 52)),
    h: Math.max(layout.h, Math.ceil(metrics.height + 36)),
  };
}

function frameInner(frame) {
  return {
    x: frame.x + LAYOUT_RULES.framePaddingX,
    y: frame.y + LAYOUT_RULES.framePaddingTop,
    w: frame.w - LAYOUT_RULES.framePaddingX * 2,
    h: frame.h - LAYOUT_RULES.framePaddingTop - LAYOUT_RULES.framePaddingBottom,
  };
}

function centerInFrame(frame, node, y = null) {
  const inner = frameInner(frame);
  return {
    ...node,
    x: inner.x + (inner.w - node.w) / 2,
    y: y == null ? inner.y + (inner.h - node.h) / 2 : y,
  };
}

function rowInFrame(frame, nodes, y = null) {
  const inner = frameInner(frame);
  const totalWidth = nodes.reduce((sum, node) => sum + node.w, 0) + LAYOUT_RULES.nodeGapX * (nodes.length - 1);
  let x = inner.x + (inner.w - totalWidth) / 2;
  const maxHeight = nodes.reduce((max, node) => Math.max(max, node.h), 0);
  const rowY = y == null ? inner.y + (inner.h - maxHeight) / 2 : y;
  return nodes.map((node) => {
    const placed = { ...node, x, y: rowY + (maxHeight - node.h) / 2 };
    x += node.w + LAYOUT_RULES.nodeGapX;
    return placed;
  });
}

function stackInFrame(frame, nodes) {
  const inner = frameInner(frame);
  const totalHeight = nodes.reduce((sum, node) => sum + node.h, 0);
  const availableGap = nodes.length > 1 ? (inner.h - totalHeight) / (nodes.length - 1) : 0;
  const gap = Math.max(LAYOUT_RULES.nodeGapY, availableGap);
  let y = inner.y;
  return nodes.map((node) => {
    const placed = { ...node, x: inner.x + (inner.w - node.w) / 2, y };
    y += node.h + gap;
    return placed;
  });
}

function baseNodeBox(id, node, fontSize) {
  const base = NODE_LAYOUT[id] || LAYOUT[id];
  if (!base) return null;
  return fittedNodeBox(base, node.label, fontSize);
}

function createLayoutModel(model) {
  const frames = new Map(Object.entries(LAYOUT).filter(([id]) => id.endsWith("_LAYER")));
  const boxes = new Map();
  const fontSizes = new Map();
  const nodeBox = (id) => {
    const node = model.nodes.get(id);
    if (!node) return null;
    const fontSize = id === "EXT" ? 15 : 15;
    fontSizes.set(id, fontSize);
    return baseNodeBox(id, node, fontSize);
  };
  const set = (id, box) => {
    if (box) boxes.set(id, { ...box, subgraph: model.nodes.get(id)?.subgraph || null, nodeId: id });
  };

  set("EXT", centerInFrame({ x: LAYOUT.EXT.x, y: LAYOUT.EXT.y, w: LAYOUT.EXT.w, h: LAYOUT.EXT.h + LAYOUT_RULES.framePaddingTop + LAYOUT_RULES.framePaddingBottom }, nodeBox("EXT"), LAYOUT.EXT.y));
  rowInFrame(frames.get("ADMIN_LAYER"), [nodeBox("AW"), nodeBox("AA")]).forEach((box, idx) => set(idx === 0 ? "AW" : "AA", box));
  stackInFrame(frames.get("FE_LAYER"), [nodeBox("GATE"), nodeBox("WEB")]).forEach((box, idx) => set(idx === 0 ? "GATE" : "WEB", box));
  set("GW", centerInFrame(frames.get("GW_LAYER"), nodeBox("GW")));

  const be = frames.get("BE_LAYER");
  const beInner = frameInner(be);
  set("AGG", { ...nodeBox("AGG"), x: beInner.x, y: be.y + 150 });
  set("API", { ...nodeBox("API"), x: be.x + be.w - LAYOUT_RULES.framePaddingX - nodeBox("API").w, y: be.y + 108 });
  set("PBK", { ...nodeBox("PBK"), x: be.x + be.w - LAYOUT_RULES.framePaddingX - nodeBox("PBK").w, y: be.y + 306 });

  rowInFrame(frames.get("EVENT_LAYER"), [nodeBox("IP"), nodeBox("KAFKA"), nodeBox("CONSUMERS")]).forEach((box, idx) => {
    set(["IP", "KAFKA", "CONSUMERS"][idx], box);
  });
  set("BATCH", centerInFrame(frames.get("BATCH_LAYER"), nodeBox("BATCH")));
  stackInFrame(frames.get("STORAGE_LAYER"), [nodeBox("ES"), nodeBox("ORA"), nodeBox("MONGO"), nodeBox("REDIS")]).forEach((box, idx) => {
    set(["ES", "ORA", "MONGO", "REDIS"][idx], box);
  });

  return { frames, boxes, fontSizes };
}

function edgeStyleFor(label) {
  const normalized = String(label || "").toLowerCase();
  if (normalized.includes("redis")) return EDGE_STYLE.redis;
  if (normalized.includes("jdbc") || normalized.includes("jpa")) return EDGE_STYLE.jpa;
  if (normalized.includes("spring data") || normalized.includes("mongo")) return EDGE_STYLE.springData;
  if (normalized.includes("elastic") || normalized.includes("index")) return EDGE_STYLE.elastic;
  if (normalized.includes("webclient")) return EDGE_STYLE.webclient;
  if (normalized.includes("http") || normalized.includes("https")) return EDGE_STYLE.http;
  if (normalized.includes("publish") || normalized.includes("subscribe") || normalized.includes("kafka")) return EDGE_STYLE.kafka;
  if (normalized.includes("feign") || normalized.includes("route")) return EDGE_STYLE.feign;
  return EDGE_STYLE.neutral;
}

function textElement(id, text, x, y, opts, nextIndex) {
  const fontSize = opts.fontSize || 14;
  const metrics = opts.width && opts.height ? { width: opts.width, height: opts.height } : textMetrics(text, fontSize);
  return {
    ...baseElement(id, "text", x, y, metrics.width, metrics.height, nextIndex()),
    strokeColor: opts.color || "#111827",
    backgroundColor: opts.backgroundColor || "transparent",
    fillStyle: "solid",
    strokeWidth: 1,
    frameId: opts.frameId || null,
    text,
    fontSize,
    fontFamily: 2,
    textAlign: opts.textAlign || "center",
    verticalAlign: opts.verticalAlign || "middle",
    containerId: opts.containerId || null,
    originalText: text,
    lineHeight: 1.25,
    autoResize: true,
    rawText: "",
  };
}

function centerText(id, text, box, opts, nextIndex) {
  const fontSize = opts.fontSize || 14;
  const metrics = textMetrics(text, fontSize);
  return textElement(
    id,
    text,
    box.x + (box.w - metrics.width) / 2,
    box.y + (box.h - metrics.height) / 2,
    { ...opts, fontSize, containerId: opts.containerId || null },
    nextIndex,
  );
}

function arrowElement(id, absPoints, style, nextIndex) {
  const minX = Math.min(...absPoints.map((p) => p[0]));
  const minY = Math.min(...absPoints.map((p) => p[1]));
  const maxX = Math.max(...absPoints.map((p) => p[0]));
  const maxY = Math.max(...absPoints.map((p) => p[1]));
  return {
    ...baseElement(id, "arrow", minX, minY, maxX - minX, maxY - minY, nextIndex()),
    strokeColor: style.stroke,
    backgroundColor: "transparent",
    strokeWidth: style.strokeWidth,
    roundness: null,
    points: absPoints.map(([x, y]) => [x - minX, y - minY]),
    lastCommittedPoint: null,
    startBinding: null,
    endBinding: null,
    startArrowhead: null,
    endArrowhead: "arrow",
    elbowed: true,
  };
}

function labelElement(edgeId, label, x, y, style, nextIndex) {
  const fontSize = 12;
  const metrics = textMetrics(label, fontSize);
  return textElement(`tl_${edgeId}`, label, x - metrics.width / 2, y - metrics.height / 2, {
    fontSize,
    color: style.labelText,
    backgroundColor: style.labelFill,
  }, nextIndex);
}

function port(box, side, offset = 0) {
  if (side === "left") return [box.x, box.y + box.h / 2 + offset];
  if (side === "right") return [box.x + box.w, box.y + box.h / 2 + offset];
  if (side === "top") return [box.x + box.w / 2 + offset, box.y];
  if (side === "bottom") return [box.x + box.w / 2 + offset, box.y + box.h];
  throw new Error(`Unknown side ${side}`);
}

function routeEdge(edge, boxes) {
  const from = boxes.get(edge.from);
  const to = boxes.get(edge.to);
  if (!from || !to) throw new Error(`Missing node box for edge ${edge.from} -> ${edge.to}`);

  const fromSub = from.subgraph;
  const toSub = to.subgraph;
  const fromRight = port(from, "right");
  const toLeft = port(to, "left");

  if (edge.to === "AGG" && edge.from !== "AGG") {
    return {
      points: [fromRight, [INBOUND_RAIL_X, fromRight[1]], [INBOUND_RAIL_X, toLeft[1]], toLeft],
      labelAt: [INBOUND_RAIL_X + 22, fromRight[1] - 34],
    };
  }

  if (toSub === "STORAGE_LAYER") {
    const style = edgeStyleFor(edge.label);
    const railX = STORAGE_RAIL_X + style.railOffset;
    const labelLaneYOffset = {
      API: -34,
      PBK: 0,
      BATCH: 34,
    }[edge.from] || 0;
    const labelXOffset = edge.from === "BATCH" ? 86 : 38;
    return {
      points: [fromRight, [railX, fromRight[1]], [railX, toLeft[1]], toLeft],
      labelAt: [railX - labelXOffset, (fromRight[1] + toLeft[1]) / 2 + labelLaneYOffset],
    };
  }

  if (edge.from === "CONSUMERS" && edge.to === "PBK") {
    const start = port(from, "top");
    const target = port(to, "bottom");
    const eventToBackendRailX = target[0];
    return {
      points: [start, [eventToBackendRailX, start[1]], [eventToBackendRailX, target[1]], target],
      labelAt: [eventToBackendRailX + 28, (start[1] + target[1]) / 2],
    };
  }

  if (edge.from === "EXT") {
    const startOffset = edge.to === "GATE" ? -20 : edge.to === "WEB" ? 0 : 24;
    const start = port(from, "right", startOffset);
    const target = port(to, "left");
    const railX = from.x + from.w + 45;
    return {
      points: [start, [railX, start[1]], [railX, target[1]], target],
      labelAt: [(start[0] + railX) / 2, start[1] - 14],
    };
  }

  return {
    points: [fromRight, toLeft[1] === fromRight[1] ? toLeft : [toLeft[0], fromRight[1]], toLeft].filter((p, i, arr) => i === 0 || p[0] !== arr[i - 1][0] || p[1] !== arr[i - 1][1]),
    labelAt: [
      (fromRight[0] + toLeft[0]) / 2,
        Math.abs(fromRight[1] - toLeft[1]) < 24 ? Math.min(from.y, to.y) - 34 : fromRight[1] - 20,
    ],
  };
}

function buildExcalidraw(model) {
  const nextIndex = makeIndexGenerator();
  const elements = [];
  const layoutModel = createLayoutModel(model);
  const boxes = layoutModel.boxes;

  for (const [id, subgraph] of model.subgraphs) {
    const box = layoutModel.frames.get(id);
    if (!box) continue;
    const style = LAYER_STYLE[id] || { stroke: "#d1d5db", fill: "#f8fafc" };
    elements.push(frameElement(makeId("f", id), subgraph.label, box, style, nextIndex));
    elements.push(textElement(makeId("ft", id), subgraph.label, box.x, box.y - 38, {
      fontSize: 22,
      color: "#6b7280",
      textAlign: "left",
    }, nextIndex));
  }

  for (const [id, node] of model.nodes) {
    const rect = boxes.get(id);
    if (!rect) continue;
    const style = CLASS_STYLE[node.className] || CLASS_STYLE.app;
    const frameId = node.subgraph ? makeId("f", node.subgraph) : null;
    const strokeWidth = id === "EXT" ? 2 : 1;
    const fontSize = layoutModel.fontSizes.get(id) || 15;
    const rectId = makeId("n", id);
    const textId = makeId("t", id);
    elements.push(rectElement(rectId, rect, { ...style, strokeWidth }, frameId, nextIndex, textId));
    elements.push(centerText(makeId("t", id), node.label, rect, {
      fontSize,
      color: style.text,
      frameId,
      containerId: rectId,
    }, nextIndex));
  }

  for (const [idx, edge] of model.edges.entries()) {
    const route = routeEdge(edge, boxes);
    const edgeStyle = edgeStyleFor(edge.label);
    const edgeId = `a_${edge.from.toLowerCase()}_${edge.to.toLowerCase()}_${idx}`;
    elements.push(arrowElement(edgeId, route.points, edgeStyle, nextIndex));
    elements.push(labelElement(edgeId, edge.label, route.labelAt[0], route.labelAt[1], edgeStyle, nextIndex));
  }

  return {
    type: "excalidraw",
    version: 2,
    source: SOURCE,
    elements,
    appState: {
      gridSize: null,
      viewBackgroundColor: "#ffffff",
      currentItemArrowType: "elbow",
      currentItemRoundness: null,
      frameRendering: {
        enabled: true,
        clip: true,
        name: false,
        outline: true,
        markerName: false,
        markerEnabled: false,
      },
    },
    files: {},
  };
}

function absolutePoints(arrow) {
  return (arrow.points || []).map(([x, y]) => [arrow.x + x, arrow.y + y]);
}

function bbox(element, pad = 0) {
  return {
    id: element.id,
    type: element.type,
    nodeId: element.id.replace(/^n_/, "").toUpperCase(),
    frameId: element.frameId || null,
    x: element.x - pad,
    y: element.y - pad,
    w: element.width + pad * 2,
    h: element.height + pad * 2,
  };
}

function segIntersectsBox(p1, p2, box) {
  const minX = Math.min(p1[0], p2[0]);
  const maxX = Math.max(p1[0], p2[0]);
  const minY = Math.min(p1[1], p2[1]);
  const maxY = Math.max(p1[1], p2[1]);
  if (maxX < box.x || minX > box.x + box.w || maxY < box.y || minY > box.y + box.h) return false;
  if (p1[0] === p2[0]) return p1[0] > box.x && p1[0] < box.x + box.w;
  if (p1[1] === p2[1]) return p1[1] > box.y && p1[1] < box.y + box.h;
  return true;
}

function textBox(element) {
  return bbox(element, 2);
}

function boxesOverlap(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function gapBetween(a, b) {
  const horizontalOverlap = a.x < b.x + b.w && a.x + a.w > b.x;
  const verticalOverlap = a.y < b.y + b.h && a.y + a.h > b.y;
  const horizontalGap = a.x + a.w <= b.x ? b.x - (a.x + a.w) : a.x - (b.x + b.w);
  const verticalGap = a.y + a.h <= b.y ? b.y - (a.y + a.h) : a.y - (b.y + b.h);
  return { horizontalOverlap, verticalOverlap, horizontalGap, verticalGap };
}

function validateFrameLayout(doc) {
  const errors = [];
  const epsilon = 0.5;
  const frames = doc.elements.filter((el) => !el.isDeleted && el.type === "frame");
  const nodes = doc.elements.filter((el) => !el.isDeleted && el.type === "rectangle" && el.id.startsWith("n_"));
  for (const frame of frames) {
    const children = nodes.filter((node) => node.frameId === frame.id);
    if (!children.length) continue;
    const minX = Math.min(...children.map((node) => node.x));
    const maxX = Math.max(...children.map((node) => node.x + node.width));
    const minY = Math.min(...children.map((node) => node.y));
    const maxY = Math.max(...children.map((node) => node.y + node.height));
    const left = minX - frame.x;
    const right = frame.x + frame.width - maxX;
    const top = minY - frame.y;
    const bottom = frame.y + frame.height - maxY;
    if (left + epsilon < LAYOUT_RULES.framePaddingX || right + epsilon < LAYOUT_RULES.framePaddingX) {
      errors.push(`${frame.id}: child horizontal padding too small (${left.toFixed(1)}, ${right.toFixed(1)})`);
    }
    if (top + epsilon < LAYOUT_RULES.framePaddingTop || bottom + epsilon < LAYOUT_RULES.framePaddingBottom) {
      errors.push(`${frame.id}: child vertical padding too small (${top.toFixed(1)}, ${bottom.toFixed(1)})`);
    }
    if (Math.abs(left - right) > LAYOUT_RULES.frameMarginToleranceX) {
      errors.push(`${frame.id}: left/right margins are unbalanced (${left.toFixed(1)}, ${right.toFixed(1)})`);
    }
    if (Math.abs(top - bottom) > LAYOUT_RULES.frameMarginToleranceY) {
      errors.push(`${frame.id}: top/bottom margins are unbalanced (${top.toFixed(1)}, ${bottom.toFixed(1)})`);
    }

    for (let i = 0; i < children.length; i += 1) {
      for (let j = i + 1; j < children.length; j += 1) {
        const gap = gapBetween(bbox(children[i]), bbox(children[j]));
        if (gap.horizontalOverlap && gap.verticalOverlap) {
          errors.push(`${frame.id}: ${children[i].id} overlaps ${children[j].id}`);
        } else if (gap.verticalOverlap && gap.horizontalGap < LAYOUT_RULES.nodeGapX) {
          errors.push(`${frame.id}: ${children[i].id}/${children[j].id} horizontal gap ${gap.horizontalGap.toFixed(1)} < ${LAYOUT_RULES.nodeGapX}`);
        } else if (gap.horizontalOverlap && gap.verticalGap < LAYOUT_RULES.nodeGapY) {
          errors.push(`${frame.id}: ${children[i].id}/${children[j].id} vertical gap ${gap.verticalGap.toFixed(1)} < ${LAYOUT_RULES.nodeGapY}`);
        }
      }
    }
  }
  return errors;
}

function validateExcalidraw(doc, model = null) {
  const errors = [];
  const nodeBoxes = doc.elements
    .filter((el) => !el.isDeleted && el.type === "rectangle" && el.id.startsWith("n_"))
    .map((el) => bbox(el, 3));
  const nodeBoxById = new Map(doc.elements
    .filter((el) => !el.isDeleted && el.type === "rectangle" && el.id.startsWith("n_"))
    .map((el) => [el.id.replace(/^n_/, ""), bbox(el, 0)]));
  const nodeTextBoxes = doc.elements
    .filter((el) => !el.isDeleted && el.type === "text" && el.id.startsWith("t_"))
    .map((el) => ({ id: el.id, nodeId: el.id.replace(/^t_/, ""), box: textBox(el) }));
  const labelBoxes = doc.elements
    .filter((el) => !el.isDeleted && el.type === "text" && (el.id.startsWith("tl_") || el.backgroundColor === "#f3e8ff"))
    .map(textBox);
  const arrows = doc.elements.filter((el) => !el.isDeleted && el.type === "arrow");

  errors.push(...validateFrameLayout(doc));

  const namedFrames = doc.elements
    .filter((el) => !el.isDeleted && el.type === "frame" && typeof el.name === "string" && el.name.trim());
  if (namedFrames.length) {
    errors.push(`Frame names must be hidden; found ${namedFrames.map((el) => el.id).join(", ")}`);
  }

  if (doc.appState?.frameRendering?.name !== false) {
    errors.push("appState.frameRendering.name must be false");
  }

  if (model && arrows.length !== model.edges.length) {
    errors.push(`Arrow count mismatch: expected ${model.edges.length}, got ${arrows.length}`);
  }

  if (model) {
    const storageEdges = model.edges
      .map((edge, idx) => ({ edge, idx }))
      .filter(({ edge }) => model.nodes.get(edge.to)?.subgraph === "STORAGE_LAYER");
    const expectedStorageKeys = new Set(storageEdges.map(({ edge }) => edgeStyleFor(edge.label).key));
    const storageColors = new Set();
    for (const { edge, idx } of storageEdges) {
      const arrowId = `a_${edge.from.toLowerCase()}_${edge.to.toLowerCase()}_${idx}`;
      const arrow = arrows.find((item) => item.id === arrowId);
      if (arrow) storageColors.add(arrow.strokeColor);
    }
    if (expectedStorageKeys.size >= 4 && storageColors.size < 4) {
      errors.push(`Storage edge colors must be protocol-distinct; expected at least 4 colors, got ${storageColors.size}`);
    }
  }

  for (const arrow of arrows) {
    if (arrow.elbowed !== true) errors.push(`${arrow.id}: elbowed must be true`);
    if (arrow.roundness !== null) errors.push(`${arrow.id}: roundness must be null`);
    const points = absolutePoints(arrow);
    for (let i = 1; i < points.length; i += 1) {
      if (points[i - 1][0] !== points[i][0] && points[i - 1][1] !== points[i][1]) {
        errors.push(`${arrow.id}: segment ${i} is diagonal`);
      }
      for (const box of nodeBoxes) {
        const isEndpointBox = pointInside(points[0], box, 4) || pointInside(points[points.length - 1], box, 4);
        if (!isEndpointBox && segIntersectsBox(points[i - 1], points[i], box)) {
          errors.push(`${arrow.id}: segment ${i} crosses ${box.id}`);
        }
      }
    }
  }

  for (const label of labelBoxes) {
    for (const box of nodeBoxes) {
      if (boxesOverlap(label, box)) errors.push(`${label.id}: overlaps ${box.id}`);
    }
  }

  for (const text of nodeTextBoxes) {
    const nodeBox = nodeBoxById.get(text.nodeId);
    if (!nodeBox) continue;
    const textCenterX = text.box.x + text.box.w / 2;
    const textCenterY = text.box.y + text.box.h / 2;
    const nodeCenterX = nodeBox.x + nodeBox.w / 2;
    const nodeCenterY = nodeBox.y + nodeBox.h / 2;
    if (
      Math.abs(textCenterX - nodeCenterX) > LAYOUT_RULES.centerTolerance ||
      Math.abs(textCenterY - nodeCenterY) > LAYOUT_RULES.centerTolerance
    ) {
      errors.push(`${text.id}: text is not centered in n_${text.nodeId}`);
    }
    if (
      text.box.x < nodeBox.x ||
      text.box.y < nodeBox.y ||
      text.box.x + text.box.w > nodeBox.x + nodeBox.w ||
      text.box.y + text.box.h > nodeBox.y + nodeBox.h
    ) {
      errors.push(`${text.id}: text overflows n_${text.nodeId}`);
    }
  }

  for (let i = 0; i < labelBoxes.length; i += 1) {
    for (let j = i + 1; j < labelBoxes.length; j += 1) {
      if (boxesOverlap(labelBoxes[i], labelBoxes[j])) {
        errors.push(`${labelBoxes[i].id}: overlaps label ${labelBoxes[j].id}`);
      }
    }
  }

  return errors;
}

function pointInside(point, box, pad = 0) {
  return point[0] >= box.x - pad && point[0] <= box.x + box.w + pad && point[1] >= box.y - pad && point[1] <= box.y + box.h + pad;
}

function loadExcalidraw(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function main() {
  const args = parseArgs(process.argv);
  if (args.validateOnly) {
    const doc = loadExcalidraw(args.output);
    const errors = validateExcalidraw(doc);
    if (errors.length) {
      console.error(errors.join("\n"));
      process.exit(1);
    }
    console.log(`${args.output}: Excalidraw QA passed`);
    return;
  }

  const markdown = fs.readFileSync(args.input, "utf8");
  const mermaid = extractMermaid(markdown);
  const model = parseMermaid(mermaid);
  const doc = buildExcalidraw(model);
  const errors = validateExcalidraw(doc, model);
  if (errors.length) {
    console.error(errors.join("\n"));
    process.exit(1);
  }

  fs.mkdirSync(path.dirname(args.output), { recursive: true });
  fs.writeFileSync(args.output, `${JSON.stringify(doc, null, "\t")}\n`);
  console.log(`${args.output}: rendered ${model.nodes.size} node(s), ${model.edges.length} arrow(s)`);
}

main();
