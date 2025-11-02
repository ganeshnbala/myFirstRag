"""
Test script to demonstrate BBC headlines fetching and display in Paint.
"""

import os
from dotenv import load_dotenv
import logging
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv('config.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def test_bbc_headlines():
    """Test BBC headlines fetching and display."""
    
    print("\n" + "="*70)
    print("BBC HEADLINES TEST")
    print("="*70)
    
    try:
        logger.info("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command=".venv\\Scripts\\python.exe",
            args=["example2.py"]
        )
        
        async with stdio_client(server_params) as (read, write):
            logger.info("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                logger.info("Session created, initializing...")
                await session.initialize()
                
                # Step 1: Fetch BBC headlines
                print("\nStep 1: Fetching BBC headlines...")
                logger.info("Calling fetch_bbc_headlines...")
                result1 = await session.call_tool("fetch_bbc_headlines", arguments={"num_headlines": 10})
                
                if hasattr(result1, 'content'):
                    for item in result1.content:
                        if hasattr(item, 'text'):
                            print(f"Result: {item.text}")
                
                # Step 2: Display in Paint
                print("\nStep 2: Displaying headlines in Paint...")
                logger.info("Calling display_headlines_in_paint...")
                result2 = await session.call_tool("display_headlines_in_paint", arguments={})
                
                if hasattr(result2, 'content'):
                    for item in result2.content:
                        if hasattr(item, 'text'):
                            print(f"Result: {item.text}")
                
                print("\n" + "="*70)
                print("Test completed!")
                print("="*70)
                
                # Wait a bit to keep Paint open
                await asyncio.sleep(5)
                
    except Exception as e:
        logger.error(f"Error in test: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    try:
        await test_bbc_headlines()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

