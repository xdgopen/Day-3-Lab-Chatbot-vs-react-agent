# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: [Nhóm 34]
- **Team Members**: [Nguyễn Danh Thành-2A202600581, Vũ Tuấn Phương-2A202600772, Vũ Ngọc Vinh-2A202600864]
- **Deployment Date**: [2026-06-01]

---

## 1. Executive Summary

*Brief overview of the agent's goal and success rate compared to the baseline chatbot.*

- **Success Rate**: 100% đối với ReAct Agent (5/5 câu trả lời chính xác và xử lý được các trường hợp đặc biệt), so với 40% của Baseline Chatbot (2/5 câu hỏi đúng, gặp hiện tượng bịa đặt thông tin ở các câu hỏi học sinh không tồn tại và gặp khó khăn khi thông tin bị trùng lắp).
- **Key Outcome**: Hệ thống Agent của chúng tôi đạt tỷ lệ chính xác cao hơn 60% so với chatbot cơ sở nhờ sử dụng thành công công cụ tìm kiếm dữ liệu thực tế và lấy điểm, loại bỏ hoàn toàn các câu trả lời bịa đặt đối với học sinh không có trong hệ thống và phân định rõ ràng khi có hai học sinh trùng tên.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
*Diagram or description of the Thought-Action-Observation loop.*

Quy trình hoạt động của vòng lặp ReAct được thực hiện tuần tự như sau:
1. **Khởi tạo**: Nhận câu hỏi từ người dùng, nạp System Prompt chứa đặc tả công cụ dưới dạng JSON Schema.
2. **Suy luận (Thought)**: LLM phân tích câu hỏi và lịch sử để lên kế hoạch hành động.
3. **Hành động (Action)**: LLM gọi công cụ theo định dạng `Action: tên_công_cụ(tham_số=giá_trị)`.
4. **Thực thi & Quan sát (Observation)**: Agent trích xuất cú pháp gọi công cụ, thực thi code Python tương ứng và trả kết quả dưới dạng chuỗi Observation cho LLM.
5. **Lặp lại hoặc Kết thúc**: Vòng lặp tiếp diễn cho đến khi mô hình sinh ra `Final Answer` hoặc đạt số bước giới hạn tối đa (5 bước).

Sơ đồ quy trình hoạt động:
```
[Câu hỏi người dùng] -> [Thought] -> [Action] -> [Thực thi công cụ] -> [Observation] -|
     ^                                                                                |
     |---------------------- Cập nhật lịch sử hội thoại -------------------------------|
                                    |
                            (Nếu có Final Answer)
                                    v
                           [Câu trả lời cuối cùng]
```

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `search_student` | `name: string` | Tìm kiếm một hoặc nhiều học sinh theo tên (không phân biệt hoa thường, cho phép khớp một phần). Trả về danh sách học sinh kèm ID học sinh. |
| `get_student_points` | `student_id: string` | Truy vấn điểm số chi tiết và môn học của một học sinh cụ thể dựa trên ID học sinh duy nhất (ví dụ: S001). |

### 2.3 LLM Providers Used
- **Primary**: Phi-3 (Mô hình chạy cục bộ thông qua LocalProvider) / GPT-4o (OpenAIProvider)
- **Secondary (Backup)**: Gemini Pro (GeminiProvider)

---

## 3. Telemetry & Performance Dashboard

*Analyze the industry metrics collected during the final test run.*

- **Average Latency (P50)**: Khoảng 3,450ms cho mỗi bước suy luận và gọi công cụ.
- **Max Latency (P99)**: Khoảng 18,520ms đối với các tác vụ phức tạp cần thực hiện nhiều bước suy luận và gọi công cụ tuần tự (như xử lý trường hợp trùng tên hoặc tự phục hồi khi lỗi định dạng).
- **Average Tokens per Task**: Khoảng 1,200 tokens (do lưu trữ lịch sử các bước Thought - Action - Observation tích lũy qua từng vòng lặp).
- **Total Cost of Test Suite**: Khoảng $0.02 (khi chạy thử nghiệm qua API thương mại) hoặc hoàn toàn miễn phí khi chạy cục bộ bằng mô hình Phi-3.

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed.*

### Case Study: Lỗi mã hóa CSV (BOM KeyError)
- **Input**: "What are Alice Johnson's points?"
- **Observation**: Công cụ phản hồi thông báo lỗi thực thi: `Tool error: Error searching for student: 'student_id'`
- **Root Cause**: Tệp tin CSV nguồn chứa dữ liệu học sinh được lưu ở định dạng mã hóa UTF-8 có chứa ký tự Byte Order Mark (BOM). Khi Python đọc tệp tin với cấu hình mặc định `utf-8`, ký tự BOM này dính vào tên trường dữ liệu đầu tiên khiến nó bị hiểu sai thành `\ufeffstudent_id` thay vì `student_id`. Hệ quả là dòng dữ liệu sau khi phân tích không có khóa `'student_id'` hợp lệ, gây ra ngoại lệ `KeyError: 'student_id'` khi mã nguồn công cụ truy cập để đóng gói dữ liệu trả về.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**: Cập nhật System Prompt từ hướng dẫn chung chung sang hướng dẫn định dạng nghiêm ngặt có kèm ví dụ cụ thể của cú pháp gọi công cụ: `Action: tên_công_cụ(tham_số=giá_trị)`.
- **Result**: Giảm thiểu hoàn toàn tỷ lệ lỗi phân tích cú pháp (Parsing Error) từ 40% xuống dưới 5% đối với các mô hình nhỏ.

### Experiment 2 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Q | Correct (Đoán đúng theo kiến thức nền) | Correct (Truy xuất từ dữ liệu thực tế) | Draw |
| Multi-step | Hallucinated (Bịa đặt điểm của học sinh không tồn tại) | Correct (Trả về kết quả học sinh không tìm thấy) | **Agent** |
| Ambiguous | Picked one (Chỉ chọn một trong hai học sinh trùng tên John Smith) | Correct (Phát hiện trùng lặp và liệt kê thông tin cả hai người) | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**: Thực hiện kiểm tra dữ liệu và làm sạch đầu vào đối với các tham số do mô hình LLM truyền vào trước khi thực thi mã lệnh Python để tránh rủi ro chèn ép lệnh gọi hệ thống.
- **Guardrails**: Thiết lập giới hạn nghiêm ngặt số bước lặp tối đa (`max_steps` = 5) để phòng ngừa vòng lặp vô hạn gây tiêu tốn tài nguyên và tăng chi phí ngoài ý muốn khi LLM bị kẹt.
- **Scaling**: Thay thế vòng lặp đơn bằng kiến trúc đồ thị quản lý tác vụ (ví dụ: LangGraph) nhằm tối ưu hóa việc phân nhánh logic phức tạp, gọi nhiều công cụ song song và tích hợp bộ nhớ cache Redis cho các truy vấn trùng lặp.

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
