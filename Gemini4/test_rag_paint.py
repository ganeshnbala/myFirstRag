"""
Test script to demonstrate RAG functionality with Paint-related queries.
"""

import os
from dotenv import load_dotenv
import logging
import asyncio

from Perception import Perception

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


async def test_rag_with_paint_query():
    """Test RAG with a Paint-related query."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found")
        return
    
    # Initialize Perception with RAG
    perception = Perception(api_key)
    
    # Test queries
    test_queries = [
        "How do I open Paint application?",
        "Can you help me draw a rectangle in Paint?",
        "I want to add text to Paint. How do I do that?",
        "What's the workflow for using Paint to draw something?",
        "Find the ASCII values of characters in INDIA and then return sum of exponentials of those values."
    ]
    
    print("\n" + "="*70)
    print("RAG TEST WITH PAINT QUERIES")
    print("="*70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {query}")
        print(f"{'='*70}")
        
        # Process query through Perception with RAG
        result = await perception.process_user_input(query)
        
        # Display results
        print(f"\nQuery Type: {result.get('query_type')}")
        print(f"Requires Visualization: {result.get('requires_visualization')}")
        
        # Show RAG context if available
        if "rag_context" in result and result["rag_context"]:
            print(f"\n{'='*70}")
            print("RAG ENHANCED CONTEXT:")
            print(f"{'='*70}")
            print(result["rag_context"])
        
        # Show RAG recommendations if available
        if "rag_recommendations" in result and result["rag_recommendations"]:
            print(f"\nRecommended Functions: {', '.join(result['rag_recommendations'])}")
        
        print()


async def main():
    """Main test function."""
    try:
        await test_rag_with_paint_query()
    except Exception as e:
        logger.error(f"Error in test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

