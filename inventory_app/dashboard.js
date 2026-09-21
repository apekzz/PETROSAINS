const CONFIG = window.ONESHOT_CONFIG;

let statsReady = false;
let lastIdentifiedNames = [];
let selectedItemName = "";
let inventoryItemNames = [];
let inventoryDisplayToOriginal = Object.create(null);
let inventoryOriginalToDisplay = Object.create(null);
let currentRecognizedStaffName = "";

function animateValue(obj, start, end, duration) {
    const target = Number(end) || 0;
    let startTimestamp = null;
    let finished = false;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.textContent = Math.floor(progress * (target - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.textContent = target;
            finished = true;
        }
    };
    window.requestAnimationFrame(step);
    setTimeout(() => {
        if (!finished) obj.textContent = target;
    }, duration + 80);
}

function setStatValue(id, value) {
    document.getElementById(id).textContent = Number(value) || 0;
}

async function fetchStats(animate = false) {
    if (selectedItemName) {
        await fetchSelectedItemStats(selectedItemName);
        return;
    }
    try {
        const response = await fetch(CONFIG.statsUrl, { cache: "no-store" });
        if (!response.ok) throw new Error("Stats request failed");
        const data = await response.json();
        const total = data.total || 0;
        const available = data.available || 0;
        const checkedOut = data.checked_out || 0;
        const lowStock = data.low_stock || 0;

        if (animate && !statsReady) {
            const duration = CONFIG.statsAnimMs;
            animateValue(document.getElementById("total-items"), 0, total, duration);
            animateValue(document.getElementById("available-items"), 0, available, duration);
            animateValue(document.getElementById("checked-items"), 0, checkedOut, duration);
            animateValue(document.getElementById("low-stock"), 0, lowStock, duration);
            statsReady = true;
            return;
        }

        setStatValue("total-items", total);
        setStatValue("available-items", available);
        setStatValue("checked-items", checkedOut);
        setStatValue("low-stock", lowStock);
        statsReady = true;
    } catch (error) { console.error("Stats error:", error); }
}

function setGlobalStatTitles() {
    document.getElementById("statTitleTotal").textContent = "Total unique items";
    document.getElementById("statTitleAvailable").textContent = "Staff registered";
    document.getElementById("statTitleChecked").textContent = "Checkout sessions";
    document.getElementById("lowStockCard").classList.remove("is-hidden");
    document.querySelector(".stats-row").classList.remove("is-item-focus");
}

async function fetchSelectedItemStats(name) {
    try {
        const response = await fetch(
            `/api/item-summary?name=${encodeURIComponent(name)}`,
            { cache: "no-store" },
        );
        if (!response.ok) throw new Error("Item summary request failed");
        const data = await response.json();
        document.getElementById("statTitleTotal").textContent = "Original stock";
        document.getElementById("statTitleAvailable").textContent = "Available stock";
        document.getElementById("statTitleChecked").textContent = "Frequency of checkout";
        document.getElementById("lowStockCard").classList.add("is-hidden");
        document.querySelector(".stats-row").classList.add("is-item-focus");
        setStatValue("total-items", data.original_stock);
        setStatValue("available-items", data.available_stock);
        setStatValue("checked-items", data.checkout_frequency);
    } catch (error) {
        console.error("Item summary error:", error);
    }
}

async function loadItemOptions() {
    try {
        const response = await fetch(CONFIG.inventoryUrl || "/api/inventory", {
            cache: "no-store",
        });
        if (!response.ok) throw new Error("Inventory names request failed");
        const rows = await response.json();
        inventoryItemNames = [...new Set(
            rows.map((row) => row.inventory_name).filter(Boolean),
        )].sort((left, right) => left.localeCompare(right));
        inventoryDisplayToOriginal = Object.create(null);
        inventoryOriginalToDisplay = Object.create(null);
        inventoryItemNames.forEach((originalName) => {
            const displayName = toDisplayItemName(originalName);
            inventoryOriginalToDisplay[originalName] = displayName;
            inventoryDisplayToOriginal[displayName.toLocaleLowerCase()] = originalName;
        });
        renderItemOptions();
    } catch (error) {
        console.error("Item options error:", error);
    }
}

function toDisplayItemName(name) {
    return String(name || "").replace(
        /\S+/g,
        (word) => word.charAt(0).toLocaleUpperCase() + word.slice(1).toLocaleLowerCase(),
    );
}

function setItemOptionsOpen(open) {
    const list = document.getElementById("itemOptions");
    const input = document.getElementById("itemSelector");
    const visible = Boolean(open && list.childElementCount);
    list.classList.toggle("is-open", visible);
    input.setAttribute("aria-expanded", visible ? "true" : "false");
}

function renderItemOptions(query = "") {
    const list = document.getElementById("itemOptions");
    const needle = String(query || "").trim().toLocaleLowerCase();
    const matches = inventoryItemNames.filter((originalName) => {
        const displayName = inventoryOriginalToDisplay[originalName] || originalName;
        return (
            !needle
            || originalName.toLocaleLowerCase().includes(needle)
            || displayName.toLocaleLowerCase().includes(needle)
        );
    });
    list.replaceChildren(...matches.slice(0, 60).map((originalName) => {
        const option = document.createElement("button");
        option.type = "button";
        option.className = "item-option";
        option.setAttribute("role", "option");
        option.dataset.originalName = originalName;
        option.textContent = inventoryOriginalToDisplay[originalName] || originalName;
        return option;
    }));
    setItemOptionsOpen(document.activeElement === document.getElementById("itemSelector"));
}

