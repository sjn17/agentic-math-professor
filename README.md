# agentic-math-professor
An Agentic-RAG system that acts as a math tutor

## Phase 1: Knowledge Base Creation

This project uses a local vector database to store mathematical questions and answers for quick retrieval.

-   **Database**: ChromaDB is used for local storage, requiring no Docker or server setup.
-   **Embeddings**: Google's `embedding-001` model (via Gemini) is used to convert the text into numerical vectors.
-   **Execution**: The knowledge base is created by running the `load_data.py` script located in the `backend` folder.
