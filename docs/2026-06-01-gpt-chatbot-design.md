
# Design Spec: GPT-Style Chatbot for Student Grades with Rules

## 1. Overview
This spec describes implementing a GPT-style chat interface with the following key features:
- Dark theme, GPT-inspired design
- Collapsible right sidebar for logs (showing ReAct steps)
- Full implementation of RULES.md (scope, phone verification, etc.)
- Session-based conversation state management

## 2. UI Design
### 2.1 Layout
- **Header**: Title "Student Grade Assistant", small rules reminder
- **Left/Center (Main Chat)**:
  - Chat messages container (scrollable)
  - Each message has avatar, name, text
- **Right Sidebar**:
  - Collapsible panel with "Logs" tab
  - Shows full ReAct history: thoughts, actions, observations
  - Expand/collapse button
- **Bottom Input Bar**:
  - Text area (multi-line)
  - Send button
  - Provider selector (moved from sidebar, or keep in sidebar?)

### 2.2 Color Scheme (GPT Dark Mode)
- Background: `#0f0f0f` (dark gray)
- Chat bubbles: User `#2d2d2d`, Assistant `#1e1e1e`
- Text: `#e0e0e0`
- Primary accent: `#10a37f` (GPT green)

## 3. Rules Implementation (RULES.md)
### 3.1 Rule 1: Out-of-Scope Questions
- Check if query is about grades/student info
- If not:
  ```
  Xin lỗi, tôi chỉ có thể trả lời các câu hỏi về điểm số và thông tin học tập. Vui lòng hỏi về học sinh, điểm các môn học hoặc GPA tổng hợp.
  ```

### 3.2 Rule 2: Parent Phone Verification
- Before answering any grade-related question:
  1. Ask user: "Vui lòng cung cấp số điện thoại phụ huynh để xác thực"
  2. When user provides phone number:
     a. Check if it matches any student's `parent_phone` in DB
     b. If match: proceed to answer grade questions for that student
     c. If no match: "Xin lỗi, số điện thoại không khớp với thông tin học sinh trong hệ thống. Vui lòng kiểm tra lại."
  3. Once verified, remember the student/phone for the session

### 3.3 Rule 3: No Sensitive Info
- Never reveal `parent_phone` or `teacher_remarks` (if sensitive)
- Only show: name, student ID, class, grades, GPA, conduct

## 4. Backend Implementation
### 4.1 Session State
- Store per-session state (in-memory for now):
  ```javascript
  session = {
    verified_student_id: string | null,
    verified_parent_phone: string | null,
    conversation_history: array
  }
  ```
- Use session tokens (or just in-memory for simplicity)

### 4.2 API Changes
- Update `/api/chat` endpoint to accept `session_id` (optional)
- Return `session_id` in response to maintain state
- Add tool: `verify_parent_phone(phone_number)` → returns student info if valid

### 4.3 MockReActProvider Updates
- Implement scope check
- Implement phone verification flow
- Follow all rules from RULES.md

## 5. Frontend Implementation
- Replace `server/static/index.html` with GPT-style design
- Implement sidebar collapse/expand
- Maintain session ID in localStorage
- Render chat messages and logs correctly

## 6. File Changes
- New/Updated Files:
  - `server/api.py`: Update chat endpoint, add session handling
  - `server/static/index.html`: Complete UI redesign
  - `src/agent/academic_tools.py`: Add `verify_parent_phone` tool
  - `src/data/database.py`: Add function to get student by parent phone
