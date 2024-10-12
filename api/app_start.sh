#!/bin/bash
if [ $FASTAPI_MODE == "development" ]; then
    uvicorn main:app --host 0.0.0.0 --reload --port 6000
else
    uvicorn main:app --host 0.0.0.0 --port 6000
fi
