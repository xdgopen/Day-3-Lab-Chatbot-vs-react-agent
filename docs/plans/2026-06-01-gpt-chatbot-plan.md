
# GPT-Style Chatbot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a GPT-style dark theme chat interface with collapsible right sidebar logs, and implement rules from RULES.md.

**Architecture:** 
- Frontend: GPT-inspired dark theme, chat interface in `server/static/index.html`
- Backend: Update `/api/chat` endpoint with session state and rule enforcement
- Database: Add parent phone verification functions

**Tech Stack:** FastAPI, Vanilla JS, CSS3

---

## File Structure
| File | Responsibility |
|------|----------------|
| `server/static/index.html` | New GPT-style UI with chat, logs, input |
| `src/data/database.py` | Add `get_student_by_parent_phone` function |
| `src/agent/academic_tools.py` | Add `verify_parent_phone` tool |
| `server/api.py` | Add session handling, rule enforcement, session ID |
| `src/agent/agent.py` | (Minor changes if needed) |

---

## Task 1: Rewrite `server/static/index.html` with GPT-style UI

**Files:**
- Modify: `server/static/index.html` (complete rewrite)

- [ ] **Step 1: Replace current HTML with GPT-style structure**

```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trợ lý Học tập</title>
    <style>
        /* CSS Reset & Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f0f0f;
            color: #e0e0e0;
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        /* Main Container */
        .app-container {
            display: flex;
            width: 100%;
            height: 100%;
        }

        /* Chat Area */
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        /* Header */
        .chat-header {
            background-color: #1e1e1e;
            padding: 12px 20px;
            border-bottom: 1px solid #2d2d2d;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .chat-header h1 {
            font-size: 18px;
            font-weight: 600;
        }

        .rules-reminder {
            font-size: 12px;
            color: #888;
            margin-left: auto;
        }

        /* Messages Container */
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        /* Message */
        .message {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }

        .message.user {
            flex-direction: row-reverse;
        }

        /* Avatar */
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            flex-shrink: 0;
        }

        .avatar.assistant {
            background-color: #10a37f;
            color: white;
        }

        .avatar.user {
            background-color: #2d2d2d;
            color: white;
        }

        /* Message Content */
        .message-content {
            padding: 12px 16px;
            border-radius: 8px;
            line-height: 1.5;
        }

        .message.user .message-content {
            background-color: #2d2d2d;
        }

        .message.assistant .message-content {
            background-color: #1e1e1e;
        }

        /* Input Area */
        .input-container {
            background-color: #1e1e1e;
            border-top: 1px solid #2d2d2d;
            padding: 16px 20px;
            display: flex;
            gap: 12px;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }

        .input-area {
            flex: 1;
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 12px;
            padding: 12px 16px;
            color: #e0e0e0;
            font-family: inherit;
            font-size: 16px;
            resize: none;
            outline: none;
            transition: border-color 0.2s;
        }

        .input-area:focus {
            border-color: #10a37f;
        }

        .send-btn {
            background-color: #10a37f;
            color: white;
            border: none;
            border-radius: 10px;
            width: 40px;
            height: 40px;
            cursor: pointer;
            font-size: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s;
        }

        .send-btn:hover {
            background-color: #0d8a6a;
        }

        .send-btn:disabled {
            background-color: #3d3d3d;
            cursor: not-allowed;
        }

        /* Sidebar */
        .sidebar {
            width: 400px;
            background-color: #1e1e1e;
            border-left: 1px solid #2d2d2d;
            display: flex;
            flex-direction: column;
            transition: width 0.3s;
        }

        .sidebar.collapsed {
            width: 50px;
        }

        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid #2d2d2d;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .sidebar-toggle {
            background: none;
            border: none;
            color: #e0e0e0;
            cursor: pointer;
            font-size: 20px;
        }

        .sidebar-title {
            font-size: 16px;
            font-weight: 600;
        }

        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }

        .sidebar.collapsed .sidebar-content,
        .sidebar.collapsed .sidebar-title {
            display: none;
        }

        /* Log Items */
        .log-item {
            border-bottom: 1px solid #2d2d2d;
            padding: 12px 0;
        }

        .log-step {
            font-size: 12px;
            text-transform: uppercase;
            color: #888;
            margin-bottom: 8px;
        }

        .log-thought, .log-action, .log-observation {
            font-size: 14px;
            margin-bottom: 4px;
        }

        .log-action {
            color: #10a37f;
        }

        .log-observation {
            color: #888;
            font-family: monospace;
            font-size: 13px;
        }
    </style>
</head>
<body>

    <div class="app-container">
        <!-- Chat Container -->
        <div class="chat-container">
            <!-- Header -->
            <div class="chat-header">
                <h1>🧠 Trợ lý Học tập</h1>
                <span class="rules-reminder">Chỉ trả lời về điểm số & học tập</span>
            </div>
            <!-- Messages -->
            <div class="messages-container" id="messagesContainer">
                <div class="message assistant">
                    <div class="avatar assistant">AI</div>
                    <div class="message-content">
                        Xin chào! Tôi có thể giúp bạn tìm hiểu về điểm số học sinh. Vui lòng hỏi về điểm hoặc thông tin học tập!
                    </div>
                </div>
            </div>
            <!-- Input -->
            <div class="input-container">
                <textarea class="input-area" id="messageInput" placeholder="Nhập câu hỏi của bạn..." rows="1"></textarea>
                <button class="send-btn" id="sendBtn" onclick="sendMessage()">➤</button>
            </div>
        </div>
        <!-- Sidebar -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <button class="sidebar-toggle" onclick="toggleSidebar()">☰</button>
                <span class="sidebar-title">📋 Logs</span>
            </div>
            <div class="sidebar-content" id="logsContent">
                <p style="color:#888; font-size:14px;">Logs sẽ hiện ở đây...</p>
            </div>
        </div>
    </div>

    <script>
        // Session State
        let sessionId = localStorage.getItem('sessionId') || null;
        let isLoading = false;

        // Toggle Sidebar
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        // Render Message
        function addMessage(content, isUser) {
            const container = document.getElementById('messagesContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            messageDiv.innerHTML = `
                <div class="avatar ${isUser ? 'user' : 'assistant'}">
                    ${isUser ? 'B' : 'AI'}
                </div>
                <div class="message-content">
                    ${content}
                </div>
            `;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        // Render Logs
        function addLogs(steps) {
            const logsContent = document.getElementById('logsContent');
            logsContent.innerHTML = '';
            if (steps.forEach((step, i) => {
                const logDiv = document.createElement('div');
                logDiv.className = 'log-item';
                logDiv.innerHTML = `
                    <div class="log-step">Bước ${i + 1}</div>
                    ${step.thought ? `<div class="log-thought">💡 ${step.thought}</div>` : ''}
                    ${step.action ? `<div class="log-action">⚙️ ${step.action}</div>` : ''}
                    ${step.observation ? `<div class="log-observation">📄 ${step.observation}</div>` : ''}
                `;
                logsContent.appendChild(logDiv);
            });
        }

        // Send Message
        async function sendMessage() {
            if (isLoading) return;
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, true);
            input.value = '';
            input.style.height = 'auto';

            isLoading = true;
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = true;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: message,
                        provider: 'mock',
                        max_steps: 5,
                        session_id: sessionId
                    }),
                });

                if (!response.ok) {
                    throw new Error('Server error');
                }

                const data = await response.json();
                sessionId = data.session_id || sessionId;
                if (sessionId) {
                    localStorage.setItem('sessionId', sessionId);
                }

                // Add assistant message
                addMessage(data.response, false);

                // Add logs
                if (data.steps && data.steps.length > 0) {
                    addLogs(data.steps);
                }

            } catch (err) {
                addMessage('Đã xảy ra lỗi, vui lòng thử lại!', false);
            } finally {
                isLoading = false;
                sendBtn.disabled = false;
            }
        }

        // Auto-resize textarea
        const input = document.getElementById('messageInput');
        input.addEventListener('input', () => {
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 200) + 'px';
        });

        // Enter to send
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    </script>
</body>
</html>
```

