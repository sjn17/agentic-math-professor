import os
from dotenv import load_dotenv
from datasets import load_dataset

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

def create_and_populate_db():
    """
    Downloads the ASDiv dataset, processes it, and incrementally adds it to ChromaDB.
    """
    # --- 1. Load the Dataset from Hugging Face ---
    print("Loading ASDiv dataset from Hugging Face...")
    # We'll use the 'train' split of the dataset
    dataset = load_dataset("EleutherAI/asdiv", split="validation")
    print(f"Loaded {len(dataset)} examples from the dataset.")

    # --- 2. Initialize Embeddings Model and ChromaDB Client ---
    print("Initializing embeddings model and ChromaDB client...")
    load_dotenv()
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    persist_directory = 'chroma_db'
    
    # This connects to an existing DB or creates a new one if it doesn't exist
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    print("ChromaDB client initialized.")

    # --- 3. Preprocess and Add Data Incrementally ---
    print("Processing and adding documents to ChromaDB...")
    documents_to_add = []
    for item in dataset:
        # For better retrieval, we combine the question and the formula (solution steps)
        # into the main text that gets embedded.
        combined_text = f"Question: {item['body']}\nSolution Steps: {item['formula']}"
        
        # We store the final numerical answer and the source in the metadata.
        metadata = {
            "solution": str(item.get('answer', 'N/A')),
            "source": f"ASDiv - {item.get('grade', 'N/A')}"
        }
        
        doc = Document(page_content=combined_text, metadata=metadata)
        documents_to_add.append(doc)

    # Add the documents in batches to be efficient
    if documents_to_add:
        vector_store.add_documents(documents_to_add)
        print(f"✅ Successfully added {len(documents_to_add)} documents to the knowledge base.")

if __name__ == "__main__":
    create_and_populate_db()