function selectInventoryItem(name) {
    const query = String(name || "").trim();
    if (!query) return;
    const mapped = inventoryDisplayToOriginal[query.toLocaleLowerCase()];
    const exact = inventoryItemNames.find(
        (item) => item.toLocaleLowerCase() === query.toLocaleLowerCase(),
    );
    const substring = inventoryItemNames.find(
        (item) => (
            item.toLocaleLowerCase().includes(query.toLocaleLowerCase())
            || (inventoryOriginalToDisplay[item] || item)
                .toLocaleLowerCase()
                .includes(query.toLocaleLowerCase())
        ),
    );
    selectedItemName = mapped || exact || substring || "";
    if (!selectedItemName) return;
    document.getElementById("itemSelector").value =
        inventoryOriginalToDisplay[selectedItemName] || selectedItemName;
    document.getElementById("btnClearItem").classList.remove("is-hidden");
    setItemOptionsOpen(false);
    fetchSelectedItemStats(selectedItemName);
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

let knownMovementIds = new Set();
let movementsPrimed = false;

async function fetchInventory() {
    if (!currentRecognizedStaffName) {
        renderMovements([]);
        return;
    }
    try {
        const base = CONFIG.movementsUrl || "/api/movements";
        const response = await fetch(
            `${base}?staff_name=${encodeURIComponent(currentRecognizedStaffName)}`,
            { cache: "no-store" },
        );
        if (!response.ok) throw new Error("Movements request failed");
        renderMovements(await response.json());
    } catch (error) { console.error("Movements error:", error); }
}

function renderMovements(rows) {
    const table = document.getElementById("inventoryTable");
    if (!rows.length) {
        table.innerHTML = `<tr class="empty-row"><td colspan="7">No movements for the recognized staff</td></tr>`;
        knownMovementIds = new Set();
        movementsPrimed = true;
        return;
    }
    const incoming = new Set();
    table.innerHTML = rows.map((row) => {
        incoming.add(row.id);
        const isNew = movementsPrimed && !knownMovementIds.has(row.id);
        return `
            <tr class="${isNew ? "is-enter" : ""}" data-id="${row.id}">
                <td>${escapeHtml(row.id)}</td>
                <td>${escapeHtml(row.inventory_name)}</td>
                <td>${escapeHtml(row.out_staff_name ?? "")}</td>
                <td>${escapeHtml(row.in_staff_name ?? "")}</td>
                <td>${escapeHtml(row.quantity)}</td>
                <td>${escapeHtml(row.out_dt || "")}</td>
                <td>${escapeHtml(row.in_dt || "")}</td>
            </tr>`;
    }).join("");
    if (movementsPrimed) {
        const wrap = document.querySelector(".inventory-table-wrap");
        if (wrap && [...incoming].some((id) => !knownMovementIds.has(id))) {
            wrap.scrollTop = 0;
        }
    }
    knownMovementIds = incoming;
    movementsPrimed = true;
}

const cameraFeed = document.getElementById("cameraFeed");
const liveVideo = document.getElementById("liveVideo");
const landmarkLayer = document.getElementById("landmarkLayer");
const cameraCtx = cameraFeed.getContext("2d", { alpha: false });
const faceToggleWrap = document.getElementById("faceToggleWrap");
const flowToggleWrap = document.getElementById("flowToggleWrap");
const flowModeToggle = document.getElementById("flowModeToggle");
const objectRecognitionGate = document.getElementById("objectRecognitionGate");
const btnStartObjectRecognition = document.getElementById("btnStartObjectRecognition");
const objectRecognitionGateText = objectRecognitionGate
    ? objectRecognitionGate.querySelector("span")
    : null;
let flowArmed = false;
let objectArmBusy = false;
let detectionPreviewShowing = false;
let detectionPreviewTimer = null;
const landmarkCtx = landmarkLayer.getContext("2d");
let localStream = null;
let usingLocalCamera = false;
let faceAnalyzeEnabled = true;
let scanIngestEnabled = false;
let analyzeBusy = false;
let scanBusy = false;
let faceLandmarker = null;
let FaceLandmarkerClass = null;
let pendingFaceBlob = null;
let lastLandmarks = null;
let facePreviewObjectUrl = "";
let capturedForModal = false;
const COVERAGE_READY = 0.90;
const GATE_OVAL = { cx: 0.50, cy: 0.50, rx: 0.115, ry: 0.195 };
const FACE_OVAL_IDX = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
    172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109,
];
const FACE_CONTOURS = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    [17, 18, 19, 20, 21],
    [22, 23, 24, 25, 26],
    [27, 28, 29, 30, 31, 32, 33, 34, 35],
    [36, 37, 38, 39, 40, 41, 36],
    [42, 43, 44, 45, 46, 47, 42],
    [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 48],
];

function updateFacePreviews(blob) {
    if (!blob) return;
    const previousUrl = facePreviewObjectUrl;
    facePreviewObjectUrl = URL.createObjectURL(blob);
    const registerPreview = document.getElementById("registerFacePreview");
    const recognizedPreview = document.getElementById("recognizedFacePreview");
    if (registerPreview) registerPreview.src = facePreviewObjectUrl;
    if (recognizedPreview) recognizedPreview.src = facePreviewObjectUrl;
    if (previousUrl) URL.revokeObjectURL(previousUrl);
}

function base64JpegToBlob(value) {
    const binary = atob(value);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) {
        bytes[index] = binary.charCodeAt(index);
    }
    return new Blob([bytes], { type: "image/jpeg" });
}

function sizeOverlayToVideo() {
    const width = liveVideo.videoWidth || 640;
    const height = liveVideo.videoHeight || 480;
    if (landmarkLayer.width !== width || landmarkLayer.height !== height) {
        landmarkLayer.width = width;
        landmarkLayer.height = height;
    }
}

function pointInGate(x, y) {
    const dx = (x - GATE_OVAL.cx) / GATE_OVAL.rx;
    const dy = (y - GATE_OVAL.cy) / GATE_OVAL.ry;
    return dx * dx + dy * dy <= 1;
}

function faceCoverage(landmarks) {
    if (!landmarks || !landmarks.length) return 0;
    let inside = 0;
    landmarks.forEach((point) => {
        if (pointInGate(point.x, point.y)) inside += 1;
    });
    return inside / landmarks.length;
}

function faceSpan(landmarks) {
    let minX = 1;
    let minY = 1;
    let maxX = 0;
    let maxY = 0;
    landmarks.forEach((point) => {
        minX = Math.min(minX, point.x);
        minY = Math.min(minY, point.y);
        maxX = Math.max(maxX, point.x);
        maxY = Math.max(maxY, point.y);
    });
    return { w: maxX - minX, h: maxY - minY };
}

function faceReady(landmarks) {
    if (!landmarks || !landmarks.length) return false;
    if (faceUiMode === "register") return faceCoverage(landmarks) >= COVERAGE_READY;
    const span = faceSpan(landmarks);
    return span.w >= 0.08 && span.h >= 0.1;
}

function updateCoverageLabel(ratio) {
    const el = document.getElementById("faceCoverage");
    if (!el) return;
    const pct = Math.round(Math.max(0, Math.min(1, ratio)) * 100);
    el.textContent = `${pct}%`;
    el.classList.toggle("is-ready", ratio >= COVERAGE_READY);
}

