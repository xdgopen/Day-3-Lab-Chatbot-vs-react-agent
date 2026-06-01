# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Vũ Tuấn Phương
- **Student ID**: 2A202600772
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: 
  - `src/data/database.py`: Optim hóa các hàm truy vấn cơ sở dữ liệu `get_student_by_name_and_phone` để hỗ trợ lọc bằng `grade_level` tùy chọn. Đồng thời xây dựng hàm `get_student_grades_list_by_phone` giúp bóc tách toàn bộ các dòng điểm tương ứng với các năm học khác nhau (lớp 10, 11, 12) của học sinh dựa trên số điện thoại và tên phụ huynh.
  - `src/agent/academic_tools.py`: Nâng cấp các tool `verify_parent_phone` và `search_student_by_name_and_phone` để tự động phát hiện tình trạng học sinh học nhiều lớp (`multiple_grades = True`) và trả về danh sách các lớp học khả dụng nhằm yêu cầu người dùng xác nhận lớp học chính xác. Đồng thời cập nhật mô tả tham số trong schema tại `get_tool_specs()`.
  - `src/agent/agent.py`: Tối ưu hóa System Prompt của `ReActAgent` bổ sung các quy tắc thông minh (SMART RULES) hướng dẫn Agent cách xử lý khi tool trả về nhiều lớp học và yêu cầu trình bày kết quả bảng điểm chi tiết bằng tiếng Việt tự nhiên chuẩn xác.
  - `server/api.py`: Nâng cấp `MockReActProvider` để lưu vết trạng thái session khi xác thực, xử lý lựa chọn lớp và định dạng bảng điểm cực kỳ chi tiết bằng Tiếng Việt tự nhiên với toàn bộ điểm thành phần hệ số 1, hệ số 2, điểm thi hệ số 3, GPA, xếp loại hạnh kiểm, điểm rèn luyện và nhận xét của giáo viên.

- **Code Highlights**:
  - *Hàm lấy toàn bộ danh sách lớp học của học sinh từ số điện thoại (`src/data/database.py`):*
    ```python
    def get_student_grades_list_by_phone(parent_phone: str, name: str) -> List[Dict[str, Any]]:
        phone = parent_phone.strip()
        query_name = _remove_accents(name)
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM students WHERE parent_phone = ? ORDER BY grade_level ASC",
                (phone,)
            )
            rows = cursor.fetchall()
            matches = []
            for row in rows:
                student_name_clean = _remove_accents(row["name"])
                if query_name in student_name_clean or student_name_clean in query_name:
                    matches.append(dict(row))
            return matches
        finally:
            conn.close()
    ```
  - *Luật trích xuất lớp học thông minh và xử lý đa lớp trong Mock Agent (`server/api.py`):*
    ```python
    # Trích xuất lớp học hỗ trợ đầy đủ bảng mã tiếng Việt
    def extract_grade_level(text: str):
        pattern = r"(?:l[óôơớo]p|lớp|lop)\s*(\d+)"
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1)
        match_num = re.search(r"\b(10|11|12)\b", text)
        return match_num.group(1) if match_num else None
    ```

- **Documentation**: 
  - Khi người dùng hỏi về điểm số, Agent sẽ gọi tool `search_student_by_name_and_phone` hoặc `verify_parent_phone`. 
  - Nếu tool phát hiện học sinh có nhiều hơn 1 lớp học khả dụng và người dùng chưa chỉ định lớp cụ thể trong câu hỏi, tool sẽ trả về kết quả JSON với `"multiple_grades": true` và danh sách các lớp học khả dụng (`"available_grades": ["10", "11", "12"]`).
  - Dựa trên phản hồi này của Observation, Agent sẽ chuyển sang Thought tiếp theo để yêu cầu người dùng xác nhận lớp học chính xác thông qua câu hỏi trong Final Answer.
  - Khi người dùng cung cấp lớp học (ví dụ: "lớp 11"), hệ thống sẽ gọi `get_grades_by_grade_level` để truy xuất chính xác hàng điểm tương ứng của năm học đó.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Hệ thống không thể tìm thấy dữ liệu điểm của học sinh tại lớp 10 hoặc lớp 11, mặc dù tệp CSV `database_master.csv` chứa đầy đủ 3 năm học của mỗi học sinh. Hệ thống cũng liên tục phản hồi *"Vui lòng nhập đúng lớp học"* khi người dùng nhập câu trả lời là `"lớp 11"`.
- **Log Source**: 
  - Dữ liệu in ra từ câu lệnh SQL rà soát:
    ```
    [('S001', 'Lý Duy Giang', '12', '2025-2026', '0990092379')]
    ```
  - Log của Mock Agent tại Bước 5:
    ```
    Thought: Tôi đang chờ người dùng nhập lớp học khả dụng.
    Final Answer: Vui lòng nhập đúng lớp học (lớp 10, lớp 11 hoặc lớp 12) của em Lý Duy Giang.
    ```
