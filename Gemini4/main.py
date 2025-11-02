"""
Main Module
Orchestrates the complete agent system using Perception, Memory, Decision-Making, and Action modules.
"""

import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import logging

from Perception import Perception
from Memory import Memory
from Decision_Making import DecisionMaking
from Action import Action

# Load environment variables
load_dotenv('config.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentSystem:
    """
    Main agent system that orchestrates all modules.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the agent system with all modules.
        
        Args:
            api_key: Gemini API key for AI capabilities
        """
        logger.info("Initializing Agent System")
        
        # Initialize all modules
        self.perception = Perception(api_key)
        self.memory = Memory()
        self.decision_making = DecisionMaking(api_key)
        self.action = None  # Will be set after MCP session is created
        
        # Configuration
        self.max_iterations = 5
        self.current_iteration = 0
        
        logger.info("Agent System initialized successfully")
    
    async def run(self):
        """
        Run the main agent execution loop.
        """
        logger.info("=== Starting Agent Execution ===")
        
        try:
            # Create MCP server connection
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
                    
                    # Initialize action module with session
                    self.action = Action(session)
                    
                    # Get available tools
                    logger.info("Requesting tool list...")
                    tools_result = await session.list_tools()
                    tools = [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        }
                        for tool in tools_result.tools
                    ]
                    logger.info(f"Retrieved {len(tools)} tools")
                    
                    # Main execution loop
                    await self._execute_main_loop(tools)
                    
        except Exception as e:
            logger.error(f"Error in main execution: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.memory.log_execution("=== Agent Execution Complete ===")
    
    async def _execute_main_loop(self, tools: list):
        """
        Execute the main agent loop with complete integration of all modules.
        
        Args:
            tools: List of available tools
        """
        # User query
        user_query = "Find the ASCII values of characters in INDIA and then return sum of exponentials of those values."
        
        print("\n" + "="*70)
        print("STARTING AGENT EXECUTION")
        print("="*70)
        print(f"\nUser Query: {user_query}\n")
        
        # Process user input through perception
        logger.info("Processing user input through perception...")
        perception_data = await self.perception.process_user_input(user_query)
        
        # Store perception data in memory
        self.memory.store_input(perception_data.get("raw_query", user_query), source="user")
        self.memory.store_prompt_facts(perception_data.get("prompt_facts", {}))
        
        # Get memory data for decision making
        memory_data = {
            "iteration_history": self.memory.state["iteration_history"],
            "iteration_summary": self.memory.get_iteration_summary(),
            "last_response": self.memory.get_last_response(),
            "performance_metrics": self.memory.get_performance_metrics(),
            "function_usage": dict(self.memory.data_store.get("function_usage", {})),
            "context_facts": self.memory.data_store.get("context_facts", [])
        }
        
        # Main iteration loop
        final_answer_reached = False
        
        while self.current_iteration < self.max_iterations and not final_answer_reached:
            iteration_num = self.current_iteration + 1
            logger.info(f"\n--- Iteration {iteration_num} ---")
            print(f"\n[Iteration {iteration_num}]")
            
            # Observe environment
            observed_data = await self.perception.observe_environment({
                "query": user_query,
                "iteration": self.current_iteration,
                "tools": tools
            })
            
            # Increment iteration counter
            current_iter = self.memory.increment_iteration()
            
            # Make decision using Decision-Making module
            logger.info("Making decision based on perception and memory...")
            decision_type, decision_data = await self.decision_making.generate_decision(
                perception_data=perception_data,
                memory_data=memory_data,
                available_tools=tools
            )
            
            logger.info(f"Decision type: {decision_type}")
            logger.info(f"Decision data: {decision_data}")
            
            # Execute the action using Action module with memory integration
            logger.info("Executing action...")
            success, result, visualization_config = await self.action.execute_decision(
                decision_type,
                decision_data,
                visualization_needed=perception_data.get("requires_visualization", False),
                memory_instance=self.memory
            )
            
            if not success:
                logger.error(f"Action execution failed: {result}")
                self.memory.store_error(
                    error=Exception(f"Action execution failed: {result}"),
                    context={"iteration": current_iter, "decision_type": decision_type}
                )
                break
            
            # Store iteration in memory
            self.memory.store_iteration(
                current_iter,
                user_query,
                decision_data,
                result
            )
            
            logger.info(f"Action result: {result}")
            
            # Check if we have an exponential sum result (indicates completion)
            result_str = str(result) if not isinstance(result, list) else ' '.join(map(str, result))
            if "e33" in result_str or "e31" in result_str or "e32" in result_str:
                # We have the exponential sum, treat as final answer
                print("\n" + "="*70)
                print("FINAL RESULT")
                print("="*70)
                print(f"Answer: {result}")
                print("="*70 + "\n")
                
                # Execute visualization
                logger.info("Executing final visualization with TSAI text...")
                visualization_config = {
                    "tool": "draw_rectangle_with_turtle",
                    "arguments": {
                        "width": 400,
                        "height": 150,
                        "text": "TSAI"
                    }
                }
                
                vis_success, vis_result = await self.action.execute_visualization(
                    visualization_config,
                    memory_instance=self.memory
                )
                
                if vis_success:
                    print("\n" + "="*70)
                    print("VISUALIZATION EXECUTED SUCCESSFULLY")
                    print("="*70)
                    print("Turtle graphics window displayed with rectangle and text 'TSAI'")
                    print("Window will automatically close after 12 seconds")
                    print("="*70 + "\n")
                
                final_answer_reached = True
                break
            
            # Handle visualization if needed
            if visualization_config:
                logger.info("Executing visualization...")
                vis_success, vis_result = await self.action.execute_visualization(
                    visualization_config, 
                    memory_instance=self.memory
                )
                
                if vis_success:
                    print("\n" + "="*70)
                    print("VISUALIZATION EXECUTED SUCCESSFULLY")
                    print("="*70)
                    print("Turtle graphics window displayed with rectangle and text 'TSAI'")
                    print("Window will automatically close after 12 seconds")
                    print("="*70 + "\n")
                
                # Final answer reached after visualization
                final_answer_reached = True
                break
            
            # Check if we have a final answer
            if decision_type == "final_answer":
                final_answer_reached = True
                logger.info("Final answer reached")
                
                # Extract and display the final answer
                final_result = result.get("final_answer", result) if isinstance(result, dict) else result
                formatted_result = self.action.format_result(final_result)
                
                print("\n" + "="*70)
                print("FINAL RESULT")
                print("="*70)
                print(f"Answer: {formatted_result}")
                print("="*70 + "\n")
                
                logger.info(f"Final result: {formatted_result}")
                
                # Always execute visualization for the TSAI rectangle
                logger.info("Executing final visualization with TSAI text...")
                visualization_config = {
                    "tool": "draw_rectangle_with_turtle",
                    "arguments": {
                        "width": 400,
                        "height": 150,
                        "text": "TSAI"
                    }
                }
                
                vis_success, vis_result = await self.action.execute_visualization(
                    visualization_config,
                    memory_instance=self.memory
                )
                
                if vis_success:
                    print("\n" + "="*70)
                    print("VISUALIZATION EXECUTED SUCCESSFULLY")
                    print("="*70)
                    print("Turtle graphics window displayed with rectangle and text 'TSAI'")
                    print("Window will automatically close after 12 seconds")
                    print("="*70 + "\n")
                else:
                    print("\n" + "="*70)
                    print("VISUALIZATION FAILED")
                    print("="*70 + "\n")
                
                break
            
            # Increment iteration counter
            self.current_iteration += 1
            
            # Update memory data for next iteration
            memory_data = {
                "iteration_history": self.memory.state["iteration_history"],
                "iteration_summary": self.memory.get_iteration_summary(),
                "last_response": self.memory.get_last_response(),
                "performance_metrics": self.memory.get_performance_metrics(),
                "function_usage": dict(self.memory.data_store.get("function_usage", {})),
                "context_facts": self.memory.data_store.get("context_facts", [])
            }
        
        if self.current_iteration >= self.max_iterations and not final_answer_reached:
            logger.warning("Maximum iterations reached without final answer")
            print("\nMaximum iterations reached")
        
        # Print memory summary
        print("\n" + "="*70)
        print("MEMORY SUMMARY")
        print("="*70)
        print(self.memory.get_memory_summary())
        print("="*70 + "\n")


async def main():
    """
    Main entry point for the agent system.
    """
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables")
        return
    
    # Create and run agent system
    agent = AgentSystem(api_key)
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
