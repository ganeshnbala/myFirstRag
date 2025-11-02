"""
Decision-Making Module
Handles AI reasoning, planning, and decision making.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import google.generativeai as genai
import asyncio
import re

logger = logging.getLogger(__name__)


class DecisionMaking:
    """
    Handles decision making and AI reasoning.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Decision-Making module.
        
        Args:
            api_key: Gemini API key for AI reasoning
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("Decision-Making module initialized")
    
    async def generate_decision(
        self,
        perception_data: Dict[str, Any],
        memory_data: Dict[str, Any],
        available_tools: List[Dict[str, Any]],
        timeout: int = 30
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a decision based on perception and memory.
        
        Args:
            perception_data: Data from perception module
            memory_data: Data from memory module
            available_tools: List of available tools
            timeout: Timeout for AI response
            
        Returns:
            Tuple of (decision_type, decision_data)
        """
        logger.info("Generating decision")
        
        # Analyze perception and memory inputs
        analysis = self._analyze_inputs(perception_data, memory_data)
        logger.info(f"Input analysis: {analysis}")
        
        # Build system prompt with tools
        tools_description = self._format_tools(available_tools)
        system_prompt = self._create_system_prompt(tools_description)
        
        # Build context query with enhanced perception and memory data
        context_query = self._build_enhanced_context_query(
            perception_data,
            memory_data,
            analysis
        )
        
        # Generate AI response
        full_prompt = f"{system_prompt}\n\nQuery: {context_query}"
        
        try:
            response = await self._generate_with_timeout(full_prompt, timeout)
            response_text = response.text.strip()
            
            logger.info(f"Decision generated: {response_text[:100]}...")
            
            # Parse the decision
            decision_type, decision_data = self._parse_decision(
                response_text,
                available_tools
            )
            
            return decision_type, decision_data
            
        except Exception as e:
            logger.error(f"Error in decision generation: {e}")
            raise
    
    def _analyze_inputs(self, perception_data: Dict[str, Any], memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze inputs from perception and memory modules.
        
        Args:
            perception_data: Data from perception module
            memory_data: Data from memory module
            
        Returns:
            Dictionary containing analysis results
        """
        analysis = {
            "perception_analysis": {},
            "memory_analysis": {},
            "context_signals": [],
            "decision_hints": []
        }
        
        # Analyze perception data
        if "prompt_facts" in perception_data:
            prompt_facts = perception_data.get("prompt_facts", {})
            analysis["perception_analysis"]["prompt_facts_count"] = len(prompt_facts)
            
            # Extract key facts that influence decisions
            if "reasoning_requirements" in prompt_facts:
                analysis["decision_hints"].extend(prompt_facts["reasoning_requirements"])
            
            if "output_formats" in prompt_facts:
                analysis["context_signals"].append(f"Expected output formats: {prompt_facts['output_formats']}")
        
        if "query_type" in perception_data:
            analysis["perception_analysis"]["query_type"] = perception_data["query_type"]
            analysis["context_signals"].append(f"Query type: {perception_data['query_type']}")
        
        if "key_concepts" in perception_data:
            concepts = perception_data["key_concepts"]
            if concepts:
                analysis["context_signals"].append(f"Key concepts: {', '.join(concepts)}")
        
        if "requires_visualization" in perception_data:
            if perception_data["requires_visualization"]:
                analysis["decision_hints"].append("Visualization required")
        
        # Analyze memory data
        if "iteration_history" in memory_data:
            iterations = memory_data["iteration_history"]
            analysis["memory_analysis"]["total_iterations"] = len(iterations)
            
            if iterations:
                last_iteration = iterations[-1]
                analysis["context_signals"].append(
                    f"Last result: {last_iteration.get('result', 'N/A')}"
                )
        
        if "performance_metrics" in memory_data:
            metrics = memory_data["performance_metrics"]
            analysis["memory_analysis"]["errors_count"] = metrics.get("errors_count", 0)
            
            if metrics.get("errors_count", 0) > 0:
                analysis["decision_hints"].append("Previous errors encountered")
        
        if "function_usage" in memory_data:
            function_usage = memory_data["function_usage"]
            if function_usage:
                most_used = max(function_usage.items(), key=lambda x: x[1])
                analysis["context_signals"].append(
                    f"Most used function: {most_used[0]} ({most_used[1]} times)"
                )
        
        # Store context facts from memory
        if "context_facts" in memory_data:
            context_facts = memory_data["context_facts"]
            if context_facts:
                analysis["context_signals"].append(
                    f"Recent context facts: {len(context_facts)} available"
                )
        
        logger.info(f"Input analysis complete: {len(analysis['context_signals'])} signals, {len(analysis['decision_hints'])} hints")
        return analysis
    
    def _build_enhanced_context_query(
        self,
        perception_data: Dict[str, Any],
        memory_data: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """
        Build enhanced context query with perception, memory, and analysis.
        
        Args:
            perception_data: Data from perception module
            memory_data: Data from memory module
            analysis: Analysis results
            
        Returns:
            Enhanced context query string
        """
        query_parts = []
        
        # Add original user query from perception
        user_query = perception_data.get("raw_query", perception_data.get("user_query", ""))
        query_parts.append(user_query)
        
        # Add RAG context if available (Paint-related instructions)
        if "rag_context" in perception_data and perception_data["rag_context"]:
            query_parts.append("\n\n=== KNOWLEDGE BASE CONTEXT ===")
            query_parts.append(perception_data["rag_context"])
        
        # Add context signals
        if analysis.get("context_signals"):
            query_parts.append("\n\nContext Information:")
            for signal in analysis["context_signals"]:
                query_parts.append(f"- {signal}")
        
        # Add decision hints
        if analysis.get("decision_hints"):
            query_parts.append("\nDecision Guidelines:")
            for hint in analysis["decision_hints"]:
                query_parts.append(f"- {hint}")
        
        # Add iteration history from memory
        if memory_data.get("iteration_history"):
            iteration_summary = self._format_iteration_history(memory_data["iteration_history"])
            if iteration_summary:
                query_parts.append(f"\n\n{iteration_summary}")
                query_parts.append("What should I do next?")
        
        # Add prompt facts context
        if "prompt_facts" in perception_data:
            prompt_facts = perception_data["prompt_facts"]
            if prompt_facts and "examples" in prompt_facts:
                query_parts.append("\n\nAvailable examples:")
                for ex in prompt_facts["examples"][:3]:  # Limit to 3 examples
                    query_parts.append(f"- {ex}")
        
        return "\n".join(query_parts)
    
    def _format_iteration_history(self, iteration_history: List[Dict]) -> str:
        """
        Format iteration history into a readable summary.
        
        Args:
            iteration_history: List of iteration records
            
        Returns:
            Formatted iteration history string
        """
        if not iteration_history:
            return ""
        
        summary_lines = []
        for iter_data in iteration_history:
            iteration_num = iter_data.get("iteration", "?")
            result = iter_data.get("result", "N/A")
            summary_lines.append(
                f"In iteration {iteration_num} you called the system, and it returned {result}."
            )
        
        return "\n".join(summary_lines)
    
    def _format_tools(self, tools: List[Dict[str, Any]]) -> str:
        """
        Format the list of available tools for the prompt.
        
        Args:
            tools: List of tool dictionaries
            
        Returns:
            Formatted tools description string
        """
        tools_description = []
        
        for i, tool in enumerate(tools):
            params = tool.get('inputSchema', {})
            desc = tool.get('description', 'No description')
            name = tool.get('name', f'tool_{i}')
            
            if 'properties' in params:
                param_details = []
                for param_name, param_info in params['properties'].items():
                    param_type = param_info.get('type', 'unknown')
                    param_details.append(f"{param_name}: {param_type}")
                params_str = ', '.join(param_details)
            else:
                params_str = 'no parameters'
            
            tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
            tools_description.append(tool_desc)
        
        return "\n".join(tools_description)
    
    def _create_system_prompt(self, tools_description: str) -> str:
        """
        Create the system prompt for the AI.
        
        Args:
            tools_description: Description of available tools
            
        Returns:
            System prompt string
        """
        return f"""You are an intelligent agent solving problems in iterations. You have access to various mathematical, visualization, and news tools.

Available tools:
{tools_description}

You must respond with EXACTLY ONE line in one of these formats (no additional text):
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
   
2. For final answers:
   FINAL_ANSWER: [result]

Important:
- Think step by step about what needs to be done
- When a function returns multiple values, you need to process all of them
- Only give FINAL_ANSWER when you have completed all necessary calculations
- Do not repeat function calls with the same parameters
- Use appropriate tools for visualization when needed
- For news: First fetch headlines, then display in browser if requested

Examples:
- FUNCTION_CALL: add|5|3
- FUNCTION_CALL: strings_to_chars_to_int|INDIA
- FUNCTION_CALL: fetch_bbc_headlines|10
- FUNCTION_CALL: display_headlines_in_browser
- FINAL_ANSWER: [42]

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""
    

    
    async def _generate_with_timeout(self, prompt: str, timeout: int) -> Any:
        """
        Generate AI response with timeout.
        
        Args:
            prompt: Input prompt
            timeout: Timeout in seconds
            
        Returns:
            AI response object
        """
        logger.info(f"Generating AI response (timeout: {timeout}s)")
        
        loop = asyncio.get_event_loop()
        
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            ),
            timeout=timeout
        )
        
        return response
    
    def _parse_decision(
        self,
        response_text: str,
        available_tools: List[Dict[str, Any]]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Parse the AI response into a decision.
        
        Args:
            response_text: AI response text
            available_tools: List of available tools
            
        Returns:
            Tuple of (decision_type, decision_data)
        """
        # Extract the actual response line
        original_response = response_text
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith("FUNCTION_CALL:") or line.startswith("FINAL_ANSWER:"):
                response_text = line
                break
        
        # If no proper format found, check if the response contains a final answer pattern
        if not response_text.startswith("FUNCTION_CALL:") and not response_text.startswith("FINAL_ANSWER:"):
            # Try to extract a final answer from explanatory text
            # Look for scientific notation or numbers
            numbers_with_e = re.findall(r'[\d.]+[eE][+\-]?\d+', original_response)
            if numbers_with_e:
                return "final_answer", {"answer": f"[{numbers_with_e[-1]}]"}
            # Look for regular decimal numbers
            decimal_numbers = re.findall(r'\d+\.\d+', original_response[-100:])
            if decimal_numbers:
                return "final_answer", {"answer": f"[{decimal_numbers[-1]}]"}
            # Look for any numbers in the last 50 characters
            any_numbers = re.findall(r'\d+', original_response[-50:])
            if any_numbers and len(any_numbers) <= 3:  # If there are too many numbers, it's not a final answer
                return "final_answer", {"answer": f"[{any_numbers[-1]}]"}
        
        # Fall back to original parsing if no numbers found
        response_text = original_response
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith("FUNCTION_CALL:") or line.startswith("FINAL_ANSWER:"):
                response_text = line
                break
        
        if response_text.startswith("FUNCTION_CALL:"):
            # Parse function call
            _, function_info = response_text.split(":", 1)
            parts = [p.strip() for p in function_info.split("|")]
            func_name = parts[0]
            params = parts[1:]
            
            # Find the tool schema
            tool = next((t for t in available_tools if t.get('name') == func_name), None)
            
            if not tool:
                raise ValueError(f"Unknown tool: {func_name}")
            
            # Prepare arguments according to tool schema
            arguments = {}
            schema_properties = tool.get('inputSchema', {}).get('properties', {})
            
            for param_name, param_info in schema_properties.items():
                if not params:
                    raise ValueError(f"Not enough parameters for {func_name}")
                
                value = params.pop(0)
                param_type = param_info.get('type', 'string')
                
                # Type conversion
                if param_type == 'integer':
                    arguments[param_name] = int(value)
                elif param_type == 'number':
                    arguments[param_name] = float(value)
                elif param_type == 'array':
                    if isinstance(value, str):
                        # Try to detect array format and parse accordingly
                        if value.startswith('[') and value.endswith(']'):
                            # Format: ['73', '78', '68', '73', '65'] or [73,78,68,73,65]
                            value = value.strip("[]'\"")
                            # Split by comma and clean up each element
                            value_list = [x.strip().strip("'\"") for x in value.split(',')]
                            arguments[param_name] = [int(x) for x in value_list]
                        else:
                            # Format: single number (should have been multiple params for array)
                            # Check if there are more params remaining for this array
                            remaining_params = params.copy()
                            if remaining_params:
                                # Collect all remaining params for this array
                                array_values = [int(value)]  # Add the first value
                                # Try to get more values until we exhaust params or schema
                                array_values.extend([int(p) for p in remaining_params])
                                arguments[param_name] = array_values
                                # Clear params since we consumed them
                                params.clear()
                            else:
                                arguments[param_name] = [int(value)]
                    else:
                        arguments[param_name] = value
                else:
                    arguments[param_name] = str(value)
            
            return "function_call", {
                "function_name": func_name,
                "arguments": arguments
            }
        
        elif response_text.startswith("FINAL_ANSWER:"):
            # Parse final answer
            _, answer = response_text.split(":", 1)
            answer = answer.strip()
            
            return "final_answer", {
                "answer": answer
            }
        
        else:
            raise ValueError(f"Unknown decision format: {response_text}")
