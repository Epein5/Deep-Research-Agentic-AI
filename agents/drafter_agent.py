import google.generativeai as genai
from langchain.schema import Document
from config import config

class DrafterAgent:
    """Agent responsible for drafting and refining responses using Gemini API."""
    
    def __init__(self):
        genai.configure(api_key=config.GOOGLE_STUDIO_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def draft_response(self, query: str, research_data: list[Document]) -> str:
        """Generate an initial draft response based on research data."""
        context = "\n".join(
            f"{doc.page_content}\nSource URL: {doc.metadata.get('url', 'URL not available')}"
            for doc in research_data
        )
        prompt = f"Using the provided research data, generate clear answer to: '{query}'. Structure the response as a brief summary followed by list of source URLs from the data.\n\nResearch data: {context}"        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response else "Sorry, I couldn't generate a response."
        except Exception as e:
            raise Exception(f"Draft generation failed: {str(e)}")

    def refine_response(self, draft: str) -> str:
        """Refine the draft for clarity and brevity."""
        prompt = f"Refine this draft for clarity and brevity, keeping it concise (around 20-30 words). If URLs are present, include only the top 3 most relevant ones in the source list, prioritizing those best supporting the summary.\n\nDraft: {draft}"
        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response else "Sorry, I couldn't refine the response."
        except Exception as e:
            raise Exception(f"Refinement failed: {str(e)}")