# ─────────── BASE IMAGE ───────────
FROM python:3.10-slim

# ─────────── SYSTEM CONFIG ───────────
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ─────────── WORKDIR ───────────
WORKDIR /app

# ─────────── SYSTEM DEPENDENCIES ───────────
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# ─────────── COPY FILES ───────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ─────────── STORAGE DIR ───────────
RUN mkdir -p storage

# ─────────── EXPOSE API PORT ───────────
EXPOSE 8000

# ─────────── DEFAULT COMMAND ───────────
# NOTE:
# Platform ke hisaab se override ho sakta hai (Heroku/Render)
CMD ["bash", "-c", "python -m bot.main & python -m api.main"]
