# Every Dockerfile must start with a base layer.
# This downloads an official pre-built Linux operating system image from Docker Hub.
FROM python:3.14.4-bookworm

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv pip install --system --requirement pyproject.toml

COPY src/ ./src/

EXPOSE 8000

# Tells Docker that this container's primary job is to execute the 
# uvicorn production web server using the uv tool runner.
ENTRYPOINT ["uv", "run", "uvicorn"]

# Defines the default arguments passed directly into your ENTRYPOINT command.
CMD ["--app-dir", "src", "--host", "0.0.0.0", "app:app"]

# When they combine ENTRYPOINT and CMD
# uv run uvicorn --app-dir src --host 0.0.0.0 app:app

# --app-dir src: Tells Uvicorn to look inside the src folder to find your application files.
# --host 0.0.0.0: Tells Uvicorn to bind to all available network interfaces inside the container, allowing outside traffic (like your host network) to connect to it.
# app:app: Tells Uvicorn to look inside the file named app.py and run the FastAPI instance variable named app.