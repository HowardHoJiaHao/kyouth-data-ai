FROM python:3.14.4-bookworm

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv pip install --system --requirement pyproject.toml

COPY src/ ./src/

# 1. Change this to 8000 to match your internal proxy layout
EXPOSE 8000

ENTRYPOINT ["uv", "run", "uvicorn"]

# 2. Change --port to 8000 and change main:app to app:app
CMD ["--app-dir", "src", "--host", "0.0.0.0", "--port", "8000", "app:app"]
