from workflow.research_graph import ResearchWorkflow

def main():
    workflow = ResearchWorkflow()
    query = "Waht is the latest news on covid-19 vaccines?"
    try:
        response = workflow.run(query)
        print("Final Response:")
        print(response)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()