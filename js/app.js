const CARD_W_INCH = 3.5;
const CARD_H_INCH = 2.25;
const DPI = 72;
const CARD_W = CARD_W_INCH * DPI;
const CARD_H = CARD_H_INCH * DPI;
const COLS = 2;
const ROWS = 5;
const MAX_QTY = COLS * ROWS;
const PAGE_W = 595;
const PAGE_H = 842;

const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

let frontData = null;
let backData = null;
let currentView = "front";
let quantity = MAX_QTY;
let showCrop = false;
let showSafe = false;

const canvas = $("#preview-canvas");
const ctx = canvas.getContext("2d");
let cw = 0, ch = 0, dpr = 1;

function init() {
  // Generate quantity buttons
  const qtyRow = $("#qty-row");
  for (let i = 1; i <= MAX_QTY; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    btn.dataset.qty = i;
    if (i === MAX_QTY) btn.classList.add("active");
    qtyRow.appendChild(btn);
  }

  bindUpload("front", "#front-area", "#front-input");
  bindUpload("back", "#back-area", "#back-input");

  $$(".view-toggle button").forEach((btn) => {
    btn.onclick = () => {
      $$(".view-toggle button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentView = btn.dataset.view;
      render();
    };
  });

  $$(".qty-row button").forEach((btn) => {
    btn.onclick = () => {
      $$(".qty-row button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      quantity = +btn.dataset.qty;
      updateInfo();
      render();
    };
  });

  $("#chk-crop").onchange = () => { showCrop = $("#chk-crop").checked; render(); };
  $("#chk-safe").onchange = () => { showSafe = $("#chk-safe").checked; render(); };

  $("#btn-export").onclick = generatePDF;

  $("#sidebar-toggle").onclick = toggleSidebar;
  $("#sidebar-overlay").onclick = toggleSidebar;

  resize();
  render();
  updateInfo();
}

function resize() {
  dpr = window.devicePixelRatio || 1;
  const wrap = $("#preview-wrap");
  cw = wrap.clientWidth * dpr;
  ch = wrap.clientHeight * dpr;
  canvas.width = cw;
  canvas.height = ch;
  canvas.style.width = wrap.clientWidth + "px";
  canvas.style.height = wrap.clientHeight + "px";
  render();
}
window.addEventListener("resize", resize);

function bindUpload(side, areaSel, inputSel) {
  const area = $(areaSel);
  const input = $(inputSel);

  input.onchange = () => {
    if (input.files?.[0]) loadImage(side, input.files[0], area, input);
  };

  area.addEventListener("dragover", (e) => {
    e.preventDefault();
    area.classList.add("dragover");
  });
  area.addEventListener("dragleave", () => area.classList.remove("dragover"));
  area.addEventListener("drop", (e) => {
    e.preventDefault();
    area.classList.remove("dragover");
    const file = e.dataTransfer?.files?.[0];
    if (file && file.type.startsWith("image/")) {
      input.files = e.dataTransfer.files;
      loadImage(side, file, area, input);
    }
  });
}

function loadImage(side, file, area, input) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      const data = { dataUrl: e.target.result, file, width: img.width, height: img.height };
      if (side === "front") frontData = data;
      else backData = data;

      area.classList.add("loaded");
      area.querySelector(".label").textContent =
        `✓ ${side === "front" ? "Front" : "Back"} loaded`;

      updateInfo();
      render();
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function clearImage(side) {
  if (side === "front") frontData = null;
  else backData = null;
  const area = side === "front" ? $("#front-area") : $("#back-area");
  const input = side === "front" ? $("#front-input") : $("#back-input");
  area.classList.remove("loaded");
  area.querySelector(".label").textContent = `Upload ${side === "front" ? "Front" : "Back"} Image`;
  input.value = "";
  updateInfo();
  render();
}

function gapCalc() {
  const tw = COLS * CARD_W;
  const th = ROWS * CARD_H;
  return {
    gx: (PAGE_W - tw) / (COLS + 1),
    gy: (PAGE_H - th) / (ROWS + 1),
  };
}

function render() {
  const { gx, gy } = gapCalc();

  ctx.clearRect(0, 0, cw, ch);

  const sx = cw / PAGE_W;
  const sy = ch / PAGE_H;
  const scale = Math.min(sx, sy) * 0.92;
  const dw = PAGE_W * scale;
  const dh = PAGE_H * scale;
  const ox = (cw - dw) / 2;
  const oy = (ch - dh) / 2;

  ctx.fillStyle = "#1f1f23";
  ctx.strokeStyle = "#27272a";
  ctx.lineWidth = 1 * dpr;
  roundRect(ctx, ox, oy, dw, dh, 8 * dpr);
  ctx.fill();
  ctx.stroke();

  const imgData = currentView === "front" ? frontData : backData;
  const img = imgData ? new Image() : null;
  if (imgData) img.src = imgData.dataUrl;

  for (let i = 0; i < quantity; i++) {
    const row = Math.floor(i / COLS);
    const col = i % COLS;

    const x = ox + scale * (gx + col * (CARD_W + gx));
    const y = oy + scale * (gy + row * (CARD_H + gy));
    const w = CARD_W * scale;
    const h = CARD_H * scale;

    ctx.fillStyle = "#18181b";
    ctx.strokeStyle = "#3f3f46";
    ctx.lineWidth = 1.5 * dpr;
    roundRect(ctx, x, y, w, h, 4 * dpr);
    ctx.fill();
    ctx.stroke();

    if (imgData && img.complete) {
      try {
        const iw = img.naturalWidth, ih = img.naturalHeight;
        const margin = 4 * dpr;
        const mw = w - 2 * margin;
        const mh = h - 2 * margin;
        const is = Math.min(mw / iw, mh / ih);
        const nw = iw * is, nh = ih * is;
        ctx.save();
        ctx.beginPath();
        roundRect(ctx, x, y, w, h, 4 * dpr);
        ctx.clip();
        ctx.drawImage(img, x + (w - nw) / 2, y + (h - nh) / 2, nw, nh);
        ctx.restore();
      } catch (_) {}
    }

    if (showCrop) {
      const mk = 8 * dpr;
      ctx.strokeStyle = "#ef4444";
      ctx.lineWidth = 1.5 * dpr;
      for (const [dx, dy] of [[0, 0], [w, 0], [0, h], [w, h]]) {
        const fx = x + dx, fy = y + dy;
        ctx.beginPath();
        ctx.moveTo(fx - mk, fy); ctx.lineTo(fx + mk, fy);
        ctx.moveTo(fx, fy - mk); ctx.lineTo(fx, fy + mk);
        ctx.stroke();
      }
    }

    if (showSafe) {
      const safe = 0.2 * DPI * scale;
      ctx.strokeStyle = "#f59e0b";
      ctx.lineWidth = 1 * dpr;
      ctx.setLineDash([4, 6]);
      roundRect(ctx, x + safe, y + safe, w - 2 * safe, h - 2 * safe, 2 * dpr);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function updateInfo() {
  const front = frontData ? "✅" : "❌";
  const back = backData ? "✅" : "❌";
  $("#info-qty").textContent = quantity;
  $("#info-front").textContent = `${front} ${frontData ? "Loaded" : "Not loaded"}`;
  $("#info-back").textContent = `${back} ${backData ? "Loaded" : "Not loaded"}`;
  $("#header-count").textContent = `${quantity} card${quantity === 1 ? "" : "s"}`;
}

async function generatePDF() {
  if (!frontData && !backData) { toast("Upload at least one image", "error"); return; }
  const btn = $("#btn-export");
  btn.disabled = true;
  btn.textContent = "Generating…";
  try {
    const pdfBytes = await buildPDF();
    const blob = new Blob([pdfBytes], { type: "application/pdf" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "GridCopy_ID_Cards.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 5000);
    toast("PDF downloaded!", "success");
  } catch (e) {
    toast("PDF generation failed", "error");
    console.error(e);
  }
  btn.disabled = false;
  btn.textContent = "Export to PDF";
}

async function buildPDF() {
  const { PDFDocument, rgb } = PDFLib;
  const doc = await PDFDocument.create();
  const { gx, gy } = gapCalc();

  const images = [];
  if (frontData) images.push(frontData);
  if (backData) images.push(backData);

  for (const imgData of images) {
    let cardsPlaced = 0;
    while (cardsPlaced < quantity) {
      const page = doc.addPage([PAGE_W, PAGE_H]);

      for (let row = 0; row < ROWS && cardsPlaced < quantity; row++) {
        for (let col = 0; col < COLS && cardsPlaced < quantity; col++) {
          const x = gx + col * (CARD_W + gx);
          const y = PAGE_H - (gy + (row + 1) * CARD_H + row * gy);

          page.drawRectangle({
            x, y, width: CARD_W, height: CARD_H,
            borderColor: rgb(0.2, 0.2, 0.22),
            borderWidth: 1,
          });

          try {
            const resp = await fetch(imgData.dataUrl);
            const blob = await resp.blob();
            let img;
            if (blob.type === "image/png") {
              img = await doc.embedPng(await blob.arrayBuffer());
            } else {
              img = await doc.embedJpg(await blob.arrayBuffer());
            }
            const margin = 10;
            const mw = CARD_W - 2 * margin;
            const mh = CARD_H - 2 * margin;
            const is = Math.min(mw / img.width, mh / img.height);
            const nw = img.width * is;
            const nh = img.height * is;
            const ix = x + margin + (mw - nw) / 2;
            const iy = y + (CARD_H - nh) / 2;
            page.drawImage(img, { x: ix, y: iy, width: nw, height: nh });
          } catch (_) {}

          if (showCrop) {
            const mk = 10;
            const cl = rgb(0.94, 0.27, 0.27);
            for (const [dx, dy] of [[0, 0], [CARD_W, 0], [0, CARD_H], [CARD_W, CARD_H]]) {
              const fx = x + dx, fy = y + dy;
              page.drawLine({ start: { x: fx - mk, y: fy }, end: { x: fx + mk, y: fy }, color: cl, thickness: 1 });
              page.drawLine({ start: { x: fx, y: fy - mk }, end: { x: fx, y: fy + mk }, color: cl, thickness: 1 });
            }
          }

          cardsPlaced++;
        }
      }
    }
  }

  return await doc.save();
}

function toast(msg, type) {
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  document.body.appendChild(el);
  requestAnimationFrame(() => el.classList.add("show"));
  setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => el.remove(), 300);
  }, 2500);
}

function toggleSidebar() {
  const sb = document.getElementById("sidebar");
  sb.classList.toggle("open");
}

window.addEventListener("load", () => {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  }
  init();
});