- [ ] **Step 2: Save and test UI (open in browser to check layout)

---

## Task 2: Add `get_student_by_parent_phone` to `src/data/database.py`

**Files:**
- Modify: `src/data/database.py`

- [ ] **Step 1: Add new function to `src/data/database.py`

```python
def get_student_by_parent_phone(parent_phone: str, academic_year: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get student by parent phone number, returns latest year if academic_year not specified
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM students WHERE parent_phone = ?
    params = [parent_phone]
    if academic_year:
        query += " AND academic_year = ?"
        params.append(academic_year)
    else:
        # Order by academic_year DESC to get latest year
        query += " ORDER BY academic_year DESC"
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    return dict(row)
```

- [ ] **Step 2: Verify new function is accessible in `src/data/__init__.py`

```python
__all__ = [
    # ... existing ...,
    "get_student_by_parent_phone"
]
```

---

## Task 3: Add `verify_parent_phone` to `src/agent/academic_tools.py`

**Files:**
- Modify: `src/agent/academic_tools.py`

- [ ] **Step 1: Add new tool function

```python
def verify_parent_phone(phone_number: str) -> str:
    """
    Verify parent phone number and return student info if valid
    """
    from src.data.database import get_student_by_parent_phone
    
    student = get_student_by_parent_phone(phone_number)
    if not student:
        return json.dumps({
            "status": "error",
            "tool": "verify_parent_phone",
            "message": "Không tìm thấy học sinh với số điện thoại này"
        }, ensure_ascii=False, indent=2)
    return json.dumps({
        "status": "success",
        "tool": "verify_parent_phone",
        "student_id": student["student_id"],
        "name": student["name"],
        "class": student["class"],
        "academic_year": student["academic_year"]
    }, ensure_ascii=False, indent=2)
```

