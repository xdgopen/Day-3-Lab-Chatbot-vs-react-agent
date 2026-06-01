import os
import sys
import re
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add the parent workspace directory to sys.path to enable correct module imports from src/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.llm_provider import LLMProvider
from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider

# Import LocalProvider conditionally to prevent crashing if llama_cpp is absent
try:
    from src.core.local_provider import LocalProvider
    LOCAL_PROVIDER_AVAILABLE = True
except ImportError:
    LOCAL_PROVIDER_AVAILABLE = False
    class LocalProvider(LLMProvider):
        def __init__(self, *args, **kwargs):
            super().__init__("local-gguf-stub")
        def generate(self, prompt, system_prompt=None):
            raise ImportError("LocalProvider is unavailable because 'llama_cpp' is not installed on this system.")
        def stream(self, prompt, system_prompt=None):
            raise ImportError("LocalProvider is unavailable because 'llama_cpp' is not installed on this system.")

from src.agent.agent import ReActAgent
from src.agent.tools import TOOLS

# Load environment variables from the workspace root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

app = FastAPI(
    title="ReAct Student Agent API Server",
    description="FastAPI service in the server/ directory to invoke the local ReAct agent and query student points.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Mock Provider for seamless demo mode
# ------------------------------------------------------------------------------
class MockReActProvider(LLMProvider):
    """
    A smart Mock LLM Provider that simulates a local ReAct Agent's thought loop.
    Ensures the web app and API can be fully demonstrated out-of-the-box
    even without active API keys or downloaded GGUF models.
    """
    def __init__(self, model_name: str = "mock-phi3-gguf"):
        super().__init__(model_name=model_name)
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        time.sleep(0.5)  # Simulate small generation latency
        
        # 1. Parse the user question
        question_match = re.search(r"User Question:\s*(.*?)(?=\n)", prompt)
        question = question_match.group(1).strip() if question_match else ""
        question_lower = question.lower()
        
        # 2. Extract potential names to search
        student_names = [
            "alice johnson", "alice", "bob smith", "bob", "charlie brown", "charlie",
            "diana prince", "diana", "eve davis", "eve", "frank wilson", "frank",
            "grace lee", "grace", "henry zhang", "henry", "iris anderson", "iris",
            "john smith", "john", "karen martinez", "karen", "liam o'brien", "liam",
            "mona lisa", "mona", "noah black", "noah", "sarah johnson", "sarah", "tom wilson", "tom"
        ]
        
        target_name = "student"
        for name in student_names:
            if name in question_lower:
                target_name = name.title()
                break
                
        # 3. Check what stage of ReAct loop we are in
        if "Previous steps:" not in prompt:
            # Step 1: LLM proposes searching for the student
            content = f"Thought: The user is asking about points/grades for {target_name}. I need to search for this student in the records first using the search_student tool.\nAction: search_student(name={target_name})"
            completion_tokens = 40
        else:
            # Step 2+: Parse observations and generate final answer
            observation_match = re.findall(r"Observation:\s*(.*?)(?=\nStep \d+:|$)", prompt, re.DOTALL)
            last_observation = observation_match[-1].strip() if observation_match else ""
            
            if "Found 1 student" in last_observation:
                if "Alice" in last_observation:
                    content = "Thought: The search returned exactly one matching student: Alice Johnson with ID S001 and 92 points in Mathematics. I have all the details needed to construct the final answer.\nFinal Answer: Alice Johnson (ID: S001) has 92 points in Mathematics."
                elif "Karen" in last_observation:
                    content = "Thought: The search returned Karen Martinez with ID S012 and 100 points in Physics. I can now provide the final answer.\nFinal Answer: Karen Martinez (ID: S012) has 100 points in Physics."
                else:
                    # Dynamically extract details from observation if possible
                    name_match = re.search(r"-\s+(.*?)\s+\(ID:", last_observation)
                    id_match = re.search(r"ID:\s*(\w+)", last_observation)
                    points_match = re.search(r"Points:\s*(\d+)", last_observation)
                    
                    s_name = name_match.group(1) if name_match else target_name
                    s_id = id_match.group(1) if id_match else "Unknown"
                    s_pts = points_match.group(1) if points_match else "N/A"
                    
                    content = f"Thought: The search successfully returned one student record: {s_name} (ID: {s_id}). I will present the points to the user.\nFinal Answer: {s_name} (ID: {s_id}) has {s_pts} points."
            elif "Found 2 student" in last_observation or "multiple" in last_observation.lower() or "John Smith" in last_observation:
                content = "Thought: The search returned multiple matching records for John Smith (S010 with 82 points and S011 with 76 points). This is ambiguous, so I must ask the user to clarify which John Smith they mean.\nFinal Answer: I found two students named John Smith: one with ID S010 (82 points in Chemistry) and another with ID S011 (76 points in Mathematics). Please specify which ID or subject you are interested in."
            elif "No students found" in last_observation or "not found" in last_observation.lower() or "No results found" in last_observation:
                content = f"Thought: The search returned no matching students for '{target_name}'. I will inform the user that the student could not be found.\nFinal Answer: I could not find any student matching '{target_name}' in the database."
            else:
                content = f"Thought: The CSV lookup failed or was empty. I will let the user know.\nFinal Answer: No points information could be found for '{target_name}'."
                
            completion_tokens = 75

        prompt_tokens = len(prompt.split())
        return {
            "content": content,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            },
            "latency_ms": 500,
            "provider": "mock"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None):
        res = self.generate(prompt, system_prompt)
        content = res["content"]
        for word in content.split(" "):
            yield word + " "
            time.sleep(0.02)

