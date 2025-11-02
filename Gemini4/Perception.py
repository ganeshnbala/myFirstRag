"""
Perception Module
Handles input processing, environment observation, and information gathering.
"""

import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
import asyncio

logger = logging.getLogger(__name__)

# Import RAG module
try:
    from RAG import RAG
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("RAG module not available")

# Student prompt template
STUDENT_PROMPT_TEMPLATE = """You are a math agent solving problems in iterations. You have access to various mathematical tools.

Available tools:
{tools_description}

Instructions:
1. Think step-by-step before producing any output. Explain your reasoning internally and tag the type of reasoning used (e.g., arithmetic, logic, lookup, drawing) before deciding which function to call or what the final answer is.
2. Before giving a FINAL_ANSWER, perform internal self-checks to verify calculations or logic are correct.
3. If a tool fails, returns unexpected values, or you are uncertain, provide a safe fallback by either retrying the function call or reasoning through an alternative method.
4. You must respond with EXACTLY ONE line in one of these formats (no additional text):
   a. For function calls:
      FUNCTION_CALL: function_name|param1|param2|...
   b. For final answers:
      FINAL_ANSWER: [number]
   c. Open the Paint and draw a rectangle and add text in it. The text should be "TSAI"

Important:
- When a function returns multiple values, you need to process all of them.
- Only give FINAL_ANSWER when you have completed all necessary calculations and verified them.
- Do not repeat function calls with the same parameters.
- Use the existing function to draw a rectangle and add text in it.
- Think through your reasoning before each step to avoid mistakes.

Examples:
- FUNCTION_CALL: add|5|3
- FUNCTION_CALL: strings_to_chars_to_int|INDIA
- FINAL_ANSWER: [42]

DO NOT include any explanations or additional text. Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""


class Perception:
    """
    Handles perception of the environment and input processing.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Perception module with API key for AI capabilities.
        
        Args:
            api_key: Gemini API key for AI processing
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.student_prompt_template = STUDENT_PROMPT_TEMPLATE
        
        # Initialize RAG if available
        if RAG_AVAILABLE:
            self.rag = RAG(api_key)
            logger.info("RAG module integrated into Perception")
        else:
            self.rag = None
            logger.info("RAG module not available")
        
        logger.info("Perception module initialized")
    
    def get_student_prompt(self, tools_description: str) -> str:
        """
        Get the student prompt with tools description.
        
        Args:
            tools_description: Formatted tools description
            
        Returns:
            Complete student prompt
        """
        return self.student_prompt_template.format(
            tools_description=tools_description
        )
    
    def extract_facts_from_prompt(self) -> Dict[str, Any]:
        """
        Extract all key facts from the student prompt.
        
        Returns:
            Dictionary containing extracted facts
        """
        prompt = self.student_prompt_template
        
        facts = {
            "agent_role": "math agent",
            "problem_solving_approach": "iterations",
            "reasoning_requirements": [],
            "output_formats": [],
            "response_requirements": [],
            "visualization_instructions": [],
            "examples": []
        }
        
        # Extract reasoning requirements
        if "Think step-by-step" in prompt:
            facts["reasoning_requirements"].append("step-by-step reasoning")
        
        if "Explain your reasoning internally" in prompt:
            facts["reasoning_requirements"].append("internal reasoning explanation")
        
        if "tag the type of reasoning used" in prompt:
            facts["reasoning_requirements"].append("reasoning type tagging (arithmetic, logic, lookup, drawing)")
        
        if "perform internal self-checks" in prompt:
            facts["reasoning_requirements"].append("internal self-verification")
        
        if "safe fallback" in prompt.lower():
            facts["reasoning_requirements"].append("fallback mechanism for failures")
        
        # Extract output formats
        if "FUNCTION_CALL:" in prompt:
            facts["output_formats"].append("FUNCTION_CALL: function_name|param1|param2|...")
        
        if "FINAL_ANSWER:" in prompt:
            facts["output_formats"].append("FINAL_ANSWER: [number]")
        
        if "draw a rectangle and add text" in prompt.lower():
            facts["visualization_instructions"].append("draw rectangle with text")
        
        if '"TSAI"' in prompt:
            facts["visualization_instructions"].append("text should be 'TSAI'")
        
        # Extract response requirements
        if "EXACTLY ONE line" in prompt:
            facts["response_requirements"].append("single line response")
        
        if "no additional text" in prompt.lower():
            facts["response_requirements"].append("no explanations")
        
        if "process all of them" in prompt:
            facts["response_requirements"].append("process all returned values")
        
        if "only give FINAL_ANSWER when completed" in prompt.lower():
            facts["response_requirements"].append("complete verification before final answer")
        
        if "Do not repeat function calls" in prompt:
            facts["response_requirements"].append("no repeated function calls")
        
        if "Think through your reasoning" in prompt:
            facts["response_requirements"].append("reasoning before each step")
        
        # Extract examples
        if "add|5|3" in prompt:
            facts["examples"].append("FUNCTION_CALL: add|5|3")
        
        if "strings_to_chars_to_int|INDIA" in prompt:
            facts["examples"].append("FUNCTION_CALL: strings_to_chars_to_int|INDIA")
        
        if "FINAL_ANSWER: [42]" in prompt:
            facts["examples"].append("FINAL_ANSWER: [42]")
        
        logger.info(f"Extracted {len(facts)} fact categories from prompt")
        return facts
    
    def format_facts_summary(self) -> str:
        """
        Format the extracted facts into a readable summary.
        
        Returns:
            Formatted facts summary
        """
        facts = self.extract_facts_from_prompt()
        
        summary_lines = [
            "=== Student Prompt Facts ===",
            "",
            f"Agent Role: {facts['agent_role']}",
            f"Approach: {facts['problem_solving_approach']}",
            "",
            "Reasoning Requirements:",
        ]
        
        for req in facts["reasoning_requirements"]:
            summary_lines.append(f"  - {req}")
        
        summary_lines.append("\nOutput Formats:")
        for fmt in facts["output_formats"]:
            summary_lines.append(f"  - {fmt}")
        
        summary_lines.append("\nResponse Requirements:")
        for req in facts["response_requirements"]:
            summary_lines.append(f"  - {req}")
        
        summary_lines.append("\nVisualization Instructions:")
        for instr in facts["visualization_instructions"]:
            summary_lines.append(f"  - {instr}")
        
        summary_lines.append("\nExamples:")
        for ex in facts["examples"]:
            summary_lines.append(f"  - {ex}")
        
        return "\n".join(summary_lines)

    async def observe_environment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Observe and gather information from the environment.
        
        Args:
            context: Current context information
            
        Returns:
            Dictionary containing observed environment data
        """
        logger.info("Observing environment")
        
        observed_data = {
            "timestamp": context.get("timestamp", None),
            "user_query": context.get("query", ""),
            "available_tools": context.get("tools", []),
            "iteration_state": context.get("iteration", 0),
            "previous_results": context.get("last_response", None),
            "prompt_facts": self.extract_facts_from_prompt()
        }
        
        logger.info(f"Environment observation complete: {len(observed_data)} data points")
        return observed_data
    
    async def process_user_input(self, user_query: str) -> Dict[str, Any]:
        """
        Process and understand user input with RAG enhancement.
        
        Args:
            user_query: The user's input query
            
        Returns:
            Dictionary containing processed input information
        """
        logger.info(f"Processing user input: {user_query[:50]}...")
        
        processed_input = {
            "raw_query": user_query,
            "query_type": self._classify_query(user_query),
            "key_concepts": self._extract_concepts(user_query),
            "requires_visualization": self._requires_visualization(user_query),
            "prompt_facts": self.extract_facts_from_prompt()
        }
        
        # Add RAG context if available and query is related to Paint or BBC headlines
        if self.rag and any(keyword in user_query.lower() for keyword in ["paint", "draw", "bbc", "headlines", "news"]):
            keyword = "Paint" if any(kw in user_query.lower() for kw in ["paint", "draw"]) else "BBC headlines"
            logger.info(f"Applying RAG context enhancement for {keyword}-related query")
            rag_context = self.rag.enhance_context(user_query)
            processed_input["rag_context"] = rag_context.get("context_summary")
            processed_input["rag_recommendations"] = self.rag.get_function_recommendations(user_query)
            logger.info(f"Added {len(rag_context.get('relevant_documents', []))} relevant documents")
        
        logger.info(f"Input processed: Type={processed_input['query_type']}")
        return processed_input
    
    def _classify_query(self, query: str) -> str:
        """
        Classify the type of query.
        
        Args:
            query: User query string
            
        Returns:
            Query type classification
        """
        query_lower = query.lower()
        
        if "bbc" in query_lower or "headlines" in query_lower or "news" in query_lower:
            return "news_fetching"
        elif "sum" in query_lower or "add" in query_lower:
            return "mathematical"
        elif "draw" in query_lower or "show" in query_lower or "display" in query_lower:
            return "visual"
        elif "find" in query_lower or "calculate" in query_lower:
            return "computation"
        elif "ascii" in query_lower or "exponential" in query_lower:
            return "data_processing"
        else:
            return "general"
    
    def _extract_concepts(self, query: str) -> List[str]:
        """
        Extract key concepts from the query.
        
        Args:
            query: User query string
            
        Returns:
            List of key concepts
        """
        concepts = []
        query_lower = query.lower()
        
        # Extract common concepts
        concept_keywords = ["ascii", "exponential", "sum", "india", "values", "characters", 
                           "bbc", "headlines", "news", "browser", "paint", "draw"]
        
        for keyword in concept_keywords:
            if keyword in query_lower:
                concepts.append(keyword)
        
        return concepts
    
    def _requires_visualization(self, query: str) -> bool:
        """
        Determine if the query requires visual output.
        
        Args:
            query: User query string
            
        Returns:
            True if visualization is needed, False otherwise
        """
        query_lower = query.lower()
        visualization_keywords = ["draw", "show", "display", "graph", "window", "paint", "turtle", "browser"]
        
        return any(keyword in query_lower for keyword in visualization_keywords)
    
    async def analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the current context and state.
        
        Args:
            context: Current context information
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info("Analyzing context")
        
        analysis = {
            "iteration_count": context.get("iteration", 0),
            "max_iterations": context.get("max_iterations", 3),
            "has_results": context.get("last_response") is not None,
            "is_final": False,
            "next_action_suggested": "continue"
        }
        
        if analysis["iteration_count"] >= analysis["max_iterations"]:
            analysis["is_final"] = True
            analysis["next_action_suggested"] = "finalize"
        
        logger.info(f"Context analysis: {analysis}")
        return analysis
