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
        </style>
    """, unsafe_allow_html=True)
