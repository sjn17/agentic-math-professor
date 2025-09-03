# agentic-math-professor
An Agentic-RAG system that acts as a math tutor

## Phase 1: Knowledge Base Creation

This project uses a local vector database to store mathematical questions and answers for quick retrieval.

-   **Database**: ChromaDB is used for local storage, requiring no Docker or server setup.
-   **Embeddings**: Google's `embedding-001` model (via Gemini) is used to convert the text into numerical vectors.
-   **Execution**: The knowledge base is created by running the `load_data.py` script located in the `backend` folder.

## Phase 2: Self-Correcting RAG Agent

[cite_start]To ensure a robust and reliable routing pipeline[cite: 6], the initial simple router was upgraded to a more sophisticated **Self-Correcting / Adaptive RAG** agent. This agent doesn't try to guess the best tool upfront. Instead, it retrieves information first and then grades the result to make a more informed decision.

### Agent Workflow

The agent follows a multi-step, conditional workflow managed by LangGraph:

1.  **Retrieve**: The agent always starts by retrieving the most relevant document from the local **ChromaDB** knowledge base using vector similarity search. This step also fetches the similarity score of the document.

2.  **Grade**: A deterministic `grade_documents_by_score` node checks the similarity score of the retrieved document against a preset threshold. This is a fast and reliable way to check for relevance without an extra LLM call.

3.  **Decide (Conditional Branching)**: Based on the score, a conditional edge routes the agent down one of two paths:
    * **If the score is below the threshold (good match)**: The document is considered relevant, and the agent proceeds directly to the `generate` node.
    * **If the score is above the threshold (poor match)**: The document is considered not relevant, and the agent self-corrects by proceeding to the `web_search` node.

4.  **Web Search (If Needed)**: If triggered, this node uses the **Tavily** API to search the web for relevant information.

5.  **Generate**: Both paths converge at the `generate` node. Using the context gathered from either the knowledge base or the web search, the **Gemini 1.5 Flash** model generates the final, step-by-step mathematical explanation.

This self-correcting pattern ensures that the agent always uses its local, curated knowledge base when possible but reliably falls back to a web search when necessary, fulfilling the core logic of the assignment.