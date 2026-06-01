import os
import sys
import re
import json
import time
import uuid
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
from src.agent.academic_tools import ACADEMIC_TOOLS as TOOLS

# Load environment variables from the workspace root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

app = FastAPI(
    title="ReAct Student Agent API Server",
    description="FastAPI service in the server/ directory to invoke the local ReAct agent and query student points.",
    version="1.0.0"
)

# Session store (in-memory for now)
sessions = {}

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
    Uses academic tools (lookup_student_id, get_academic_grades, etc.)
    Follows RULES.md strictly:
    1. Only answers about grades/student info
    2. Asks for parent phone first
    3. Verifies phone before showing grades
    4. No sensitive info exposure
    5. Supports grade level specific queries (e.g., "lớp 11")
    """
    def __init__(self, model_name: str = "mock-phi3-gguf", session_id: Optional[str] = None):
        super().__init__(model_name=model_name)
        self.session_id = session_id
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        time.sleep(0.5)  # Simulate small generation latency
        
        # Helper function to extract JSON from observation part
        def extract_json_from_text(text: str):
            # Find first {
            start = text.find('{')
            if start == -1:
                return None
            # Count braces to find matching }
            brace_count = 0
            end = -1
            for i, c in enumerate(text[start:], start):
                if c == '{':
                    brace_count +=1
                elif c == '}':
                    brace_count -=1
                    if brace_count ==0:
                        end = i
                        break
            if end == -1:
                return None
            return text[start:end+1]

        # Helper function to extract grade level (lớp 11 → "11")
        def extract_grade_level(text: str):
            # Match "lớp 11", "lop 11", "lớp học 11"
            pattern = r"(?:l[óôơớo]p|lớp|lop)\s*(\d+)"
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1)
            # Try to match isolated 10, 11, 12
            match_num = re.search(r"\b(10|11|12)\b", text)
            return match_num.group(1) if match_num else None
        
        # 1. Parse user question from prompt
        question_match = re.search(r"User Question:\s*(.*?)(?=\n)", prompt)
        question = question_match.group(1).strip() if question_match else ""
        
        # Get session state
        session = sessions.get(self.session_id, {
            "verified_student_id": None,
            "verified_parent_phone": None,
            "waiting_for_phone": False,
            "pending_query": None,
            "grade_level": None,
            "name": None,
            "waiting_for_grade": False
        })

        # Extract grade level if present
        grade_level = extract_grade_level(question)
        if grade_level and not session.get("grade_level"):
            session["grade_level"] = grade_level
        
        # Check if we have an observation in the prompt first
        obs_match = re.search(r"Observation:\s*(.*?)(?=\s*Step\s+\d+:|$)", prompt, re.DOTALL)
        if obs_match:
            obs_text = obs_match.group(1).strip()
            obs_json_str = extract_json_from_text(obs_text)
            try:
                if obs_json_str:
                    obs_data = json.loads(obs_json_str)
                    if obs_data.get("status") == "success":
                        if obs_data.get("tool") in ("verify_parent_phone", "search_student_by_name_and_phone"):
                            # Check if multiple grades are found
                            if obs_data.get("multiple_grades") is True:
                                student_id = obs_data["student_id"]
                                name = obs_data["name"]
                                phone = obs_data["parent_phone"]
                                
                                # Update session to remember verified student info but wait for grade
                                sessions[self.session_id] = {
                                    **session,
                                    "verified_student_id": student_id,
                                    "verified_parent_phone": phone,
                                    "name": name,
                                    "waiting_for_grade": True,
                                    "waiting_for_phone": False
                                }
                                
                                content = f"Thought: Tìm thấy nhiều lớp học khả dụng cho học sinh {name}. Tôi cần yêu cầu người dùng xác nhận lớp học muốn tìm điểm.\nFinal Answer: {obs_data.get('message')}"
                                completion_tokens = 80
                            else:
                                # Phone verified and single/specified grade row found
                                student_id = obs_data["student_id"]
                                name = obs_data["name"]
                                current_session = sessions.get(self.session_id, {})
                                grade_level_for_query = obs_data.get("grade_level") or current_session.get("grade_level")
                                
                                sessions[self.session_id] = {
                                    **current_session,
                                    "verified_student_id": student_id,
                                    "verified_parent_phone": obs_data.get("parent_phone"),
                                    "name": name,
                                    "waiting_for_phone": False,
                                    "waiting_for_grade": False,
                                    "pending_query": None,
                                    "grade_level": grade_level_for_query
                                }
                                
                                if grade_level_for_query:
                                    content = f"Thought: Số điện thoại đã được xác thực. Bây giờ lấy điểm cho học sinh {student_id} tại lớp {grade_level_for_query}.\nAction: get_grades_by_grade_level(student_id={student_id}, grade_level={grade_level_for_query})"
                                    completion_tokens = 70
                                else:
                                    content = f"Thought: Số điện thoại đã được xác thực. Bây giờ lấy điểm cho học sinh {student_id}.\nAction: get_academic_grades(student_id={student_id})"
                                    completion_tokens = 60
                        elif obs_data.get("tool") in ("get_academic_grades", "get_grades_by_grade_level"):
                            # Build final answer in premium natural language
                            name = obs_data["name"]
                            sid = obs_data["student_id"]
                            cls = obs_data.get("class", "N/A")
                            gl = obs_data.get("grade_level", "12")  # default to 12 if not specified
                            year = obs_data.get("academic_year", "N/A")
                            overall_gpa = obs_data.get("overall_gpa", "N/A")
                            
                            vi_subjects = {
                                "Math": "Toán", "Literature": "Ngữ văn", "English": "Tiếng Anh",
                                "Physics": "Vật lý", "Chemistry": "Hóa học", "Biology": "Sinh học",
                                "History": "Lịch sử", "Geography": "Địa lý"
                            }
                            
                            # Let's get conduct details if available
                            from src.data.database import get_conduct
                            conduct = get_conduct(sid, year) or {}
                            remarks = conduct.get("teacher_remarks", "Em có ý thức học tập tốt, ngoan ngoãn và lễ phép.")
                            conduct_grade = conduct.get("conduct_grade", "Tốt")
                            behavior_score = conduct.get("behavior_score", 90)
                            
                            if "subject" in obs_data and obs_data["subject"] != "All":
                                # Single subject
                                subj_key = obs_data["subject"]
                                subj_name = vi_subjects.get(subj_key, subj_key)
                                f1 = ", ".join(map(str, obs_data.get("factor_1", []))) or "N/A"
                                f2 = ", ".join(map(str, obs_data.get("factor_2", []))) or "N/A"
                                f3 = obs_data.get("factor_3", "N/A")
                                gpa = obs_data.get("gpa", "N/A")
                                final_answer = f"Dạ, đây là điểm môn **{subj_name}** lớp **{gl}** của em **{name}** (Lớp **{cls}**, năm học **{year}**) ạ:\n" \
                                               f"- Điểm kiểm tra miệng & 15 phút (Hệ số 1): `[{f1}]`\n" \
                                               f"- Điểm kiểm tra 1 tiết (Hệ số 2): `[{f2}]`\n" \
                                               f"- Điểm thi học kỳ (Hệ số 3): `{f3}`\n" \
                                               f"➔ Điểm trung bình môn {subj_name}: **{gpa}**"
                            else:
                                # All subjects
                                intro = f"Dạ, đây là bảng điểm học tập chi tiết của em **{name}** (Mã số học sinh: **{sid}**) lúc đang học **lớp {gl}** (Lớp cụ thể: **{cls}**, năm học: **{year}**) ạ:\n\n"
                                
                                grade_details = []
                                for subj, subj_key in [("Toán", "Math"), ("Ngữ văn", "Literature"), ("Tiếng Anh", "English"),
                                                       ("Vật lý", "Physics"), ("Hóa học", "Chemistry"), ("Sinh học", "Biology"),
                                                       ("Lịch sử", "History"), ("Địa lý", "Geography")]:
                                    subj_data = obs_data["subjects"].get(subj_key, {})
                                    f1 = ", ".join(map(str, subj_data.get("factor_1", []))) or "N/A"
                                    f2 = ", ".join(map(str, subj_data.get("factor_2", []))) or "N/A"
                                    f3 = subj_data.get("factor_3", "N/A")
                                    gpa = subj_data.get("gpa", "N/A")
                                    grade_details.append(f"- **Môn {subj}**: Điểm hệ số 1: `[{f1}]`; Hệ số 2: `[{f2}]`; Điểm thi (Hệ số 3): `{f3}` ➔ Điểm trung bình môn: **{gpa}**")
                                
                                summary = f"\n\n➔ **Điểm GPA trung bình học tập cả năm**: **{overall_gpa}**\n"
                                summary += f"➔ **Xếp loại hạnh kiểm**: **{conduct_grade}** (Điểm rèn luyện: **{behavior_score}/100**)\n"
                                summary += f"➔ **Nhận xét của giáo viên chủ nhiệm**: *\"{remarks}\"*"
                                
                                final_answer = intro + "\n".join(grade_details) + summary
                            
                            content = f"Thought: Tôi đã lấy được thông tin đầy đủ, tôi sẽ trình bày kết quả cho người dùng bằng ngôn ngữ tự nhiên.\nFinal Answer: {final_answer}"
                            completion_tokens = 300
                        else:
                            content = f"Thought: Tôi đã lấy được thông tin, tôi sẽ trình bày.\nFinal Answer: {json.dumps(obs_data, ensure_ascii=False, indent=2)}"
                            completion_tokens = 100
                    else:
                        # Error from tool
                        content = f"Thought: Có lỗi khi truy vấn dữ liệu.\nFinal Answer: {obs_data.get('message', 'Đã xảy ra lỗi không xác định.')}"
                        completion_tokens = 50
                else:
                    raise ValueError("No JSON in observation")
            except Exception as e:
                import traceback
                print(f"[DEBUG] Parse error: {traceback.format_exc()}")
                content = "Thought: Không thể phân tích kết quả tool.\nFinal Answer: Đã xảy ra lỗi khi xử lý yêu cầu của bạn."
                completion_tokens = 50
        else:
            # Rule 1: Check if query is allowed
            greeting_keywords = ["xin chào", "chào bạn", "chào", "hi", "hello", "hey"]
            is_greeting = any(kw.lower() in question.lower() for kw in greeting_keywords)
            
            # Check if question is a phone number (for verification)
            phone_match = re.search(r"(\d{10,11})", question)
            is_phone_input = bool(phone_match)
            
            scope_keywords = [
                "điểm", "học sinh", "học tập", "GPA", "môn học", "hạnh kiểm",
                "lớp", "số điện thoại", "parent", "grade", "student", "score",
                "S00", "S01"
            ]
            is_academic_query = any(kw.lower() in question.lower() for kw in scope_keywords)
            
            in_scope = is_greeting or is_academic_query or (session.get("waiting_for_phone") and is_phone_input) or session.get("waiting_for_grade")
            
            if not in_scope:
                content = (
                    "Thought: Câu hỏi này không liên quan đến điểm số hoặc thông tin học sinh.\n"
                    "Final Answer: Xin lỗi, tôi chỉ có thể trả lời các câu hỏi về điểm số và thông tin học tập. Vui lòng hỏi về học sinh, điểm các môn học hoặc GPA tổng hợp."
                )
                completion_tokens = 50
            elif is_greeting and not session.get("waiting_for_phone") and not session.get("verified_student_id"):
                # Handle greeting
                content = (
                    "Thought: Người dùng chào hỏi, tôi sẽ chào lại.\n"
                    "Final Answer: Xin chào! Tôi có thể giúp bạn tìm hiểu về điểm số học sinh. Vui lòng hỏi về điểm hoặc thông tin học tập!"
                )
                completion_tokens = 50
            elif session.get("waiting_for_phone"):
                if is_phone_input:
                    phone = phone_match.group(1)
                    # Call verify_parent_phone with potential grade_level in session
                    g_level = session.get("grade_level")
                    g_param = f", grade_level={g_level}" if g_level else ""
                    content = f"Thought: Người dùng đã cung cấp số điện thoại. Tôi cần xác thực số điện thoại này.\nAction: verify_parent_phone(parent_phone={phone}{g_param})"
                    completion_tokens = 60
                else:
                    content = (
                        "Thought: Tôi đang chờ số điện thoại phụ huynh để xác thực.\n"
                        "Final Answer: Xin vui lòng cung cấp số điện thoại phụ huynh để tôi xác thực trước khi xem điểm."
                    )
                    completion_tokens = 50
            elif session.get("waiting_for_grade"):
                # Extract grade level from user selection
                selected_grade = extract_grade_level(question) or (question if question.strip() in ("10", "11", "12") else None)
                if selected_grade:
                    # Update session with specified grade
                    selected_grade = str(selected_grade).strip()
                    student_id = session["verified_student_id"]
                    sessions[self.session_id] = {
                        **session,
                        "grade_level": selected_grade,
                        "waiting_for_grade": False
                    }
                    content = f"Thought: Người dùng đã chọn lớp {selected_grade}. Tôi sẽ gọi tool để lấy điểm của học sinh tại lớp đó.\nAction: get_grades_by_grade_level(student_id={student_id}, grade_level={selected_grade})"
                    completion_tokens = 70
                else:
                    name = session.get("name", "học sinh")
                    content = (
                        f"Thought: Tôi đang chờ người dùng nhập lớp học khả dụng.\n"
                        f"Final Answer: Vui lòng nhập đúng lớp học (lớp 10, lớp 11 hoặc lớp 12) của em {name}."
                    )
                    completion_tokens = 50
            elif session.get("verified_student_id"):
                # Already verified, get grades
                target_id = session["verified_student_id"]
                if session.get("grade_level"):
                    content = f"Thought: Người dùng hỏi về điểm số của học sinh đã được xác thực {target_id} tại lớp {session['grade_level']}. Tôi cần lấy thông tin điểm học tập.\nAction: get_grades_by_grade_level(student_id={target_id}, grade_level={session['grade_level']})"
                    completion_tokens = 70
                else:
                    # No grade level, check database to see how many grades are available
                    # Since this is a Mock LLM Provider running in server/api.py, we can query our python database helpers directly!
                    from src.data.database import get_student_grades_list_by_phone
                    matches = get_student_grades_list_by_phone(session["verified_parent_phone"], session.get("name", ""))
                    if len(matches) > 1:
                        grades = [m["grade_level"] for m in matches]
                        sessions[self.session_id] = {
                            **session,
                            "waiting_for_grade": True
                        }
                        content = f"Thought: Tìm thấy nhiều lớp học khả dụng. Tôi cần hỏi lại người dùng để chọn lớp học.\nFinal Answer: Tìm thấy điểm của học sinh {session.get('name')} ở các lớp: {', '.join(['lớp ' + g for g in grades])}. Bạn muốn tìm điểm của học sinh {session.get('name')} lớp mấy?"
                        completion_tokens = 80
                    else:
                        content = f"Thought: Người dùng hỏi về điểm số của học sinh đã được xác thực {target_id}. Tôi cần lấy thông tin điểm học tập.\nAction: get_academic_grades(student_id={target_id})"
                        completion_tokens = 60
            else:
                # Need to ask for phone first, store grade level and name
                sessions[self.session_id] = {
                    **session,
                    "waiting_for_phone": True,
                    "pending_query": question,
                    "grade_level": grade_level
                }
                content = (
                    "Thought: Tôi cần xác thực người dùng trước khi cung cấp thông tin điểm.\n"
                    "Final Answer: Xin vui lòng cung cấp số điện thoại phụ huynh để xác thực trước khi xem điểm."
                )
                completion_tokens = 50
        
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
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    response: str
    provider: str
    model: str
    steps: List[Dict[str, Any]]
    latency_ms: int
    usage: Dict[str, int]
    session_id: str

# Helper to load requested provider
def get_provider(provider_name: Optional[str], session_id: Optional[str] = None) -> LLMProvider:
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
        try:
            return LocalProvider(model_path=model_path)
        except Exception as e:
            raise ValueError(f"Failed to load Local GGUF model: {e}. If your CPU is older or lacks AVX2, llama-cpp-python may crash with 0xc000001d. Please use 'mock' or cloud providers.")
            
    elif provider_name == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key or "your_" in api_key:
            raise ValueError("DeepSeek API Key is missing. Please set DEEPSEEK_API_KEY in your env.")
        from src.core.deepseek_provider import DeepSeekProvider
        return DeepSeekProvider(model_name=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"), api_key=api_key)
        
    elif provider_name == "qwen":
        model_path = os.getenv("QWEN_MODEL_PATH", "./models/qwen2.5-0.5b-instruct-q4_k_m.gguf")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Local Qwen model not found at {model_path}.")
        try:
            return LocalProvider(model_path=model_path)
        except Exception as e:
            raise ValueError(f"Failed to load Qwen GGUF model: {e}")
        
    elif provider_name == "mock":
        return MockReActProvider(session_id=session_id)
        
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
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    deepseek_ok = deepseek_key is not None and "your_" not in deepseek_key and len(deepseek_key) > 5
    
    qwen_path = os.getenv("QWEN_MODEL_PATH", "./models/qwen2.5-0.5b-instruct-q4_k_m.gguf")
    qwen_ok = LOCAL_PROVIDER_AVAILABLE and os.path.exists(qwen_path)
    
    return {
        "default_provider": os.getenv("DEFAULT_PROVIDER", "openai"),
        "default_model": os.getenv("DEFAULT_MODEL", "gpt-4o"),
        "local_model_path": local_path,
        "providers": {
            "openai": {"available": openai_ok, "description": "OpenAI GPT-4o (requires OPENAI_API_KEY)"},
            "google": {"available": gemini_ok, "description": "Google Gemini-1.5-Flash (requires GEMINI_API_KEY)"},
            "local": {"available": local_ok, "description": "Phi-3 GGUF model via llama-cpp (requires GGUF file)"},
            "deepseek": {"available": deepseek_ok, "description": "DeepSeek LLM (requires DEEPSEEK_API_KEY)"},
            "qwen": {"available": qwen_ok, "description": "Local Qwen GGUF model via llama-cpp"},
            "mock": {"available": True, "description": "Mock ReAct loop simulation (Always available, no setup needed)"}
        }
    }

@app.post("/api/chat", response_model=QueryResponse)
async def chat_endpoint(payload: QueryRequest):
    """
    Invoke the local ReAct Agent on the user query.
    """
    start_time = time.time()
    session_id = payload.session_id or str(uuid.uuid4())
    
    # Initialize session if new
    if session_id not in sessions:
        sessions[session_id] = {
            "verified_student_id": None,
            "verified_parent_phone": None,
            "waiting_for_phone": False,
            "pending_query": None,
            "grade_level": None
        }
    
    try:
        # Load the selected provider with a safe fallback to Mock if configuration is incomplete
        try:
            provider = get_provider(payload.provider, session_id)
        except (ValueError, FileNotFoundError) as e:
            if payload.provider in ["openai", "google", "gemini", "local", "deepseek", "qwen"]:
                provider = MockReActProvider(session_id=session_id)
            else:
                raise HTTPException(status_code=400, detail=str(e))
                
        # Instantiate ReActAgent
        agent = ReActAgent(llm=provider, tools=list(TOOLS.values()), max_steps=payload.max_steps)
        
        # Execute query
        final_answer = agent.run(payload.query)
        
        # Collect intermediate reasoning steps
        steps = agent.history
        
        # Check steps for verify_parent_phone success to update session
        for step in steps:
            obs = step.get("observation", "")
            if isinstance(obs, str) and "verify_parent_phone" in obs:
                try:
                    json_str = obs[obs.find("{"):obs.rfind("}")+1]
                    obs_data = json.loads(json_str)
                    if obs_data.get("status") == "success" and obs_data.get("tool") == "verify_parent_phone":
                        # Update session with verified student
                        sessions[session_id] = {
                            **sessions[session_id],
                            "verified_student_id": obs_data.get("student_id"),
                            "verified_parent_phone": obs_data.get("parent_phone"),
                            "waiting_for_phone": False,
                            "pending_query": None
                        }
                except Exception as e:
                    print(f"[DEBUG] Failed to parse observation for session update: {e}")
        
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
            },
            session_id=session_id
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
