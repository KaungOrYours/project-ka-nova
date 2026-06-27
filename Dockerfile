# Ka-Nova Phase 3 — RunPod Docker Image
# Base: Python 3.9 + CUDA 12.1 compatible
# Strategy: bake dependencies + Ollama, pull codebase from GitHub at runtime

FROM python:3.11-slim

# ── System ────────────────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=-1

RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    ca-certificates \
    zstd \
    apt-transport-https \
    software-properties-common \
    && curl -fsSL https://dl.grafana.com/oss/release/grafana_11.1.0_amd64.deb -o /tmp/grafana.deb \
    && apt-get install -y /tmp/grafana.deb \
    && rm /tmp/grafana.deb \
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
    langchain-openai \
    pydantic \
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
