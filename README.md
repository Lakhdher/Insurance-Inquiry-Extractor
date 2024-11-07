## Background Info

YachtSicher GmbH has approached Lucid Labs with a specific goal: they want to leverage generative AI to increase operational efficiency and enhance customer experience. We figured out that one interesting generative AI use case is about handling incoming insurance requests. It is common for YachtSicher GmbH that they get emails with a yacht model number, etc. (see the Email examples below). Their staff then have to go and search the details for the yacht manually and create a quote. As the AI Engineer, you've been tasked with developing a PoC / prototype that uses generative AI to help speed up the process.

## Objective

Create a Research Agent that can analyze incoming emails related to yacht insurance inquiries and extract relevant datapoints. The agent should be able to handle various levels of detail and uncertainty in the information provided.

## Workflow

### Task Initialization:
**Agent Setup**: Three agents are configured to extract and complete yacht insurance data from emails and supplementary documents:
- **Extractor**: Extracts primary data from email content.
- **Parser**: Extracts missing information from PDF attachments (if provided).
- **Researcher**: Performs internet searches for any missing yacht characteristics.

### Task Execution:

1. **Task 1 (Email Extraction)**: 
   - The **Extractor** agent identifies key data points within the email.
   - If any field is incomplete or unavailable, it is marked as "Missing" or "None."

2. **Task 2 (Document Parsing)**:
   - If a **PDF** document is uploaded, the **Parser** agent searches it to fill in missing fields.
   - Any remaining unavailable information is marked as "Missing."

3. **Task 3 (Online Research)**:
   - For fields marked "None" after email and document extraction, the **Researcher** agent searches online to provide additional details.

### Crew Execution:
- **Sequential Processing**: The tasks are executed in sequence by the **Crew**, which manages task flow and combines outputs from all agents to complete the extraction.

## Challenges

- **API Quota Limit**: 
   - The Gemini API’s quota may limit task frequency.

- **Latency in Attachment Processing**: 
   - Processing attachments introduces delays, especially for PDF searches.

## Next Steps

- **LLM Choice**: 
   - Study the trade-off between LLM usage, performance, and resources to choose wisely.

- **Manage Task Prompts**: 
   - Improve prompts to account for uncertain or incomplete data.
