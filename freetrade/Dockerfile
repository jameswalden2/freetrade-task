ARG PYTHON_VERSION=3.10-slim

FROM python:${PYTHON_VERSION} as builder

WORKDIR /build

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.6.1

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock* /build/

RUN poetry config virtualenvs.in-project true \
    && poetry install --no-dev --no-interaction --no-ansi

FROM python:${PYTHON_VERSION}

WORKDIR /freetrade

COPY --from=builder /build/.venv /opt/venv

COPY ./ ./

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="./:$PYTHONPATH"

CMD ["python", "freetrade/etl.py"]

