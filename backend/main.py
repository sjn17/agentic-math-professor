import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import TypedDict, List, Tuple
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults

# --- 1. Load Environment Variables and Initialize Models ---
load_dotenv()

app = FastAPI(
    title="Math Professor Agent API",
    description="An API for a self-correcting RAG agent."
)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


# --- 2. Define Agent State ---
class GraphState(TypedDict):
    question: str
    context: str
    documents: List[Tuple[Document, float]] # NEW: Now stores documents AND their similarity scores
    generation: str
    route_decision: str


# --- 3. Initialize Tools ---
persist_directory = 'chroma_db'
vector_store = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)
web_search_tool = TavilySearchResults(k=3)


# --- 4. Define the Nodes and Decision Logic ---

def retrieve_documents(state):
    print("---NODE: RETRIEVING DOCUMENTS WITH SCORES---")
    question = state["question"]
    # NEW: Use similarity_search_with_score to get documents and their scores
    documents_with_scores = vector_store.similarity_search_with_score(question, k=1)
    return {"documents": documents_with_scores, "question": question}

def grade_documents_by_score(state):
    print("---NODE: GRADING DOCUMENTS BY SIMILARITY SCORE---")
    question = state["question"]
    documents_with_scores = state["documents"]
    
    if not documents_with_scores:
        print("---GRADING: NO DOCUMENTS FOUND, ROUTING TO WEB SEARCH---")
        return {"route_decision": "web_search"}

    # The score from Chroma is a distance metric; lower is better.
    # We set a threshold. If the score is above this, we consider it "not relevant".
    score_threshold = 0.5 
    
    score = documents_with_scores[0][1]
    
    if score < score_threshold:
        print(f"---GRADING: SCORE ({score}) IS BELOW THRESHOLD. DOCUMENTS ARE RELEVANT.---")
        # Extract just the documents to create the context
        documents = [doc for doc, score in documents_with_scores]
        context = "\n".join([doc.page_content for doc in documents])
        return {"context": context, "route_decision": "generate"}
    else:
        print(f"---GRADING: SCORE ({score}) IS ABOVE THRESHOLD. DOCUMENTS NOT RELEVANT. ROUTING TO WEB SEARCH.---")
        return {"route_decision": "web_search"}

def web_search(state):
    print("---NODE: WEB SEARCH---")
    question = state["question"]
    web_results = web_search_tool.invoke({"query": question})
    context = "\n".join([d["content"] for d in web_results])
    return {"context": context}

def generate_answer(state):
    print("---NODE: GENERATING ANSWER---")
    question = state['question']
    context = state['context']
    
    template = "You are a helpful math professor. Your goal is to provide a clear, step-by-step solution to the user's question based on the context provided.\n\nCONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"
    prompt = PromptTemplate.from_template(template)
    rag_prompt = prompt.format(context=context, question=question)
    generation = llm.invoke(rag_prompt)
    
    return {"generation": generation.content}

def decide_next_node(state):
    return state["route_decision"]


# --- 5. Build the Graph ---
workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("grade_documents", grade_documents_by_score) # Use the new score-based grader
workflow.add_node("web_search", web_search)
workflow.add_node("generate", generate_answer)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_next_node,
    {
        "web_search": "web_search",
        "generate": "generate",
    },
)
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

graph_app = workflow.compile()


# --- 6. Define the FastAPI Endpoint ---
class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_rag(query: Query):
    inputs = {"question": query.question}
    result = graph_app.invoke(inputs)
    return {"answer": result["generation"]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)