async function grabSegmentedFace(landmarks) {
    if (!liveVideo.videoWidth || !landmarks || !landmarks.length) return null;
    const width = liveVideo.videoWidth;
    const height = liveVideo.videoHeight;
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(liveVideo, 0, 0);
    ctx.globalCompositeOperation = "destination-in";
    ctx.beginPath();
    FACE_OVAL_IDX.forEach((index, step) => {
        const point = landmarks[index];
        if (!point) return;
        const x = point.x * width;
        const y = point.y * height;
        if (step === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fill();

    let minX = width;
    let minY = height;
    let maxX = 0;
    let maxY = 0;
    FACE_OVAL_IDX.forEach((index) => {
        const point = landmarks[index];
        if (!point) return;
        const x = point.x * width;
        const y = point.y * height;
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
    });
    const pad = 8;
    minX = Math.max(0, Math.floor(minX - pad));
    minY = Math.max(0, Math.floor(minY - pad));
    maxX = Math.min(width, Math.ceil(maxX + pad));
    maxY = Math.min(height, Math.ceil(maxY + pad));
    if (maxX - minX < 24 || maxY - minY < 24) return null;

    const FACE_EMBED_SIZE = 224;
    const crop = document.createElement("canvas");
    crop.width = FACE_EMBED_SIZE;
    crop.height = FACE_EMBED_SIZE;
    crop.getContext("2d").drawImage(
        canvas,
        minX,
        minY,
        maxX - minX,
        maxY - minY,
        0,
        0,
        FACE_EMBED_SIZE,
        FACE_EMBED_SIZE,
    );
    return new Promise((resolve) => crop.toBlob(resolve, "image/jpeg", 0.82));
}

function drawMediaPipeLandmarks(landmarks) {
    sizeOverlayToVideo();
    landmarkCtx.clearRect(0, 0, landmarkLayer.width, landmarkLayer.height);
    const width = landmarkLayer.width;
    const height = landmarkLayer.height;
    landmarkCtx.strokeStyle = "rgba(0, 212, 200, 0.55)";
    landmarkCtx.fillStyle = "rgba(62, 224, 176, 0.95)";
    landmarkCtx.lineWidth = 1;
    const groups = FaceLandmarkerClass
        ? [
            FaceLandmarkerClass.FACE_LANDMARKS_TESSELATION,
            FaceLandmarkerClass.FACE_LANDMARKS_FACE_OVAL,
            FaceLandmarkerClass.FACE_LANDMARKS_LEFT_EYE,
            FaceLandmarkerClass.FACE_LANDMARKS_RIGHT_EYE,
            FaceLandmarkerClass.FACE_LANDMARKS_LIPS,
        ].filter(Boolean)
        : [];
    groups.forEach((connections) => {
        connections.forEach((pair) => {
            const start = landmarks[pair.start];
            const end = landmarks[pair.end];
            if (!start || !end) return;
            landmarkCtx.beginPath();
            landmarkCtx.moveTo(start.x * width, start.y * height);
            landmarkCtx.lineTo(end.x * width, end.y * height);
            landmarkCtx.stroke();
        });
    });
    landmarks.forEach((point) => {
        landmarkCtx.beginPath();
        landmarkCtx.arc(point.x * width, point.y * height, 1.4, 0, Math.PI * 2);
        landmarkCtx.fill();
    });
}

function applyLocalFace(ready, detected, coverage) {
    updateCoverageLabel(coverage || 0);
    if (detected && ready) {
        lastFaceReady = true;
        if (registerModalOpen) updateRegisterSave();
        setFaceHint(
            faceUiMode === "register"
                ? "Face captured — enter staff name and ID"
                : "Recognizing current face"
        );
        return;
    }
    if (registerModalOpen && faceUiMode === "register") {
        return;
    }
    lastFaceReady = false;
    if (!detected) setFaceHint("Looking for a face");
    else if ((coverage || 0) < COVERAGE_READY) {
        setFaceHint(`Fill the outline · ${Math.round((coverage || 0) * 100)}%`);
    } else {
        setFaceHint("Move your face into the outline");
    }
}

async function sendSegmentedEmbed(blob) {
    if (!blob) return false;
    const body = new FormData();
    body.append("file", blob, "face.jpg");
    body.append("mode", faceUiMode);
    const response = await fetch("/api/face/embed", { method: "POST", body, cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.detail || "Could not store the captured face");
    }
    return data;
}

async function captureReadyFace(landmarks) {
    const blob = await grabSegmentedFace(landmarks);
    if (!blob) return false;
    pendingFaceBlob = blob;
    lastFaceReady = true;
    updateFacePreviews(blob);
    if (faceUiMode === "register") {
        if (!registerModalOpen) showRegisterModal(true);
        updateRegisterSave();
        return true;
    }
    try {
        const status = await sendSegmentedEmbed(blob);
        applyFaceStatus(status);
        if (faceUiMode === "recognize" && !status.recognized) {
            setFaceHint(status.message || "Face not found in staff registry");
        }
    } catch (error) {
        console.error("Capture embed error:", error);
        const statusEl = document.getElementById("registerStatus");
        if (statusEl) statusEl.textContent = error.message || "Could not store the captured face.";
        return false;
    }
    return true;
}

let recognizeBusy = false;
let lastRecognizeAt = 0;

function runBrowserFaceLoop() {
    if (!faceAnalyzeEnabled || !liveVideo.videoWidth || !faceLandmarker) {
        window.requestAnimationFrame(runBrowserFaceLoop);
        return;
    }
    try {
        const result = faceLandmarker.detectForVideo(liveVideo, performance.now());
        const landmarks = result && result.faceLandmarks && result.faceLandmarks[0];
        if (landmarks && landmarks.length) {
            lastLandmarks = landmarks;
            const coverage = faceCoverage(landmarks);
            const ready = faceReady(landmarks);
            if (coverage >= 0.4 || ready) {
                drawMediaPipeLandmarks(landmarks);
            } else {
                landmarkCtx.clearRect(0, 0, landmarkLayer.width, landmarkLayer.height);
            }
            applyLocalFace(ready, true, coverage);
            if (ready && faceUiMode === "recognize") {
                const now = performance.now();
                if (!recognizeBusy && now - lastRecognizeAt > 1000) {
                    lastRecognizeAt = now;
                    recognizeBusy = true;
                    captureReadyFace(landmarks).finally(() => {
                        recognizeBusy = false;
                    });
                }
            } else if (ready && !capturedForModal) {
                capturedForModal = true;
                captureReadyFace(landmarks);
            }
            if (!ready && !registerModalOpen && faceUiMode !== "recognize") {
                capturedForModal = false;
                pendingFaceBlob = null;
            }
        } else {
            lastLandmarks = null;
            landmarkCtx.clearRect(0, 0, landmarkLayer.width, landmarkLayer.height);
            applyLocalFace(false, false, 0);
            if (!registerModalOpen && faceUiMode !== "recognize") {
                capturedForModal = false;
                pendingFaceBlob = null;
            }
        }
    } catch (error) {
        console.error("Browser face loop error:", error);
    }
    window.requestAnimationFrame(runBrowserFaceLoop);
}

async function startBrowserFaceLandmarker() {
    try {
        const vision = await import("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs");
        FaceLandmarkerClass = vision.FaceLandmarker;
        const fileset = await vision.FilesetResolver.forVisionTasks(
            "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm"
        );
        const modelUrl =
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";
        try {
            faceLandmarker = await FaceLandmarkerClass.createFromOptions(fileset, {
                baseOptions: { modelAssetPath: modelUrl, delegate: "GPU" },
                runningMode: "VIDEO",
                numFaces: 1,
            });
        } catch (gpuError) {
            faceLandmarker = await FaceLandmarkerClass.createFromOptions(fileset, {
                baseOptions: { modelAssetPath: modelUrl, delegate: "CPU" },
                runningMode: "VIDEO",
                numFaces: 1,
            });
        }
        console.log("[FACE] Browser Face Landmarker ready");
        window.requestAnimationFrame(runBrowserFaceLoop);
    } catch (error) {
        console.error("[FACE] Browser Face Landmarker failed, using server YuNet:", error);
        setInterval(analyzeLocalFrame, 140);
    }
}

function drawLandmarks(points, mesh, inRegion) {
    sizeOverlayToVideo();
    landmarkCtx.clearRect(0, 0, landmarkLayer.width, landmarkLayer.height);
    if (!inRegion || (!(points && points.length) && !(mesh && mesh.length))) {
        return;
    }
    const width = landmarkLayer.width;
    const height = landmarkLayer.height;
    landmarkCtx.strokeStyle = "rgba(0, 212, 200, 0.95)";
    landmarkCtx.fillStyle = "rgba(62, 224, 176, 1)";
    landmarkCtx.lineWidth = 2;
    if (mesh && mesh.length) {
        FACE_CONTOURS.forEach((loop) => {
            landmarkCtx.beginPath();
            loop.forEach((index, step) => {
                if (index >= mesh.length) return;
                const x = mesh[index].x * width;
                const y = mesh[index].y * height;
                if (step === 0) landmarkCtx.moveTo(x, y);
                else landmarkCtx.lineTo(x, y);
            });
            landmarkCtx.stroke();
        });
    }
    (points || []).forEach((point) => {
        landmarkCtx.beginPath();
        landmarkCtx.arc(point.x * width, point.y * height, 4.5, 0, Math.PI * 2);
        landmarkCtx.fill();
    });
}

async function grabLocalFrame() {
    if (liveVideo.videoWidth) {
        const canvas = document.createElement("canvas");
        canvas.width = liveVideo.videoWidth;
        canvas.height = liveVideo.videoHeight;
        canvas.getContext("2d").drawImage(liveVideo, 0, 0);
        return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.85));
    }
    if (snapshotReady && cameraFeed.width) {
        return new Promise((resolve) => cameraFeed.toBlob(resolve, "image/jpeg", 0.85));
    }
    return null;
}

async function analyzeLocalFrame() {
    if (!usingLocalCamera || !faceAnalyzeEnabled || analyzeBusy || document.hidden) return;
    const blob = await grabLocalFrame();
    if (!blob) return;
    analyzeBusy = true;
    try {
        const body = new FormData();
        body.append("file", blob, "frame.jpg");
        const response = await fetch("/api/face/analyze", { method: "POST", body, cache: "no-store" });
        if (!response.ok) return;
        const data = await response.json();
        if (data.in_region && data.face_preview_b64 && !capturedForModal) {
            const faceBlob = base64JpegToBlob(data.face_preview_b64);
            pendingFaceBlob = faceBlob;
            capturedForModal = true;
            lastFaceReady = true;
            updateFacePreviews(faceBlob);
            if (faceUiMode === "register" && !registerModalOpen) {
                showRegisterModal(true);
            }
            updateRegisterSave();
        } else if (!data.in_region && !registerModalOpen) {
            capturedForModal = false;
            pendingFaceBlob = null;
        }
        drawLandmarks(data.points || [], data.mesh || [], Boolean(data.in_region));
        applyFaceStatus(data);
    } catch (error) {
        console.error("Face analyze error:", error);
    } finally {
        analyzeBusy = false;
    }
}

async function ingestScanFrame() {
    if (!usingLocalCamera || !scanIngestEnabled || scanBusy || document.hidden) return;
    const blob = await grabLocalFrame();
    if (!blob) return;
    scanBusy = true;
    try {
        const body = new FormData();
        body.append("file", blob, "frame.jpg");
        await fetch("/api/scan/frame", { method: "POST", body, cache: "no-store" });
    } catch (error) {
        console.error("Scan frame error:", error);
    } finally {
        scanBusy = false;
    }
}

let cameraFacing = "user";
let cameraStartPromise = null;
let captureFallback = false;
let snapshotReady = false;

function isPhoneDevice() {
    return /iPhone|iPad|iPod|Android/i.test(navigator.userAgent || "");
}

function isLoopbackHost() {
    const host = (location.hostname || "").toLowerCase();
    return host === "localhost" || host === "127.0.0.1" || host === "::1";
}

function needsCaptureFallback() {
    return isPhoneDevice() && location.protocol === "http:" && !isLoopbackHost();
}

async function refreshCameraList(activeId) {
    const select = document.getElementById("cameraSource");
    if (!select || !navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
    const devices = (await navigator.mediaDevices.enumerateDevices())
        .filter((device) => device.kind === "videoinput");
    const current = activeId || select.value;
    select.replaceChildren();
    const auto = document.createElement("option");
    auto.value = "";
    auto.textContent = isPhoneDevice() ? "This phone" : "Default camera";
    select.appendChild(auto);
    devices.forEach((device, index) => {
        const option = document.createElement("option");
        option.value = device.deviceId;
        option.textContent = device.label || `Camera ${index + 1}`;
        select.appendChild(option);
    });
    if (current && [...select.options].some((option) => option.value === current)) {
        select.value = current;
    }
}

function enableCaptureFallback() {
    const cameraUnlock = document.getElementById("cameraUnlock");
    const cameraView = document.querySelector(".camera-view");
    captureFallback = true;
    usingLocalCamera = true;
    liveVideo.classList.add("is-hidden");
    if (cameraUnlock) {
        cameraUnlock.textContent = cameraFacing === "environment" ? "Rear camera" : "Front camera";
        cameraUnlock.classList.remove("is-hidden");
    }
    if (cameraView) cameraView.classList.toggle("is-rear", cameraFacing === "environment");
    setFaceHint("Safari blocks live camera on http. Tap the button and take a photo.");
}

function applyCapturedPhoto(file) {
    if (!file) return;
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
        cameraFeed.width = img.naturalWidth;
        cameraFeed.height = img.naturalHeight;
        cameraCtx.drawImage(img, 0, 0);
        snapshotReady = true;
        usingLocalCamera = true;
        cameraFeed.classList.remove("is-hidden");
        liveVideo.classList.add("is-hidden");
        URL.revokeObjectURL(url);
        sizeOverlayToVideo();
        setFaceHint("Photo ready. Tap again for a new shot.");
        analyzeLocalFrame();
    };
    img.onerror = () => URL.revokeObjectURL(url);
    img.src = url;
}

function openNativeCamera() {
    const input = cameraFacing === "environment"
        ? document.getElementById("iosCamEnv")
        : document.getElementById("iosCamUser");
    if (input) input.click();
}

async function startLocalCamera(deviceId, facing) {
    const want = facing || cameraFacing || "user";
    cameraFacing = want;
    if (needsCaptureFallback()) {
        enableCaptureFallback();
        return;
    }
    if (cameraStartPromise) return cameraStartPromise;
    cameraStartPromise = (async () => {
        try {
            if (localStream) {
                localStream.getTracks().forEach((track) => track.stop());
                localStream = null;
            }
            const video = deviceId
                ? { deviceId: { exact: deviceId }, width: { ideal: 1280 }, height: { ideal: 720 } }
                : { facingMode: { ideal: want }, width: { ideal: 1280 }, height: { ideal: 720 } };
            localStream = await navigator.mediaDevices.getUserMedia({ video, audio: false });
            const track = localStream.getVideoTracks()[0];
            const activeId = track && track.getSettings ? track.getSettings().deviceId : deviceId;
            liveVideo.srcObject = localStream;
            liveVideo.setAttribute("playsinline", "true");
            liveVideo.muted = true;
            await liveVideo.play();
            usingLocalCamera = true;
            captureFallback = false;
            snapshotReady = false;
            liveVideo.classList.remove("is-hidden");
            cameraFeed.classList.add("is-hidden");
            const cameraUnlock = document.getElementById("cameraUnlock");
            if (cameraUnlock) cameraUnlock.classList.add("is-hidden");
            if (!faceLandmarker && !FaceLandmarkerClass) startBrowserFaceLandmarker();
            if (!window._oneshotScanTimer) {
                window._oneshotScanTimer = setInterval(ingestScanFrame, 140);
            }
            await refreshCameraList(activeId || "");
            setFaceHint("Camera ready");
        } catch (error) {
            console.error("getUserMedia error:", error);
            enableCaptureFallback();
        } finally {
            cameraStartPromise = null;
        }
    })();
    return cameraStartPromise;
}

function stopLocalCamera() {
    usingLocalCamera = false;
    if (localStream) {
        localStream.getTracks().forEach((track) => track.stop());
        localStream = null;
    }
    liveVideo.srcObject = null;
    landmarkCtx.clearRect(0, 0, landmarkLayer.width, landmarkLayer.height);
}

async function pumpVideo() {
    if (usingLocalCamera) {
        window.setTimeout(pumpVideo, 200);
        return;
    }
    try {
        const response = await fetch(`/video_frame?t=${Date.now()}`, { cache: "no-store" });
        if (response.ok) {
            const blob = await response.blob();
            const bitmap = await createImageBitmap(blob);
            if (cameraFeed.width !== bitmap.width || cameraFeed.height !== bitmap.height) {
                cameraFeed.width = bitmap.width;
                cameraFeed.height = bitmap.height;
            }
            cameraCtx.drawImage(bitmap, 0, 0);
            bitmap.close();
        }
    } catch (error) {
        console.error("Video pump error:", error);
    }
    window.setTimeout(pumpVideo, 33);
}

startLocalCamera();

function applyObjectRecognitionState(canArm, armed, previewActive = false) {
    const readyForClick = Boolean(canArm && !armed && !previewActive);
    scanIngestEnabled = Boolean(canArm && armed);
    if (objectRecognitionGate) {
        objectRecognitionGate.classList.toggle("is-hidden", !readyForClick);
    }
    if (btnStartObjectRecognition && !objectArmBusy) {
        btnStartObjectRecognition.disabled = false;
        btnStartObjectRecognition.textContent = "Start object recognition";
    }
    if (objectRecognitionGateText && !objectArmBusy) {
        objectRecognitionGateText.textContent = "Object recognition is paused";
    }
}

function restoreLiveDetectionStream() {
    if (detectionPreviewTimer) {
        clearTimeout(detectionPreviewTimer);
        detectionPreviewTimer = null;
    }
    detectionPreviewShowing = false;
    if (usingLocalCamera) {
        cameraFeed.classList.add("is-hidden");
        liveVideo.classList.remove("is-hidden");
        landmarkLayer.classList.remove("is-hidden");
    }
}

async function showFrozenDetectionPreview(remainingMs) {
    if (detectionPreviewShowing) return;
    detectionPreviewShowing = true;
    try {
        const response = await fetch(
            `/api/detection/preview?t=${Date.now()}`,
            { cache: "no-store" },
        );
        if (!response.ok) throw new Error("Detection preview is unavailable");
        const bitmap = await createImageBitmap(await response.blob());
        cameraFeed.width = bitmap.width;
        cameraFeed.height = bitmap.height;
        cameraCtx.drawImage(bitmap, 0, 0);
        bitmap.close();
        liveVideo.classList.add("is-hidden");
        landmarkLayer.classList.add("is-hidden");
        cameraFeed.classList.remove("is-hidden");
        detectionPreviewTimer = window.setTimeout(
            restoreLiveDetectionStream,
            Math.max(100, Number(remainingMs) || 6000) + 75,
        );
    } catch (error) {
        console.error("Detection preview error:", error);
        restoreLiveDetectionStream();
    }
}

async function startObjectRecognition() {
    if (objectArmBusy) return;
    objectArmBusy = true;
    if (btnStartObjectRecognition) {
        btnStartObjectRecognition.disabled = true;
        btnStartObjectRecognition.textContent = "Starting…";
    }
    if (objectRecognitionGateText) {
        objectRecognitionGateText.textContent = "Preparing detection";
    }
    try {
        const response = await fetch("/api/detection/arm", {
            method: "POST",
            cache: "no-store",
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.detail || "Could not start object recognition");
        }
        applyObjectRecognitionState(true, Boolean(data.detection_armed), false);
    } catch (error) {
        console.error("Object recognition start error:", error);
        applyObjectRecognitionState(true, false);
        if (objectRecognitionGateText) {
            objectRecognitionGateText.textContent =
                error.message || "Could not start detection";
        }
    } finally {
        objectArmBusy = false;
        if (btnStartObjectRecognition) {
            btnStartObjectRecognition.disabled = false;
            btnStartObjectRecognition.textContent = "Start object recognition";
        }
    }
}

if (btnStartObjectRecognition) {
    btnStartObjectRecognition.addEventListener("click", startObjectRecognition);
}

async function setMode(mode) {
    try {
        const response = await fetch(`/api/mode/${mode}`, {
            method: "POST",
            cache: "no-store",
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Mode change failed");
        }
        applyMode(data.mode);
    } catch (error) {
        console.error("Mode error:", error);
    }
}

async function loadCurrentMode() {
    try {
        const response = await fetch("/api/mode", { cache: "no-store" });
        if (!response.ok) throw new Error("Mode request failed");
        const data = await response.json();
        applyMode(data.mode);
    } catch (error) {
        console.error("Mode load error:", error);
    }
}

function applyMode(mode) {
    if (flowModeToggle) {
        flowModeToggle.checked = mode === "OUT";
    }
}

let lastSeenCapture = null;
let lastInventoryRevision = null;

async function updateTriggerStatus() {
    try {
        const response = await fetch("/api/trigger_status", { cache: "no-store" });
        if (!response.ok) throw new Error("Trigger status request failed");
        const data = await response.json();
        const state = (data.state || "WAITING").toUpperCase();
        const detectionArmed = Boolean(data.detection_armed);
        const previewActive = Boolean(data.preview_active);
        applyObjectRecognitionState(
            Boolean(data.can_arm_detection),
            detectionArmed,
            previewActive,
        );
        if (previewActive) {
            showFrozenDetectionPreview(data.preview_remaining_ms);
        } else if (detectionPreviewShowing) {
            restoreLiveDetectionStream();
        }
        const statusEl = document.getElementById("triggerStatus");
        const textEl = document.getElementById("triggerStatusText");
        if (state === "FACE") {
            statusEl.className = "trigger-status face";
            textEl.textContent = "FACE";
        } else if (state === "READY") {
            statusEl.className = "trigger-status waiting";
            textEl.textContent = "READY";
        } else if (state === "PREVIEW") {
            statusEl.className = "trigger-status capturing";
            textEl.textContent =
                `PREVIEW ${Math.max(1, Math.ceil((data.preview_remaining_ms || 0) / 1000))}S`;
        } else {
            statusEl.className = `trigger-status ${state.toLowerCase()}`;
            textEl.textContent = state;
        }

        const yoloEl = document.getElementById("yoloDetections");
        const labels = data.yolo_labels || [];
        yoloEl.innerHTML = labels
            .map((label) => `<span class="yolo-chip">${label}</span>`)
            .join("");

        const overlay = document.getElementById("objectDetectionOverlay");
        const boxes = detectionArmed && !previewActive
            ? (data.yolo_boxes || [])
            : [];
        overlay.innerHTML = boxes.map((item) => {
            const box = item.box || [];
            if (box.length !== 4) return "";
            const left = Math.max(0, Math.min(1, Number(box[0]) || 0)) * 100;
            const top = Math.max(0, Math.min(1, Number(box[1]) || 0)) * 100;
            const right = Math.max(0, Math.min(1, Number(box[2]) || 0)) * 100;
            const bottom = Math.max(0, Math.min(1, Number(box[3]) || 0)) * 100;
            const confidence = Math.round((Number(item.confidence) || 0) * 100);
            const similarity = item.similarity == null
                ? "—"
                : `${Math.round(Number(item.similarity) * 100)}%`;
            return `
                <div class="object-detection-box" style="
                    left:${left}%; top:${top}%;
                    width:${Math.max(0, right - left)}%;
                    height:${Math.max(0, bottom - top)}%;
                ">
                    <div class="object-detection-label">
                        <strong>${escapeHtml(item.name || "object")}</strong>
                        <span>DET ${confidence}%</span>
                        <span>SIM ${similarity}</span>
                    </div>
                </div>`;
        }).join("");

        const identified = data.last_classes || [];
        if (identified.length) {
            lastIdentifiedNames = identified;
        }

        const revision = data.inventory_revision;
        const captureChanged = data.last_capture && data.last_capture !== lastSeenCapture;
        const inventoryChanged = lastInventoryRevision !== null && revision !== lastInventoryRevision;
        if (lastInventoryRevision === null && revision !== undefined) {
            lastInventoryRevision = revision;
        }
        if (captureChanged) {
            lastSeenCapture = data.last_capture;
        }
        if (captureChanged || inventoryChanged) {
            lastInventoryRevision = revision;
            fetchInventory();
            fetchStats(false);
        }
    } catch (error) {
        console.error("Trigger status error:", error);
    }
}

fetchStats(true);
fetchInventory();
loadItemOptions();
setInterval(() => fetchStats(false), 1000);
document.getElementById("itemSelector").addEventListener("change", (event) => {
    selectInventoryItem(event.target.value);
});
document.getElementById("itemSelector").addEventListener("input", (event) => {
    renderItemOptions(event.target.value);
    if (event.target.value) return;
    selectedItemName = "";
    document.getElementById("btnClearItem").classList.add("is-hidden");
    setGlobalStatTitles();
    fetchStats(false);
});
document.getElementById("itemSelector").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        selectInventoryItem(event.target.value);
    } else if (event.key === "Escape") {
        setItemOptionsOpen(false);
    } else if (event.key === "ArrowDown") {
        event.preventDefault();
        document.querySelector("#itemOptions .item-option")?.focus();
    }
});
document.getElementById("itemSelector").addEventListener("focus", (event) => {
    renderItemOptions(event.target.value);
});
document.getElementById("itemOptions").addEventListener("pointerdown", (event) => {
    event.preventDefault();
});
document.getElementById("itemOptions").addEventListener("click", (event) => {
    const option = event.target.closest(".item-option");
    if (option) selectInventoryItem(option.dataset.originalName);
});
document.getElementById("btnClearItem").addEventListener("click", () => {
    selectedItemName = "";
    document.getElementById("itemSelector").value = "";
    document.getElementById("btnClearItem").classList.add("is-hidden");
    setItemOptionsOpen(false);
    setGlobalStatTitles();
    fetchStats(false);
});
document.addEventListener("pointerdown", (event) => {
    if (!event.target.closest(".item-selector")) setItemOptionsOpen(false);
});
loadCurrentMode();
updateTriggerStatus();
setInterval(updateTriggerStatus, CONFIG.triggerPollMs || 500);

