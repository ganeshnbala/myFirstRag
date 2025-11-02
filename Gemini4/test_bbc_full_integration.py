"""
Full integration test: Agent system with BBC headlines using RAG
This demonstrates the complete workflow with all modules working together.
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
        logging.FileHandler('bbc_full_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def test_bbc_full_integration():
    """Test full agent system with BBC headlines."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found")
        return
    
    print("\n" + "="*70)
    print("🚀 FULL AGENT INTEGRATION: BBC HEADLINES 🚀")
    print("="*70)
    
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
            
            print(f"\n✅ Connected! Found {len(tools)} available tools\n")
            
            # User query
            user_query = "Get me the latest BBC headlines and display them in browser"
            
            print("="*70)
            print("STARTING AGENT EXECUTION")
            print("="*70)
            print(f"\nUser Query: {user_query}\n")
            
            # Process user input through perception
            logger.info("Processing user input through perception...")
            perception_data = await perception.process_user_input(user_query)
            
            # Store perception data in memory
            memory.store_input(perception_data.get("raw_query", user_query), source="user")
            memory.store_prompt_facts(perception_data.get("prompt_facts", {}))
            
            # Get memory data for decision making
            memory_data = {
                "iteration_history": memory.state["iteration_history"],
                "iteration_summary": memory.get_iteration_summary(),
                "last_response": memory.get_last_response(),
                "performance_metrics": memory.get_performance_metrics(),
                "function_usage": dict(memory.data_store.get("function_usage", {})),
                "context_facts": memory.data_store.get("context_facts", [])
            }
            
            # Main iteration loop
            max_iterations = 3
            current_iteration = 0
            final_answer_reached = False
            
            while current_iteration < max_iterations and not final_answer_reached:
                iteration_num = current_iteration + 1
                logger.info(f"\n--- Iteration {iteration_num} ---")
                print(f"\n[Iteration {iteration_num}]")
                
                # Observe environment
                observed_data = await perception.observe_environment({
                    "query": user_query,
                    "iteration": current_iteration,
                    "tools": tools
                })
                
                # Increment iteration counter
                current_iter = memory.increment_iteration()
                
                # Generate decision
                print("  -> Generating decision...")
                decision_type, decision_data = await decision_making.generate_decision(
                    perception_data=perception_data,
                    memory_data=memory_data,
                    available_tools=tools
                )
                
                print(f"  -> Decision: {decision_type}")
                print(f"     Function: {decision_data.get('function_name', 'N/A')}")
                
                # Execute decision
                success, result, vis_config = await action.execute_decision(
                    decision_type=decision_type,
                    decision_data=decision_data,
                    visualization_needed=perception_data.get('requires_visualization', False),
                    memory_instance=memory
                )
                
                if not success:
                    print(f"  -> ❌ Action failed: {result}")
                    break
                
                # Store iteration
                memory.store_iteration(
                    iteration=current_iter,
                    query=user_query,
                    response=f"{decision_type}: {decision_data}",
                    result=result
                )
                
                # Update memory data for next iteration
                memory_data = {
                    "iteration_history": memory.state["iteration_history"],
                    "iteration_summary": memory.get_iteration_summary(),
                    "last_response": memory.get_last_response(),
                    "performance_metrics": memory.get_performance_metrics(),
                    "function_usage": dict(memory.data_store.get("function_usage", {})),
                    "context_facts": memory.data_store.get("context_facts", [])
                }
                
                # Check if we should continue
                if decision_type == "final_answer":
                    final_answer_reached = True
                    print(f"  -> ✅ Final answer reached")
                
                current_iteration += 1
                
                # Small delay between iterations
                await asyncio.sleep(1)
            
            # Print results
            print("\n" + "="*70)
            print("AGENT EXECUTION COMPLETE")
            print("="*70)
            print("\n📊 MEMORY SUMMARY:")
            print(memory.get_memory_summary())
            
            # Print context facts if any
            context_facts = memory.data_store.get("context_facts", [])
            if context_facts:
                print("\n📝 CONTEXT FACTS:")
                for fact in context_facts:
                    print(f"   - {fact.get('fact', 'N/A')}")
            
            print("\n" + "="*70)
            print("✅ Integration Test Complete!")
            print("="*70 + "\n")
            
            # Check for generated files
            files_to_check = ['bbc_headlines.txt', 'bbc_headlines.html']
            print("📁 Generated Files:")
            for filename in files_to_check:
                if os.path.exists(filename):
                    size = os.path.getsize(filename)
                    print(f"   ✅ {filename} ({size} bytes)")
                else:
                    print(f"   ❌ {filename} (not found)")
            print()


async def main():
    """Main entry point."""
    try:
        await test_bbc_full_integration()
    except Exception as e:
        logger.error(f"Main error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

