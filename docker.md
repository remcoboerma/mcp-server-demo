# Docker Setup

## Wat doet dit?

Draait de MCP server in een container, toegankelijk via netwerk (niet alleen lokaal).

**Transport:** SSE (Server-Sent Events) over HTTP/HTTPS  
**Access:** `https://mcp-demo.localhost/sse`

## Gebruik

```bash
# Build image
inv docker-build

# Start (detached)
inv docker-up

# Check logs
inv docker-logs

# Stop
inv docker-down
```

## Verschil met lokale dev

| Lokaal (`inv dev`) | Docker (`inv docker-up`) |
|--------------------|--------------------------|
| stdio transport | SSE transport |
| subprocess communication | HTTP endpoints |
| alleen deze machine | netwerk toegankelijk |
| `python server.py` | container op 0.0.0.0:8000 |

## Netwerk

**Traefik routing:**
- Container op `broker` network
- Expose port 8000 (niet publish)
- Traefik proxy: `https://mcp-demo.localhost/sse`
- Let's Encrypt SSL (productie domains)

**Config:** `.env`
```env
PROJECT=mcp-demo
HOSTINGDOMAIN=localhost  # of productie domain
```

## Testen

```bash
.venv/bin/python3 test_sse.py
```

**Let op:** `test_sse.py` disabled SSL verification voor localhost. Voor productie: verwijder `verify=False`.

## Productie

1. Update `.env`: `HOSTINGDOMAIN=jouwnaam.nl`
2. DNS: `mcp-demo.jouwnaam.nl` → server IP
3. Rebuild: `inv docker-down && inv docker-build && inv docker-up`
4. Test zonder SSL errors (echte cert via Let's Encrypt)
