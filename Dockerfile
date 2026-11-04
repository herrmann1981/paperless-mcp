FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev
RUN groupadd --system --gid 10001 paperless \
    && useradd --uid 10001 --gid paperless --home-dir /app --no-create-home --shell /usr/sbin/nologin paperless

ENV PATH="/app/.venv/bin:$PATH"
ENV HOME="/tmp"
USER paperless
CMD ["paperless-mcp"]
