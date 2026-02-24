FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https lsb-release sudo
# Download the package to configure the Microsoft repo
RUN curl -sSL -O https://packages.microsoft.com/config/debian/$(grep VERSION_ID /etc/os-release | cut -d '"' -f 2 | cut -d '.' -f 1)/packages-microsoft-prod.deb
# Install the package
RUN sudo dpkg -i packages-microsoft-prod.deb
# Delete the file
RUN rm packages-microsoft-prod.deb

RUN sudo apt-get update
RUN sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18


# Copy the project into the image
COPY . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app

RUN uv sync --locked

# Presuming there is a `my_app` command provided by the project
CMD ["uv", "run", "fastapi","run","app/main.py", "--host", "0.0.0.0", "--port", "8000"]