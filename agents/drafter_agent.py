import google.generativeai as genai
from langchain.schema import Document
from config import config
import time
import logging
import os
from typing import List
from utils.fallback_generator import FallbackGenerator

# Import Azure OpenAI with fallback
try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None

logger = logging.getLogger(__name__)

class DrafterAgent:
    """Agent responsible for drafting and refining responses using Gemini API."""
    
    def __init__(self):
        genai.configure(api_key=config.GOOGLE_STUDIO_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")  # Use stable version
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Minimum 2 seconds between requests
        self.fallback_generator = FallbackGenerator()
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=600,  # Reduced from 800 to make responses shorter
            top_p=0.8,
            top_k=40
        )

        # Azure OpenAI fallback client (configured via env vars)
        self.azure_client = None
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-mini-2").strip()
        azure_key = os.getenv("AZURE_OPENAI_KEY", "").strip()
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview").strip()

        logger.info(f"Azure config - Deployment: {self.azure_deployment}, Endpoint: {azure_endpoint}")
        logger.info(f"Azure config - Key present: {bool(azure_key)}, OpenAI module: {bool(AzureOpenAI)}")

        if AzureOpenAI and azure_key and azure_endpoint and self.azure_deployment:
            try:
                self.azure_client = AzureOpenAI(
                    api_version=azure_api_version,
                    azure_endpoint=azure_endpoint,
                    api_key=azure_key,
                )
                logger.info("✅ Azure OpenAI fallback configured successfully")
            except Exception as e:
                logger.error(f"❌ Failed to configure Azure OpenAI fallback: {e}")
        else:
            missing = []
            if not AzureOpenAI: missing.append("openai module")
            if not azure_key: missing.append("AZURE_OPENAI_KEY")
            if not azure_endpoint: missing.append("AZURE_OPENAI_ENDPOINT") 
            if not self.azure_deployment: missing.append("AZURE_OPENAI_DEPLOYMENT")
            logger.warning(f"❌ Azure OpenAI fallback not configured - missing: {', '.join(missing)}")

    def _rate_limit(self):
        """Ensure we don't exceed rate limits by waiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.info(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _try_azure_openai(self, prompt: str) -> str:
        """Try Azure OpenAI as a fallback when Gemini fails."""
        if not self.azure_client:
            logger.warning("Azure OpenAI client not configured - cannot use fallback")
            return None
        
        try:
            logger.info("🔗 Attempting Azure OpenAI request...")
            logger.info(f"📋 Using deployment: {self.azure_deployment}")
            logger.info(f"🌐 Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT', '').strip()}")
            response = self.azure_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant. Provide clear, comprehensive answers based on the given information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=1000,  # Increased to prevent truncation
                model=self.azure_deployment
            )
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                finish_reason = response.choices[0].finish_reason
                
                logger.info(f"📄 Raw content: '{content}'")
                logger.info(f"📊 Content type: {type(content)}")
                logger.info(f"📏 Content length: {len(content) if content else 'None'}")
                logger.info(f"🏁 Finish reason: {finish_reason}")
                
                if finish_reason == 'length':
                    logger.warning("⚠️ Response was truncated due to token limit")
                
                if content and content.strip():  # Check for non-empty content
                    logger.info(f"✅ Azure OpenAI succeeded - generated {len(content)} characters")
                    return content
                else:
                    logger.error("❌ Azure OpenAI returned empty or None content")
                    logger.error(f"📋 Full response choices: {response.choices}")
                    if finish_reason == 'length':
                        logger.error("💡 Suggestion: Response was likely truncated - consider reducing prompt size or increasing max_completion_tokens")
                    return None
            else:
                logger.error("❌ Azure OpenAI returned empty response structure")
                logger.error(f"📋 Response: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Azure OpenAI failed with error: {type(e).__name__}: {str(e)}")
            return None

    def _make_api_request(self, prompt: str) -> str:
        """Make API request: try Azure OpenAI first since Gemini has 0 quota."""
        
        # Try Azure OpenAI first (since Gemini quota is 0)
        logger.info("🚀 Trying Azure OpenAI first...")
        azure_response = self._try_azure_openai(prompt)
        if azure_response:
            logger.info("✅ Azure OpenAI successful")
            return azure_response
        else:
            logger.warning("❌ Azure OpenAI failed or returned None")
        
        # Fallback to Gemini (will likely fail due to quota)
        try:
            self._rate_limit()
            logger.info("🔄 Azure failed, trying Gemini API as fallback...")
            
            response = self.model.generate_content(
                prompt, 
                generation_config=self.generation_config
            )
            
            if response and response.text:
                logger.info("✅ Gemini API successful")
                return response.text
            else:
                logger.warning("Gemini returned empty response")
                
        except Exception as e:
            error_str = str(e)
            logger.error(f"Gemini API failed: {error_str}")
        
        # Both services failed - return user-friendly message
        logger.error("❌ Both Azure OpenAI and Gemini failed")
        return self._create_server_busy_response()

    def _create_server_busy_response(self) -> str:
        """Create a user-friendly response when both AI services are unavailable."""
        return ("🤖 **Server Busy**\n\n"
                "Our AI services are currently experiencing high demand. "
                "Please try again in a few moments. If the issue persists, "
                "it may be due to API quota limits or temporary service disruptions.")

    def _create_fallback_response(self, error_message: str) -> str:
        """Create a fallback response when API fails."""
        # Keep fallback minimal so UI can decide how to present it
        return f"AI model unavailable: {error_message}"

    def draft_response(self, query: str, research_data: List[Document]) -> str:
        """Generate an initial draft response based on research data."""
        if not research_data:
            return "I apologize, but I couldn't find relevant information to answer your question."
        
        # Store data for fallback use
        self._current_query = query
        self._current_research_data = research_data
        
        # Limit context to avoid token limits and improve relevance
        top_docs = research_data[:8]  # Reduced from 10 to save tokens
        context = ""
        source_urls = []
        
        for i, doc in enumerate(top_docs, 1):
            content = doc.page_content[:180] + "..." if len(doc.page_content) > 180 else doc.page_content  # Reduced from 250
            url = doc.metadata.get('url', 'URL not available')
            source_urls.append(url)
            context += f"\nSource {i}: {content}\nURL: {url}\n"
        
        prompt = f"""You are a research assistant providing comprehensive answers based on the latest available information.

