FROM python:3.12-slim

WORKDIR /api

RUN apt-get update && apt-get install -y --no-install-recommends vim build-essential wget git curl libmariadb3 libmariadb-dev \
    && apt-get clean autoclean \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

COPY . .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# so openshift has perms to run the app
RUN chgrp -R 0 . && chmod -R g=u . && chmod -R 755 .

CMD if [ "$FASTAPI_MODE" = "development" ] ; \
    then echo "running in development mode"; uvicorn main:app --host 0.0.0.0 --port 6000 --reload ; \
    else uvicorn main:app --host 0.0.0.0 --port 6000 ; \
    fi
