"use strict";

(() => {
    const byId = (id) => document.getElementById(id);
    const ui = {
        launch: byId("btnSamRegister"),
        modal: byId("samModal"),
        close: byId("samClose"),
        runtime: byId("samRuntime"),
        stage: byId("samStage"),
        editor: byId("samEditor"),
        loading: byId("samLoading"),
        loadingText: byId("samLoadingText"),
        message: byId("samMessage"),
        mode: byId("samMode"),
        coordinates: byId("samCoordinates"),
        maskState: byId("samMaskState"),
        fg: byId("samFg"),
        bg: byId("samBg"),
        generate: byId("samGenerate"),
        clearPoints: byId("samClearPoints"),
        brush: byId("samBrush"),
        eraser: byId("samEraser"),
        brushSize: byId("samBrushSize"),
        brushValue: byId("samBrushValue"),
        opacity: byId("samOpacity"),
        opacityValue: byId("samOpacityValue"),
        undo: byId("samUndo"),
        redo: byId("samRedo"),
        reset: byId("samReset"),
        preview: byId("samPreview"),
        previewStage: document.querySelector(".sam-preview-stage"),
        proceed: byId("samProceed"),
        detailsModal: byId("samDetailsModal"),
        detailsImage: byId("samDetailsImage"),
        objectName: byId("samObjectName"),
        saveStatus: byId("samSaveStatus"),
        back: byId("samBack"),
        save: byId("samSave"),
    };
    if (!ui.launch || !ui.editor) return;

    const display = ui.editor.getContext("2d");
    const sourceCanvas = document.createElement("canvas");
    const maskCanvas = document.createElement("canvas");
    const sourceCtx = sourceCanvas.getContext("2d");
    const maskCtx = maskCanvas.getContext("2d", { willReadFrequently: true });
    const previewCtx = ui.preview.getContext("2d");
    const state = {
        open: false,
        busy: false,
        sessionId: "",
        width: 0,
        height: 0,
        tool: "fg",
        points: [],
        maskPixels: 0,
        opacity: 0.55,
        brushSize: 24,
        baseMask: null,
        undo: [],
        redo: [],
        pointerId: null,
        drawing: false,
        lastPoint: null,
        hoverPoint: null,
        previousRuntime: null,
        transform: { scale: 1, x: 0, y: 0 },
    };

    function setMessage(message, error = false) {
        ui.message.textContent = message;
        ui.message.classList.toggle("error", error);
    }

    function setBusy(busy, message = "Working…") {
        state.busy = busy;
        ui.loading.classList.toggle("is-hidden", !busy);
        ui.loadingText.textContent = message;
        updateControls();
    }

    function updateControls() {
        const hasImage = Boolean(state.width && state.height);
        const hasMask = state.maskPixels > 0;
        ui.generate.disabled = state.busy || !state.points.some((point) => point.label === 1);
        ui.clearPoints.disabled = state.busy || !state.points.length;
        ui.proceed.disabled = state.busy || !hasMask;
        ui.undo.disabled = state.busy || !state.undo.length;
        ui.redo.disabled = state.busy || !state.redo.length;
        ui.reset.disabled = state.busy || !state.baseMask;
        ui.maskState.textContent = hasMask
            ? `Mask · ${state.maskPixels.toLocaleString()} px`
            : "Mask · empty";
        ui.stage.setAttribute("aria-busy", state.busy ? "true" : "false");
        if (!hasImage) ui.generate.disabled = true;
    }

    async function requestJson(url, options = {}) {
        const response = await fetch(url, { cache: "no-store", ...options });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            const detail = data.detail;
            const message = Array.isArray(detail)
                ? detail.map((item) => item.msg || item).join("; ")
                : (detail || `Request failed (${response.status})`);
            throw new Error(message);
        }
        return data;
    }

    function selectTool(tool) {
        state.tool = tool;
        ["fg", "bg", "brush", "eraser"].forEach((name) => {
            ui[name].classList.toggle("active", name === tool);
        });
        const labels = {
            fg: "Mode · foreground point",
            bg: "Mode · background point",
            brush: "Mode · add mask brush",
            eraser: "Mode · erase mask",
        };
        ui.mode.textContent = labels[tool];
        ui.stage.style.cursor = ["brush", "eraser"].includes(tool) ? "none" : "crosshair";
        render();
    }

    function resizeDisplay() {
        const rect = ui.stage.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        ui.editor.width = Math.max(1, Math.round(rect.width * dpr));
        ui.editor.height = Math.max(1, Math.round(rect.height * dpr));
        render();
    }

    function calculateTransform() {
        const dpr = window.devicePixelRatio || 1;
        const canvasWidth = ui.editor.width / dpr;
        const canvasHeight = ui.editor.height / dpr;
        if (!state.width || !state.height) {
            return { scale: 1, x: 0, y: 0 };
        }
        const scale = Math.min(
            (canvasWidth - 24) / state.width,
            (canvasHeight - 24) / state.height,
        );
        return {
            scale,
            x: (canvasWidth - state.width * scale) / 2,
            y: (canvasHeight - state.height * scale) / 2,
        };
    }

    function screenToImage(event) {
        const rect = ui.stage.getBoundingClientRect();
        const point = {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top,
        };
        const transform = state.transform;
        return {
            x: (point.x - transform.x) / transform.scale,
            y: (point.y - transform.y) / transform.scale,
        };
    }

    function insideImage(point) {
        return (
            point.x >= 0
            && point.y >= 0
            && point.x < state.width
            && point.y < state.height
        );
    }

    function render() {
        const dpr = window.devicePixelRatio || 1;
        const width = ui.editor.width / dpr;
        const height = ui.editor.height / dpr;
        display.setTransform(dpr, 0, 0, dpr, 0, 0);
        display.clearRect(0, 0, width, height);
        display.fillStyle = "#02070b";
        display.fillRect(0, 0, width, height);
        if (!state.width || !state.height) return;
        state.transform = calculateTransform();
        const { scale, x, y } = state.transform;
        display.save();
        display.translate(x, y);
        display.scale(scale, scale);
        display.drawImage(sourceCanvas, 0, 0);
        display.globalAlpha = state.opacity;
        display.drawImage(maskCanvas, 0, 0);
        display.globalAlpha = 1;
        state.points.forEach((point) => {
            const radius = 8 / scale;
            display.beginPath();
            display.arc(point.x, point.y, radius, 0, Math.PI * 2);
            display.fillStyle = point.label ? "#5ee9a0" : "#ff5a98";
            display.fill();
            display.lineWidth = 2 / scale;
            display.strokeStyle = "#ffffff";
            display.stroke();
        });
        if (
            state.maskPixels
            && state.hoverPoint
            && ["brush", "eraser"].includes(state.tool)
        ) {
            const radius = state.brushSize / 2;
            display.beginPath();
            display.arc(
                state.hoverPoint.x,
                state.hoverPoint.y,
                radius,
                0,
                Math.PI * 2,
            );
            display.lineWidth = 4 / scale;
            display.strokeStyle = "rgba(2, 7, 11, 0.86)";
            display.stroke();
            display.beginPath();
            display.arc(
                state.hoverPoint.x,
                state.hoverPoint.y,
                radius,
                0,
                Math.PI * 2,
            );
            display.setLineDash([5 / scale, 3 / scale]);
            display.lineWidth = 2 / scale;
            display.strokeStyle = state.tool === "eraser" ? "#ff5a98" : "#ffffff";
            display.stroke();
            display.setLineDash([]);
        }
        display.restore();
    }

    function maskBytes() {
        const rgba = maskCtx.getImageData(0, 0, state.width, state.height).data;
        const bytes = new Uint8Array(state.width * state.height);
        for (let pixel = 0, index = 3; index < rgba.length; pixel += 1, index += 4) {
            bytes[pixel] = rgba[index] >= 128 ? 1 : 0;
        }
        return bytes;
    }

    function restoreMask(bytes) {
        const imageData = maskCtx.createImageData(state.width, state.height);
        let count = 0;
        for (let pixel = 0, index = 0; pixel < bytes.length; pixel += 1, index += 4) {
            if (!bytes[pixel]) continue;
            imageData.data[index] = 0;
            imageData.data[index + 1] = 212;
            imageData.data[index + 2] = 200;
            imageData.data[index + 3] = 255;
            count += 1;
        }
        maskCtx.putImageData(imageData, 0, 0);
        state.maskPixels = count;
        updateControls();
        render();
        renderPreview();
    }

    function normalizeMask() {
        const imageData = maskCtx.getImageData(0, 0, state.width, state.height);
        let count = 0;
        for (let index = 0; index < imageData.data.length; index += 4) {
            const selected = imageData.data[index + 3] >= 128;
            imageData.data[index] = 0;
            imageData.data[index + 1] = 212;
            imageData.data[index + 2] = 200;
            imageData.data[index + 3] = selected ? 255 : 0;
            if (selected) count += 1;
        }
        maskCtx.putImageData(imageData, 0, 0);
        state.maskPixels = count;
        updateControls();
    }

    function pushHistory() {
        if (!state.width) return;
        state.undo.push(maskBytes());
        if (state.undo.length > 8) state.undo.shift();
        state.redo = [];
        updateControls();
    }

    function drawMaskStroke(from, to, tool) {
        maskCtx.save();
        maskCtx.globalCompositeOperation = tool === "eraser"
            ? "destination-out"
            : "source-over";
        maskCtx.strokeStyle = "#00d4c8";
        maskCtx.lineWidth = state.brushSize;
        maskCtx.lineCap = "round";
        maskCtx.lineJoin = "round";
        maskCtx.beginPath();
        maskCtx.moveTo(from.x, from.y);
        maskCtx.lineTo(to.x, to.y);
        maskCtx.stroke();
        maskCtx.restore();
    }

    function selectedBounds(bytes) {
        let minX = state.width;
        let minY = state.height;
        let maxX = -1;
        let maxY = -1;
        for (let y = 0; y < state.height; y += 1) {
            for (let x = 0; x < state.width; x += 1) {
                if (!bytes[y * state.width + x]) continue;
                minX = Math.min(minX, x);
                minY = Math.min(minY, y);
                maxX = Math.max(maxX, x);
                maxY = Math.max(maxY, y);
            }
        }
        if (maxX < 0) return null;
        return {
            x1: Math.max(0, minX - 8),
            y1: Math.max(0, minY - 8),
            x2: Math.min(state.width, maxX + 9),
            y2: Math.min(state.height, maxY + 9),
        };
    }

    function segmentedCanvas() {
        const bytes = maskBytes();
        const bounds = selectedBounds(bytes);
        if (!bounds) return null;
        const isolated = document.createElement("canvas");
        isolated.width = state.width;
        isolated.height = state.height;
        const isolatedCtx = isolated.getContext("2d");
        isolatedCtx.drawImage(sourceCanvas, 0, 0);
        isolatedCtx.globalCompositeOperation = "destination-in";
        isolatedCtx.drawImage(maskCanvas, 0, 0);
        const result = document.createElement("canvas");
        result.width = bounds.x2 - bounds.x1;
        result.height = bounds.y2 - bounds.y1;
        const resultCtx = result.getContext("2d");
        resultCtx.fillStyle = "#000000";
        resultCtx.fillRect(0, 0, result.width, result.height);
        resultCtx.drawImage(
            isolated,
            bounds.x1,
            bounds.y1,
            result.width,
            result.height,
            0,
            0,
            result.width,
            result.height,
        );
        return result;
    }

    function renderPreview() {
        const segmented = state.maskPixels ? segmentedCanvas() : null;
        if (!segmented) {
            ui.previewStage.classList.remove("has-preview");
            previewCtx.clearRect(0, 0, ui.preview.width, ui.preview.height);
            return null;
        }
        const scale = Math.min(1, 440 / segmented.width, 380 / segmented.height);
        ui.preview.width = Math.max(1, Math.round(segmented.width * scale));
        ui.preview.height = Math.max(1, Math.round(segmented.height * scale));
        previewCtx.drawImage(segmented, 0, 0, ui.preview.width, ui.preview.height);
        ui.previewStage.classList.add("has-preview");
        return segmented;
    }

    function exportMask() {
        const bytes = maskBytes();
        const canvas = document.createElement("canvas");
        canvas.width = state.width;
        canvas.height = state.height;
        const ctx = canvas.getContext("2d");
        const output = ctx.createImageData(state.width, state.height);
        for (let pixel = 0, index = 0; pixel < bytes.length; pixel += 1, index += 4) {
            const value = bytes[pixel] ? 255 : 0;
            output.data[index] = value;
            output.data[index + 1] = value;
            output.data[index + 2] = value;
            output.data[index + 3] = 255;
        }
        ctx.putImageData(output, 0, 0);
        return canvas.toDataURL("image/png");
    }

    async function captureFrozenFrame() {
        const videoReady = Boolean(liveVideo && liveVideo.videoWidth);
        const source = videoReady ? liveVideo : cameraFeed;
        const width = videoReady ? liveVideo.videoWidth : cameraFeed.width;
        const height = videoReady ? liveVideo.videoHeight : cameraFeed.height;
        if (!width || !height) throw new Error("Take a photo first, then open SAM");
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        canvas.getContext("2d").drawImage(source, 0, 0, width, height);
        const blob = await new Promise((resolve, reject) => {
            canvas.toBlob(
                (value) => value ? resolve(value) : reject(new Error("Could not freeze frame")),
                "image/jpeg",
                0.94,
            );
        });
        return { canvas, blob };
    }

    function loadSourceCanvas(canvas) {
        state.width = canvas.width;
        state.height = canvas.height;
        sourceCanvas.width = maskCanvas.width = state.width;
        sourceCanvas.height = maskCanvas.height = state.height;
        sourceCtx.drawImage(canvas, 0, 0);
        maskCtx.clearRect(0, 0, state.width, state.height);
        state.points = [];
        state.maskPixels = 0;
        state.baseMask = null;
        state.undo = [];
        state.redo = [];
        updateControls();
        render();
        renderPreview();
    }

    async function openEditor() {
        if (state.open || state.busy) return;
        state.open = true;
        state.previousRuntime = { faceAnalyzeEnabled, scanIngestEnabled };
        faceAnalyzeEnabled = false;
        scanIngestEnabled = false;
        ui.modal.classList.remove("is-hidden");
        ui.modal.setAttribute("aria-hidden", "false");
        ui.detailsModal.classList.add("is-hidden");
        setBusy(true, "Freezing camera frame…");
        setMessage("Freezing the current camera frame.");
        try {
            const frozen = await captureFrozenFrame();
            if (usingLocalCamera) liveVideo.pause();
            loadSourceCanvas(frozen.canvas);
            setBusy(true, "Preparing SAM image features…");
            const form = new FormData();
            form.append("file", frozen.blob, "sam-capture.jpg");
            const data = await requestJson("/api/sam/capture", {
                method: "POST",
                body: form,
            });
            state.sessionId = data.session_id;
            ui.runtime.textContent = `SAM · ${data.model_type} · ${data.device}`;
            ui.runtime.classList.remove("error");
            setBusy(false);
            selectTool("fg");
            setMessage("Frame ready. Add foreground and optional background points.");
        } catch (error) {
            setBusy(false);
            ui.runtime.textContent = "SAM · unavailable";
            ui.runtime.classList.add("error");
            setMessage(error.message || "Could not start SAM.", true);
        }
    }

    async function closeEditor() {
        const sessionId = state.sessionId;
        state.open = false;
        state.sessionId = "";
        ui.detailsModal.classList.add("is-hidden");
        ui.modal.classList.add("is-hidden");
        ui.modal.setAttribute("aria-hidden", "true");
        if (sessionId) {
            fetch(`/api/sam/session/${encodeURIComponent(sessionId)}`, {
                method: "DELETE",
                keepalive: true,
            }).catch(() => {});
        }
        if (state.previousRuntime) {
            faceAnalyzeEnabled = state.previousRuntime.faceAnalyzeEnabled;
            scanIngestEnabled = state.previousRuntime.scanIngestEnabled;
        }
        if (usingLocalCamera && liveVideo.paused) {
            liveVideo.play().catch(() => {});
        }
    }

    async function generateMask() {
        if (!state.sessionId || state.busy) return;
        setBusy(true, "Generating SAM mask…");
        setMessage("Segment Anything is processing your point prompts.");
        try {
            const data = await requestJson("/api/sam/mask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: state.sessionId,
                    points: state.points.map((point) => [point.x, point.y]),
                    labels: state.points.map((point) => point.label),
                }),
            });
            const image = new Image();
            await new Promise((resolve, reject) => {
                image.onload = resolve;
                image.onerror = reject;
                image.src = data.mask_data;
            });
            pushHistory();
            maskCtx.clearRect(0, 0, state.width, state.height);
            maskCtx.drawImage(image, 0, 0, state.width, state.height);
            const imageData = maskCtx.getImageData(0, 0, state.width, state.height);
            for (let index = 0; index < imageData.data.length; index += 4) {
                const selected = imageData.data[index] >= 128;
                imageData.data[index] = 0;
                imageData.data[index + 1] = 212;
                imageData.data[index + 2] = 200;
                imageData.data[index + 3] = selected ? 255 : 0;
            }
            maskCtx.putImageData(imageData, 0, 0);
            normalizeMask();
            state.baseMask = maskBytes();
            render();
            renderPreview();
            selectTool("brush");
            const confidence = Math.max(0, Math.min(100, Math.round(data.score * 100)));
            setMessage(`Mask ready · ${confidence}% SAM confidence.`);
        } catch (error) {
            setMessage(error.message || "Could not generate mask.", true);
        } finally {
            setBusy(false);
        }
    }

    ui.stage.addEventListener("contextmenu", (event) => event.preventDefault());
    ui.stage.addEventListener("pointerdown", (event) => {
        if (!state.width || state.busy) return;
        const point = screenToImage(event);
        if (!insideImage(point)) return;
        event.preventDefault();
        const tool = event.button === 2 && state.tool === "fg" ? "bg" : state.tool;
        if (["fg", "bg"].includes(tool)) {
            state.points.push({ x: point.x, y: point.y, label: tool === "fg" ? 1 : 0 });
            updateControls();
            render();
            setMessage(`${tool === "fg" ? "Foreground" : "Background"} prompt added.`);
            return;
        }
        pushHistory();
        state.pointerId = event.pointerId;
        state.drawing = true;
        state.lastPoint = point;
        ui.stage.setPointerCapture(event.pointerId);
        drawMaskStroke(point, point, tool);
        render();
    });

    ui.stage.addEventListener("pointermove", (event) => {
        const point = screenToImage(event);
        state.hoverPoint = insideImage(point) ? point : null;
        ui.coordinates.textContent = insideImage(point)
            ? `X ${Math.round(point.x)} · Y ${Math.round(point.y)}`
            : "X — · Y —";
        if (state.drawing && event.pointerId === state.pointerId) {
            drawMaskStroke(state.lastPoint, point, state.tool);
            state.lastPoint = point;
        }
        render();
    });

    ui.stage.addEventListener("pointerleave", () => {
        if (state.drawing) return;
        state.hoverPoint = null;
        ui.coordinates.textContent = "X — · Y —";
        render();
    });

    function endStroke(event) {
        if (!state.drawing || event.pointerId !== state.pointerId) return;
        state.drawing = false;
        state.pointerId = null;
        state.lastPoint = null;
        normalizeMask();
        render();
        renderPreview();
        setMessage("Mask refined. Continue editing or proceed to embedding.");
    }

    ui.stage.addEventListener("pointerup", endStroke);
    ui.stage.addEventListener("pointercancel", endStroke);

    ui.launch.addEventListener("click", openEditor);
    ui.close.addEventListener("click", closeEditor);
    ui.fg.addEventListener("click", () => selectTool("fg"));
    ui.bg.addEventListener("click", () => selectTool("bg"));
    ui.brush.addEventListener("click", () => selectTool("brush"));
    ui.eraser.addEventListener("click", () => selectTool("eraser"));
    ui.generate.addEventListener("click", generateMask);
    ui.clearPoints.addEventListener("click", () => {
        state.points = [];
        updateControls();
        render();
        setMessage("SAM point prompts cleared. The current mask is preserved.");
    });
    ui.brushSize.addEventListener("input", () => {
        state.brushSize = Number(ui.brushSize.value);
        ui.brushValue.value = `${state.brushSize} px`;
    });
    ui.opacity.addEventListener("input", () => {
        state.opacity = Number(ui.opacity.value) / 100;
        ui.opacityValue.value = `${ui.opacity.value}%`;
        render();
    });
    ui.undo.addEventListener("click", () => {
        if (!state.undo.length) return;
        state.redo.push(maskBytes());
        restoreMask(state.undo.pop());
        setMessage("Mask edit undone.");
    });
    ui.redo.addEventListener("click", () => {
        if (!state.redo.length) return;
        state.undo.push(maskBytes());
        restoreMask(state.redo.pop());
        setMessage("Mask edit restored.");
    });
    ui.reset.addEventListener("click", () => {
        if (!state.baseMask) return;
        pushHistory();
        restoreMask(state.baseMask);
        setMessage("Mask reset to the latest SAM result.");
    });
    ui.proceed.addEventListener("click", () => {
        const segmented = renderPreview();
        if (!segmented) return;
        ui.detailsImage.src = segmented.toDataURL("image/png");
        ui.objectName.value = "";
        ui.saveStatus.textContent = "";
        ui.save.disabled = true;
        ui.detailsModal.classList.remove("is-hidden");
        ui.detailsModal.setAttribute("aria-hidden", "false");
        ui.objectName.focus();
    });
    ui.back.addEventListener("click", () => {
        ui.detailsModal.classList.add("is-hidden");
        ui.detailsModal.setAttribute("aria-hidden", "true");
    });
    ui.objectName.addEventListener("input", () => {
        ui.save.disabled = state.busy || !ui.objectName.value.trim();
    });
    ui.save.addEventListener("click", async () => {
        const objectName = ui.objectName.value.trim();
        if (!objectName || state.busy) return;
        state.busy = true;
        ui.save.disabled = true;
        ui.back.disabled = true;
        ui.saveStatus.textContent = "Creating OpenCLIP embedding and saving…";
        try {
            const data = await requestJson("/api/sam/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: state.sessionId,
                    object_name: objectName,
                    mask_data: exportMask(),
                }),
            });
            ui.saveStatus.textContent = `Saved ${data.object_name} · ${data.embedding_dim}-d`;
            state.sessionId = "";
            fetchStats(false);
            loadItemOptions();
            setTimeout(closeEditor, 650);
        } catch (error) {
            ui.saveStatus.textContent = error.message || "Could not save embedding.";
            ui.save.disabled = false;
        } finally {
            state.busy = false;
            ui.back.disabled = false;
        }
    });

    window.addEventListener("keydown", (event) => {
        if (!state.open || ["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return;
        if (event.key === "Escape") closeEditor();
        if (event.key.toLowerCase() === "b") selectTool("brush");
        if (event.key.toLowerCase() === "e") selectTool("eraser");
        if (event.ctrlKey && event.key.toLowerCase() === "z") {
            event.preventDefault();
            ui.undo.click();
        }
    });
    new ResizeObserver(resizeDisplay).observe(ui.stage);
    resizeDisplay();
    updateControls();
    selectTool("fg");
})();
