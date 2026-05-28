# backend

Backend workspace initialized with FastAPI skeleton.

## Structure

- `app/main.py`: FastAPI entrypoint
- `app/api/`: API routes
- `app/core/`: Configuration
- `requirements.txt`: Dependencies
- `.python-version`: Python version hint (`3.11`)

## Install

```powershell
python -m pip install -r requirements.txt
```

## Run (Dev)

```powershell
uvicorn app.main:app --reload
```

## Health Check

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health | Select-Object -ExpandProperty Content
```
