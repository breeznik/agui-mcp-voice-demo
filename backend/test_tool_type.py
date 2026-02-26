"""Quick test: what type does MCP tool.coroutine() return?"""
import asyncio, os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    client = MultiServerMCPClient({
        "shopping": {
            "command": "python",
            "args": [str(Path("src/mcp_servers/shopping_server.py"))],
            "transport": "stdio",
            "env": dict(os.environ),
        }
    })
    tools = await client.get_tools()
    search = [t for t in tools if t.name == "search_products"][0]
    result = await search.coroutine(query="keyboard")
    print(f"Type: {type(result)}")
    print(f"Value: {repr(result)[:300]}")
    print(f"isinstance dict: {isinstance(result, dict)}")
    print(f"isinstance str:  {isinstance(result, str)}")

asyncio.run(main())
