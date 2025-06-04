# Python 3.12 base
FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

# Install system dependencies
# - gcc: Might be needed for building some Python C extensions if wheels aren't available
# - ffmpeg: Presumably needed for audio processing by your app
# - curl: Keeping just in case, though pip is installing uv now.
# --no-install-recommends keeps the image smaller
# - build-essential: Added for better cross-platform compatibility
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        ffmpeg \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# --- Copy project files BEFORE installing dependencies ---
# uv pip install . needs pyproject.toml and potentially src/
COPY pyproject.toml ./
COPY src ./src
# If you have other files needed for the *build* (e.g., README.md if referenced in pyproject.toml), copy them too.
# COPY README.md ./

# --- Install uv using pip AND install the project + dependencies from pyproject.toml ---
# This ensures 'uv' is available for the second part of the command.
# 'uv pip install .' reads pyproject.toml and installs dependencies + the project itself.
RUN pip install uv && \
    uv pip install --system .
# --- End change ---

# No longer need a separate project install step, as 'uv pip install .' handled it.

# Expose the port the FastAPI app will run on
EXPOSE 8000

# Default command to run the FastAPI application with Uvicorn
# Uvicorn finds 'app.main:app' because the package was installed by 'uv pip install .'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
