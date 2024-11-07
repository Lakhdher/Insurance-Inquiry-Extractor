from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, tool, PDFSearchTool
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, LLM
from crewai import Agent, Task, Crew
import streamlit as st
from crewai_tools import tool
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

search_tool = SerperDevTool()

my_llm = LLM(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini/gemini-1.5-pro-latest",
)

st.title("Yacht Insurance Inquiry Processor")
st.write("Upload an email and optional document for insurance inquiry data extraction.")
# Input for email content
email_content = st.text_area(
    "Email Content", placeholder="Paste the insurance inquiry email content here..."
)


@tool("Ask Human to provide the email to be extracted")
def ask_human(question: str) -> str:
    """Ask human to provide the email to be extracted"""
    return email_content


extractor = Agent(
    role="Insurance Inquiry Extractor",
    goal="Extract structured data from yacht insurance inquiry emails.",
    backstory="""You specialize in analyzing customer emails for yacht insurance and identifying key data points.
    Your role is to parse out all relevant details for insurance quoting purposes.""",
    verbose=True,
    allow_delegation=True,
    tools=[ask_human],
    llm=my_llm,
)

researcher = Agent(
    role="Insurance Inquiry Internet Researcher",
    goal="Research missing yacht characteristic from internet in order to fill in the None values in the table.",
    backstory="""You are tasked with conducting additional research to provide context and insights for yacht insurance inquiries.
Your role is to gather relevant information about Characteristics marked as none at the table from the internet.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=my_llm,
)

task1 = Task(
    description="""Extract all necessary yacht insurance data from the email. 
    If there's no info, and there was a mention about pdf attachment, mark everything as missing, and pass.
    If a field is missing, mark it as Missing. 
    Do not mark a field using implicit data, if a field is incomplete or incertain, mention it, 
    if a there was no mention about previous claims or current insurance coverage or experience, mark it as None.""",
    expected_output="""{
| Data Point                   | Value                                           |
|------------------------------|-------------------------------------------------|
| Yacht Model                  | [yacht_model]                                   |
| Yacht Length                 | [yacht_length]                                  |
| Year of Manufacture          | [year_of_manufacture]                           |
| Current Value/Purchase Price | [purchase_price]                                |
| Current Location             | [current_location]                              |
| Intended Cruising Area       | [intended_cruising_area]                        |
| Owner's Name                 | [owner_name]                                    |
| Owner's Contact Information  | [contact_information]                           |
| Owner's Boating Experience   | [boating_experience]                            |
| Previous Insurance Claims    | [insurance_claims]                              |
| Additional Equipment         | [additional_equipment]                          |
| Current Insurance Coverage   | [current_coverage]                              |
| Other                        | [other_information]                             |
}""",
    agent=extractor,
)

task3 = Task(
    description="Research missing yacht characteristics from the internet.",
    expected_output="""
| Data Point                   | Value                                           |
|------------------------------|-------------------------------------------------|
| Yacht Model                  | [yacht_model]                                   |
| Yacht Length                 | [yacht_length]                                  |
| Year of Manufacture          | [year_of_manufacture]                           |
| Current Value/Purchase Price | [purchase_price]                                |
| Current Location             | [current_location]                              |
| Intended Cruising Area       | [intended_cruising_area]                        |
| Owner's Name                 | [owner_name]                                    |
| Owner's Contact Information  | [contact_information]                           |
| Owner's Boating Experience   | [boating_experience]                            |
| Previous Insurance Claims    | [insurance_claims]                              |
| Additional Equipment         | [additional_equipment]                          |
| Current Insurance Coverage   | [current_coverage]                              |
| Other                        | [other_information]                             |
""",
    agent=researcher,
)


# Upload field for documents
uploaded_document = st.file_uploader("Upload Additional Document (PDF)", type="pdf")
if uploaded_document:
    # save it to the folder ./data
    with open(f"./data/{uploaded_document.name}", "wb") as f:
        f.write(uploaded_document.getbuffer())
    with st.spinner("Extracting text from PDF..."):
        pdf_tool = PDFSearchTool(
            config=dict(
                llm=dict(
                    provider="google",  # or google, openai, anthropic, llama2, ...
                    config=dict(
                        model="gemini/gemini-1.5-pro",
                        api_key=os.getenv("GOOGLE_API_KEY"),
                    ),
                ),
                embedder=dict(
                    provider="huggingface",  # or openai, ollama, ...
                    config=dict(model="BAAI/bge-m3"),
                ),
            ),
            pdf=f"./data/{uploaded_document.name}",
        )
    st.write(f"Document uploaded and embedded successfully: {uploaded_document.name}")

    parser = Agent(
        role="Insurance Inquiry Doc Parser",
        goal="Research yacht characteristic from the document in order to fill in the None values in the table.",
        backstory="""You are tasked with conducting additional research to provide context and insights for yacht insurance inquiries.
    Your role is to gather relevant information about Characteristics marked as Missing at the table from the pdf document.""",
        verbose=True,
        allow_delegation=True,
        tools=[pdf_tool],
        llm=my_llm,
    )

    task2 = Task(
        description="""Parse the PDF document to extract all the yacht characteristics : for each point in the table, ask a question,
        and search in the pdf if still unavailable, mark it as Missing.""",
        expected_output="""
| Data Point                   | Value                                           |
|------------------------------|-------------------------------------------------|
| Yacht Model                  | [yacht_model]                                   |
| Yacht Length                 | [yacht_length]                                  |
| Year of Manufacture          | [year_of_manufacture]                           |
| Current Value/Purchase Price | [purchase_price]                                |
| Current Location             | [current_location]                              |
| Intended Cruising Area       | [intended_cruising_area]                        |
| Owner's Name                 | [owner_name]                                    |
| Owner's Contact Information  | [contact_information]                           |
| Owner's Boating Experience   | [boating_experience]                            |
| Previous Insurance Claims    | [insurance_claims]                              |
| Additional Equipment         | [additional_equipment]                          |
| Current Insurance Coverage   | [current_coverage]                              |
| Other                        | [other_information]                             |
    """,
        agent=parser,
    )

    crew = Crew(
        agents=[extractor, researcher, parser],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential,
    )
    st.write("Crew with document")

else:
    crew = Crew(
        agents=[extractor, researcher],
        tasks=[task1, task3],
        verbose=True,
        process=Process.sequential,
    )
    st.write("Crew without document")


if st.button("Start Crew"):
    with st.spinner("Crew is working on the task..."):
        results = crew.kickoff()
    st.write("Crew has finished the task!")
    st.write("Extracted Data:")
    st.write(results)
