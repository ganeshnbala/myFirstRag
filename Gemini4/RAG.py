"""
RAG (Retrieval-Augmented Generation) Module
Handles document retrieval and context enhancement using vector embeddings.
"""

import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class RAG:
    """
    RAG system for document retrieval and context enhancement.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the RAG module.
        
        Args:
            api_key: Gemini API key for embeddings
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.embedding_model = "models/embedding-001"  # Google's embedding model
        
        # Document store - storing Paint-related documents
        self.documents = []
        self.document_embeddings = []
        
        # Initialize with Paint documentation
        self._initialize_paint_docs()
        
        # Initialize with BBC headlines documentation
        self._initialize_bbc_docs()
        
        logger.info("RAG module initialized")
    
    def _initialize_paint_docs(self):
        """
        Initialize the document store with Paint-related instructions.
        """
        paint_documents = [
            {
                "title": "Opening Paint",
                "content": "To open Microsoft Paint application, use the open_paint_maximized function. This will open Paint in a maximized window. You must wait for Paint to fully load before attempting to draw or add text.",
                "category": "paint_basics",
                "keywords": ["open", "paint", "maximize", "window", "start"]
            },
            {
                "title": "Drawing Rectangles in Paint",
                "content": "To draw a rectangle in Paint, first call open_paint_maximized. Then use draw_rectangle_paint function with coordinates (x1, y1, x2, y2). The rectangle tool is located at coordinates (180, 80) in the toolbar.",
                "category": "paint_drawing",
                "keywords": ["rectangle", "draw", "coordinates", "x1", "y1", "x2", "y2"]
            },
            {
                "title": "Adding Text in Paint",
                "content": "To add text in Paint, first ensure Paint is open using open_paint_maximized. Then use add_text_in_paint function with your desired text string. The text tool is located at coordinates (120, 70) in the toolbar.",
                "category": "paint_text",
                "keywords": ["text", "add", "type", "string", "insert"]
            },
            {
                "title": "Paint Workflow",
                "content": "Complete Paint workflow: 1) Call open_paint_maximized to open Paint, 2) Wait for Paint to load fully, 3) Call draw_rectangle_paint with coordinates, 4) Call add_text_in_paint with your text. Always ensure Paint is open before drawing or adding text.",
                "category": "paint_workflow",
                "keywords": ["workflow", "steps", "process", "sequence", "order"]
            },
            {
                "title": "Turtle Graphics Alternative",
                "content": "For more reliable drawing, use draw_rectangle_with_turtle function instead of Paint. This creates a Turtle graphics window with a rectangle and text. The window displays for 12 seconds and closes automatically. Parameters: width, height, text.",
                "category": "visualization_alternative",
                "keywords": ["turtle", "graphics", "alternative", "reliable", "display", "window"]
            },
            {
                "title": "Paint Coordinates",
                "content": "Paint uses screen coordinates. Rectangle tool at (180, 80), Text tool at (120, 70). Recommended rectangle coordinates: from (100, 100) to (500, 400). Text placement: (200, 150) for center. Screen dimensions vary, adjust accordingly.",
                "category": "paint_coordinates",
                "keywords": ["coordinates", "toolbar", "position", "click", "tool"]
            },
            {
                "title": "Paint Troubleshooting",
                "content": "If Paint operations fail: 1) Ensure open_paint_maximized was called first, 2) Wait longer for Paint to load (add delays), 3) Verify Paint window is active and focused, 4) Try Turtle graphics as alternative if Paint continues to fail.",
                "category": "paint_troubleshooting",
                "keywords": ["error", "troubleshoot", "fail", "fix", "problem", "delay"]
            }
        ]
        
        for doc in paint_documents:
            self.add_document(doc)
        
        logger.info(f"Initialized with {len(paint_documents)} Paint documents")
    
    def _initialize_bbc_docs(self):
        """
        Initialize the document store with BBC headlines instructions.
        """
        bbc_documents = [
            {
                "title": "Fetching BBC Headlines",
                "content": "To fetch BBC headlines, use the fetch_bbc_headlines function with num_headlines parameter (e.g., 10 for 10 headlines). This function fetches from BBC RSS feed and saves to bbc_headlines.txt file in the project directory.",
                "category": "bbc_basics",
                "keywords": ["fetch", "bbc", "headlines", "news", "rss", "text"]
            },
            {
                "title": "Displaying Headlines in Browser",
                "content": "To display BBC headlines in a web browser, first run fetch_bbc_headlines to get the headlines. Then use display_headlines_in_browser function. This creates a beautiful HTML page with gradient background, animations, and auto-closes after 10 seconds with a countdown timer.",
                "category": "bbc_display",
                "keywords": ["display", "browser", "html", "show", "visual", "beautiful", "auto-close"]
            },
            {
                "title": "Displaying Headlines in Paint",
                "content": "To display BBC headlines in Paint, first run fetch_bbc_headlines. Then use display_headlines_in_paint function. This creates a PNG image with the headlines text and opens it in Microsoft Paint. The Paint window is automatically maximized.",
                "category": "bbc_display",
                "keywords": ["paint", "display", "image", "png", "show", "maximize"]
            },
            {
                "title": "BBC Workflow",
                "content": "Complete BBC headlines workflow: 1) Call fetch_bbc_headlines with desired number (e.g., 10), 2) Wait for headlines to be saved, 3) Call display_headlines_in_browser for browser display OR display_headlines_in_paint for Paint display. Browser display is recommended with auto-close after 10 seconds.",
                "category": "bbc_workflow",
                "keywords": ["workflow", "steps", "process", "sequence", "order", "recommended"]
            },
            {
                "title": "BBC Text File Output",
                "content": "BBC headlines are saved to bbc_headlines.txt file with timestamp header and separator lines. The file contains numbered headlines in a clean text format. This file is automatically generated and can be used as reference or documentation.",
                "category": "bbc_output",
                "keywords": ["text", "file", "output", "save", "txt", "timestamp"]
            }
        ]
        
        for doc in bbc_documents:
            self.add_document(doc)
        
        logger.info(f"Initialized with {len(bbc_documents)} BBC documents")
    
    def add_document(self, document: Dict[str, Any]):
        """
        Add a document to the store.
        
        Args:
            document: Document dictionary with title, content, category, keywords
        """
        self.documents.append(document)
        # For simplicity, we'll use keyword-based retrieval
        # In production, you'd generate embeddings here
        self.document_embeddings.append(document)
    
    def retrieve_relevant_docs(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents based on query.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        query_lower = query.lower()
        
        # Score documents based on keyword matches
        scored_docs = []
        for doc in self.documents:
            score = 0
            keywords = doc.get("keywords", [])
            title = doc.get("title", "").lower()
            content = doc.get("content", "").lower()
            category = doc.get("category", "").lower()
            
            # Score based on keyword matches
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 2
            
            # Score based on title match
            if any(word in title for word in query_lower.split()):
                score += 3
            
            # Score based on content match
            if any(word in content for word in query_lower.split() if len(word) > 3):
                score += 1
            
            # Score based on category match
            if any(word in category for word in query_lower.split()):
                score += 2
            
            scored_docs.append((score, doc))
        
        # Sort by score and return top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        relevant_docs = [doc for score, doc in scored_docs if score > 0][:top_k]
        
        logger.info(f"Retrieved {len(relevant_docs)} relevant documents for query: {query[:50]}")
        return relevant_docs
    
    def enhance_context(self, query: str, max_docs: int = 3) -> Dict[str, Any]:
        """
        Enhance query context with retrieved documents.
        
        Args:
            query: User query
            max_docs: Maximum number of documents to include
            
        Returns:
            Dictionary with enhanced context
        """
        relevant_docs = self.retrieve_relevant_docs(query, top_k=max_docs)
        
        enhanced_context = {
            "original_query": query,
            "relevant_documents": relevant_docs,
            "context_summary": None
        }
        
        if relevant_docs:
            # Create a summary of the retrieved context
            context_parts = []
            for doc in relevant_docs:
                context_parts.append(f"**{doc['title']}**: {doc['content']}")
            
            enhanced_context["context_summary"] = "\n\n".join(context_parts)
            
            logger.info("Context enhanced with retrieved documents")
        else:
            logger.info("No relevant documents found for context enhancement")
        
        return enhanced_context
    
    def generate_rag_prompt(self, query: str) -> str:
        """
        Generate a prompt enhanced with retrieved context.
        
        Args:
            query: User query
            
        Returns:
            Enhanced prompt with RAG context
        """
        context_data = self.enhance_context(query)
        
        if context_data["relevant_documents"]:
            rag_context = f"\n\n=== RELEVANT INFORMATION FROM KNOWLEDGE BASE ===\n{context_data['context_summary']}\n\n"
        else:
            rag_context = ""
        
        enhanced_prompt = f"{query}{rag_context}"
        return enhanced_prompt
    
    def get_function_recommendations(self, query: str) -> List[str]:
        """
        Get recommended functions based on the query.
        
        Args:
            query: User query
            
        Returns:
            List of recommended function names
        """
        relevant_docs = self.retrieve_relevant_docs(query, top_k=3)
        recommendations = []
        
        # Extract function mentions from relevant documents
        for doc in relevant_docs:
            content = doc.get("content", "")
            # Look for function patterns
            functions = re.findall(r'(\w+_\w+|open_\w+|draw_\w+|add_\w+)', content)
            recommendations.extend(functions)
        
        # Remove duplicates
        recommendations = list(set(recommendations))
        
        logger.info(f"Generated {len(recommendations)} function recommendations")
        return recommendations