const bootOverlay = document.getElementById("bootOverlay");
const bootStage = document.getElementById("bootStage");
const bootFill = document.getElementById("bootFill");
const bootPct = document.getElementById("bootPct");
const bootStartedAt = Date.now();

function hideBootOverlay() {
    bootOverlay.classList.add("is-done");
}

async function pollBootStatus() {
    try {
        const response = await fetch("/api/boot_status", { cache: "no-store" });
        if (response.ok) {
            const data = await response.json();
            const percent = Math.max(8, data.percent || 0);
            bootStage.textContent = data.stage || "initializing vision core";
            bootFill.style.width = `${percent}%`;
            bootPct.textContent = `${percent}%`;
            if (data.ready) {
                const wait = Math.max(0, 1200 - (Date.now() - bootStartedAt));
                setTimeout(hideBootOverlay, wait);
                return;
            }
        }
    } catch (error) {
        bootStage.textContent = "waiting for OneShot core";
    }
    setTimeout(pollBootStatus, 140);
}

pollBootStatus();

function setDbBadge(state, text) {
    const badge = document.getElementById("dbStatusBadge");
    const label = document.getElementById("dbStatusText");
    badge.className = `status-badge ${state}`;
    label.textContent = text;
}

async function updateDbStatus() {
    try {
        const response = await fetch(CONFIG.dbStatusUrl, { cache: "no-store" });
        const data = await response.json();
        if (data.connected) {
            setDbBadge("live", "LIVE");
            return;
        }
        throw new Error(data.error || "Database unavailable");
    } catch (error) {
        console.error("DB status error:", error);
        setDbBadge("error", "DB ERROR");
        setTimeout(updateDbStatus, CONFIG.dbRetryMs || 5000);
    }
}

