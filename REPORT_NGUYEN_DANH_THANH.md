# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Nguyễn Danh Thành]
- **Student ID**: [2A202600581]
- **Date**: [2026-06-01]

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implemented**:
  - `agent.py`: Thiết lập vòng lặp ReAct cốt lõi trong hàm `run()`, xây dựng bộ phân tích cú pháp biểu thức chính quy (`_parse_action()`) để tách biệt rõ ràng giữa Thought và Action, hiện thực bộ trích xuất câu trả lời cuối cùng (`_extract_final_answer()`), xử lý tách đối số công cụ (`_parse_tool_args()`) và đóng gói quan sát của công cụ (`_execute_tool()`). Đồng thời tích hợp ghi nhận telemetry và đo lường tài nguyên sử dụng (`tracker.track_request()`).
  - `tools.py`: Xây dựng các công cụ tra cứu thông tin học sinh (`search_student`, `get_student_points`, `load_students`, và mô tả đặc tả công cụ qua `get_tool_specs()`). Sửa lỗi mã hóa encoding để loại bỏ Byte Order Mark (BOM).
  - `baseline_chatbot.py`: Phát triển chatbot cơ sở để đối chiếu hiệu quả suy luận thực tế.
  - `test_agent.py` & `test_baseline.py`: Xây dựng các kịch bản kiểm thử nhằm đánh giá độ chính xác của mô hình trong các trường hợp dữ liệu hợp lệ, không hợp lệ và bị trùng lặp thông tin.

- **Code Highlights**:
  - **Vòng lặp ReAct và cơ chế tự sửa lỗi phân tích**: Đảm bảo khi mô hình sinh ra định dạng không chính xác, lỗi này sẽ được trả về dưới dạng Observation để mô hình tự nhận diện và điều chỉnh ở bước sau.
    ```python
    # Trích từ agent.py
    thought, action_name, action_args = self._parse_action(llm_output)
    if "final answer" in llm_output.lower():
        final_answer = self._extract_final_answer(llm_output)
        break
    if action_name:
        observation = self._execute_tool(action_name, action_args)
    else:
        observation = "Error: Could not parse action. Please follow the format: Action: tool_name(param_name=value)"
    ```
  - **Regex Parser để bóc tách Thought và Action**: Sử dụng các biểu thức chính quy linh hoạt để định vị chính xác nội dung Thought và Action của LLM.
    ```python
    # Trích từ agent.py
    thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|Final Answer:|$)", llm_output, re.IGNORECASE | re.DOTALL)
    action_match = re.search(r"Action:\s*(\w+)\s*\((.*?)\)", llm_output, re.IGNORECASE)
    ```

- **Documentation**:
  Class `ReActAgent` quản lý vòng lặp suy luận qua lịch sử hội thoại (`history`):
  1. Hàm `_build_prompt` tiến hành tuần tự hóa các bước suy luận trước đó (gồm Thought, Action, Observation).
  2. Prompt này được gửi kèm với System Prompt chứa đặc tả công cụ định dạng JSON Schema đến mô hình LLM.
  3. Khi LLM phản hồi, Agent phân tích hành động cần thực thi. Nếu phát hiện lệnh gọi công cụ hợp lệ, Agent sẽ kích hoạt thông qua dictionary ánh xạ `TOOLS` và ghi nhận kết quả.
  4. Kết quả thực thi dưới dạng Observation sẽ được nối vào lịch sử để chuẩn bị cho lượt suy luận kế tiếp.
  5. Vòng lặp dừng lại khi LLM trả về `Final Answer` hoặc đạt số bước giới hạn `max_steps`.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**:
  Hệ thống chạy thử nghiệm ReAct Agent liên tục gặp lỗi thực thi công cụ trong hàm tìm kiếm hoặc lấy điểm học sinh, ghi nhận thông báo lỗi liên quan đến `'student_id'`. Do công cụ trả về kết quả lỗi, Agent không nhận được thông tin cần thiết, dẫn đến việc mô hình đoán mò tham số hoặc chạy vượt quá giới hạn số bước.
- **Log Source**:
  Trích từ file log:
  ```json
  {"timestamp": "2026-06-01T09:25:27.895631", "event": "RESULT", "data": {"result": {"status": "error", "message": "Error searching for student: 'student_id'", "matches": [], "timestamp": "2026-06-01T16:25:27.895440", "tool": "search_student"}}}
  ```
  Sau đó Agent cố gắng gọi lại với tham số sai định dạng:
  ```json
  {"timestamp": "2026-06-01T09:25:31.386257", "event": "TOOL_EXECUTION_ERROR", "data": {"tool": "search_student", "args": "student_id=Alice Johnson", "error": "search_student() got an unexpected keyword argument 'student_id'"}}
  ```
