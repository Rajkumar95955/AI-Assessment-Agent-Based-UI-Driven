"""
FastAPI Backend
Exposes the agent pipeline via REST API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import AgentPipeline, GeneratorAgent, ReviewerAgent
from agents.pipeline import PipelineInput, PipelineOutput

app = FastAPI(
    title="AI Assessment API",
    description="Agent-based educational content generation and review",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = AgentPipeline()


# ============== Request/Response Models ==============

class GenerateRequest(BaseModel):
    grade: int
    topic: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "grade": 4,
                "topic": "Types of angles"
            }
        }


# ============== API Endpoints ==============

@app.get("/")
async def root():
    return {
        "message": "AI Assessment API",
        "endpoints": {
            "POST /generate": "Run the full agent pipeline",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/generate", response_model=PipelineOutput)
async def generate_content(request: GenerateRequest):
    """
    Run the full agent pipeline:
    1. Generator creates content
    2. Reviewer evaluates content
    3. If review fails, refine once with feedback
    """
    try:
        input_data = PipelineInput(
            grade=request.grade,
            topic=request.topic
        )
        result = pipeline.run(input_data)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Run Server ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)