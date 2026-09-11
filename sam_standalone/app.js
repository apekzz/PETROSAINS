"use strict";

const $ = (selector) => document.querySelector(selector);
const ui = {
  file: $("#file"), fileName: $("#fileName"), name: $("#name"), stage: $("#stage"), editor: $("#editor"),
  empty: $("#emptyState"), loading: $("#loading"), loadingText: $("#loadingText"), message: $("#message"),
  mode: $("#modeLabel"), instruction: $("#instruction"), coordinate: $("#coordinateValue"), maskState: $("#maskState"),
  generate: $("#generate"), clearPoints: $("#clearPoints"), size: $("#size"), sizeValue: $("#sizeValue"),
  opacity: $("#opacity"), opacityValue: $("#opacityValue"), zoomValue: $("#zoomValue"), zoomMirror: $("#zoomMirror"),
  zoomIn: $("#zoomIn"), zoomOut: $("#zoomOut"), actual: $("#actual"), fit: $("#fit"), pan: $("#pan"),
  undo: $("#undo"), redo: $("#redo"), resetMask: $("#resetMask"), previewButton: $("#previewButton"),
  save: $("#save"), preview: $("#preview"), previewStage: $(".preview-stage"), sourceSize: $("#sourceSize"),
  maskPixels: $("#maskPixels"), samStatus: $("#samStatus"), gpuStatus: $("#gpuStatus"), dbStatus: $("#dbStatus")
};

const display = ui.editor.getContext("2d");
const sourceImage = document.createElement("canvas");
const sourceMask = document.createElement("canvas");
const imageCtx = sourceImage.getContext("2d");
const maskCtx = sourceMask.getContext("2d", { willReadFrequently: true });
const previewCtx = ui.preview.getContext("2d");

const state = {
  sessionId: null, imageLoaded: false, imageWidth: 0, imageHeight: 0,
  tool: "fg", previousTool: "fg", brushSize: 24, maskOpacity: .55,
  points: [], maskPixels: 0, samBaseMask: null, maskModified: false,
  view: { zoom: 1, panX: 0, panY: 0 },
  pointer: { inside: false, screenX: 0, screenY: 0, activeId: null, drawing: false, panning: false, lastImage: null, lastScreen: null },
  spaceDown: false, undoStack: [], redoStack: [], historyLimit: 8, strokeBounds: null,
  renderPending: false, busy: false, saved: false
};

const toolCopy = {
  fg: ["MODE · FOREGROUND POINT", "Click inside the object."],
  bg: ["MODE · BACKGROUND POINT", "Click outside areas SAM should exclude."],
  brush: ["MODE · BRUSH", "Drag to add areas to the mask."],
  eraser: ["MODE · ERASER", "Drag to remove areas from the mask."],
  pan: ["MODE · HAND / PAN", "Drag to move around the image."]
};

function setMessage(text, type = "") { ui.message.textContent = text; ui.message.className = type; }
function setBusy(busy, text = "ANALYZING IMAGE...") {
  state.busy = busy; ui.loading.hidden = !busy; ui.loadingText.textContent = text;
  ui.generate.disabled = busy || !state.points.length; ui.save.disabled = busy || !state.maskPixels || state.saved;
}
async function post(url, payload) {
  const response = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

function resizeDisplay() {
  const rect = ui.stage.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.round(rect.width * dpr));
  const height = Math.max(1, Math.round(rect.height * dpr));
  if (ui.editor.width !== width || ui.editor.height !== height) { ui.editor.width = width; ui.editor.height = height; scheduleRender(); }
}
function stagePoint(event) {
  const rect = ui.stage.getBoundingClientRect();
  return { x: event.clientX - rect.left, y: event.clientY - rect.top };
}
function screenToImage(point) {
  return { x: (point.x - state.view.panX) / state.view.zoom, y: (point.y - state.view.panY) / state.view.zoom };
}
function imageToScreen(point) {
  return { x: point.x * state.view.zoom + state.view.panX, y: point.y * state.view.zoom + state.view.panY };
}
function insideImage(point) { return point.x >= 0 && point.y >= 0 && point.x < state.imageWidth && point.y < state.imageHeight; }
function fitScale() {
  if (!state.imageLoaded) return 1;
  return Math.min((ui.stage.clientWidth - 28) / state.imageWidth, (ui.stage.clientHeight - 28) / state.imageHeight);
}
function minimumZoom() { return Math.min(.25, fitScale()); }
function updateZoomLabels() {
  const value = `${Math.round(state.view.zoom * 100)}%`;
  ui.zoomValue.value = value; ui.zoomMirror.textContent = value;
}
function centerAtZoom(zoom) {
  state.view.zoom = Math.max(minimumZoom(), Math.min(8, zoom));
  state.view.panX = (ui.stage.clientWidth - state.imageWidth * state.view.zoom) / 2;
  state.view.panY = (ui.stage.clientHeight - state.imageHeight * state.view.zoom) / 2;
  updateZoomLabels(); scheduleRender();
}
function fitImage() { if (state.imageLoaded) centerAtZoom(fitScale()); }
function zoomAt(nextZoom, screenPoint = { x: ui.stage.clientWidth / 2, y: ui.stage.clientHeight / 2 }) {
  if (!state.imageLoaded) return;
  const anchor = screenToImage(screenPoint);
  state.view.zoom = Math.max(minimumZoom(), Math.min(8, nextZoom));
  state.view.panX = screenPoint.x - anchor.x * state.view.zoom;
  state.view.panY = screenPoint.y - anchor.y * state.view.zoom;
  updateZoomLabels(); scheduleRender();
}

