"""
Test BBC headlines fetching through the main agent system.
"""

import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import logging
import google.generativeai as genai

from Perception import Perception
from Memory import Memory
from Decision_Making import DecisionMaking
from Action import Action

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


async def test_bbc_headlines_with_agent():
    """Test BBC headlines with the full agent system."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found")
        return
    
    print("\n" + "="*70)
    print("BBC HEADLINES AGENT TEST")
    print("="*70)
    
    try:
        # Initialize modules
        perception = Perception(api_key)
        memory = Memory()
        decision_making = DecisionMaking(api_key)
        
        # Connect to MCP server
        logger.info("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command=".venv\\Scripts\\python.exe",
            args=["example2.py"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                action = Action(session)
                
                # Get tools
                tools_result = await session.list_tools()
                tools = [
                    {"name": tool.name, "description": tool.description, "inputSchema": tool.inputSchema}
                    for tool in tools_result.tools
                ]
                
                # User query
                user_query = "Get the latest BBC headlines and display them in Paint"
                print(f"\nUser Query: {user_query}\n")
                
                # Process query
                perception_data = await perception.process_user_input(user_query)
                memory.store_input(user_query, source="user")
                memory_data = {
                    "iteration_history": memory.state["iteration_history"],
                    "iteration_summary": memory.get_iteration_summary(),
                    "last_response": memory.get_last_response(),
                    "performance_metrics": memory.get_performance_metrics(),
                    "function_usage": dict(memory.data_store.get("function_usage", {})),
                    "context_facts": memory.data_store.get("context_facts", [])
                }
                
                max_iterations = 5
                current_iteration = 0
                
                while current_iteration < max_iterations:
                    current_iteration += 1
                    print(f"\n[Iteration {current_iteration}]")
                    
                    # Generate decision
                    decision_type, decision_data = await decision_making.generate_decision(
                        perception_data=perception_data,
                        memory_data=memory_data,
                        available_tools=tools
                    )
                    
                    print(f"Decision: {decision_type}")
                    print(f"Data: {decision_data}")
                    
                    # Execute decision
                    success, result, visualization_config = await action.execute_decision(
                        decision_type,
                        decision_data,
                        visualization_needed=False,
                        memory_instance=memory
                    )
                    
                    if not success:
                        print(f"Error: {result}")
                        break
                    
                    print(f"Result: {result}")
                    
                    if decision_type == "final_answer":
                        break
                    
                    # Update memory data
                    memory_data = {
                        "iteration_history": memory.state["iteration_history"],
                        "iteration_summary": memory.get_iteration_summary(),
                        "last_response": memory.get_last_response(),
                        "performance_metrics": memory.get_performance_metrics(),
                        "function_usage": dict(memory.data_store.get("function_usage", {})),
                        "context_facts": memory.data_store.get("context_facts", [])
                    }
                
                print("\n" + "="*70)
                print("TEST COMPLETE")
                print("="*70 + "\n")
                
                # Wait for Paint to stay open
                await asyncio.sleep(10)
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    try:
        await test_bbc_headlines_with_agent()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

