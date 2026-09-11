# Standalone SAM registration POC

This folder is independent of `inventory_app` and its dashboard.

Run from the repository root in Command Prompt:

```cmd
set PGPASSWORD=ai_squad
python sam_standalone\app.py
```

Open `http://127.0.0.1:8001`.

Use left click for a foreground prompt, right click for a background prompt, then generate and refine the SAM mask. Saving creates a normalized OpenCLIP embedding and inserts it into the existing `object_embeddings` pgvector table.
