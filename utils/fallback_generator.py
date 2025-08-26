"""
Fallback response generator for when API quotas are exceeded.
This provides basic text processing to create responses from research data.
"""

from langchain.schema import Document
from typing import List
import re
from collections import Counter

class FallbackGenerator:
    """Simple text-based response generator when AI APIs are unavailable."""
    
    def __init__(self):
        self.max_sources = 5
        self.max_content_length = 200
    
    def generate_response(self, query: str, research_data: List[Document]) -> str:
        """Generate a basic response from research data without AI."""
        if not research_data:
            return "No relevant information found for your query."
        
        # Extract key information
        sources = []
        combined_content = ""
        
        for doc in research_data[:self.max_sources]:
            # Get source info
            url = doc.metadata.get('url', 'URL not available')
            title = doc.metadata.get('title', 'Untitled')
            
            sources.append(f"- {title}: {url}")
            
            # Add content for analysis
            content = doc.page_content[:self.max_content_length]
            combined_content += f" {content}"
        
        # Find query-relevant sentences
        relevant_sentences = self._find_relevant_sentences(query, combined_content)
        
        # Create response
        response = f"""Based on the research data collected, here's what I found regarding "{query}":

{relevant_sentences}

**Sources:**
{chr(10).join(sources)}

*Note: This response was generated using fallback mode due to API limitations. For more detailed analysis, please try again later when API quotas are restored.*
"""
        
        return response
    
    def _find_relevant_sentences(self, query: str, content: str) -> str:
        """Extract sentences most relevant to the query."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Score sentences based on query word matches
        query_words = set(query.lower().split())
        scored_sentences = []
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            score = len(query_words.intersection(sentence_words))
            if score > 0:
                scored_sentences.append((score, sentence))
        
        # Sort by relevance and take top sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [sent[1] for sent in scored_sentences[:3]]
        
        if top_sentences:
            return ". ".join(top_sentences) + "."
        else:
            # If no relevant sentences found, return a summary
            return "The research data contains relevant information about your query, but automatic extraction is limited in fallback mode."
