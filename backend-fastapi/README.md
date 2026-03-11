# Backend FastAPI (Football Tactical Analysis)

This is a minimal FastAPI backend skeleton for football tactical video analysis.
It provides a single upload endpoint and a modular pipeline structure with
placeholder services for future CV/ML integration.

## Endpoint

- `POST /analyze-video`
  - Input: multipart video upload
  - Output: placeholder tracking payload

## Run (later)

```bash
uvicorn app.main:app --reload
```
