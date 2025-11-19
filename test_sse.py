import asyncio
import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test():
    def no_verify_client_factory(**kwargs):
        return httpx.AsyncClient(verify=False, **kwargs)
    
    async with sse_client("https://mcp-demo.localhost/sse", httpx_client_factory=no_verify_client_factory) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool('add', {'a': 5, 'b': 3})
            print(f"add(5,3) = {result.content[0].text}")

asyncio.run(test())
