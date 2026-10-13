import os
import time

import psycopg
from fastapi import FastAPI, HTTPException

app = FastAPI(title="CloudSage demo application")


@app.get("/")
def root():
    return {"service": "cloudsage-demo", "health": "/health"}


@app.get("/health")
def health():
    try:
        with psycopg.connect(
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            connect_timeout=2,
        ) as connection:
            connection.execute("SELECT 1")
        return {"status": "healthy", "database": "query succeeded"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"database query failed: {exc.__class__.__name__}") from exc


if __name__ == "__main__":
    import uvicorn

    for attempt in range(10):
        try:
            with psycopg.connect(
                host=os.getenv("DB_HOST", "db"), port=int(os.getenv("DB_PORT", "5432")),
                dbname=os.environ["DB_NAME"], user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"], connect_timeout=2,
            ) as connection:
                connection.execute("SELECT 1")
            break
        except Exception:
            print(f"Waiting for database ({attempt + 1}/10)...", flush=True)
            time.sleep(2)
    else:
        print("Startup database check failed; API starts so /health can report 503.", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=8080)
