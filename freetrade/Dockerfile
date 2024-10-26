# build image
ARG PYTHON_VERSION=3.10-slim

FROM python:${PYTHON_VERSION} as builder

WORKDIR /build

# poetry install
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.6.1
RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock* /build/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# final image
FROM python:${PYTHON_VERSION}

WORKDIR /freetrade

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./ ./

ENV PYTHONPATH="./:"

CMD ["poetry", "run", "python", "freetrade/etl.py"]