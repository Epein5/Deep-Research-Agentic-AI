import streamlit as st
from workflow.research_graph import ResearchWorkflow
from favicon_helper import add_custom_favicon, add_custom_css
import time
from agents.drafter_agent import DrafterAgent
from agents.research_agent import ResearchAgent
from langchain.schema import Document
import os

def stream_research_response(query: str):
    """Generator function that yields response chunks as they're generated."""
    try:
        # Initialize agents
        research_agent = ResearchAgent()
        drafter_agent = DrafterAgent()

        # Step 1: Research
        yield "🔍 Searching for information...\n\n"
        research_data = research_agent.search(query)

        if not research_data:
            yield "❌ No relevant research data found. Please try rephrasing your query.\n"
            return

        yield f"✅ Found {len(research_data)} sources\n\n"

        # Step 2: Generate response with streaming
        # Removed generating message for cleaner output

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

        # Try to stream from Azure OpenAI first
        if hasattr(drafter_agent, 'azure_client') and drafter_agent.azure_client:
            try:
                # Removed writing message for cleaner output
                response = drafter_agent.azure_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a knowledgeable research assistant. Provide comprehensive, well-structured answers using paragraphs and clear organization. Be informative yet accessible. Use **bold** for key terms, *italics* for emphasis, and `code` for technical terms. Format naturally for readability."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_completion_tokens=800,  # Increased to prevent truncation
                    model=drafter_agent.azure_deployment,
                    stream=True  # Enable streaming
                )

                full_response = ""
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            content = delta.content
                            full_response += content
                            yield content

                # Store the response and sources for later use
                st.session_state.full_response = full_response
                st.session_state.sources = []
                for i, doc in enumerate(research_data, 1):
                    url = doc.metadata.get('url', 'URL not available')
                    title = doc.metadata.get('title', f'Source {i}')
                    st.session_state.sources.append({
                        'number': i,
                        'title': title,
                        'url': url,
                        'snippet': doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                    })

                # Removed completion message for cleaner output
                return

            except Exception as e:
                yield f"\n⚠️ Streaming failed ({str(e)}), falling back to regular generation...\n\n"

        # Fallback to regular generation
        try:
            response = drafter_agent._make_api_request(prompt)
            if response:
                st.session_state.full_response = response
                st.session_state.sources = []
                for i, doc in enumerate(research_data, 1):
                    url = doc.metadata.get('url', 'URL not available')
                    title = doc.metadata.get('title', f'Source {i}')
                    st.session_state.sources.append({
                        'number': i,
                        'title': title,
                        'url': url,
                        'snippet': doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                    })

                # Yield the response in chunks for visual effect
                words = response.split()
                for i in range(0, len(words), 10):
                    chunk = ' '.join(words[i:i+10])
                    yield chunk + ' '
                    time.sleep(0.1)  # Small delay for streaming effect

                # Removed completion message for cleaner output
            else:
                yield "\n❌ Failed to generate response. Please try again.\n"

        except Exception as e:
            yield f"\n❌ Error generating response: {str(e)}\n"

    except Exception as e:
        yield f"❌ An error occurred: {str(e)}\n"