- **Diagnosis**:
  Tệp dữ liệu CSV lưu danh sách học sinh bị dính ký tự UTF-8 BOM ở đầu tệp. Khi Python đọc file bằng encoding mặc định `utf-8`, tiêu đề cột đầu tiên được nhận dạng thành `\ufeffstudent_id` thay vì `student_id`. Do đó, các dòng dữ liệu do `csv.DictReader` tạo ra không tồn tại thuộc tính `'student_id'`, dẫn đến ngoại lệ `KeyError: 'student_id'` khi mã nguồn công cụ truy cập dữ liệu để định dạng đầu ra.
- **Solution**:
  Cập nhật mã lệnh mở file CSV trong hàm `load_students()` của tệp `tools.py` sang mã hóa `encoding="utf-8-sig"`. Bộ giải mã này sẽ tự động loại bỏ ký tự BOM ở đầu luồng dữ liệu, đưa cột tiêu đề về đúng tên `student_id` và khắc phục triệt để lỗi truy xuất.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1. **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?
   Khối `Thought` đóng vai trò như một bảng nháp suy nghĩ (Chain of Thought), thúc đẩy mô hình thiết lập kế hoạch rõ ràng trước khi gọi công cụ. Ví dụ, để tra cứu điểm số của học sinh Alice Johnson, Agent sử dụng Thought để lập luận rằng nó cần tìm mã số học sinh (ID) thông qua công cụ tìm kiếm trước, sau đó mới dùng ID đó để truy xuất điểm số. Trái lại, chatbot thông thường không có bảng nháp và công cụ hỗ trợ, dẫn tới việc phản hồi ngay lập tức bằng các dữ liệu tự bịa ra (hallucination) dựa trên xác suất từ ngữ của mô hình.

2. **Reliability**: In which cases did the Agent actually perform *worse* than the Chatbot?
   ReAct Agent có thể hoạt động kém hơn chatbot thông thường trong các tình huống sau:
   - **Lỗi định dạng đầu ra của LLM**: Khi LLM sinh lỗi cú pháp định dạng (ví dụ như bỏ quên từ khóa `Action:` hoặc gọi nhiều công cụ cùng lúc), làm cho bộ phân tích cú pháp thất bại và Agent rơi vào vòng lặp sửa lỗi cho đến khi vượt quá giới hạn số bước.
   - **Hạn chế tài nguyên và hạn ngạch API**: Các lỗi kết nối mạng hoặc lỗi hết hạn mức (quota) từ nhà cung cấp mô hình làm suy giảm độ tin cậy của Agent do quy trình thực thi ReAct phụ thuộc vào nhiều lượt gọi API liên tục.
   - **Các truy vấn đơn giản**: Với các câu hỏi cơ bản hoặc kiến thức chung, việc sử dụng ReAct Agent tạo ra độ trễ (latency) lớn và tiêu tốn nhiều token vô ích so với phản hồi trực tiếp của chatbot.

3. **Observation**: How did the environment feedback (observations) influence the next steps?
   Các quan sát từ môi trường đóng vai trò phản hồi neo giữ thông tin thực tế. Khi Agent tìm kiếm một cái tên bị trùng lắp (ví dụ: John Smith có hai người trong danh sách), thông tin trả về từ Observation sẽ báo cho Agent biết có sự mơ hồ. Từ đó, Agent phân tích và điều chỉnh bước tiếp theo để lấy điểm của cả hai mã học sinh hoặc phản hồi lại sự trùng khớp này cho người dùng, thay vì tự ý chọn ngẫu nhiên một kết quả.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**:
  Chuyển dịch từ vòng lặp tuyến tính sang kiến trúc đồ thị trạng thái phức tạp (như LangGraph) để hỗ trợ các rẽ nhánh logic nâng cao và gọi công cụ song song. Triển khai cơ chế tìm kiếm công cụ theo ngữ nghĩa (Semantic Tool Retrieval) để chỉ nạp các công cụ phù hợp nhất vào prompt, tránh làm quá tải ngữ cảnh của LLM khi hệ thống tích hợp hàng trăm công cụ khác nhau.
- **Safety**:
  Tích hợp các lớp kiểm tra dữ liệu đầu vào nghiêm ngặt (như Pydantic) để lọc mã độc hoặc dữ liệu lạ trong tham số truyền vào công cụ. Sử dụng bộ giám sát độc lập (như Supervisor LLM hoặc các bộ lọc an toàn) để kiểm định các hành động và câu trả lời của Agent trước khi gửi tới người dùng cuối.
- **Performance**:
  Thiết lập lớp bộ nhớ đệm (như Redis) để lưu trữ nhanh kết quả của các yêu cầu tìm kiếm lặp lại nhằm giảm thiểu số lần gọi API và truy xuất ổ đĩa. Áp dụng cơ chế định tuyến mô hình (model routing) để điều phối các tác vụ đơn giản cho mô hình nhẹ, giá rẻ xử lý, và chỉ dùng các mô hình lớn cho các tác vụ suy luận ReAct phức tạp.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