updateDbStatus();

const faceGate = document.getElementById("faceGate");
const faceGateHint = document.getElementById("faceGateHint");
const faceModeToggle = document.getElementById("faceModeToggle");
const registerModal = document.getElementById("registerModal");
const recognizedStaffEl = document.getElementById("recognizedStaff");
let faceUiMode = "recognize";
let registerModalOpen = false;
let lastFaceReady = false;

function setFaceHint(message) {
    if (faceGateHint) faceGateHint.textContent = message || "Position your face in the outline";
}

function showRegisterModal(show) {
    registerModalOpen = Boolean(show);
    registerModal.classList.toggle("is-hidden", !show);
    registerModal.setAttribute("aria-hidden", show ? "false" : "true");
    if (show) {
        document.getElementById("registerStatus").textContent = "";
        const progress = document.getElementById("registerProgress");
        if (progress) progress.classList.add("is-hidden");
        setRegisterProgress(0);
        updateRegisterSave();
        document.getElementById("staffName").focus();
    }
}

function hasCapturedRegisterFace() {
    return Boolean(pendingFaceBlob || lastFaceReady);
}

function updateRegisterSave() {
    const name = document.getElementById("staffName").value.trim();
    const staffId = document.getElementById("staffId").value.trim();
    document.getElementById("btnRegisterSave").disabled = !(
        name && staffId && hasCapturedRegisterFace()
    );
}

