FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Copy the project into the image
COPY . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app

RUN uv sync --locked

EXPOSE 1433

# Presuming there is a `my_app` command provided by the project
CMD ["uv", "run", "fastapi", "dev","app/main.py"]