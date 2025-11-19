FROM educationwarehouse/edwhale-3.13:latest

# Install dependencies
RUN uvenv install --no-cache fastmcp

WORKDIR /app

# Copy server
COPY server.py .

EXPOSE 8000

# SSE transport on 0.0.0.0:8000
CMD ["/root/.local/bin/fastmcp", "run", "--transport", "sse", "--host", "0.0.0.0", "--path", "/sse", "server.py"]