async function openRegisterPopup() {
    if (faceUiMode !== "register") {
        await setFaceMode("register");
    }
    if (!pendingFaceBlob && lastLandmarks) {
        const blob = await grabSegmentedFace(lastLandmarks);
        if (blob) {
            pendingFaceBlob = blob;
            lastFaceReady = true;
            capturedForModal = true;
            updateFacePreviews(blob);
        }
    }
    showRegisterModal(true);
    const statusEl = document.getElementById("registerStatus");
    if (statusEl && !pendingFaceBlob) {
        statusEl.textContent = "Stay in the outline until a face is captured, then fill in both fields.";
    }
    updateRegisterSave();
}

function renderRecognized(staff, unknownStaff = false, matchScore = null, matchThreshold = 0.78) {
    const viewer = document.getElementById("recognizedViewer");
    const viewerName = document.getElementById("recognizedViewerName");
    const viewerMeta = document.getElementById("recognizedViewerMeta");
    const viewerKicker = viewer ? viewer.querySelector(".recognized-viewer-kicker") : null;
    if (unknownStaff) {
        const confidence = Math.max(0, Math.round((Number(matchScore) || 0) * 100));
        if (recognizedStaffEl) {
            recognizedStaffEl.textContent = "UNKNOWN STAFF";
            recognizedStaffEl.classList.remove("is-hidden");
            recognizedStaffEl.classList.add("is-unknown");
        }
        if (viewerKicker) viewerKicker.textContent = "Identity rejected";
        if (viewerName) viewerName.textContent = "UNKNOWN STAFF";
        if (viewerMeta) {
            const need = Math.round((Number(matchThreshold) || 0.78) * 100);
            viewerMeta.textContent = `${confidence}% similarity · ${need}% required`;
        }
        if (viewer) {
            viewer.classList.remove("is-hidden");
            viewer.classList.add("is-unknown");
        }
        return;
    }
    if (!staff) {
        if (recognizedStaffEl) {
            recognizedStaffEl.textContent = "";
            recognizedStaffEl.classList.add("is-hidden");
            recognizedStaffEl.classList.remove("is-unknown");
        }
        if (viewer) {
            viewer.classList.add("is-hidden");
            viewer.classList.remove("is-unknown");
        }
        return;
    }
    const confidence = Math.round((Number(staff.score) || 0) * 100);
    const staffChanged = currentRecognizedStaffName !== staff.staff_name;
    currentRecognizedStaffName = staff.staff_name;
    if (recognizedStaffEl) {
        recognizedStaffEl.textContent = `Staff · ${staff.staff_name}`;
        recognizedStaffEl.classList.remove("is-hidden");
        recognizedStaffEl.classList.remove("is-unknown");
    }
    if (viewerKicker) viewerKicker.textContent = "Identity verified";
    if (viewerName) viewerName.textContent = staff.staff_name;
    if (viewerMeta) {
        viewerMeta.textContent = `${staff.staff_id} · ${confidence}% similarity`;
    }
    if (viewer) {
        viewer.classList.remove("is-hidden");
        viewer.classList.remove("is-unknown");
    }
    if (staffChanged) fetchInventory();
}

