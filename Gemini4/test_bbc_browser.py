"""
Test BBC headlines display in browser.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_bbc_browser():
    """Test BBC headlines in browser."""
    try:
        server_params = StdioServerParameters(
            command=".venv\\Scripts\\python.exe",
            args=["example2.py"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("Step 1: Fetching headlines...")
                result1 = await session.call_tool("fetch_bbc_headlines", arguments={"num_headlines": 10})
                print(f"Result: {result1.content[0].text}")
                
                print("\nStep 2: Displaying in browser...")
                result2 = await session.call_tool("display_headlines_in_browser", arguments={})
                print(f"Result: {result2.content[0].text}")
                
                print("\nBrowser should now be open with the headlines!")
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_bbc_browser())

