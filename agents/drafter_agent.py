import google.generativeai as genai
from langchain.schema import Document
from config import config
import time
import logging
from typing import List
from utils.fallback_generator import FallbackGenerator

logger = logging.getLogger(__name__)

class DrafterAgent:
    """Agent responsible for drafting and refining responses using Gemini API."""
    
    def __init__(self):
        genai.configure(api_key=config.GOOGLE_STUDIO_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")  # Use stable version
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Minimum 2 seconds between requests
        self.max_retries = 3
        self.fallback_generator = FallbackGenerator()
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=800,
            top_p=0.8,
            top_k=40
        )

    def _rate_limit(self):
        """Ensure we don't exceed rate limits by waiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.info(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _make_api_request(self, prompt: str) -> str:
        """Make API request with retry logic and rate limiting."""
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                logger.info(f"Making API request (attempt {attempt + 1}/{self.max_retries})")
                
                response = self.model.generate_content(
                    prompt, 
                    generation_config=self.generation_config
                )
                
                if response and response.text:
                    return response.text
                else:
                    logger.warning("Empty response from API")
                    return "Sorry, I received an empty response from the AI service."
                    
            except Exception as e:
                error_str = str(e)
                logger.error(f"API request failed (attempt {attempt + 1}): {error_str}")
                
                # Handle specific rate limit errors
                if "429" in error_str or "RATE_LIMIT_EXCEEDED" in error_str:
                    if attempt < self.max_retries - 1:
                        wait_time = (attempt + 1) * 10  # Exponential backoff: 10, 20, 30 seconds
                        logger.info(f"Rate limit exceeded. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return self._create_fallback_response("Rate limit exceeded. Please try again later.")
                
                # Handle quota exceeded errors
                elif "quota" in error_str.lower() or "GenerateContent request limit" in error_str:
                    logger.warning("API quota exceeded, using fallback generator")
                    # Use fallback generator for the research data if available
                    if hasattr(self, '_current_research_data') and self._current_research_data:
                        return self.fallback_generator.generate_response(
                            self._current_query, 
                            self._current_research_data
                        )
                    else:
                        return self._create_fallback_response(
                            "API quota exceeded. Please check your Google Cloud Console settings or try again later."
                        )
                
                # Handle other API errors
                elif attempt == self.max_retries - 1:
                    return self._create_fallback_response(f"API service unavailable: {error_str}")
                else:
                    time.sleep(2)  # Wait 2 seconds before retry
        
        return self._create_fallback_response("Unable to generate response after multiple attempts.")

    def _create_fallback_response(self, error_message: str) -> str:
        """Create a fallback response when API fails."""
        return f"""
            I apologize, but I'm currently unable to generate a response due to API limitations.

            Error: {error_message}

            Please try:
            1. Waiting a few minutes and trying again
            2. Checking your Google Cloud Console for API quotas
            3. Ensuring billing is enabled for your project

            For immediate assistance, you can search for your query manually using the research data that was collected.
            """

    def draft_response(self, query: str, research_data: List[Document]) -> str:
        """Generate an initial draft response based on research data."""
        if not research_data:
            return "I apologize, but I couldn't find relevant information to answer your question."
        
        # Store data for fallback use
        self._current_query = query
        self._current_research_data = research_data
        
        # Limit context to avoid token limits and improve relevance
        top_docs = research_data[:5]  # Use only top 5 documents
        context = ""
        source_urls = []
        
        for i, doc in enumerate(top_docs, 1):
            content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            url = doc.metadata.get('url', 'URL not available')
            source_urls.append(url)
            context += f"\nSource {i}: {content}\nURL: {url}\n"
        
        prompt = f"""Based on the research data below, provide a clear and comprehensive answer to this question: "{query}"

IMPORTANT INSTRUCTIONS:
- Write a well-structured response with key facts and insights
- Keep it informative but concise
- DO NOT include a "Sources:" section in your response
- DO NOT mention URLs or links in your answer
- DO NOT use placeholder text like "[Insert best source...]" 
- Focus ONLY on the content and findings
- The sources will be displayed separately

Research Data with URLs:
{context}

Question: {query}

        Please provide ONLY your analysis and findings (NO sources section):"""
        
        return self._make_api_request(prompt)

    def get_sources_from_research_data(self, research_data: List[Document]) -> List[dict]:
        """Extract source information from research data."""
        sources = []
        for i, doc in enumerate(research_data[:5], 1):
            url = doc.metadata.get('url', 'URL not available')
            title = doc.metadata.get('title', f'Source {i}')
            sources.append({
                'number': i,
                'title': title,
                'url': url,
                'snippet': doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
            })
        return sources

    def refine_response(self, draft: str) -> str:
        """Refine the draft for clarity and brevity."""
        # Skip refinement if draft is already a fallback message
        if "I apologize, but I'm currently unable" in draft or "API quota exceeded" in draft:
            return draft
            
        prompt = f"""Please refine the following response to make it:
1. More concise and clear
2. Better structured with proper paragraphs
3. Maintain factual accuracy
4. DO NOT add any "Sources:" section or URLs
5. Focus only on improving the content and readability

Draft to refine:
{draft}

Refined response (content only, no sources):"""
        
        return self._make_api_request(prompt)