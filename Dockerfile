# Ka-Nova Phase 3 — RunPod Docker Image
# Base: CUDA 12.1 + Ubuntu 22.04 (RTX 4090 compatible)
# Strategy: bake dependencies + Ollama, pull codebase from GitHub at runtime

FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# ── System ────────────────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=0.0.0.0

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3-pip \
    python3.9-venv \
    git \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ── Python default ────────────────────────────────────────────────────────────
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
RUN python3 -m pip install --upgrade pip

# ── Ollama ────────────────────────────────────────────────────────────────────
RUN curl -fsSL https://ollama.com/install.sh | sh

# ── Python dependencies ───────────────────────────────────────────────────────
RUN pip install \
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
    deepeval \
    matplotlib \
    seaborn

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /workspace

# ── Startup script ────────────────────────────────────────────────────────────
COPY docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

EXPOSE 8000 11434

CMD ["/startup.sh"]
