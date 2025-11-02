"""
Test RAG + BBC headlines integration with full agent system.
Demonstrates RAG-enhanced agent processing BBC headline requests.
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_bbc_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def test_rag_bbc_agent():
    """Test RAG-enhanced agent with BBC headlines request."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found")
        return
    
    print("\n" + "="*70)
    print("🎉 RAG + BBC HEADLINES INTEGRATION TEST 🎉")
    print("="*70)
    print("\nThis test demonstrates:")
    print("1. Perception module identifying BBC query")
    print("2. RAG providing contextual knowledge")
    print("3. Decision-Making generating proper workflow")
    print("4. Action executing BBC tools with memory tracking")
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
                
                # Test Query: Get BBC headlines and display in browser
                user_query = "Get me the latest BBC headlines and display them in browser"
                
                print("📝 User Query:")
                print(f"   {user_query}\n")
                
                # Step 1: Perception
                print("🔍 Step 1: Perception Processing...")
                perception_data = await perception.process_user_input(user_query)
                print(f"   Query Type: {perception_data.get('query_type')}")
                print(f"   Key Concepts: {perception_data.get('key_concepts')}")
                print(f"   Requires Visualization: {perception_data.get('requires_visualization')}")
                if 'rag_context' in perception_data:
                    print(f"   RAG Context Applied: ✅")
                    print(f"   RAG Recommendations: {len(perception_data.get('rag_recommendations', []))} recommendations")
                print()
                
                # Store in memory
                memory.store_input(user_query, source="user")
                memory.store_prompt_facts(perception_data.get("prompt_facts", {}))
                if 'rag_context' in perception_data:
                    memory.store_context_fact("RAG context applied for BBC query", source="perception")
                
                # Step 2: Decision Making with RAG context
                print("🧠 Step 2: Decision Making (with RAG context)...")
                memory_data = {
                    "iteration_history": memory.state["iteration_history"],
                    "iteration_summary": memory.get_iteration_summary(),
                    "last_response": memory.get_last_response(),
                    "performance_metrics": memory.get_performance_metrics(),
                    "function_usage": dict(memory.data_store.get("function_usage", {})),
                    "context_facts": memory.data_store.get("context_facts", [])
                }
                
                decision_type, decision_data = await decision_making.generate_decision(
                    perception_data=perception_data,
                    memory_data=memory_data,
                    available_tools=tools
                )
                print(f"   Decision Type: {decision_type}")
                print(f"   Decision Data: {decision_data}")
                print()
                
                # Step 3: Action Execution
                print("⚡ Step 3: Action Execution...")
                success, result, vis_config = await action.execute_decision(
                    decision_type=decision_type,
                    decision_data=decision_data,
                    visualization_needed=perception_data.get('requires_visualization', False),
                    memory_instance=memory
                )
                print(f"   Success: {success}")
                print(f"   Result: {result}")
                print(f"   Visualization Config: {vis_config}")
                print()
                
                # Store iteration
                memory.store_iteration(
                    iteration=1,
                    query=user_query,
                    response=f"{decision_type}: {decision_data}",
                    result=result
                )
                
                # Step 4: Display Results
                print("📊 Step 4: Results & Memory Summary...")
                print("\n" + memory.get_memory_summary())
                print("\n" + "="*70)
                print("✅ RAG + BBC Integration Test Complete!")
                print("="*70 + "\n")
                
    except Exception as e:
        logger.error(f"Test error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point."""
    try:
        await test_rag_bbc_agent()
    except Exception as e:
        logger.error(f"Main error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