function scheduleRender() {
  if (state.renderPending) return;
  state.renderPending = true;
  requestAnimationFrame(() => { state.renderPending = false; render(); });
}
function renderPoint(ctx, point) {
  const radius = 8 / state.view.zoom;
  ctx.save(); ctx.lineWidth = 2 / state.view.zoom; ctx.strokeStyle = "white";
  ctx.fillStyle = point.label ? "#0cfa77" : "#e562c0";
  ctx.beginPath(); ctx.arc(point.x, point.y, radius, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  ctx.strokeStyle = "#061017"; ctx.lineWidth = 1.7 / state.view.zoom; ctx.beginPath();
  if (point.label) { ctx.moveTo(point.x - radius / 2, point.y); ctx.lineTo(point.x + radius / 2, point.y); ctx.moveTo(point.x, point.y - radius / 2); ctx.lineTo(point.x, point.y + radius / 2); }
  else { ctx.moveTo(point.x - radius / 2, point.y); ctx.lineTo(point.x + radius / 2, point.y); }
  ctx.stroke(); ctx.restore();
}
function render() {
  const dpr = window.devicePixelRatio || 1, width = ui.editor.width / dpr, height = ui.editor.height / dpr;
  display.setTransform(dpr, 0, 0, dpr, 0, 0); display.clearRect(0, 0, width, height); display.fillStyle = "#020509"; display.fillRect(0, 0, width, height);
  if (state.imageLoaded) {
    display.save(); display.translate(state.view.panX, state.view.panY); display.scale(state.view.zoom, state.view.zoom);
    display.drawImage(sourceImage, 0, 0); display.globalAlpha = state.maskOpacity; display.drawImage(sourceMask, 0, 0); display.globalAlpha = 1;
    state.points.forEach((point) => renderPoint(display, point)); display.restore();
  }
  if (state.pointer.inside && ["brush", "eraser"].includes(activeInteractionTool())) {
    display.save(); display.lineWidth = 1.5; display.strokeStyle = activeInteractionTool() === "eraser" ? "#e562c0" : "#00f0ff";
    display.beginPath(); display.arc(state.pointer.screenX, state.pointer.screenY, state.brushSize * state.view.zoom / 2, 0, Math.PI * 2); display.stroke();
    display.beginPath(); display.arc(state.pointer.screenX, state.pointer.screenY, 1.5, 0, Math.PI * 2); display.fillStyle = display.strokeStyle; display.fill(); display.restore();
  }
}

function maskBytes() {
  const data = maskCtx.getImageData(0, 0, state.imageWidth, state.imageHeight).data;
  const bytes = new Uint8Array(state.imageWidth * state.imageHeight);
  for (let pixel = 0, index = 3; index < data.length; pixel++, index += 4) bytes[pixel] = data[index] >= 128 ? 1 : 0;
  return bytes;
}
function restoreMask(bytes) {
  const imageData = maskCtx.createImageData(state.imageWidth, state.imageHeight); let count = 0;
  for (let pixel = 0, index = 0; pixel < bytes.length; pixel++, index += 4) {
    if (bytes[pixel]) { imageData.data[index] = 0; imageData.data[index + 1] = 240; imageData.data[index + 2] = 255; imageData.data[index + 3] = 255; count++; }
  }
  maskCtx.putImageData(imageData, 0, 0); state.maskPixels = count; updateMaskUi(); scheduleRender();
}
function normalizeMask(bounds = null) {
  const left = bounds ? Math.max(0, Math.floor(bounds.left)) : 0, top = bounds ? Math.max(0, Math.floor(bounds.top)) : 0;
  const right = bounds ? Math.min(state.imageWidth, Math.ceil(bounds.right)) : state.imageWidth, bottom = bounds ? Math.min(state.imageHeight, Math.ceil(bounds.bottom)) : state.imageHeight;
  const data = maskCtx.getImageData(left, top, right - left, bottom - top); let delta = 0;
  for (let i = 0; i < data.data.length; i += 4) { const wasFilled = data.data[i + 3] > 0, filled = data.data[i + 3] >= 128; delta += Number(filled) - Number(wasFilled); data.data[i] = 0; data.data[i + 1] = 240; data.data[i + 2] = 255; data.data[i + 3] = filled ? 255 : 0; }
  maskCtx.putImageData(data, left, top); state.maskPixels = Math.max(0, state.maskPixels + delta);
}
function pushHistory() {
  if (!state.imageLoaded) return;
  state.undoStack.push(maskBytes()); if (state.undoStack.length > state.historyLimit) state.undoStack.shift(); state.redoStack = []; updateHistoryUi();
}
function undo() {
  if (!state.undoStack.length) return;
  state.redoStack.push(maskBytes()); restoreMask(state.undoStack.pop()); state.maskModified = true; updateHistoryUi(); renderPreview(); setMessage("Mask edit undone.");
}
function redo() {
  if (!state.redoStack.length) return;
  state.undoStack.push(maskBytes()); restoreMask(state.redoStack.pop()); state.maskModified = true; updateHistoryUi(); renderPreview(); setMessage("Mask edit restored.");
}
function updateHistoryUi() { ui.undo.disabled = !state.undoStack.length; ui.redo.disabled = !state.redoStack.length; }
function updateMaskUi() {
  ui.maskPixels.textContent = `${state.maskPixels.toLocaleString()} PX`; ui.maskState.textContent = state.maskPixels ? `MASK · ${state.maskModified ? "MODIFIED" : "READY"}` : "MASK · EMPTY";
  ui.maskState.classList.toggle("modified", state.maskModified); ui.previewButton.disabled = !state.maskPixels; ui.save.disabled = state.busy || !state.maskPixels || state.saved; ui.resetMask.disabled = !state.samBaseMask;
}

function activeInteractionTool() { return state.spaceDown ? "pan" : state.tool; }
function selectTool(tool) {
  state.tool = tool; if (tool !== "pan") state.previousTool = tool;
  ["fg", "bg", "brush", "eraser", "pan"].forEach((id) => $("#" + id).classList.toggle("active", id === tool));
  [ui.mode.textContent, ui.instruction.textContent] = toolCopy[tool]; updateCursor(); scheduleRender();
}
function updateCursor() {
  const tool = activeInteractionTool();
  ui.stage.style.cursor = tool === "pan" ? (state.pointer.panning ? "grabbing" : "grab") : ["brush", "eraser"].includes(tool) ? "none" : "crosshair";
}
function drawDot(point, tool) {
  maskCtx.save(); maskCtx.globalCompositeOperation = tool === "eraser" ? "destination-out" : "source-over"; maskCtx.fillStyle = "#00f0ff";
  maskCtx.beginPath(); maskCtx.arc(point.x, point.y, state.brushSize / 2, 0, Math.PI * 2); maskCtx.fill(); maskCtx.restore();
}
function drawSegment(from, to, tool) {
  maskCtx.save(); maskCtx.globalCompositeOperation = tool === "eraser" ? "destination-out" : "source-over"; maskCtx.strokeStyle = "#00f0ff";
  maskCtx.lineWidth = state.brushSize; maskCtx.lineCap = "round"; maskCtx.lineJoin = "round";
  maskCtx.beginPath(); maskCtx.moveTo(from.x, from.y); maskCtx.lineTo(to.x, to.y); maskCtx.stroke(); maskCtx.restore();
}
function finishStroke() {
  if (!state.pointer.drawing) return;
  state.pointer.drawing = false; state.pointer.lastImage = null; normalizeMask(state.strokeBounds); state.strokeBounds = null; state.maskModified = true; state.saved = false; updateHistoryUi(); updateMaskUi(); setMessage("Mask modified locally. Select Preview Object when ready.");
}
function expandStrokeBounds(a, b) {
  const radius = state.brushSize / 2 + 2;
  const left = Math.min(a.x, b.x) - radius, top = Math.min(a.y, b.y) - radius, right = Math.max(a.x, b.x) + radius, bottom = Math.max(a.y, b.y) + radius;
  if (!state.strokeBounds) state.strokeBounds = { left, top, right, bottom };
  else { state.strokeBounds.left = Math.min(state.strokeBounds.left, left); state.strokeBounds.top = Math.min(state.strokeBounds.top, top); state.strokeBounds.right = Math.max(state.strokeBounds.right, right); state.strokeBounds.bottom = Math.max(state.strokeBounds.bottom, bottom); }
}

ui.stage.addEventListener("contextmenu", (event) => event.preventDefault());
ui.stage.addEventListener("pointerenter", () => { state.pointer.inside = true; scheduleRender(); });
ui.stage.addEventListener("pointerleave", () => { if (state.pointer.activeId === null) { state.pointer.inside = false; scheduleRender(); } });
ui.stage.addEventListener("pointerdown", (event) => {
  if (!state.imageLoaded || state.busy) return;
  event.preventDefault(); ui.stage.focus(); const screen = stagePoint(event), image = screenToImage(screen), tool = event.button === 2 && state.tool === "fg" ? "bg" : activeInteractionTool();
  state.pointer.activeId = event.pointerId; ui.stage.setPointerCapture(event.pointerId);
  if (tool === "pan") { state.pointer.panning = true; state.pointer.lastScreen = screen; updateCursor(); return; }
  if (["fg", "bg"].includes(tool)) {
    if (insideImage(image)) { state.points.push({ x: image.x, y: image.y, label: tool === "fg" ? 1 : 0 }); ui.generate.disabled = false; ui.clearPoints.disabled = false; setMessage(`${tool === "fg" ? "Foreground" : "Background"} point added at ${Math.round(image.x)}, ${Math.round(image.y)}.`); scheduleRender(); }
    return;
  }
  pushHistory(); state.pointer.drawing = true; state.pointer.lastImage = image; state.strokeBounds = null; expandStrokeBounds(image, image); drawDot(image, tool); scheduleRender();
});
ui.stage.addEventListener("pointermove", (event) => {
  const screen = stagePoint(event), image = screenToImage(screen); state.pointer.screenX = screen.x; state.pointer.screenY = screen.y; state.pointer.inside = true;
  ui.coordinate.textContent = insideImage(image) ? `X ${Math.round(image.x)} · Y ${Math.round(image.y)}` : "X — · Y —";
  if (state.pointer.panning) { state.view.panX += screen.x - state.pointer.lastScreen.x; state.view.panY += screen.y - state.pointer.lastScreen.y; state.pointer.lastScreen = screen; scheduleRender(); return; }
  if (state.pointer.drawing) {
    const events = typeof event.getCoalescedEvents === "function" ? event.getCoalescedEvents() : [event];
    for (const sample of events) { const next = screenToImage(stagePoint(sample)); expandStrokeBounds(state.pointer.lastImage, next); drawSegment(state.pointer.lastImage, next, state.tool); state.pointer.lastImage = next; }
  }
  scheduleRender();
});
function endPointer(event) {
  if (event.pointerId !== state.pointer.activeId) return;
  finishStroke(); state.pointer.panning = false; state.pointer.activeId = null; state.pointer.lastScreen = null;
  if (ui.stage.hasPointerCapture(event.pointerId)) ui.stage.releasePointerCapture(event.pointerId); updateCursor(); scheduleRender();
}
ui.stage.addEventListener("pointerup", endPointer); ui.stage.addEventListener("pointercancel", endPointer);
ui.stage.addEventListener("lostpointercapture", () => { finishStroke(); state.pointer.panning = false; state.pointer.activeId = null; updateCursor(); });
ui.stage.addEventListener("wheel", (event) => { if (!state.imageLoaded) return; event.preventDefault(); zoomAt(state.view.zoom * Math.exp(-event.deltaY * .0015), stagePoint(event)); }, { passive: false });

function renderPreview() {
  if (!state.imageLoaded || !state.maskPixels) { ui.previewStage.classList.remove("has-preview"); previewCtx.clearRect(0, 0, ui.preview.width, ui.preview.height); return; }
  const scale = Math.min(1, 480 / state.imageWidth, 420 / state.imageHeight), width = Math.max(1, Math.round(state.imageWidth * scale)), height = Math.max(1, Math.round(state.imageHeight * scale));
  ui.preview.width = width; ui.preview.height = height; previewCtx.fillStyle = "white"; previewCtx.fillRect(0, 0, width, height);
  previewCtx.drawImage(sourceImage, 0, 0, width, height); previewCtx.globalCompositeOperation = "destination-in"; previewCtx.drawImage(sourceMask, 0, 0, width, height); previewCtx.globalCompositeOperation = "source-over"; ui.previewStage.classList.add("has-preview");
}
function exportMask() {
  const bytes = maskBytes(), canvas = document.createElement("canvas"); canvas.width = state.imageWidth; canvas.height = state.imageHeight; const ctx = canvas.getContext("2d"), output = ctx.createImageData(canvas.width, canvas.height);
  for (let pixel = 0, index = 0; pixel < bytes.length; pixel++, index += 4) { const value = bytes[pixel] ? 255 : 0; output.data[index] = output.data[index + 1] = output.data[index + 2] = value; output.data[index + 3] = 255; }
  ctx.putImageData(output, 0, 0); return canvas.toDataURL("image/png");
}

ui.file.addEventListener("change", () => {
  const file = ui.file.files[0]; if (!file) return; const reader = new FileReader();
  reader.onload = async () => { setBusy(true, "LOADING IMAGE..."); setMessage("Uploading original-resolution image...");
    try { const data = await post("/api/image", { filename: file.name, image_data: reader.result }), image = new Image();
      image.onload = () => { state.sessionId = data.session_id; state.imageLoaded = true; state.imageWidth = data.width; state.imageHeight = data.height; state.points = []; state.samBaseMask = null; state.undoStack = []; state.redoStack = []; state.maskPixels = 0; state.maskModified = false; state.saved = false;
        sourceImage.width = sourceMask.width = data.width; sourceImage.height = sourceMask.height = data.height; imageCtx.drawImage(image, 0, 0, data.width, data.height); maskCtx.clearRect(0, 0, data.width, data.height);
        ui.fileName.textContent = file.name; ui.sourceSize.textContent = `${data.width} × ${data.height}`; ui.empty.hidden = true; ui.clearPoints.disabled = true; updateHistoryUi(); updateMaskUi(); setBusy(false); fitImage(); selectTool("fg"); setMessage("Image ready. Add foreground and optional background points.", "success"); };
      image.src = reader.result;
    } catch (error) { setBusy(false); setMessage(error.message, "error"); }
  }; reader.readAsDataURL(file);
});
ui.generate.addEventListener("click", async () => {
  setBusy(true, "ANALYZING IMAGE..."); setMessage("Generating segmentation mask with SAM...");
  try { const data = await post("/api/mask", { session_id: state.sessionId, points: state.points.map(p => [p.x, p.y]), labels: state.points.map(p => p.label) }), image = new Image();
    image.onload = () => { pushHistory(); maskCtx.clearRect(0, 0, state.imageWidth, state.imageHeight); maskCtx.drawImage(image, 0, 0); maskCtx.globalCompositeOperation = "source-in"; maskCtx.fillStyle = "#00f0ff"; maskCtx.fillRect(0, 0, state.imageWidth, state.imageHeight); maskCtx.globalCompositeOperation = "source-over"; normalizeMask(); state.samBaseMask = maskBytes(); state.maskModified = false; state.saved = false; setBusy(false); selectTool("brush"); updateMaskUi(); renderPreview(); refreshRuntimeStatus(); setMessage(`SAM mask ready · ${data.pixels.toLocaleString()} selected pixels.`, "success"); };
    image.src = data.mask_data;
  } catch (error) { setBusy(false); setMessage(error.message, "error"); }
});

ui.clearPoints.addEventListener("click", () => { state.points = []; ui.generate.disabled = true; ui.clearPoints.disabled = true; scheduleRender(); setMessage("SAM points cleared. The current mask was preserved."); });
ui.resetMask.addEventListener("click", () => { if (!state.samBaseMask) return; pushHistory(); restoreMask(state.samBaseMask); state.maskModified = false; state.saved = false; renderPreview(); setMessage("Mask reset to the last SAM result."); });
ui.previewButton.addEventListener("click", () => { renderPreview(); ui.previewStage.scrollIntoView({ behavior: "smooth", block: "nearest" }); setMessage("Preview refreshed from the current binary mask."); });
ui.save.addEventListener("click", async () => {
  const name = ui.name.value.trim(); if (!name) { ui.name.focus(); return setMessage("Enter an object name before registration.", "error"); }
  setBusy(true, "CREATING EMBEDDING..."); setMessage("Creating OpenCLIP embedding and writing to pgvector...");
  try { const data = await post("/api/register", { session_id: state.sessionId, object_name: name, mask_data: exportMask() }); state.saved = true; setBusy(false); updateMaskUi(); ui.dbStatus.textContent = "LIVE"; ui.dbStatus.closest(".status-item").className = "status-item ready"; setMessage(`Registration complete · pgvector row ${data.id}.`, "success"); }
  catch (error) { setBusy(false); ui.dbStatus.textContent = "ERROR"; ui.dbStatus.closest(".status-item").className = "status-item error"; setMessage(error.message, "error"); }
});

$("#fg").onclick = () => selectTool("fg"); $("#bg").onclick = () => selectTool("bg"); $("#brush").onclick = () => selectTool("brush"); $("#eraser").onclick = () => selectTool("eraser"); ui.pan.onclick = () => selectTool("pan");
ui.size.oninput = () => { state.brushSize = +ui.size.value; ui.sizeValue.value = `${state.brushSize} px`; scheduleRender(); };
ui.opacity.oninput = () => { state.maskOpacity = +ui.opacity.value / 100; ui.opacityValue.value = `${ui.opacity.value}%`; scheduleRender(); };
ui.zoomIn.onclick = () => zoomAt(state.view.zoom * 1.25); ui.zoomOut.onclick = () => zoomAt(state.view.zoom / 1.25); ui.actual.onclick = () => centerAtZoom(1); ui.fit.onclick = fitImage; ui.undo.onclick = undo; ui.redo.onclick = redo;
window.addEventListener("keydown", (event) => {
  if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;
  if (event.code === "Space") { event.preventDefault(); state.spaceDown = true; updateCursor(); }
  if (event.ctrlKey && event.key.toLowerCase() === "z") { event.preventDefault(); event.shiftKey ? redo() : undo(); return; }
  if (event.ctrlKey && event.key.toLowerCase() === "y") { event.preventDefault(); redo(); return; }
  const key = event.key.toLowerCase(); if (key === "b") selectTool("brush"); else if (key === "e") selectTool("eraser"); else if (key === "h") selectTool("pan"); else if (key === "f") fitImage(); else if (["+", "="].includes(event.key)) zoomAt(state.view.zoom * 1.25); else if (event.key === "-") zoomAt(state.view.zoom / 1.25);
});
window.addEventListener("keyup", (event) => { if (event.code === "Space") { state.spaceDown = false; updateCursor(); } });
window.addEventListener("blur", () => { state.spaceDown = false; finishStroke(); updateCursor(); });

function setRuntime(element, data) { element.textContent = data.label; element.closest(".status-item").className = `status-item ${data.ready ? "ready" : "error"}`; }
function refreshRuntimeStatus() { fetch("/api/status", { cache: "no-store" }).then(r => r.json()).then(data => { setRuntime(ui.samStatus, data.sam); setRuntime(ui.gpuStatus, data.gpu); setRuntime(ui.dbStatus, data.database); }).catch(() => { ui.dbStatus.textContent = "UNAVAILABLE"; ui.dbStatus.closest(".status-item").className = "status-item error"; }); }
refreshRuntimeStatus();
new ResizeObserver(resizeDisplay).observe(ui.stage); resizeDisplay(); updateZoomLabels(); updateHistoryUi(); updateMaskUi(); selectTool("fg");