Question: {query}

Based on the research data provided below, please provide a clear, well-structured answer that:

1. **Introduces the topic** with context and background
2. **Presents key findings** in a logical, easy-to-follow structure  
3. **Includes specific details** and evidence from the sources
4. **Draws conclusions** or implications where relevant
5. **Maintains objectivity** and cites supporting evidence

**Formatting Guidelines:**
- Use **bold** for key terms, important concepts, and main findings
- Use *italics* for emphasis and subtle highlighting
- Use `backticks` for technical terms, model names, and specific terminology
- Structure your response with clear paragraphs for readability
- Keep your response informative yet concise (150-250 words)

Research Data:
{context}

Please provide a comprehensive yet accessible answer with appropriate formatting:"""
        
        return self._make_api_request(prompt)

    def get_sources_from_research_data(self, research_data: List[Document]) -> List[dict]:
        """Extract source information from research data."""
        sources = []
        for i, doc in enumerate(research_data, 1):  # Show ALL sources, not just top 5
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
            
        prompt = f"""Please refine and improve this research response to make it more clear, comprehensive, and well-structured:

{draft}

Refinement guidelines:
- **Enhance clarity**: Make complex ideas easier to understand
- **Improve flow**: Ensure logical progression of information
- **Add structure**: Use paragraphs and transitions for better readability
- **Maintain accuracy**: Keep all factual information intact
- **Optimize length**: Aim for 150-250 words of high-quality content
- **Professional tone**: Write as a knowledgeable research assistant
- **Add formatting**: Use **bold** for key terms, *italics* for emphasis, and `code` for technical terms

Focus on making the response more engaging and accessible while preserving all key information and insights.

Refined response:"""
        
        return self._make_api_request(prompt)