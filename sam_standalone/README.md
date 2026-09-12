# Standalone SAM registration POC

This folder is independent of `inventory_app` and its dashboard.

Run from the repository root in Command Prompt:

```cmd
set PGPASSWORD=ai_squad
python sam_standalone\app.py
```

Open `http://127.0.0.1:8001`.

## Workflow

1. Load an image and enter the object name.
2. Add foreground points inside the object and optional background points outside it.
3. Select **Generate Mask**.
4. Refine the source-resolution binary mask with Brush and Eraser.
5. Inspect the preview, then select **Embed & Register**.

Saving creates a normalized OpenCLIP embedding and inserts it into the existing `object_embeddings` pgvector table.

## Editor controls

- Mouse wheel: zoom around the cursor, from Fit/25% up to 800%.
- Space + drag, or Hand/Pan: move the zoomed image.
- `B`, `E`, `H`, `F`: Brush, Eraser, Hand and Fit Image.
- `Ctrl+Z`, `Ctrl+Y`, `Ctrl+Shift+Z`: undo and redo completed mask actions.
- **Reset Mask** restores the most recent SAM result; **Clear SAM Points** affects prompts only; **Fit Image** affects the view only.

Brush and eraser strokes are rendered into the original-resolution mask with continuous rounded line segments. The editor thresholds each completed stroke back to a binary mask before preview or registration. Mask opacity changes display only.
