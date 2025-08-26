import streamlit as st

def add_custom_favicon():
    """Add a custom brain emoji favicon to the Streamlit app"""
    st.markdown("""
        <style>
        .favicon {
            display: none;
        }
        </style>
        <link rel="shortcut icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧠</text></svg>">
    """, unsafe_allow_html=True)

def add_custom_css():
    """Add custom CSS for better styling"""
    st.markdown("""
        <style>
        /* Hide Streamlit branding */
        .css-1dp5vir {
            background-image: none;
        }
        
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Header styling */
        .main-header {
            font-family: 'Segoe UI', sans-serif;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Button animations */
        .stButton > button {
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Text area styling */
        .stTextArea textarea {
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            font-size: 1rem;
        }
        
        .stTextArea textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Progress bar */
        .stProgress .st-bo {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Enhanced text formatting */
        .main .block-container p {
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        
        /* Bold text styling */
        .main .block-container strong {
            color: #2c3e50;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Italic text styling */
        .main .block-container em {
            color: #e74c3c;
            font-style: italic;
            text-shadow: 0 1px 2px rgba(231, 76, 60, 0.1);
        }
        
        /* Code styling */
        .main .block-container code {
            background: #f8f9fa;
            color: #e83e8c;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            border: 1px solid #dee2e6;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Response container styling */
        .main .block-container .stMarkdown {
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #f0f0f0;
        }
        
        /* Response content specific styling */
        .response-content {
            background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.08);
            animation: fadeInResponse 0.6s ease-in;
        }
        
        @keyframes fadeInResponse {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Source items styling */
        .source-item {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.75rem;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }
        
        .source-item:hover {
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }
        
        .source-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .source-url a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .source-url a:hover {
            text-decoration: underline;
        }
        
        .source-snippet {
            color: #6c757d;
            font-style: italic;
            margin-top: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
