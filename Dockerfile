# Ka-Nova Phase 3 — RunPod Docker Image
# Base: Python 3.9 + CUDA 12.1 compatible
# Strategy: bake dependencies + Ollama, pull codebase from GitHub at runtime

FROM grafana/grafana:11.1.0 AS grafana
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

# ── Grafana ───────────────────────────────────────────────────────────────────
COPY --from=grafana /usr/share/grafana /usr/share/grafana
COPY --from=grafana /etc/grafana /etc/grafana
RUN mkdir -p /var/lib/grafana /var/log/grafana
COPY docker/grafana/datasources /etc/grafana/provisioning/datasources
COPY docker/grafana/dashboards /etc/grafana/provisioning/dashboards

# ── Startup script ────────────────────────────────────────────────────────────
COPY docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

EXPOSE 8000 11434

CMD ["/startup.sh"]
