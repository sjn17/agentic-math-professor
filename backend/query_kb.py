import random
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

def view_random_db_content():
    """
    Connects to ChromaDB and retrieves 5 random entries.
    """
    print("Initializing DB and embeddings...")
    load_dotenv()
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    persist_directory = 'chroma_db'
    
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    print("\n--- Retrieving entries to select 5 random ones ---")
    
    # The .get() method retrieves all entries from the database.
    results = vector_store.get() 
    
    documents = results.get('documents', [])
    metadatas = results.get('metadatas', [])

    if not documents:
        print("No documents found in the database.")
        return

    # Combine documents and metadatas into a single list to sample from
    all_entries = list(zip(documents, metadatas))

    sample_size = 5
    if len(all_entries) < sample_size:
        print(f"Database has fewer than {sample_size} entries. Showing all {len(all_entries)}.")
        random_entries = all_entries
    else:
        # Select 5 random entries from the list
        random_entries = random.sample(all_entries, sample_size)

    print(f"\nShowing {len(random_entries)} random entries from the database:\n")
    for i, (doc, meta) in enumerate(random_entries):
        print(f"--- Random Entry {i+1} ---")
        print(f"Content: {doc}")
        print(f"Metadata: {meta}\n")


if __name__ == "__main__":
    view_random_db_content()