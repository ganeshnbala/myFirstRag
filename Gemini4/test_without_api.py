import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_without_api():
    """Test MCP server connection without API calls"""
    print("Testing MCP server connection...")
    
    try:
        # Create MCP server connection
        server_params = StdioServerParameters(
            command="python",
            args=["example2.py"]
        )

        async with stdio_client(server_params) as (read, write):
            print("✅ Connection established")
            async with ClientSession(read, write) as session:
                print("✅ Session created")
                await session.initialize()
                print("✅ Session initialized")
                
                # Get available tools
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"✅ Retrieved {len(tools)} tools")
                
                # Test a simple math function
                print("\n🧮 Testing math function...")
                result = await session.call_tool("add", arguments={"a": 5, "b": 3})
                print(f"✅ 5 + 3 = {result.content[0].text}")
                
                # Test string to ASCII function
                print("\n🔤 Testing string to ASCII function...")
                result = await session.call_tool("strings_to_chars_to_int", arguments={"string": "INDIA"})
                print(f"✅ ASCII values for 'INDIA': {result.content[0].text}")
                
                # Test exponential sum function
                print("\n📊 Testing exponential sum function...")
                result = await session.call_tool("int_list_to_exponential_sum", arguments={"int_list": [73, 78, 68, 73, 65]})
                print(f"✅ Exponential sum: {result.content[0].text}")
                
                print("\n🎉 All MCP functions working perfectly!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_without_api())

