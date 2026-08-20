FROM python:3.14-slim

LABEL authors="Ivan"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml poetry.lock* ./

RUN pip install poetry==1.8.0 \
    && poetry config virtualenvs.create false \
    && poetry install --no-root

COPY . .

EXPOSE 8000
