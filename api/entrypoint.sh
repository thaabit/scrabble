#!/bin/sh
if [ "$FASTAPI_MODE" = "development" ] ; then \
    echo "running in development mode";
    uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload ; \
else
    echo "running in live mode";
    uv run uvicorn main:app --host 0.0.0.0 --port 8000 ;
fi
