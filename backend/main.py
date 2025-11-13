import os
import uvicorn
import requests
import uuid
import json
from datetime import timezone
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import TypedDict, List, Tuple, Literal

from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate


# --- 1. Load Environment Variables and Initialize Models ---
load_dotenv()

app = FastAPI(
    title="Math Professor Agent API",
    description="An API for a self-correcting RAG agent.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "Math Professor API is running"}

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
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


# --- 4. Define the Nodes and Decision Logic ---

#---GUARDRAIL NODES---

def input_guardrail(state):
    """
    Checks if the user's question is on-topic (mathematics).
    This acts as the first line of defense.
    """
    print("---NODE: INPUT GUARDRAIL---")
    question = state["question"]
    
    guardrail_prompt = f"""
    You are a guardrail ensuring that a user's question is about mathematics.
    Look at the question below. If it is a mathematical question (including concepts, problems, history, etc.), respond with 'yes'.
    Otherwise, respond with 'no'.

    Question: {question}

    Response (yes/no):
    """
    decision = llm.invoke(guardrail_prompt)
    
    if "yes" in decision.content.lower():
        print("---GUARDRAIL PASSED: QUESTION IS ABOUT MATH---")
        return {"route_decision": "continue"}
    else:
        print("---GUARDRAIL FAILED: QUESTION IS NOT ABOUT MATH---")
        # Provide a canned response and end the workflow immediately
        return {
            "generation": "I'm sorry, as a math professor, I can only answer questions about mathematics.",
            "route_decision": "end"
        }

def output_guardrail(state):
    """
    Checks the generated answer for any harmful or inappropriate content.
    This is the final check before sending the response to the user.
    """
    print("---NODE: OUTPUT GUARDRAIL---")
    return {"generation": state["generation"]}

# --- CORE AGENT NODES ---

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
    """
    Acts as an MCP client to call the separate tool server for a web search.
    This node is now decoupled from the actual search tool implementation.
    """
    print("---NODE: WEB SEARCH (via MCP)---")
    question = state["question"]
    
    # The network address of our separate MCP tool server
    mcp_server_url = "http://localhost:8001/invoke/tavily_search"
    context = ""
    
    try:
        # Make a POST request to the MCP server with the user's question
        print(f"---MCP Client: Calling tool server at {mcp_server_url}---")
        response = requests.post(mcp_server_url, json={"query": question})
        response.raise_for_status()  # This will raise an exception for HTTP errors
        
        # Process the structured JSON response from the server
        web_results = response.json().get("result", [])
        
        # Format the results into a clear context string for the LLM
        context = "\n".join([f"URL: {d.get('url', '')}\nContent: {d.get('content', '')}" for d in web_results])
        print("---MCP Client: Successfully received and processed results.---")

    except requests.RequestException as e:
        print(f"---MCP CLIENT ERROR: Could not connect to the tool server. Error: {e}---")
        context = "Web search failed because the tool server could not be reached."

    return {"context": context}

def generate_answer(state): 
    print("---NODE: GENERATING ANSWER---")
    question = state['question']
    context = state['context']
    
    template = """
    You are a helpful math professor. Your goal is to provide a clear, step-by-step solution to the user's question.
    Base your answer on the provided context. The context may be from a local knowledge base, or from a web search which will include URLs and content.

    CONTEXT:
    {context}

    QUESTION:
    {question}

    ANSWER:
    """
    prompt = PromptTemplate.from_template(template)
    rag_prompt = prompt.format(context=context, question=question)
    generation = llm.invoke(rag_prompt)
    
    return {"generation": generation.content}

def decide_next_node(state):
    return state["route_decision"]


# --- 5. Build the Graph ---
workflow = StateGraph(GraphState)

workflow.add_node("input_guardrail", input_guardrail)
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("grade_documents", grade_documents_by_score) # Use the new score-based grader
workflow.add_node("web_search", web_search)
workflow.add_node("generate", generate_answer)
workflow.add_node("output_guardrail", output_guardrail)

workflow.set_entry_point("input_guardrail")
workflow.add_conditional_edges(
    "input_guardrail",
    decide_next_node,
    {
        "continue": "retrieve",
        "end": END,
    },
)   

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

workflow.add_edge("generate", "output_guardrail")
workflow.add_edge("output_guardrail", END)

graph_app = workflow.compile()


# --- 6. Define the FastAPI Endpoint ---
class Query(BaseModel):
    question: str

class FeedbackQuery(BaseModel):
    session_id: str
    question: str
    answer: str
    feedback: Literal["correct", "incorrect","clarify"]
        
@app.post("/ask")
async def ask_rag(query: Query):
    
    session_id = str(uuid.uuid4())
    inputs = {"question": query.question}
    result = graph_app.invoke(inputs)
    return {
        "session_id": session_id,
        "question": query.question,
        "answer": result["generation"]
        }

@app.post("/feedback")
async def log_and_refine_feedback(feedback_data: FeedbackQuery):
    print(f"---HITL: RECEIVED FEEDBACK: {feedback_data.feedback}---")
    
    log_file = "feedback_log.json"
    
    # Prepare the log entry
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": feedback_data.session_id,
        "question": feedback_data.question,
        "answer": feedback_data.answer,
        "feedback": feedback_data.feedback,
    }
    
    regenerated_answer = None

    # Handle refinement based on feedback
    if feedback_data.feedback == "incorrect":
        print("---HITL: REGENERATING FOR 'INCORRECT' FEEDBACK---")
        refinement_prompt = f"""
        Your previous answer was marked incorrect by a human. Do not justify the old answer. Instead, carefully re-derive the solution step by step from first principles, double-checking every step.Provide only the corrected derivation.

        Original Question: {feedback_data.question}
        Your Incorrect Answer: {feedback_data.answer}

        Corrected Answer:
        """
        regenerated_answer = llm.invoke(refinement_prompt).content
        log_entry["regenerated_answer"] = regenerated_answer

    elif feedback_data.feedback == "clarify":
        print("---HITL: REGENERATING FOR 'CLARIFY' FEEDBACK---")
        refinement_prompt = f"""
        A student found your previous answer unclear. 
        Please rewrite the explanation in simpler terms. Break it down into very easy-to-follow steps and include a simple example if possible.

        Original Question: {feedback_data.question}
        Your Unclear Answer: {feedback_data.answer}

        Simpler, Clarified Answer:
        """
        regenerated_answer = llm.invoke(refinement_prompt).content
        log_entry["regenerated_answer"] = regenerated_answer

    # Append the log entry to the JSON file
    try:
        # Read existing data
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        
        # Append new log
        logs.append(log_entry)
        
        # Write back to the file
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
        print(f"---HITL: FEEDBACK LOGGED TO {log_file}---")

    except Exception as e:
        print(f"---HITL: FAILED TO LOG FEEDBACK. ERROR: {e}---")
        raise HTTPException(status_code=500, detail="Failed to log feedback.")

    # Prepare API response
    response_data = {"status": "success", "logged_feedback": log_entry}
    if regenerated_answer:
        response_data["regenerated_answer"] = regenerated_answer
        
    return response_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)