- [ ] **Step 2: Add tool to ACADEMIC_TOOLS dict

```python
ACADEMIC_TOOLS = {
    # ... existing tools,
    "verify_parent_phone": verify_parent_phone
}
```

---

## Task 4: Update `server/api.py` for session state and rules

**Files:**
- Modify: `server/api.py`

- [ ] **Step 1: Add session state management
```python
# In-memory session store (temporary)
sessions = {}
```

- [ ] **Step 2: Update QueryRequest model
```python
class QueryRequest(BaseModel):
    query: str
    provider: Optional[str] = None
    max_steps: Optional[int] = 5
    session_id: Optional[str] = None
```

- [ ] **Step 3: Update QueryResponse model
```python
class QueryResponse(BaseModel):
    query: str
    response: str
    provider: str
    model: str
    steps: List[Dict[str, Any]]
    latency_ms: int
    usage: Dict[str, int]
    session_id: str
```

- [ ] **Step 4: Update MockReActProvider to follow rules
- Update generate() to handle:
  - Out-of-scope questions
  - Phone verification flow

- [ ] **Step 5: Update /api/chat endpoint to handle sessions
```python
@app.post("/api/chat", response_model=QueryResponse)
async def chat_endpoint(payload: QueryRequest):
    # ... existing ...
    session_id = payload.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = {
            "verified_student_id": None,
            "verified_parent_phone": None,
            "conversation_history": []
        }
    # ... use session state in MockReActProvider
```

---

## Task 5: Test everything end-to-end

- [ ] Run `python -m uvicorn server.api:app --reload
- [ ] Open browser to http://127.0.0.1:8000
- [ ] Test flow:
  1. Ask "Điểm của học sinh S002"
  2. Should ask for phone number
  3. Enter phone number from DB (e.g., "0936538687")
  4. Should show grades

