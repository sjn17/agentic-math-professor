import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

# Load environment variables (specifically TAVILY_API_KEY)
load_dotenv()

# Initialize the FastAPI application for our tool server
app = FastAPI(
    title="Math Professor Tool Server (MCP)",
    description="Exposes web search capabilities as a separate, callable service.",
)

# Define the expected input schema for our endpoint
class TavilyInput(BaseModel):
    query: str

@app.post("/invoke/tavily_search")
def tavily_search(request: TavilyInput):
    """
    This endpoint acts as our MCP tool provider. It takes a search query,
    calls the Tavily API, and returns the structured JSON results.
    """
    print(f"MCP Server: Received search query: '{request.query}'")
    try:
        search_tool = TavilySearchResults(k=3)
        results = search_tool.invoke({"query": request.query})
        print("MCP Server: Successfully fetched and returned results from Tavily.")
        # The response is the structured JSON directly from Tavily
        return {"result": results}
    except Exception as e:
        print(f"MCP Server: Error calling Tavily. {e}")
        # If the tool fails, return an appropriate HTTP error
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # We run this on a different port (8001) to avoid conflict with the main agent (8000)
    uvicorn.run(app, host="0.0.0.0", port=8001)