async function setFaceMode(mode) {
    faceUiMode = mode;
    faceModeToggle.checked = mode === "register";
    capturedForModal = false;
    pendingFaceBlob = null;
    lastFaceReady = false;
    try {
        const response = await fetch(CONFIG.faceModeUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode }),
            cache: "no-store",
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Face mode failed");
        applyFaceStatus(data);
    } catch (error) {
        console.error("Face mode error:", error);
        setFaceHint(error.message || "Could not change face mode");
    }
}

function applyFaceStatus(data) {
    const visible = !data.recognized;
    const unknownStaff = Boolean(data.unknown_staff);
    const view = document.querySelector(".camera-view");
    faceGate.classList.toggle("is-hidden", !visible);
    if (view) view.classList.toggle("is-gating", visible);
    if (view) view.classList.toggle("is-unknown-staff", unknownStaff);
    faceGate.classList.toggle(
        "is-ready",
        Boolean(!unknownStaff && (lastFaceReady || data.recognized)),
    );
    faceGate.classList.toggle("is-warn", visible && (unknownStaff || !lastFaceReady));
    if (!faceLandmarker) setFaceHint(data.message);
    renderRecognized(
        data.recognized,
        unknownStaff,
        data.match_score,
        data.match_threshold,
    );
    if (!data.recognized) {
        applyObjectRecognitionState(false, false);
    }
    if (data.recognized) {
        faceAnalyzeEnabled = faceUiMode !== "register";
        applyObjectRecognitionState(
            true,
            Boolean(data.detection_armed),
            Boolean(data.detection_preview_active),
        );
        landmarkCtx.clearRect(0, 0, landmarkLayer.width, landmarkLayer.height);
        if (faceToggleWrap) faceToggleWrap.classList.add("is-hidden");
        if (flowToggleWrap) flowToggleWrap.classList.remove("is-hidden");
        if (!flowArmed) {
            flowArmed = true;
            setMode("OUT");
        }
    } else if (data.mode === "register" || data.mode === "recognize") {
        faceAnalyzeEnabled = true;
        applyObjectRecognitionState(false, false);
        flowArmed = false;
        if (faceToggleWrap) faceToggleWrap.classList.remove("is-hidden");
        if (flowToggleWrap) flowToggleWrap.classList.add("is-hidden");
    }
    if (data.mode === "register" || faceUiMode === "register") {
        faceUiMode = "register";
        faceModeToggle.checked = true;
    } else if (data.mode === "recognize") {
        faceUiMode = "recognize";
        faceModeToggle.checked = false;
        if (registerModalOpen) showRegisterModal(false);
    }
    if (registerModalOpen) updateRegisterSave();
}

async function pollFaceStatus() {
    if (usingLocalCamera && faceAnalyzeEnabled) return;
    try {
        const response = await fetch(CONFIG.faceStatusUrl, { cache: "no-store" });
        if (!response.ok) throw new Error("Face status failed");
        applyFaceStatus(await response.json());
    } catch (error) {
        console.error("Face status error:", error);
    }
}

function setRegisterProgress(pct, message) {
    const fill = document.getElementById("registerProgressFill");
    const label = document.getElementById("registerProgressPct");
    const statusEl = document.getElementById("registerStatus");
    const clamped = Math.max(0, Math.min(100, Math.round(pct)));
    if (fill) fill.style.width = `${clamped}%`;
    if (label) label.textContent = `${clamped}%`;
    if (message && statusEl) statusEl.textContent = `${message} · ${clamped}%`;
}

async function blobToBase64(blob) {
    const buffer = await blob.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    let binary = "";
    const step = 0x8000;
    for (let i = 0; i < bytes.length; i += step) {
        binary += String.fromCharCode(...bytes.subarray(i, i + step));
    }
    return btoa(binary);
}

