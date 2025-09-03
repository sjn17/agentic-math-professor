import os
import json
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

def main():
    """
    Main function to load data, create embeddings, and store them in ChromaDB.
    """
    # Load environment variables from .env file
    load_dotenv()

    # --- 1. Load the data ---
    print("Loading math questions from data file...")
    with open('../data/math_questions.json', 'r') as f:
        math_data = json.load(f)
    print(f"Loaded {len(math_data)} questions.")

    # --- 2. Create LangChain Document objects ---
    # We need to convert our raw text into a format LangChain can use.
    documents = []
    for item in math_data:
        # The 'page_content' is the main text that will be embedded.
        page_content = f"Question: {item['question']}\nAnswer: {item['answer']}"
        # The metadata is extra information we can attach to the document.
        document = Document(page_content=page_content, metadata={"source": "local_kb"})
        documents.append(document)
    print("Created LangChain Document objects.")

    # --- 3. Initialize the Gemini Embedding Model ---
    # This model will convert our text documents into numerical vectors.
    print("Initializing Gemini embedding model...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    print("Embedding model initialized.")

    # --- 4. Create and persist the ChromaDB database ---
    # This is the core step. It takes our documents, uses the embedding model,
    # and saves the resulting vectors to a local directory.
    persist_directory = 'chroma_db'
    print(f"Creating and persisting the vector database in '{persist_directory}'...")
    
    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print("✅ Knowledge base created and loaded into ChromaDB successfully!")

if __name__ == "__main__":
    main()