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
    && curl -fsSL https://packages.grafana.com/gpg.key | gpg --dearmor -o /usr/share/keyrings/grafana.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/grafana.gpg] https://packages.grafana.com/oss/deb stable main" > /etc/apt/sources.list.d/grafana.list \
    && apt-get update && apt-get install -y grafana \
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