async function submitFaceRegister() {
    const staffName = document.getElementById("staffName").value.trim();
    const staffId = document.getElementById("staffId").value.trim();
    const statusEl = document.getElementById("registerStatus");
    if (!staffName || !staffId) {
        statusEl.textContent = "Fill in both fields.";
        return;
    }
    if (!hasCapturedRegisterFace()) {
        statusEl.textContent = "Keep a complete face in the outline.";
        return;
    }
    const button = document.getElementById("btnRegisterSave");
    const progress = document.getElementById("registerProgress");
    button.disabled = true;
    progress.classList.remove("is-hidden");
    progress.setAttribute("aria-hidden", "false");
    setRegisterProgress(25, "Saving staff record");
    try {
        const crop = pendingFaceBlob || await grabLocalFrame();
        const image_b64 = crop ? await blobToBase64(crop) : "";
        setRegisterProgress(70, "Writing staff record");
        const response = await fetch(CONFIG.faceRegisterUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                staff_id: staffId,
                staff_name: staffName,
                image_b64,
            }),
            cache: "no-store",
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Register failed");
        setRegisterProgress(100, `Saved ${data.staff_name}`);
        fetchStats(false);
        document.getElementById("staffName").value = "";
        document.getElementById("staffId").value = "";
        setTimeout(() => {
            showRegisterModal(false);
            progress.classList.add("is-hidden");
            setRegisterProgress(0);
        }, 700);
    } catch (error) {
        console.error("Register error:", error);
        statusEl.textContent = error.message || "Could not save the face.";
        progress.classList.add("is-hidden");
        setRegisterProgress(0);
    } finally {
        updateRegisterSave();
    }
}

faceModeToggle.addEventListener("change", () => {
    setFaceMode(faceModeToggle.checked ? "register" : "recognize");
});
document.querySelectorAll("#faceToggleWrap > span").forEach((label) => {
    label.addEventListener("click", () => {
        const mode = label.textContent.trim().toLowerCase() === "register"
            ? "register"
            : "recognize";
        faceModeToggle.checked = mode === "register";
        setFaceMode(mode);
    });
});
if (flowModeToggle) {
    flowModeToggle.addEventListener("change", () => {
        setMode(flowModeToggle.checked ? "OUT" : "IN");
    });
}
document.querySelectorAll("#flowToggleWrap > span").forEach((label) => {
    label.addEventListener("click", () => {
        const checkout = label.textContent.trim().toLowerCase() === "check out";
        flowModeToggle.checked = checkout;
        setMode(checkout ? "OUT" : "IN");
    });
});
document.getElementById("btnRegisterCancel").addEventListener("click", () => {
    showRegisterModal(false);
    capturedForModal = false;
    pendingFaceBlob = null;
    lastFaceReady = false;
});
document.getElementById("btnRegisterSave").addEventListener("click", submitFaceRegister);
document.getElementById("staffName").addEventListener("input", updateRegisterSave);
document.getElementById("staffId").addEventListener("input", updateRegisterSave);
const btnHeaderRegisterFace = document.getElementById("btnHeaderRegisterFace");
if (btnHeaderRegisterFace) {
    btnHeaderRegisterFace.addEventListener("click", openRegisterPopup);
}

const catalogImportModal = document.getElementById("catalogImportModal");
const btnImportCatalog = document.getElementById("btnImportCatalog");
const btnCatalogClose = document.getElementById("btnCatalogClose");
let catalogPollTimer = null;

function showCatalogImportModal(show) {
    catalogImportModal.classList.toggle("is-hidden", !show);
    catalogImportModal.setAttribute("aria-hidden", show ? "false" : "true");
}

function renderCatalogImport(state) {
    const stage = state.stage || "idle";
    const percent = Math.max(0, Math.min(100, Number(state.percent) || 0));
    const stageEl = document.getElementById("catalogImportStage");
    const currentEl = document.getElementById("catalogImportCurrent");
    const summaryEl = document.getElementById("catalogImportSummary");
    document.getElementById("catalogImportFill").style.width = `${percent}%`;
    document.getElementById("catalogImportPct").textContent = `${percent}%`;
    stageEl.textContent = stage === "selecting"
        ? "Select images/train, then labels/train"
        : stage;
    const counts = state.total
        ? `${state.processed || 0} / ${state.total}`
        : "";
    currentEl.textContent = [counts, state.current || ""].filter(Boolean).join(" · ");
    btnImportCatalog.disabled = Boolean(state.running);
    btnCatalogClose.disabled = Boolean(state.running);

    if (stage === "complete" && state.result) {
        const result = state.result;
        summaryEl.textContent =
            `${result.embeddings} mask embeddings saved · ${result.unique_items} unique items`;
        fetchStats();
        fetchInventory();
        loadItemOptions();
    } else if (stage === "failed") {
        summaryEl.textContent = state.error || "Catalog import failed.";
    } else if (state.running) {
        summaryEl.textContent = stage === "database"
            ? "Replacing inventory_emb and rebuilding main_inventory…"
            : `${state.embedded || 0} embeddings prepared`;
    }

    if (!state.running && catalogPollTimer) {
        window.clearInterval(catalogPollTimer);
        catalogPollTimer = null;
    }
}

async function pollCatalogImport() {
    try {
        const response = await fetch("/api/catalog/import/status", { cache: "no-store" });
        if (response.ok) renderCatalogImport(await response.json());
    } catch (error) {
        console.error("Catalog status error:", error);
    }
}

btnImportCatalog.addEventListener("click", async () => {
    showCatalogImportModal(true);
    renderCatalogImport({ running: true, stage: "selecting", percent: 2 });
    try {
        const response = await fetch("/api/catalog/import/select", {
            method: "POST",
            cache: "no-store",
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Could not start catalog import.");
        renderCatalogImport(data);
        if (!catalogPollTimer) {
            catalogPollTimer = window.setInterval(pollCatalogImport, 500);
        }
    } catch (error) {
        renderCatalogImport({
            running: false,
            stage: "failed",
            percent: 0,
            error: error.message || "Could not start catalog import.",
        });
    }
});

btnCatalogClose.addEventListener("click", () => showCatalogImportModal(false));

pollFaceStatus();
setFaceMode("recognize");
setInterval(pollFaceStatus, CONFIG.facePollMs || 220);

const cameraSource = document.getElementById("cameraSource");
const cameraFlip = document.getElementById("cameraFlip");
const cameraUnlock = document.getElementById("cameraUnlock");
if (cameraSource) {
    cameraSource.addEventListener("change", () => {
        startLocalCamera(cameraSource.value, cameraFacing);
    });
}
if (cameraFlip) {
    cameraFlip.addEventListener("click", () => {
        cameraFacing = cameraFacing === "environment" ? "user" : "environment";
        if (cameraSource) cameraSource.value = "";
        if (captureFallback) {
            enableCaptureFallback();
            return;
        }
        startLocalCamera("", cameraFacing);
    });
}
if (cameraUnlock) {
    cameraUnlock.addEventListener("click", openNativeCamera);
}
["iosCamUser", "iosCamEnv"].forEach((id) => {
    const input = document.getElementById(id);
    if (!input) return;
    input.addEventListener("change", () => {
        const file = input.files && input.files[0];
        applyCapturedPhoto(file);
        input.value = "";
    });
});

function pingClientHello() {
    fetch("/api/client/hello", { method: "POST", cache: "no-store", keepalive: true }).catch(() => {});
}

pingClientHello();
setInterval(pingClientHello, 2000);
window.addEventListener("pagehide", (event) => {
    if (event.persisted) return;
    navigator.sendBeacon("/api/client/leave");
});
window.addEventListener("beforeunload", () => {
    navigator.sendBeacon("/api/client/leave");
});