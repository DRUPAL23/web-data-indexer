#!/bin/sh
# Entry point for development (runs uvicorn)
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
