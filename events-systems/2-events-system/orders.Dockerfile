FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . .

# Install the application dependencies.
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["./.venv/bin/fastapi", "run", "orders.py", "--port", "8000", "--host", "0.0.0.0"]