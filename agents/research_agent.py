from tavily import TavilyClient
from langchain.schema import Document
from utils.document_processor import DocumentProcessor
from config import config

class ResearchAgent:
    """Agent responsible for crawling websites and collecting research data."""
    
    def __init__(self):
        self.tavily = TavilyClient(api_key=config.TAVILY_API_KEY)
        self.processor = DocumentProcessor()

    def search(self, query: str) -> list[Document]:
        """Search the web using Tavily and process results into documents."""
        try:
            results = self.tavily.search(query=query, max_results=10)
            documents = [
                Document(
                    page_content=result["content"],
                    metadata={"url": result["url"], "title": result["title"]}
                )
                for result in results["results"]
            ]
            return self.processor.process_documents(documents)
        except Exception as e:
            raise Exception(f"Research Agent failed to fetch data: {str(e)}")