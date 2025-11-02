"""
Memory Module
Handles state management, storage, and retrieval of information.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class Memory:
    """
    Comprehensive memory system that stores all execution data, facts, variables, and context.
    """
    
    def __init__(self):
        """Initialize the comprehensive Memory module."""
        # Core execution state
        self.state = {
            "iteration": 0,
            "last_response": None,
            "iteration_history": [],
            "tool_call_history": [],
            "execution_log": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        # Comprehensive data storage using different collections
        self.data_store = {
            # Facts and knowledge
            "facts": {},  # Dict of facts by category
            "prompt_facts": {},  # Extracted facts from prompts
            "context_facts": [],  # List of contextual facts
            
            # Variables and state
            "variables": {},  # Dict of all variables
            "global_variables": {},  # Global state variables
            "local_variables": {},  # Session-specific variables
            
            # Method and function tracking
            "methods_called": [],  # List of all methods called
            "methods_by_module": defaultdict(list),  # Methods grouped by module
            "function_usage": defaultdict(int),  # Count of function calls
            
            # Execution tracking
            "execution_flow": deque(maxlen=1000),  # Recent execution steps
            "decision_points": [],  # All decision points in execution
            "error_history": [],  # All errors encountered
            
            # Data processing
            "input_data": [],  # All inputs received
            "output_data": [],  # All outputs generated
            "intermediate_results": {},  # Intermediate computation results
            
            # Environment and context
            "environment": {},  # Current environment state
            "available_tools": [],  # Available tools/methods
            "tool_metadata": {},  # Metadata about tools
            
            # Performance metrics
            "performance_metrics": {
                "total_iterations": 0,
                "total_functions_called": 0,
                "average_response_time": 0,
                "errors_count": 0
            }
        }
        
        logger.info("Comprehensive Memory module initialized")
    
    def reset(self):
        """Reset all memory to initial state."""
        logger.info("Resetting memory state")
        self.__init__()
    
    def store_facts(self, facts: Dict[str, Any], category: str = "general"):
        """
        Store facts in memory.
        
        Args:
            facts: Dictionary of facts to store
            category: Category name for the facts
        """
        if category not in self.data_store["facts"]:
            self.data_store["facts"][category] = {}
        
        self.data_store["facts"][category].update(facts)
        logger.info(f"Stored facts in category: {category}")
    
    def get_facts(self, category: str = None) -> Dict[str, Any]:
        """
        Retrieve facts from memory.
        
        Args:
            category: Category to retrieve, None for all
            
        Returns:
            Dictionary of facts
        """
        if category:
            return self.data_store["facts"].get(category, {})
        return self.data_store["facts"]
    
    def store_prompt_facts(self, prompt_facts: Dict[str, Any]):
        """
        Store prompt facts extracted from system prompts.
        
        Args:
            prompt_facts: Dictionary containing prompt facts
        """
        self.data_store["prompt_facts"] = prompt_facts
        logger.info("Stored prompt facts")
    
    def get_prompt_facts(self) -> Dict[str, Any]:
        """Get stored prompt facts."""
        return self.data_store["prompt_facts"]
    
    def store_context_fact(self, fact: str, source: str = "system"):
        """
        Store a contextual fact.
        
        Args:
            fact: The fact to store
            source: Source of the fact
        """
        self.data_store["context_facts"].append({
            "fact": fact,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
    
    def store_variable(self, name: str, value: Any, scope: str = "global"):
        """
        Store a variable in memory.
        
        Args:
            name: Variable name
            value: Variable value
            scope: Variable scope (global or local)
        """
        var_data = {
            "value": value,
            "type": type(value).__name__,
            "timestamp": datetime.now().isoformat()
        }
        
        self.data_store["variables"][name] = var_data
        
        if scope == "global":
            self.data_store["global_variables"][name] = var_data
        else:
            self.data_store["local_variables"][name] = var_data
        
        logger.info(f"Stored variable: {name} (scope: {scope})")
    
    def get_variable(self, name: str) -> Any:
        """
        Get a variable from memory.
        
        Args:
            name: Variable name
            
        Returns:
            Variable value or None
        """
        return self.data_store["variables"].get(name, {}).get("value")
    
    def get_all_variables(self) -> Dict[str, Any]:
        """Get all stored variables."""
        return {
            name: data["value"] 
            for name, data in self.data_store["variables"].items()
        }
    
    def track_method_call(self, method_name: str, module_name: str, 
                         args: Dict[str, Any] = None, result: Any = None):
        """
        Track a method or function call.
        
        Args:
            method_name: Name of the method
            module_name: Name of the module
            args: Arguments passed
            result: Result returned
        """
        call_data = {
            "method_name": method_name,
            "module_name": module_name,
            "args": args,
            "result": str(result) if result is not None else None,
            "timestamp": datetime.now().isoformat()
        }
        
        self.data_store["methods_called"].append(call_data)
        self.data_store["methods_by_module"][module_name].append(call_data)
        self.data_store["function_usage"][method_name] += 1
        self.data_store["performance_metrics"]["total_functions_called"] += 1
        
        logger.info(f"Tracked method call: {module_name}.{method_name}")
    
    def get_method_calls(self, method_name: str = None, module_name: str = None) -> List[Dict]:
        """
        Get method call history.
        
        Args:
            method_name: Filter by method name
            module_name: Filter by module name
            
        Returns:
            List of method call records
        """
        calls = self.data_store["methods_called"]
        
        if method_name:
            calls = [c for c in calls if c["method_name"] == method_name]
        
        if module_name:
            calls = [c for c in calls if c["module_name"] == module_name]
        
        return calls
    
    def store_execution_step(self, step: str, details: Dict[str, Any] = None):
        """
        Store an execution step.
        
        Args:
            step: Description of the execution step
            details: Additional details
        """
        step_data = {
            "step": step,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.data_store["execution_flow"].append(step_data)
        logger.debug(f"Stored execution step: {step}")
    
    def get_recent_execution_flow(self, n: int = 10) -> List[Dict]:
        """
        Get recent execution steps.
        
        Args:
            n: Number of recent steps to retrieve
            
        Returns:
            List of recent execution steps
        """
        return list(self.data_store["execution_flow"])[-n:]
    
    def store_decision(self, decision_type: str, decision_data: Dict[str, Any], 
                      context: Dict[str, Any] = None):
        """
        Store a decision point.
        
        Args:
            decision_type: Type of decision
            decision_data: Decision data
            context: Context at decision time
        """
        decision_record = {
            "decision_type": decision_type,
            "decision_data": decision_data,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.data_store["decision_points"].append(decision_record)
        logger.info(f"Stored decision: {decision_type}")
    
    def get_decisions(self, decision_type: str = None) -> List[Dict]:
        """
        Get decision history.
        
        Args:
            decision_type: Filter by decision type
            
        Returns:
            List of decision records
        """
        if decision_type:
            return [d for d in self.data_store["decision_points"] 
                   if d["decision_type"] == decision_type]
        return self.data_store["decision_points"]
    
    def store_error(self, error: Exception, context: Dict[str, Any] = None):
        """
        Store an error.
        
        Args:
            error: The exception object
            context: Context when error occurred
        """
        error_record = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.data_store["error_history"].append(error_record)
        self.data_store["performance_metrics"]["errors_count"] += 1
        logger.error(f"Stored error: {error_record['error_type']}")
    
    def get_errors(self) -> List[Dict]:
        """Get all stored errors."""
        return self.data_store["error_history"]
    
    def store_input(self, input_data: Any, source: str = "user"):
        """
        Store input data.
        
        Args:
            input_data: The input data
            source: Source of input
        """
        self.data_store["input_data"].append({
            "data": input_data,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
    
    def store_output(self, output_data: Any, destination: str = "user"):
        """
        Store output data.
        
        Args:
            output_data: The output data
            destination: Destination of output
        """
        self.data_store["output_data"].append({
            "data": output_data,
            "destination": destination,
            "timestamp": datetime.now().isoformat()
        })
    
    def store_intermediate_result(self, key: str, value: Any, metadata: Dict = None):
        """
        Store intermediate computation result.
        
        Args:
            key: Key identifier
            value: Result value
            metadata: Additional metadata
        """
        self.data_store["intermediate_results"][key] = {
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
    
    def get_intermediate_result(self, key: str) -> Any:
        """
        Get intermediate result.
        
        Args:
            key: Result key
            
        Returns:
            Result value or None
        """
        return self.data_store["intermediate_results"].get(key, {}).get("value")
    
    def store_environment(self, env_data: Dict[str, Any]):
        """
        Store environment state.
        
        Args:
            env_data: Environment data
        """
        self.data_store["environment"].update(env_data)
    
    def update_performance_metrics(self, metrics: Dict[str, Any]):
        """
        Update performance metrics.
        
        Args:
            metrics: Dictionary of metrics to update
        """
        self.data_store["performance_metrics"].update(metrics)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.data_store["performance_metrics"].copy()

    def get_memory_summary(self) -> str:
        """
        Get a comprehensive summary of all stored memory.
        
        Returns:
            Formatted string summary
        """
        summary_lines = [
            "=== MEMORY SUMMARY ===",
            f"Total Iterations: {self.data_store['performance_metrics']['total_iterations']}",
            f"Total Functions Called: {self.data_store['performance_metrics']['total_functions_called']}",
            f"Errors Encountered: {self.data_store['performance_metrics']['errors_count']}",
            "",
            "Facts Stored:",
            f"  - Fact Categories: {len(self.data_store['facts'])}",
            f"  - Context Facts: {len(self.data_store['context_facts'])}",
            "",
            "Variables Stored:",
            f"  - Total Variables: {len(self.data_store['variables'])}",
            f"  - Global Variables: {len(self.data_store['global_variables'])}",
            "",
            "Methods Called:",
            f"  - Total Method Calls: {len(self.data_store['methods_called'])}",
            f"  - Unique Methods: {len(self.data_store['function_usage'])}",
            "",
            "Execution Data:",
            f"  - Execution Steps: {len(self.data_store['execution_flow'])}",
            f"  - Decision Points: {len(self.data_store['decision_points'])}",
            "",
            "Data Storage:",
            f"  - Inputs Recorded: {len(self.data_store['input_data'])}",
            f"  - Outputs Recorded: {len(self.data_store['output_data'])}",
            f"  - Intermediate Results: {len(self.data_store['intermediate_results'])}"
        ]
        
        return "\n".join(summary_lines)
    
    # Legacy methods for backward compatibility
    def store_iteration(self, iteration: int, query: str, response: Any, result: Any):
        """
        Store information about an iteration (legacy method).
        
        Args:
            iteration: Iteration number
            query: The query for this iteration
            response: The agent's response
            result: The result from tool execution
        """
        logger.info(f"Storing iteration {iteration}")
        
        iteration_data = {
            "iteration": iteration,
            "query": query,
            "response": response,
            "result": str(result),
            "timestamp": datetime.now().isoformat()
        }
        
        self.state["iteration_history"].append(iteration_data)
        self.state["iteration"] = iteration
        self.state["last_response"] = result
        self.data_store["performance_metrics"]["total_iterations"] += 1
    
    def store_tool_call(self, tool_name: str, arguments: Dict[str, Any], result: Any):
        """
        Store a tool call for later reference (legacy method).
        
        Args:
            tool_name: Name of the tool called
            arguments: Arguments passed to the tool
            result: Result from the tool
        """
        logger.info(f"Storing tool call: {tool_name}")
        
        tool_call_data = {
            "tool_name": tool_name,
            "arguments": arguments,
            "result": str(result),
            "timestamp": datetime.now().isoformat()
        }
        
        self.state["tool_call_history"].append(tool_call_data)
        
        # Also track as method call
        self.track_method_call(tool_name, "tools", arguments, result)
    
    def get_iteration_summary(self) -> str:
        """
        Get a summary of all iterations for context.
        
        Returns:
            Formatted string containing iteration history
        """
        if not self.state["iteration_history"]:
            return "No iterations yet"
        
        summary_lines = []
        for iter_data in self.state["iteration_history"]:
            summary_lines.append(
                f"In iteration {iter_data['iteration']} you called the system, "
                f"and it returned {iter_data['result']}."
            )
        
        return "\n".join(summary_lines)
    
    def get_last_response(self) -> Any:
        """
        Get the last response from the agent.
        
        Returns:
            Last response data
        """
        return self.state["last_response"]
    
    def increment_iteration(self) -> int:
        """
        Increment the iteration counter.
        
        Returns:
            New iteration number
        """
        self.state["iteration"] += 1
        return self.state["iteration"]
    
    def get_current_iteration(self) -> int:
        """
        Get the current iteration number.
        
        Returns:
            Current iteration number
        """
        return self.state["iteration"]
    
    def log_execution(self, message: str, level: str = "info"):
        """
        Log an execution event.
        
        Args:
            message: Log message
            level: Log level (info, warning, error)
        """
        log_entry = {
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }
        self.state["execution_log"].append(log_entry)
        
        # Store as execution step
        self.store_execution_step(message, {"level": level})
        
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the complete current state.
        
        Returns:
            Dictionary containing current state
        """
        return self.state.copy()
    
    def export_state(self, filepath: str):
        """
        Export the current state to a JSON file.
        
        Args:
            filepath: Path to save the state file
        """
        logger.info(f"Exporting state to {filepath}")
        
        state_export = {
            "state": self.state,
            "data_store": self.data_store,
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state_export, f, indent=2, default=str)
        
        logger.info("State exported successfully")
    
    def import_state(self, filepath: str):
        """
        Import state from a JSON file.
        
        Args:
            filepath: Path to load the state file from
        """
        logger.info(f"Importing state from {filepath}")
        
        with open(filepath, 'r') as f:
            state_data = json.load(f)
        
        self.state = state_data.get("state", self.state)
        if "data_store" in state_data:
            self.data_store = state_data["data_store"]
        
        logger.info("State imported successfully")
