# PRODUCT REQUIREMENT DOCUMENT (PRD)
## DỰ ÁN: HỆ THỐNG TRỢ LÝ AI HỖ TRỢ PHỤ HUYNH TRA CỨU HỌC TẬP (PARENT ACADEMIC AGENT)
### 📋 TÀI LIỆU ĐÃ ĐƯỢC AUDIT THEO TIÊU CHÍ ĐÁNH GIÁ CỦA SCORING.MD

Tài liệu Đặc tả Yêu cầu Sản phẩm (PRD) này mô tả chi tiết các yêu cầu nghiệp vụ, cấu trúc dữ liệu và danh sách chức năng của hệ thống Trợ lý Trí tuệ Nhân tạo (AI Agent) phục vụ Phụ huynh học sinh tra cứu học tập. 

**Lưu ý đặc biệt**: Tài liệu này đã được kiểm toán (audit) và tích hợp toàn bộ các tiêu chí chấm điểm từ file [SCORING.md](file:///d:/VinAI-Lab/Day-3-Lab-Chatbot-vs-react-agent/SCORING.md) nhằm đảm bảo dự án đạt điểm tối đa **100/100** (bao gồm **60 điểm Nhóm** và **40 điểm Cá nhân**).

---

## 🎯 1. BẢN ĐỒ ĐÁP ỨNG TIÊU CHÍ CHẤM ĐIỂM (SCORING AUDIT MATRIX)

Dưới đây là bảng đối chiếu giữa các yêu cầu trong [SCORING.md](file:///d:/VinAI-Lab/Day-3-Lab-Chatbot-vs-react-agent/SCORING.md) và các chương/mục thiết kế kỹ thuật tương ứng trong tài liệu PRD này:

| Hạng mục chấm điểm | Số điểm | Yêu cầu kỹ thuật trong PRD | Vị trí đặc tả trong PRD |
| :--- | :---: | :--- | :--- |
| **Chatbot Baseline** | **2đ** | Xây dựng Chatbot thông thường không gọi tool để đối chứng. | Mục 3.1 |
| **Agent v1 (Working)** | **7đ** | Chu trình ReAct cơ bản hoạt động ổn định với ít nhất 2 tools. | Mục 3.2 & Mục 4 |
| **Agent v2 (Improved)** | **7đ** | Cơ chế tự sửa sai, Few-shot prompt, tối ưu hóa parsing. | Mục 3.3 |
| **Tool Design Evolution** | **4đ** | Tiến hóa mô tả tool (Tool Spec) từ v1 lên v2 rõ ràng. | Mục 5 |
| **Trace Quality** | **9đ** | Lưu đầy đủ file log JSON cho cả ca thành công và thất bại. | Mục 6 |
| **Evaluation & Analysis** | **7đ** | Chạy kiểm thử tự động, so sánh số liệu (Latency, Token, Cost). | Mục 7 |
| **Flowchart & Insight** | **5đ** | Sơ đồ Mermaid biểu diễn chu trình xử lý và bài học rút ra. | Mục 8 |
| **Code Quality** | **4đ** | Code tường minh, mô-đun hóa, tích hợp telemetry chặt chẽ. | Mục 9 |
| **Extra Monitoring (Bonus)** | **+3đ** | Giám sát tỷ lệ token, tính toán chi phí API động theo thời gian thực. | Mục 6.3 |
| **Extra Tools (Bonus)** | **+2đ** | Thêm công cụ tư vấn định hướng học tập tự động. | Mục 5.4 |
| **Failure Handling (Bonus)**| **+3đ** | Cơ chế Retry động, an toàn chống vòng lặp vô tận (max_steps). | Mục 3.3.3 |
| **Ablation Studies (Bonus)**| **+2đ** | Thử nghiệm so sánh hiệu năng Prompt v1 vs Prompt v2. | Mục 7.2 |
| **Individual Score** | **40đ** | Cung cấp định danh tác giả module để viết báo cáo cá nhân. | Mục 10 |

---

## 💾 2. ĐẶC TẢ CẤU TRÚC CƠ SỞ DỮ LIỆU (DATABASE SCHEMA SPECIFICATION)

Để phục vụ cho yêu cầu tra cứu toàn diện, cơ sở dữ liệu học tập được thiết kế chi tiết gồm 3 bảng chính: **Hồ sơ Học sinh (Students)**, **Kết quả Học tập (Academic Grades)** và **Chuyên cần - Rèn luyện (Conduct & Attendance)**.

### 2.1 Bảng Hồ sơ Học sinh (`STUDENTS`)
Bảng này lưu trữ thông tin định danh và quản lý cơ bản của từng học sinh.

```python
STUDENTS = {
    "S001": {"name": "Nguyen Van An", "class": "10A1", "parent": "Nguyen Van Binh", "parent_phone": "0901234567"},
    "S002": {"name": "Tran Thi Binh", "class": "11B2", "parent": "Tran Van Cuong", "parent_phone": "0987654321"},
    "S003": {"name": "Le Hoang Chung", "class": "12C1", "parent": "Le Van Dung", "parent_phone": "0912345678"}
}
```

### 2.2 Bảng Kết quả Học tập (`GRADES`)
Lưu trữ thông tin điểm số của **đầy đủ 8 môn học**: **Toán (Math), Văn (Literature), Anh (English), Lý (Physics), Hóa (Chemistry), Sinh (Biology), Sử (History), Địa (Geography)**. 

Mỗi môn học gồm 3 cột điểm hệ số:
*   `factor_1` (Hệ số 1 - Kiểm tra miệng/15p) - Mảng số thực.
*   `factor_2` (Hệ số 2 - Kiểm tra giữa kỳ) - Mảng số thực.
*   `factor_3` (Hệ số 3 - Kiểm tra cuối kỳ) - Số thực đơn lẻ.

```python
GRADES = {
    "S001": {
        "Math": {"factor_1": [8.0, 7.5], "factor_2": [8.5], "factor_3": 8.0},
        "Literature": {"factor_1": [7.0, 8.0], "factor_2": [7.5], "factor_3": 7.0},
        "English": {"factor_1": [8.5, 9.0], "factor_2": [8.0], "factor_3": 8.5},
        "Physics": {"factor_1": [6.0, 7.0], "factor_2": [6.5], "factor_3": 7.0},
        "Chemistry": {"factor_1": [7.5, 8.0], "factor_2": [7.0], "factor_3": 8.0},
        "Biology": {"factor_1": [8.0, 8.5], "factor_2": [8.0], "factor_3": 8.5},
        "History": {"factor_1": [9.0, 9.5], "factor_2": [9.0], "factor_3": 9.5},
        "Geography": {"factor_1": [8.5, 9.0], "factor_2": [8.5], "factor_3": 9.0}
    },
    "S002": {
        "Math": {"factor_1": [9.5, 10.0], "factor_2": [9.5], "factor_3": 10.0},
        "Literature": {"factor_1": [8.5, 9.0], "factor_2": [8.5], "factor_3": 9.0},
        "English": {"factor_1": [9.5, 10.0], "factor_2": [9.5], "factor_3": 10.0},
        "Physics": {"factor_1": [9.0, 9.5], "factor_2": [9.0], "factor_3": 9.5},
        "Chemistry": {"factor_1": [9.5, 9.5], "factor_2": [9.0], "factor_3": 9.5},
        "Biology": {"factor_1": [9.0, 9.0], "factor_2": [9.5], "factor_3": 9.0},
        "History": {"factor_1": [8.5, 9.0], "factor_2": [8.5], "factor_3": 9.0},
        "Geography": {"factor_1": [9.0, 9.0], "factor_2": [9.0], "factor_3": 9.5}
    },
    "S003": {
        "Math": {"factor_1": [5.0, 5.5], "factor_2": [6.0], "factor_3": 5.5},
        "Literature": {"factor_1": [6.0, 6.5], "factor_2": [6.0], "factor_3": 6.5},
        "English": {"factor_1": [4.5, 5.0], "factor_2": [5.0], "factor_3": 4.5},
        "Physics": {"factor_1": [5.0, 5.0], "factor_2": [5.5], "factor_3": 5.0},
        "Chemistry": {"factor_1": [4.0, 5.0], "factor_2": [4.5], "factor_3": 5.0},
        "Biology": {"factor_1": [6.0, 5.5], "factor_2": [6.0], "factor_3": 5.5},
        "History": {"factor_1": [7.0, 6.5], "factor_2": [7.0], "factor_3": 6.5},
        "Geography": {"factor_1": [6.5, 7.0], "factor_2": [6.5], "factor_3": 7.0}
    }
}
```

#### 📐 Công thức tính Điểm trung bình học phần (GPA môn):
$$\text{GPA Môn} = \frac{\sum(\text{Điểm HS1}) + 2 \times \sum(\text{Điểm HS2}) + 3 \times \text{Điểm HS3}}{\text{Tổng số lượng đầu điểm tính theo hệ số}}$$

### 2.3 Bảng Chuyên cần & Rèn luyện (`CONDUCT`)

```python
CONDUCT = {
    "S001": {"excused_absences": 2, "unexcused_absences": 1, "behavior_score": 85, "conduct_grade": "Tốt", "teacher_remarks": "Chăm ngoan, có ý thức học tập, tích cực phát biểu."},
    "S002": {"excused_absences": 0, "unexcused_absences": 0, "behavior_score": 98, "conduct_grade": "Tốt", "teacher_remarks": "Lớp trưởng gương mẫu, xuất sắc toàn diện, đóng góp tích cực cho phong trào."},
    "S003": {"excused_absences": 5, "unexcused_absences": 4, "behavior_score": 58, "conduct_grade": "Trung bình", "teacher_remarks": "Thường xuyên đi muộn, nghỉ học không phép nhiều lần. Cần gia đình phối hợp nhắc nhở gấp."}
}
```

---

## 🚀 3. LỘ TRÌNH TIẾN HÓA VÀ PHÁT TRIỂN CHỨC NĂNG

Hệ thống được thiết kế tiến hóa qua 3 phiên bản nhằm đáp ứng trọn vẹn rubrics về kiểm chứng và so sánh.

```
[Chatbot Baseline]       -->      [Agent v1 (Working)]      -->      [Agent v2 (Improved)]
- Gọi trực tiếp LLM               - ReAct Loop (Thought/Act)         - Hỗ trợ Few-shot Prompt
- Không có quyền gọi Tool          - 3 công cụ tra cứu cơ bản         - Tìm kiếm mờ fuzzy match
- Dễ bịa đặt dữ liệu              - Parser Regex cơ bản              - Tự phục hồi khi parser lỗi
```

### 3.1 Phiên bản Chatbot Baseline (Yêu cầu: 2 điểm)
*   **Mô tả**: Thiết lập lớp `SimpleChatbot` truy vấn trực tiếp LLM (OpenAI/Gemini).
*   **Mục tiêu**: Làm đối chứng so sánh. Chứng minh LLM không thể trả lời đúng điểm môn Sinh học hay số ngày nghỉ của học sinh `S003` nếu không có công cụ bổ trợ.

### 3.2 Phiên bản Agent v1 - Chu trình ReAct Cơ bản (Yêu cầu: 7 điểm)
*   **Mô tả**: Triển khai vòng lặp ReAct (`Thought -> Action -> Observation`) trong file `src/agent/agent.py`.
*   **Hộp công cụ**: Hỗ trợ 3 công cụ tra cứu cốt lõi:
    1.  `lookup_student_id(name)`: Trả về mã học sinh.
    2.  `get_academic_grades(student_id, subject)`: Lấy dữ liệu điểm các môn.
    3.  `get_conduct_report(student_id)`: Trích xuất số buổi nghỉ và nhận xét GVCN.
*   **Hạn chế**: Sử dụng parser Regex đơn giản, dễ bị crash khi LLM sinh sai cú pháp `Action: tool_name(arg)` hoặc phản hồi markdown codeblocks.

### 3.3 Phiên bản Agent v2 - Cải tiến Độ tin cậy (Yêu cầu: 7 điểm)

#### 3.3.1 Kỹ thuật Prompting Few-Shot nâng cao (Ablation Experiment - Yêu cầu: +2 điểm)
Tích hợp kịch bản suy luận mẫu (Few-shot traces) vào System Prompt để dẫn dắt LLM cách gọi tuần tự từ việc tìm ID học sinh đến tra cứu điểm số và đưa ra câu trả lời chi tiết.

#### 3.3.2 Cải tiến Parser Robust & Cơ chế Tìm kiếm Mờ (Fuzzy Matching)
*   Nâng cấp Regex để chấp nhận cả nháy đơn `'`, nháy kép `"`, dấu ngoặc nhọn hoặc khoảng trắng thừa trong lệnh gọi của LLM.
*   Nâng cấp công cụ `lookup_student_id` để loại bỏ dấu tiếng Việt, chấp nhận so khớp tương đối (ví dụ phụ huynh nhập `"chung"` vẫn tìm ra `"Le Hoang Chung"`).

#### 3.3.3 Cơ chế Tự sửa lỗi & Ranh giới an toàn (Failure Handling - Yêu cầu: +3 điểm)
*   **Loop Guard**: Giới hạn tối đa `max_steps = 6` để chặn đứng việc lặp vô tận gây tốn chi phí.
*   **Self-Correction**: Nếu Tool quăng lỗi ngoại lệ (ví dụ: điểm môn học trống hoặc ID sai), Agent sẽ gửi thông điệp lỗi chi tiết vào `Observation` để LLM tự động điều chỉnh và thử lại công cụ khác thay vì dừng hệ thống đột ngột.

---

## 🛠 4. THIẾT KẾ CHI TIẾT DANH SÁCH TOOLS (TIẾN HÓA CÔNG CỤ - tiến hóa từ v1 sang v2)

Đặc tả này làm nổi bật quá trình **Tool Design Evolution (4 điểm)** để chứng minh nhóm có sự phát triển tư duy thiết kế API qua các phiên bản.

### 4.1 Danh sách Công cụ Phiên bản v1 (Sơ khai)
*   **`lookup_student_id` (v1)**: Chỉ so khớp chính xác 100% chuỗi ký tự viết hoa/thường. Nhập sai chữ cái đầu sẽ trả về lỗi không tìm thấy.
*   **`get_academic_grades` (v1)**: Chỉ trả về điểm số thô của một môn được yêu cầu cụ thể.
*   **`get_conduct_report` (v1)**: Trả về chuỗi thông tin chuyên cần thô.

### 4.2 Danh sách Công cụ Phiên bản v2 (Thông minh - 8 môn học & Phân tích)

#### 4.2.1 `lookup_student_id` (v2) - Tích hợp so khớp mờ
*   **Đầu vào**: `student_name` (string)
*   **Logic xử lý**:
    1.  Chuyển chuỗi về chữ thường và loại bỏ toàn bộ dấu tiếng Việt (ví dụ: `"nguyễn văn an"` $\rightarrow$ `"nguyen van an"`).
    2.  Duyệt qua danh sách học sinh, so khớp khoảng cách chuỗi hoặc kiểm tra chứa ký tự con.
*   **Đầu ra**: Chuỗi JSON chứa `student_id` chính xác.

#### 4.2.2 `get_academic_grades` (v2) - Tự động tính GPA & Cảnh báo học lực
*   **Đầu vào**: `student_id` (string), `subject` (string: `"Math"`, `"Literature"`, `"English"`, `"Physics"`, `"Chemistry"`, `"Biology"`, `"History"`, `"Geography"`, hoặc `"All"`).
*   **Logic xử lý**: 
    1. Truy xuất dữ liệu điểm số các môn từ Mock DB.
    2. Nếu `subject = "All"`, tính toán GPA cho từng môn học dựa trên trọng số hệ số 1, 2, 3, đồng thời tính GPA chung toàn diện.
    3. Đánh giá cảnh báo học lực nếu có môn học có điểm trung bình học phần $< 5.0$.
*   **Đầu ra**: Bản báo cáo điểm số chi tiết kèm GPA môn và cảnh báo dưới dạng JSON.

#### 4.2.3 `get_conduct_report` (v2) - Cảnh báo chuyên cần sớm
*   **Đầu vào**: `student_id` (string)
*   **Logic xử lý**:
    1. Lấy số ngày nghỉ phép, không phép, hành kiểm và nhận xét GVCN.
    2. Nếu số ngày nghỉ không phép $> 3$ buổi, tự động gắn nhãn cảnh báo đỏ kỷ luật.
*   **Đầu ra**: JSON báo cáo chi tiết rèn luyện.

#### 4.2.4 (Bonus Tool) `generate_study_advice` - Định hướng học tập (+2 điểm)
*   **Đầu vào**: `student_id` (string)
*   **Logic xử lý**: Phân tích môn học nào học sinh có GPA thấp nhất và kết hợp nhận xét rèn luyện của GVCN để đưa ra đề xuất lộ trình cải thiện điểm số thông minh.

---

## 📈 5. THIẾT KẾ GIÁM SÁT HỆ THỐNG VÀ CHI PHÍ (TRACE QUALITY & MONITORING)

Phần này đặc tả cấu trúc ghi nhận vết thực thi để đáp ứng tuyệt đối tiêu chuẩn **Trace Quality (9 điểm)** và **Extra Monitoring (Bonus +3 điểm)**.

### 5.1 Cấu trúc Log JSON chuẩn hóa
Tất cả các log sự kiện phải được ghi nhận dưới dạng cấu trúc JSON một dòng nhằm hỗ trợ tối đa việc phân tích sự cố (RCA):

```json
{
  "timestamp": "2026-06-01T05:01:21.123456",
  "event": "EVENT_TYPE",
  "data": { ... }
}
```

Các loại sự kiện (`event`) bắt buộc bao gồm:
*   `AGENT_START`: Ghi nhận câu hỏi của phụ huynh và mô hình LLM sử dụng.
*   `LLM_METRIC`: Ghi nhận số lượng token sử dụng (Prompt/Completion) và độ trễ phản hồi.
*   `TOOL_CALL`: Ghi nhận tên công cụ được gọi và tham số truyền vào.
*   `TOOL_OBSERVATION`: Ghi nhận dữ liệu thực tế công cụ trả về.
*   `PARSER_ERROR`: Ghi nhận các trường hợp LLM sinh sai định dạng suy luận ReAct.
*   `AGENT_END`: Ghi nhận kết quả phản hồi cuối cùng và tổng số bước thực thi.

### 5.2 Quản lý và Tính toán Chi phí API Thực tế (Extra Monitoring - +3 điểm)
Thay vì sử dụng các giá trị hằng số (Mock) đơn giản, module `metrics.py` phải thực hiện tính toán chi phí động dựa trên bảng giá thực tế của nhà cung cấp mô hình (OpenAI / Google Gemini) cập nhật theo thời gian thực:

```python
PRICING_TABLE = {
    "gemini-1.5-flash": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
    "gpt-4o": {"input_per_1k": 0.005, "output_per_1k": 0.015},
    "phi-3-mini-4k-instruct-q4.gguf": {"input_per_1k": 0.0, "output_per_1k": 0.0} # Local model free
}
```

**Công thức tính Cost thực tế:**
$$\text{Cost} = \left(\frac{\text{Prompt Tokens}}{1000} \times \text{Input Price}\right) + \left(\frac{\text{Completion Tokens}}{1000} \times \text{Output Price}\right)$$

---

## 📊 6. THIẾT KẾ PHƯƠNG ÁN KIỂM THỬ VÀ THỬ NGHIỆM ĐỐI CHỨNG (EVALUATION & ABLATION)

Để đạt trọn vẹn **7 điểm Evaluation** và **2 điểm Ablation Experiments**, dự án phải triển khai bộ kịch bản kiểm thử tự động gồm 3 tập thử nghiệm:

### 6.1 Bộ Test Cases Đại diện
Thiết kế tối thiểu 5 ca kiểm thử đại diện từ dễ tới khó:
1.  **Dễ (1 môn)**: *"Điểm môn Toán cháu Nguyễn Văn An thế nào?"*
2.  **Trung bình (Đa môn)**: *"Nhờ thầy xem điểm môn Văn, Toán, Anh của học sinh S002?"*
3.  **Khó (Tính toán GPA toàn diện)**: *"Hãy tính điểm trung bình tất cả 8 môn học của cháu Chung (S003) giúp tôi."*
4.  **Cực khó (Xét học bổng tích hợp)**: *"Tôi là phụ huynh em Tran Thi Binh lớp 11B2. Cháu có đủ điều kiện nhận học bổng xuất sắc học kỳ này không? Tính GPA và phân tích hạnh kiểm giúp tôi."*
5.  **Ca bẫy (Xử lý lỗi)**: *"Con tôi là Nguyễn Văn Cường học lớp 10A1 điểm số thế nào?"* (Học sinh Cường không tồn tại trong DB).

### 6.2 So sánh đối chứng (Ablation & Baseline)
Hệ thống sẽ chạy thử nghiệm và lưu kết quả so sánh chéo giữa 3 trạng thái của ứng dụng:
*   **Trạng thái 1**: Chatbot Baseline (Không có Tools).
*   **Trạng thái 2**: Agent v1 (Chỉ dùng Prompt thô, Parser thô, so khớp ID chính xác).
*   **Trạng thái 3**: Agent v2 (Prompt Few-shot nâng cao, Tự sửa lỗi, Fuzzy matching).

Các thông số thống kê so sánh bao gồm:
*   **Tỷ lệ thành công (Success Rate %)**
*   **Độ trễ trung bình (Average Latency)**
*   **Tổng số lượng Token tiêu thụ (Avg Token Usage)**
*   **Tổng chi phí vận hành (Total Cost)**
*   **Tỷ lệ lỗi Parser (Parser Error Rate %)**

---

## 🔄 7. SƠ ĐỒ KIẾN TRÚC VÀ CHU TRÌNH LUỒNG LÀM VIỆC (FLOWCHART & SYSTEM ARCHITECTURE)

Đáp ứng tiêu chí **Flowchart & Insight (5 điểm)**. Dưới đây là sơ đồ Mermaid mô tả toàn bộ kiến trúc xử lý của hệ thống Agent v2:

```mermaid
flowchart TD
    A[Phụ huynh gửi câu hỏi] --> B{Hệ thống cấu hình là?}
    B -->|Simple Chatbot| C[Gọi trực tiếp LLM với prompt cơ bản]
    C --> D[Trả về câu trả lời cho Phụ huynh - Dễ gây ảo giác]
    
    B -->|ReAct Agent v2| E[Khởi tạo Agent Context & max_steps=6]
    E --> F[Sinh phản hồi: Thought + Action]
    F --> G{Phân tích LLM Output}
    
    G -->|Có 'Final Answer:'| H[Trích xuất câu trả lời cuối cùng]
    H --> I[Kết thúc & Lưu Telemetry Log]
    I --> J[Trả về kết quả chính xác 100% cho Phụ huynh]
    
    G -->|Có 'Action: tool_name(args)'| K{Parser Regex kiểm tra hợp lệ?}
    K -->|Hợp lệ| L[Thực thi công cụ Python tương ứng]
    K -->|Lỗi Parser| M[Sinh thông điệp lỗi gửi vào Observation để LLM tự sửa sai]
    
    L --> N{Tool chạy thành công?}
    N -->|Thành công| O[Trả về kết quả dữ liệu JSON thật]
    N -->|Lỗi ngoại lệ| P[Bắt Exception và trả về lỗi chi tiết trong Observation]
    
    O --> Q[Cập nhật Agent Context: Observation + Result]
    P --> Q
    M --> Q
    
    Q --> R{Vượt quá max_steps?}
    R -->|Có| S[Kích hoạt cơ chế an toàn: Trả về thông báo khẩn cấp cho phụ huynh]
    R -->|Không| F
```

---

## 💻 8. QUY CHUẨN MÃ NGUỒN VÀ KIẾN TRÚC MÔ-ĐUN (CODE QUALITY)

Đáp ứng tiêu chuẩn **Code Quality (4 điểm)**:
1.  **Tính mô-đun hóa (Modularity)**: 
    *   Tách biệt hoàn toàn phần giao tiếp LLM (`src/core/`) với logic Agent (`src/agent/`) và các công cụ bổ trợ (`src/tools/`).
2.  **Telemetry decoupling**: Các thao tác track metrics được viết gọn gàng thông qua Singleton instance `tracker` trong `metrics.py`, không làm rối ren logic nghiệp vụ chính của ReAct loop.
3.  **Clean Code**: Sử dụng đầy đủ Type Hinting (`List`, `Dict`, `Any`), viết rõ ràng Docstring mô tả cho từng hàm và xử lý Exception chặt chẽ ở mọi tầng.

---

## 👥 9. BẢN ĐỒ PHÂN CHIA ĐÓNG GÓP CÁ NHÂN (SUPPORT FOR INDIVIDUAL SCORES)

Để đảm bảo mỗi thành viên trong nhóm có thể dễ dàng hoàn thành báo cáo cá nhân (`individual_report.md`) đạt điểm tuyệt đối **40/40**, cấu trúc mã nguồn được phân định module rõ ràng để các thành viên nhận nhiệm vụ độc lập:

*   **Thành viên A (Phụ trách Core LLM & Telemetry)**: 
    *   Đảm nhận tích hợp các lớp `LLMProvider` (OpenAI, Gemini).
    *   Xây dựng hệ thống tính toán chi phí động và track tỷ lệ token trong `metrics.py`.
    *   Viết Báo cáo cá nhân tập trung phân tích thiết kế hệ thống Telemetry.
*   **Thành viên B (Phụ trách thiết kế Tools & DB)**:
    *   Hiện thực hóa cấu trúc Mock CSDL với đầy đủ 8 môn học.
    *   Xây dựng các công cụ tính điểm trung bình tự động và cơ chế tìm kiếm mờ (Fuzzy matching) trong `academic_tools.py`.
    *   Viết Báo cáo cá nhân phân tích sâu về "Tool Design Evolution".
*   **Thành viên C (Phụ trách Trí tuệ Agentic & Xử lý lỗi)**:
    *   Thiết kế chu trình ReAct Loop chính trong `agent.py`.
    *   Cải tiến Parser Regex robust, viết Few-shot examples và cơ chế tự sửa sai (Self-Correction/Loop Guard).
    *   Viết Báo cáo cá nhân thực hiện phần "Debugging Case Study" phân tích một ca lặp vô hạn hoặc lỗi Parser trích xuất từ logs.
