"""
Action Module
Handles tool execution and action taking.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from mcp import ClientSession
import asyncio

logger = logging.getLogger(__name__)


class Action:
    """
    Handles execution of actions and tool calls.
    """
    
    def __init__(self, session: ClientSession):
        """
        Initialize the Action module.
        
        Args:
            session: MCP client session for tool execution
        """
        self.session = session
        logger.info("Action module initialized")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            
        Returns:
            Tuple of (success, result)
        """
        logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
        
        try:
            result = await self.session.call_tool(tool_name, arguments=arguments)
            
            # Extract the result content
            if hasattr(result, 'content'):
                if isinstance(result.content, list):
                    # Extract text from all content items
                    result_items = [
                        item.text if hasattr(item, 'text') else str(item)
                        for item in result.content
                    ]
                    result_data = result_items
                else:
                    result_data = str(result.content)
            else:
                result_data = str(result)
            
            logger.info(f"Tool execution successful: {tool_name}")
            return True, result_data
            
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {str(e)}")
            return False, str(e)
    
    async def execute_function_call(self, decision_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Execute a function call decision.
        
        Args:
            decision_data: Decision data containing function name and arguments
            
        Returns:
            Tuple of (success, result)
        """
        function_name = decision_data.get("function_name")
        arguments = decision_data.get("arguments", {})
        
        return await self.execute_tool(function_name, arguments)
    
    async def handle_final_answer(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a final answer decision.
        
        Args:
            decision_data: Decision data containing the final answer
            
        Returns:
            Dictionary containing final answer information
        """
        logger.info("Handling final answer")
        
        answer = decision_data.get("answer", "")
        
        # Check if visualization is needed
        needs_visualization = "draw" in answer.lower() or "visual" in answer.lower()
        
        result = {
            "final_answer": answer,
            "needs_visualization": needs_visualization
        }
        
        return result
    
    async def execute_visualization(self, visualization_config: Dict[str, Any], memory_instance = None) -> Tuple[bool, Any]:
        """
        Execute a visualization action with optional memory integration.
        
        Args:
            visualization_config: Configuration for visualization
            memory_instance: Memory instance for storing execution data
            
        Returns:
            Tuple of (success, result)
        """
        logger.info("Executing visualization")
        
        tool_name = visualization_config.get("tool", "draw_rectangle_with_turtle")
        arguments = visualization_config.get("arguments", {
            "width": 300,
            "height": 150,
            "text": "TSAI"
        })
        
        # Store visualization execution in memory
        if memory_instance:
            memory_instance.store_execution_step(
                step="Executing visualization",
                details={"tool": tool_name, "arguments": arguments}
            )
        
        success, result = await self.execute_tool(tool_name, arguments)
        
        # Store visualization result in memory
        if memory_instance:
            if success:
                memory_instance.store_tool_call(
                    tool_name=tool_name,
                    arguments=arguments,
                    result=result
                )
                memory_instance.store_intermediate_result(
                    key="visualization_result",
                    value=result,
                    metadata={"tool": tool_name, "visualization": True}
                )
            else:
                memory_instance.store_error(
                    error=Exception(f"Visualization failed: {result}"),
                    context={"tool": tool_name, "arguments": arguments}
                )
        
        return success, result
    
    def format_result(self, result: Any) -> str:
        """
        Format a result for display.
        
        Args:
            result: Result data to format
            
        Returns:
            Formatted string representation
        """
        if isinstance(result, list):
            if len(result) == 1:
                return str(result[0])
            return f"[{', '.join(str(item) for item in result)}]"
        else:
            return str(result)
    
    async def execute_decision(
        self,
        decision_type: str,
        decision_data: Dict[str, Any],
        visualization_needed: bool = False,
        memory_instance = None
    ) -> Tuple[bool, Any, Optional[Dict[str, Any]]]:
        """
        Execute a decision with optional memory integration.
        
        Args:
            decision_type: Type of decision (function_call, final_answer)
            decision_data: Decision data
            visualization_needed: Whether visualization is needed
            memory_instance: Memory instance for storing execution data
            
        Returns:
            Tuple of (success, result, visualization_config)
        """
        logger.info(f"Executing decision: {decision_type}")
        
        # Store decision in memory if available
        if memory_instance:
            memory_instance.store_decision(
                decision_type=decision_type,
                decision_data=decision_data,
                context={"visualization_needed": visualization_needed}
            )
            memory_instance.store_execution_step(
                step=f"Executing {decision_type}",
                details={"decision_data": decision_data}
            )
        
        if decision_type == "function_call":
            success, result = await self.execute_function_call(decision_data)
            
            # Store tool call in memory
            if memory_instance and success:
                function_name = decision_data.get("function_name", "unknown")
                arguments = decision_data.get("arguments", {})
                memory_instance.store_tool_call(
                    tool_name=function_name,
                    arguments=arguments,
                    result=result
                )
                memory_instance.track_method_call(
                    method_name=function_name,
                    module_name="tools",
                    args=arguments,
                    result=result
                )
                memory_instance.store_intermediate_result(
                    key=f"{function_name}_result",
                    value=result,
                    metadata={"iteration": memory_instance.get_current_iteration()}
                )
            elif memory_instance:
                memory_instance.store_error(
                    error=Exception(f"Tool execution failed: {result}"),
                    context={"decision_type": decision_type, "decision_data": decision_data}
                )
            
            if not success:
                return False, result, None
            
            formatted_result = self.format_result(result)
            logger.info(f"Function call result: {formatted_result}")
            
            return True, result, None
        
        elif decision_type == "final_answer":
            final_result = await self.handle_final_answer(decision_data)
            
            # Store final answer in memory
            if memory_instance:
                answer = decision_data.get("answer", "")
                memory_instance.store_output(
                    output_data=answer,
                    destination="user"
                )
                memory_instance.store_intermediate_result(
                    key="final_answer",
                    value=answer,
                    metadata={"iteration": memory_instance.get_current_iteration()}
                )
            
            visualization_config = None
            if visualization_needed or final_result.get("needs_visualization", False):
                visualization_config = {
                    "tool": "draw_rectangle_with_turtle",
                    "arguments": {
                        "width": 300,
                        "height": 150,
                        "text": "TSAI"
                    }
                }
            
            logger.info(f"Final answer: {final_result['final_answer']}")
            
            return True, final_result, visualization_config
        
        else:
            error_msg = f"Unknown decision type: {decision_type}"
            logger.error(error_msg)
            if memory_instance:
                memory_instance.store_error(
                    error=Exception(error_msg),
                    context={"decision_type": decision_type, "decision_data": decision_data}
                )
            return False, error_msg, None
    
    async def execute_complete_action(
        self,
        decision_type: str,
        decision_data: Dict[str, Any],
        perception_data: Dict[str, Any] = None,
        memory_instance = None
    ) -> Dict[str, Any]:
        """
        Execute a complete action flow based on decision, incorporating perception and memory.
        
        Args:
            decision_type: Type of decision (function_call, final_answer)
            decision_data: Decision data
            perception_data: Perception data for context
            memory_instance: Memory instance for storing execution data
            
        Returns:
            Dictionary containing action results and metadata
        """
        logger.info("Executing complete action flow")
        
        # Extract visualization requirement from perception if available
        visualization_needed = False
        if perception_data and perception_data.get("requires_visualization", False):
            visualization_needed = True
        
        # Execute the decision
        success, result, visualization_config = await self.execute_decision(
            decision_type=decision_type,
            decision_data=decision_data,
            visualization_needed=visualization_needed,
            memory_instance=memory_instance
        )
        
        action_result = {
            "success": success,
            "decision_type": decision_type,
            "result": result,
            "visualization_config": visualization_config,
            "visualization_executed": False,
            "visualization_result": None
        }
        
        # Execute visualization if needed
        if success and visualization_config:
            vis_success, vis_result = await self.execute_visualization(
                visualization_config=visualization_config,
                memory_instance=memory_instance
            )
            
            action_result["visualization_executed"] = True
            action_result["visualization_result"] = vis_result
            
            if not vis_success:
                action_result["success"] = False
                logger.warning("Visualization failed but main action succeeded")
        
        # Store complete action result in memory
        if memory_instance:
            memory_instance.store_intermediate_result(
                key="complete_action_result",
                value=action_result,
                metadata={
                    "decision_type": decision_type,
                    "iteration": memory_instance.get_current_iteration()
                }
            )
        
        logger.info(f"Complete action executed: success={success}")
        return action_result