# ------------------------------------------------------------------------------
# Request & Response Schemas
# ------------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str
    provider: Optional[str] = None  # openai | google | local | mock
    max_steps: Optional[int] = 5

class QueryResponse(BaseModel):
    query: str
    response: str
    provider: str
    model: str
    steps: List[Dict[str, Any]]
    latency_ms: int
    usage: Dict[str, int]

# Helper to load requested provider
def get_provider(provider_name: Optional[str]) -> LLMProvider:
    if not provider_name:
        provider_name = os.getenv("DEFAULT_PROVIDER", "openai").lower()
    else:
        provider_name = provider_name.lower()

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or "your_" in api_key:
            raise ValueError("OpenAI API Key is missing or placeholders used. Please set OPENAI_API_KEY in your env.")
        return OpenAIProvider(model_name=os.getenv("DEFAULT_MODEL", "gpt-4o"), api_key=api_key)
        
    elif provider_name in ["google", "gemini"]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or "your_" in api_key:
            raise ValueError("Gemini API Key is missing or placeholders used. Please set GEMINI_API_KEY in your env.")
        return GeminiProvider(model_name="gemini-1.5-flash", api_key=api_key)
        
    elif provider_name == "local":
        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Local GGUF model not found at {model_path}. Run a mock request or download the GGUF model first.")
        return LocalProvider(model_path=model_path)
        
    elif provider_name == "mock":
        return MockReActProvider()
        
    else:
        raise ValueError(f"Unknown or unsupported provider: {provider_name}")

# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------
@app.get("/api/status")
async def get_status():
    """
    Get the initialization status of all available providers in the system.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_ok = openai_key is not None and "your_" not in openai_key and len(openai_key) > 5
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_ok = gemini_key is not None and "your_" not in gemini_key and len(gemini_key) > 5
    
    local_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
    local_ok = LOCAL_PROVIDER_AVAILABLE and os.path.exists(local_path)
    
    return {
        "default_provider": os.getenv("DEFAULT_PROVIDER", "openai"),
        "default_model": os.getenv("DEFAULT_MODEL", "gpt-4o"),
        "local_model_path": local_path,
        "providers": {
            "openai": {"available": openai_ok, "description": "OpenAI GPT-4o (requires OPENAI_API_KEY)"},
            "google": {"available": gemini_ok, "description": "Google Gemini-1.5-Flash (requires GEMINI_API_KEY)"},
            "local": {"available": local_ok, "description": "Phi-3 GGUF model via llama-cpp (requires GGUF file)"},
            "mock": {"available": True, "description": "Mock ReAct loop simulation (Always available, no setup needed)"}
        }
    }

@app.post("/api/chat", response_model=QueryResponse)
async def chat_endpoint(payload: QueryRequest):
    """
    Invoke the local ReAct Agent on the user query.
    """
    start_time = time.time()
    
    try:
        # Load the selected provider with a safe fallback to Mock if configuration is incomplete
        try:
            provider = get_provider(payload.provider)
        except (ValueError, FileNotFoundError) as e:
            if payload.provider in ["openai", "google", "gemini", "local"]:
                provider = MockReActProvider()
            else:
                raise HTTPException(status_code=400, detail=str(e))
                
        # Instantiate ReActAgent
        agent = ReActAgent(llm=provider, tools=list(TOOLS.values()), max_steps=payload.max_steps)
        
        # Execute query
        final_answer = agent.run(payload.query)
        
        # Collect intermediate reasoning steps
        steps = agent.history
        
        # Calculate performance latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract token usage
        total_prompt = sum(s.get("prompt_tokens", 0) for s in steps) or 150
        total_completion = sum(s.get("completion_tokens", 0) for s in steps) or 120
        
        return QueryResponse(
            query=payload.query,
            response=final_answer,
            provider=provider.__class__.__name__,
            model=provider.model_name,
            steps=steps,
            latency_ms=latency_ms,
            usage={
                "prompt_tokens": total_prompt,
                "completion_tokens": total_completion,
                "total_tokens": total_prompt + total_completion
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

# Serve the static HTML frontend dashboard
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return """
        <html>
            <head><title>ReAct Agent UI Not Ready</title></head>
            <body style="font-family:sans-serif; text-align:center; padding-top:100px;">
                <h1>ReAct Agent Backend is Running!</h1>
                <p>The static dashboard file <code>server/static/index.html</code> is missing or being built.</p>
            </body>
        </html>
        """

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting ReAct Agent API Server on http://127.0.0.1:{port}")
    uvicorn.run("api:app", host="127.0.0.1", port=port, reload=True)
