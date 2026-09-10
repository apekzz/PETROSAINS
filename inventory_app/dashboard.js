const CONFIG = window.ONESHOT_CONFIG;

let statsReady = false;
let lastIdentifiedNames = [];

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

function currentInventoryQuery() {
    return document.getElementById("searchInput").value.trim();
}

async function fetchInventory(query = currentInventoryQuery()) {
    try {
        let url = CONFIG.inventoryUrl;
        if (query) url = `${CONFIG.searchUrl}?query=${encodeURIComponent(query)}`;
        const response = await fetch(url, { cache: "no-store" });
        if (!response.ok) throw new Error("Inventory request failed");
        renderInventory(await response.json());
    } catch (error) { console.error("Inventory error:", error); }
}

function normalizeName(name) {
    return String(name || "").replace(/_/g, " ").replace(/\s+/g, " ").trim().toLowerCase();
}

function isFreshScan(item) {
    const identified = new Set(lastIdentifiedNames.map(normalizeName));
    if (identified.has(normalizeName(item.item_name))) return true;
    if (!item.last_seen) return false;
    const scannedAt = Date.parse(String(item.last_seen).replace(" ", "T"));
    if (Number.isNaN(scannedAt)) return false;
    return Date.now() - scannedAt < 20000;
}

function renderInventory(items) {
    const table = document.getElementById("inventoryTable");
    table.innerHTML = "";
    if (!items.length) {
        table.innerHTML = `<tr class="empty-row"><td colspan="5">No matching items</td></tr>`;
        return;
    }
    items.forEach((item) => {
        const status = item.status || "Available";
        const statusClass = status.toLowerCase().replace(" ", "-");
        const fresh = isFreshScan(item);
        table.innerHTML += `
            <tr class="${fresh ? "is-new" : ""}">
                <td>${item.item_name}${fresh ? ' <span class="new-tag">new</span>' : ""}</td>
                <td>${item.quantity}</td>
                <td>${item.unit_type || "—"}</td>
                <td>${item.location || "—"}</td>
                <td><span class="status-pill ${statusClass}">${status}</span></td>
            </tr>`;
    });
    const wrap = document.querySelector(".inventory-table-wrap");
    if (wrap) wrap.scrollTop = 0;
}

const cameraFeed = document.getElementById("cameraFeed");
const cameraStatus = document.getElementById("cameraStatus");

// FORCE FRESH STREAM (Bypasses browser cache)
cameraFeed.src = `${CONFIG.videoFeedUrl}?t=${Date.now()}`;

function updateCameraStatus() {
    fetch(CONFIG.cameraStatusUrl, { cache: "no-store" })
        .then((response) => { if (!response.ok) throw new Error("Camera status request failed"); return response.json(); })
        .then((data) => {
            if (data.ok) {
                cameraStatus.textContent = `CAMERA ONLINE • ${data.width} × ${data.height}`;
                cameraStatus.classList.remove("error");
            } else {
                cameraStatus.textContent = "CAMERA ERROR: " + (data.error || "Unable to read camera");
                cameraStatus.classList.add("error");
            }
        })
        .catch((error) => {
            console.error("Camera status error:", error);
            cameraStatus.textContent = "SERVER CONNECTION ERROR";
            cameraStatus.classList.add("error");
        });
}

cameraFeed.onerror = function () {
    cameraStatus.textContent = "VIDEO FEED DISCONNECTED — RETRYING...";
    cameraStatus.classList.add("error");
    setTimeout(() => {
        cameraFeed.src = `${CONFIG.videoFeedUrl}?t=${Date.now()}`;
        updateCameraStatus();
    }, CONFIG.cameraRetryMs);
};

let searchTimer = null;
document.getElementById("searchInput").addEventListener("input", (event) => {
    const query = event.target.value.trim();
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { fetchInventory(query); }, CONFIG.searchDebounceMs);
});

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
    document.querySelectorAll(".mode-btn").forEach((btn) => {
        btn.classList.remove("active");
    });
    const buttonMap = {
        IN: "btnIn",
        SCAN: "btnScan",
        OUT: "btnOut",
    };
    const buttonId = buttonMap[mode];
    if (buttonId) {
        document.getElementById(buttonId).classList.add("active");
    }
    const modeCopy = {
        IN: "locked in · IN · stock goes up",
        SCAN: "locked in · SCAN · view only",
        OUT: "locked in · OUT · stock goes down",
    };
    document.getElementById("modeStatus").textContent =
        modeCopy[mode] || `locked in · ${mode}`;
}

let lastSeenCapture = null;
let lastInventoryRevision = null;

async function updateTriggerStatus() {
    try {
        const response = await fetch("/api/trigger_status", { cache: "no-store" });
        if (!response.ok) throw new Error("Trigger status request failed");
        const data = await response.json();
        const state = (data.state || "WAITING").toUpperCase();
        const statusEl = document.getElementById("triggerStatus");
        const textEl = document.getElementById("triggerStatusText");
        const cssClass = state.toLowerCase();

        statusEl.className = `trigger-status ${cssClass}`;
        textEl.textContent = state;

        const yoloEl = document.getElementById("yoloDetections");
        const labels = data.yolo_labels || [];
        yoloEl.innerHTML = labels
            .map((label) => `<span class="yolo-chip">${label}</span>`)
            .join("");

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
updateCameraStatus();
loadCurrentMode();
updateTriggerStatus();
setInterval(updateCameraStatus, CONFIG.cameraPollMs);
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