def main():
    # Removed research_in_progress session state handling (was causing issues)
    
    # Page configuration
    st.set_page_config(
        
        page_title="Deep Research AI",
        page_icon="🧠",
        # Use wide layout to reduce unused side margins and give columns more width
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Add custom favicon and CSS
    add_custom_favicon()
    add_custom_css()
    
    # Enhanced, modern styling
    st.markdown("""
        <style>
        /* Remove default Streamlit padding */
        .main > div {
            padding-left: 0rem;
            padding-right: 0rem;
        }
        
        /* Main container */
        /* Expand usable width & trim side padding */
        .main .block-container {
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            max-width: 90%;
            animation: fadeIn 0.6s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .main-header {
            text-align: center;
            color: #1e293b;
            margin-bottom: 0.5rem;
            font-weight: 700;
            font-size: 1.8rem;
            letter-spacing: -0.02em;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .subtitle {
            text-align: center;
            color: #64748b;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            font-weight: 400;
            letter-spacing: 0.01em;
        }
        
        /* Enhanced button styling */
        .stButton > button {
            width: 100%;
            height: 42px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button:before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
            background: linear-gradient(135deg, #5855eb 0%, #7c3aed 100%);
        }
        
        .stButton > button:hover:before {
            left: 100%;
        }
        
        .stButton > button:disabled {
            background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
            color: #94a3b8;
            cursor: not-allowed;
            transform: none;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stButton > button:disabled:hover {
            transform: none;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* Enhanced text area styling */
        .stTextArea textarea {
            border-radius: 8px;
            border: 2px solid #e2e8f0;
            font-size: 0.85rem;
            padding: 0.8rem;
            transition: all 0.3s ease;
            background: #ffffff;
            color: #1e293b;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            height: 70px !important;
            min-height: 70px !important;
            max-height: 70px !important;
        }
        
        .stTextArea textarea:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            background: #ffffff;
            outline: none;
        }
        
        /* Search prompt label styling */
        .stTextArea label {
            color: #9ca3af !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.3rem !important;
        }
        
        .metric-box {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            border: none;
            color: white;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
            transition: transform 0.3s ease;
        }
        
        .metric-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
        }
        
        .metric-box h3 {
            color: white !important;
            font-size: 1.5rem;
            margin: 0;
            font-weight: 700;
        }
        .metric-box p {
            color: rgba(255, 255, 255, 0.95) !important;
            margin: 0.2rem 0 0 0;
            font-size: 0.8rem;
            font-weight: 500;
            letter-spacing: 0.02em;
        }
        .source-item {
            position: relative;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 60%, #e2e8f0 100%);
            padding: 0.8rem 0.8rem 0.9rem 0.8rem;
            margin: 0.6rem 0;
            border-radius: 8px;
            border: 1px solid rgba(99, 102, 241, 0.15);
            box-shadow: 0 2px 8px rgba(100, 116, 139, 0.1), 0 1px 3px rgba(100, 116, 139, 0.06);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            backdrop-filter: blur(8px);
        }
        
        .source-item::before {
            content: '';
            position: absolute;
            top: 0; left: 0; bottom: 0;
            width: 3px;
            background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
            border-top-left-radius: 6px;
            border-bottom-left-radius: 6px;
        }
        
        .source-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px -4px rgba(99, 102, 241, 0.25), 0 4px 8px rgba(99, 102, 241, 0.12);
            border-color: rgba(99, 102, 241, 0.3);
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 55%, #f1f5f9 100%);
        }
        
        .source-title {
            font-weight: 600;
            color: #1e293b;
            margin: 0 0 0.4rem 0;
            font-size: 0.85rem;
            line-height: 1.3;
        }
        
        .source-url {
            font-size: 0.7rem;
            letter-spacing: 0.02em;
            color: #6366f1;
            word-break: break-all;
            margin: 0 0 0.4rem 0;
            font-weight: 500;
        }
        
        .source-url a {
            color: #6366f1;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .source-url a:hover {
            color: #4f46e5;
            text-decoration: underline;
        }
        
        .source-snippet {
            font-size: 0.75rem;
            color: #475569;
            margin-top: 0.4rem;
            font-style: italic;
            line-height: 1.4;
        }
        /* Enhanced readable width for long answer text */
        .answer-body {
            max-width: 950px;
            line-height: 1.6;
            font-size: 0.85rem;
            color: #ffffff;
        }
        
        .answer-body p {
            text-align: left;
            margin-bottom: 1rem;
            color: #ffffff;
        }
        
        /* Enhanced GitHub corner link (relocated bottom-right for visibility) */
        .github-corner {
            position: fixed;
            bottom: 18px;
            right: 18px;
            z-index: 2147483647; /* ensure always on top */
            pointer-events: auto;
        }
        .github-corner a {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 46px;
            height: 46px;
            border-radius: 14px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            box-shadow: 0 6px 18px rgba(99, 102, 241, 0.55), 0 2px 6px rgba(0,0,0,0.25);
            transition: all 0.25s ease;
            border: 1px solid rgba(255,255,255,0.25);
        }
        .github-corner a:hover {
            transform: translateY(-4px) scale(1.07);
            box-shadow: 0 10px 28px rgba(99, 102, 241, 0.65), 0 4px 10px rgba(0,0,0,0.35);
        }
        .github-corner svg {
            width: 22px;
            height: 22px;
            fill: #ffffff;
        }
        @media (max-width: 780px) {
            .github-corner a { width:40px; height:40px; }
            .github-corner svg { width:18px; height:18px; }
            .github-corner { bottom:12px; right:12px; }
        }
        
        /* Additional spacing and text size optimizations */
        h3 {
            font-size: 1.1rem !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        .stMarkdown {
            margin-bottom: 0.5rem !important;
        }
        
        /* Remove extra spacing from columns */
        .element-container {
            margin-bottom: 0.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    # GitHub link (floating button)
    st.markdown(
        """
        <div class="github-corner">
            <a href="https://github.com/Epein5/Deep-Research-Agentic-AI" target="_blank" title="GitHub Repository">
                <svg viewBox="0 0 16 16" aria-hidden="true">
                    <path d="M8 0C3.58 0 0 3.73 0 8.337c0 3.687 2.292 6.807 5.47 7.907.4.077.547-.177.547-.395 0-.194-.007-.71-.01-1.395-2.226.502-2.695-1.095-2.695-1.095-.364-.95-.89-1.203-.89-1.203-.727-.512.055-.502.055-.502.803.058 1.225.845 1.225.845.715 1.253 1.874.891 2.33.681.072-.535.28-.892.508-1.097-1.777-.207-3.644-.915-3.644-4.073 0-.9.312-1.636.824-2.212-.083-.207-.357-1.04.078-2.167 0 0 .672-.22 2.2.844a7.28 7.28 0 0 1 2-.276 7.28 7.28 0 0 1 2 .276c1.527-1.064 2.198-.844 2.198-.844.436 1.127.162 1.96.08 2.167.513.576.823 1.312.823 2.212 0 3.167-1.87 3.863-3.653 4.066.288.253.543.755.543 1.523 0 1.098-.01 1.983-.01 2.253 0 .22.146.476.55.394C13.71 15.14 16 12.02 16 8.337 16 3.73 12.42 0 8 0Z"/>
                </svg>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<h1 class="main-header">🧠 Deep Research AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ask any question and get comprehensive answers with sources</p>', unsafe_allow_html=True)
    
    # Create main layout with sidebar for sources
    # Wider overall page + adjusted ratio gives both columns more breathing room
    # You can tweak the ratio below (e.g., [5,2] or [3,1]) depending on desired sidebar width
    main_col, spacing_col, sidebar_col = st.columns([2, 0.3, 2])
    
    with main_col:
        # Query input
        query = st.text_area(
            "What would you like to research?",
            value="What are the latest developments in artificial intelligence?",
            height=70,
            placeholder="Enter your research question here..."
        )
        
        # Search button
        search_button = st.button(
            "🔍 Start Research",
            type="primary",
        )
    
    # Handle search
    if search_button:
        if not query.strip():
            st.error("Please enter a research question.")
            return

        # Clear previous results
        if 'full_response' in st.session_state:
            del st.session_state.full_response
        if 'sources' in st.session_state:
            del st.session_state.sources

        with main_col:
            # Create containers for streaming output
            progress_container = st.empty()
            response_container = st.empty()
            sources_container = st.empty()

            try:
                # Start streaming
                full_response = ""
                response_container.markdown("### � Research Results")

                for chunk in stream_research_response(query):
                    full_response += chunk
                    # Update the response container with current content
                    response_container.markdown(f"### 📋 Research Results\n\n{full_response}")

                # Display sources if available
                if 'sources' in st.session_state and st.session_state.sources:
                    with sidebar_col:
                        st.markdown(f"### 🔗 Sources ({len(st.session_state.sources)} found)")
                        for source in st.session_state.sources:
                            st.markdown(f"""
                            <div class="source-item">
                                <div class="source-title">{source['title']}</div>
                                <div class="source-url">
                                    <a href="{source['url']}" target="_blank">🔗 {source['url']}</a>
                                </div>
                                <div class="source-snippet">"{source['snippet']}"</div>
                            </div>
                            """, unsafe_allow_html=True)

                # Clear progress container
                progress_container.empty()

            except Exception as e:
                progress_container.empty()
                st.error(f"An unexpected error occurred: {str(e)}")
    
    # Simple footer
    with main_col:
        st.markdown("---")
        st.markdown("*Powered by Tavily Search, Azure OpenAI & Google Gemini AI*", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
