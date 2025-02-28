import streamlit as st
from workflow.research_graph import ResearchWorkflow

def main():
    st.title("Research Workflow Query")
    
    query = st.text_input("Enter your query:", "What is the latest news on COVID-19 vaccines?")
    
    # Inject custom CSS for the disabled button
    st.markdown("""
        <style>
        .stButton button:disabled {
            background-color: #d3d3d3;
            color: #ffffff;
            cursor: not-allowed;
            pointer-events: none;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if 'button_disabled' not in st.session_state:
        st.session_state.button_disabled = False
    
    if st.button("Run Query", disabled=st.session_state.button_disabled):
        st.session_state.button_disabled = True
        workflow = ResearchWorkflow()
        try:
            with st.spinner('Generating response...'):
                response = workflow.run(query)
            st.subheader("Final Response:")
            st.write(response)
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            st.session_state.button_disabled = False

if __name__ == "__main__":
    main()