- **Diagnosis**: 
  1. Cơ sở dữ liệu SQLite cũ (`data/students.db`) được khởi tạo trước đó có cấu trúc bảng với ràng buộc `student_id TEXT PRIMARY KEY`. Ràng buộc này khiến mỗi học sinh chỉ có thể có duy nhất 1 dòng dữ liệu trong DB. Khi script `init_sqlite_db.py` chạy câu lệnh `INSERT OR REPLACE`, dữ liệu các năm học trước (lớp 10, lớp 11) bị ghi đè hoàn toàn bởi lớp học mới nhất (lớp 12), dẫn tới việc mất dữ liệu lịch sử điểm.
  2. Hàm trích xuất lớp học cũ sử dụng regex `pattern = r"l[óô]p\s*(\d+)"`. Biểu thức này chỉ khớp với `"lóp"` hoặc `"lốp"` mà hoàn toàn bỏ qua ký tự `"lớp"` (chữ `ớ` có dấu mũ và dấu sắc trong tiếng Việt học thuật), dẫn đến việc trích xuất lớp học bị trả về `None` và Agent bị kẹt ở trạng thái yêu cầu nhập lại lớp học.
- **Solution**: 
  1. Thực hiện xóa tệp database cũ `data/students.db` và chạy lại script `python init_sqlite_db.py`. Do script khởi tạo đã có thiết kế chuẩn `UNIQUE(student_id, academic_year)`, database mới đã được nạp thành công đầy đủ **636 dòng** dữ liệu cho cả 3 khối lớp của tất cả học sinh.
  2. Nâng cấp biểu thức chính quy (regex) trích xuất lớp học thành `pattern = r"(?:l[óôơớo]p|lớp|lop)\s*(\d+)"` và bổ sung cơ chế dò số cô lập `\b(10|11|12)\b` để nhận diện chính xác lớp học bất kể định dạng gõ của người dùng.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Khối lệnh `Thought` hoạt động như một phân vùng tư duy nháp (scratchpad). So với Chatbot thông thường thường trả lời ngay lập tức dựa trên phân phối xác suất từ, ReAct Agent sử dụng `Thought` để phân tích các điều kiện ràng buộc học sinh, lập kế hoạch kiểm tra thông tin, thực hiện xác thực bắt buộc bằng số điện thoại trước khi gọi các công cụ truy cập cơ sở dữ liệu. Điều này giúp ngăn chặn hoàn toàn việc rò rỉ dữ liệu hoặc trả lời sai lệch thông tin.
2.  **Reliability**: Trong các trường hợp mô hình LLM bị suy giảm chất lượng sinh do tham số nhiệt độ (temperature) cao, Agent dễ bị kẹt vào vòng lặp vô hạn (infinite loop) do sinh sai định dạng yêu cầu của ReAct (`Action: tool_name(args)`). Ngoài ra, nếu đặc tả công cụ (tool spec) không được viết rõ ràng, Agent có thể đưa ra các tham số sai lệch, dẫn tới việc thực thi công cụ bị lỗi liên tục. Trong các tác vụ đơn giản không cần công cụ, Chatbot thông thường lại cho thấy độ trễ thấp hơn và câu trả lời mượt mà hơn.
3.  **Observation**: Dữ liệu phản hồi (`Observation`) đóng vai trò là nguồn dữ liệu thực tế khách quan (ground-truth) phản hồi từ môi trường. Khi tool trả về trạng thái `"multiple_grades": true`, dữ liệu này lập tức tác động và định hình lại tư duy nháp (`Thought`) của Agent ở bước tiếp theo, buộc nó phải thay đổi kế hoạch từ *"trích xuất điểm trực tiếp"* sang *"đặt câu hỏi lựa chọn lớp"*. Điều này chứng minh khả năng tự điều chỉnh hành vi theo ngữ cảnh động của ReAct Agent.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Triển khai kiến trúc xử lý tác vụ bất đồng bộ (Asynchronous Task Queue) sử dụng Celery kết hợp Redis/RabbitMQ để quản lý các tác vụ gọi tool tốn nhiều tài nguyên hoặc thời gian (như tạo lời khuyên học tập, phân tích xu hướng). Sử dụng cơ chế cache kết quả tra cứu dữ liệu điểm của học sinh để giảm tải cho SQLite.
- **Safety**: Xây dựng một lớp kiểm duyệt độc lập (Guardrails LLM / Supervisor Agent) để rà soát toàn bộ đầu vào của người dùng (ngăn chặn Prompt Injection) và đầu ra của Agent trước khi hiển thị cho phụ huynh để đảm bảo bảo mật thông tin cá nhân (PII) như số điện thoại, email, địa chỉ nhà.
- **Performance**: Chuyển đổi từ SQLite sang hệ quản trị cơ sở dữ liệu mạnh mẽ như PostgreSQL, bổ sung các chỉ mục (indexes) trên các cột thường xuyên tìm kiếm (`parent_phone`, `student_id`). Đối với hệ thống có hàng trăm công cụ quản lý trường học phức tạp, áp dụng kỹ thuật tìm kiếm ngữ nghĩa (Semantic Vector Search) trên bộ mô tả công cụ để tự động kích hoạt và chọn công cụ phù hợp thay vì nạp toàn bộ danh sách specs vào system prompt nhằm tiết kiệm tối đa chi phí token.
