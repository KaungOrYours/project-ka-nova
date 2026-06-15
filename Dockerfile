# Ka-Nova Phase 3 — RunPod Docker Image
# Base: Python 3.9 + CUDA 12.1 compatible
# Strategy: bake dependencies + Ollama, pull codebase from GitHub at runtime

FROM python:3.9-slim

# ── System ────────────────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=0.0.0.0

RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ── Ollama ────────────────────────────────────────────────────────────────────
RUN curl -fsSL https://ollama.com/install.sh | sh

# ── Python dependencies ───────────────────────────────────────────────────────
RUN pip install --no-cache-dir \
    mesa==2.3.0 \
    pandas \
    numpy \
    scipy \
    tqdm \
    langchain \
    langchain-community \
    langchain-ollama \
    python-telegram-bot \
    python-dotenv \
    prometheus-client \
    wandb \
    SALib \
    matplotlib \
    seaborn

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /workspace

# ── Startup script ────────────────────────────────────────────────────────────
COPY docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

EXPOSE 8000 11434

CMD ["/startup.sh"]
