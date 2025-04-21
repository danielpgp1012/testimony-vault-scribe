
# Python 3.12 base and lightning‑fast dependency management with **uv**
FROM python:3.12‑slim

WORKDIR /app

# — System deps
RUN apt-get update \
    && apt-get install -y gcc ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

# — Install uv (https://astral.sh/uv) once; it gives us super‑fast installs
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# — Install Python deps with uv (drop a lockfile later if you like)
COPY backend/requirements.txt /tmp/requirements.txt
RUN uv pip install --system -r /tmp/requirements.txt

# — Copy project
COPY backend/app ./app
COPY backend/worker.py .

# — Run the API with Uvicorn (still the ASGI server) on Python 3.12
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
