FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    AEROBMSCE_DB_PATH=/data/aerobmsce.sqlite3

WORKDIR /app
COPY . .
RUN mkdir -p /data && chown 10001:10001 /data
USER 10001:10001

EXPOSE 8000
CMD ["python", "server/app.py"]
