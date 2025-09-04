from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

def query_db(query):
    """
    Queries the ChromaDB and prints the results.
    """
    print("Initializing DB and embeddings...")
    load_dotenv()
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    persist_directory = 'chroma_db'

    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    print(f"\n--- Querying for: '{query}' ---")
    results = vector_store.similarity_search_with_score(query, k=3)

    if not results:
        print("No results found.")
        return

    print(f"Found {len(results)} results:\n")
    for i, (doc, score) in enumerate(results):
        print(f"--- Result {i+1} (Score: {score:.4f}) ---")
        print(f"Content: {doc.page_content}")
        print(f"Metadata: {doc.metadata}\n")

if __name__ == "__main__":
    # Example query based on the content of the ASDiv dataset
    sample_query = "If a maîtresse has 8 students and she gives each student 3 pencils, how many pencils will she give in total?"
    query_db(sample_query)