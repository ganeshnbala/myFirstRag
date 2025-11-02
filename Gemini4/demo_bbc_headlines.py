"""
Demo script: Get BBC headlines and display in browser
Demonstrates the complete BBC headlines feature with browser display.
"""

import os
from dotenv import load_dotenv
import logging
import asyncio

from Perception import Perception
from Memory import Memory
from Decision_Making import DecisionMaking
from Action import Action
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv('config.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bbc_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def demo_bbc_headlines():
    """Demo BBC headlines with full agent system."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found")
        return
    
    print("\n" + "="*70)
    print("🎉 BBC HEADLINES DEMO 🎉")
    print("="*70)
    print("\nThis demo will:")
    print("1. Fetch latest BBC headlines from the RSS feed")
    print("2. Display them in a beautiful browser interface")
    print("3. Auto-close after 10 seconds with countdown")
    print("\n" + "="*70 + "\n")
    
    try:
        # Initialize agent modules
        perception = Perception(api_key)
        memory = Memory()
        decision_making = DecisionMaking(api_key)
        
        # Connect to MCP server
        logger.info("Connecting to MCP server...")
        server_params = StdioServerParameters(
            command=".venv\\Scripts\\python.exe",
            args=["example2.py"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                action = Action(session)
                
                # Get available tools
                tools_result = await session.list_tools()
                tools = [
                    {"name": tool.name, "description": tool.description, "inputSchema": tool.inputSchema}
                    for tool in tools_result.tools
                ]
                
                print(f"✅ Connected! Found {len(tools)} available tools\n")
                
                # Execute step by step
                print("📡 Step 1: Fetching BBC headlines...")
                result1 = await action.execute_tool(
                    "fetch_bbc_headlines",
                    {"num_headlines": 10}
                )
                print(f"   Result: {result1[1][0] if result1[0] else result1[1]}\n")
                
                print("🌐 Step 2: Opening browser display...")
                result2 = await action.execute_tool(
                    "display_headlines_in_browser",
                    {}
                )
                print(f"   Result: {result2[1][0] if result2[0] else result2[1]}\n")
                
                print("✅ Demo complete! Browser window should show:")
                print("   - Beautiful gradient background")
                print("   - All 10 BBC headlines")
                print("   - Countdown timer (10 seconds)")
                print("   - Auto-closing animation")
                print("\n" + "="*70)
                print("Enjoy your headlines! 📰")
                print("="*70 + "\n")
                
    except Exception as e:
        logger.error(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point."""
    try:
        await demo_bbc_headlines()
    except Exception as e:
        logger.error(f"Main error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

