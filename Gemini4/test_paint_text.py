import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_paint_text():
    """Test Paint text insertion directly"""
    print("Testing Paint text insertion...")
    
    try:
        # Create MCP server connection
        server_params = StdioServerParameters(
            command="python",
            args=["example2.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Open Paint
                print("Opening Paint...")
                result = await session.call_tool("open_paint")
                print(result.content[0].text)
                
                # Wait for Paint to fully load
                await asyncio.sleep(2)
                
                # Draw a rectangle first
                print("Drawing rectangle...")
                result = await session.call_tool(
                    "draw_rectangle",
                    arguments={
                        "x1": 100,
                        "y1": 100,
                        "x2": 300,
                        "y2": 200
                    }
                )
                print(result.content[0].text)
                
                # Wait a bit
                await asyncio.sleep(1)
                
                # Try to add text
                print("Adding text...")
                result = await session.call_tool(
                    "add_text_in_paint",
                    arguments={
                        "text": "TSAI Assignment"
                    }
                )
                print(result.content[0].text)
                
                # Keep Paint open for 10 seconds
                print("Keeping Paint open for 10 seconds...")
                await asyncio.sleep(10)
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_paint_text())


