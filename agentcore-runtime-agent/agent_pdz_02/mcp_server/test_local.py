"""Test MCP Server locally"""
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def test_mcp():
    mcp_url = "http://localhost:8000/mcp"
    
    print("=" * 70)
    print(" Testing MCP Server (Local)")
    print("=" * 70)
    print(f" URL: {mcp_url}\n")
    
    try:
        async with streamablehttp_client(mcp_url, {}, timeout=30, terminate_on_close=False) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools = await session.list_tools()
                print(f"[Tools] Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                print("\n[Test 1] calculate_statistics")
                result = await session.call_tool("calculate_statistics", {"numbers": [10, 20, 30, 40, 50]})
                print(f"Result: {result.content[0].text}\n")
                
                print("[Test 2] compound_interest")
                result = await session.call_tool("compound_interest", {"principal": 1000, "rate": 5, "time": 10})
                print(f"Result: {result.content[0].text}\n")
                
                print("[Test 3] text_analyzer")
                result = await session.call_tool("text_analyzer", {"text": "Hello world. This is a test."})
                print(f"Result: {result.content[0].text}\n")
                
                print("=" * 70)
                print(" All tests passed!")
                print("=" * 70)
    except Exception as e:
        print(f"\nERROR: Connection failed - {str(e)}")
        print("\nMake sure the MCP server is running:")
        print("  docker logs mcp-server-test")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_mcp())
