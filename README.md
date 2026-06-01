# 🧠 Trợ lý Học tập Học sinh (ReAct Academic Agent) - Hướng dẫn Cài đặt & Chạy Dự án

Dự án này là một hệ thống **ReAct Agent (Thought-Action-Observation)** kết hợp với cơ sở dữ liệu SQLite giúp tra cứu điểm số, hạnh kiểm, chuyên cần và đưa ra lộ trình tư vấn học tập thông minh cho phụ huynh học sinh. 

Hệ thống được nâng cấp toàn diện với cơ chế xác thực thông minh (qua Tên học sinh + Số điện thoại phụ huynh), tự động phát hiện học sinh học nhiều lớp (khối lớp 10, 11, 12) để hỏi lại người dùng, truy xuất chính xác hàng điểm theo khối lớp yêu cầu và định dạng kết quả bằng ngôn ngữ tự nhiên (tiếng Việt) cực kỳ sinh động và chi tiết.

---

## 📁 Cấu trúc Thư mục Chính

```text
├── data/
│   └── students.db           # Cơ sở dữ liệu SQLite học sinh (636 dòng)
├── server/
│   ├── api.py                # FastAPI Backend & Mock ReAct Provider
│   └── static/
│       └── index.html        # Giao diện Web Chatbot tương tác
├── src/
│   ├── agent/
│   │   ├── agent.py          # Lớp ReActAgent (Thought-Action-Observation)
│   │   └── academic_tools.py # Bộ công cụ tra cứu học tập (Tools)
│   ├── core/
│   │   ├── llm_provider.py   # Lớp cơ sở LLM Provider
│   │   ├── gemini_provider.py# Tích hợp Google Gemini
│   │   └── local_provider.py # Tích hợp Local GGUF (Phi-3, Qwen)
│   └── data/
│       └── database.py       # Tầng giao tiếp Database SQLite
├── database_master.csv       # Dữ liệu nguồn CSV (638 dòng)
├── init_sqlite_db.py         # Script khởi tạo cơ sở dữ liệu SQLite
├── requirements.txt          # Danh sách thư viện Python phụ thuộc
└── README.md                 # Hướng dẫn sử dụng này
```

---

## 🛠️ Hướng dẫn Cài đặt & Chuẩn bị

### Bước 1: Cấu hình Môi trường ảo & Cài đặt Thư viện
Mở terminal tại thư mục gốc của dự án và chạy các lệnh sau:

1. **Tạo và kích hoạt môi trường ảo (Khuyến nghị):**
   ```bash
   # Trên Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Cài đặt các thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

### Bước 2: Thiết lập file Cấu hình `.env`
Sao chép tệp `.env.example` thành `.env` để cấu hình các API Key hoặc cấu hình chạy Local:
```bash
copy .env.example .env
```
Mở file `.env` lên và điền các khóa API của bạn nếu muốn chạy với LLM Cloud thực tế (như `OPENAI_API_KEY`, `GEMINI_API_KEY`). Nếu chạy chế độ **Mock ReAct (Mặc định)**, bạn không cần cài đặt API Key nào.

### Bước 3: Khởi tạo Cơ sở Dữ liệu SQLite
Để đảm bảo cơ sở dữ liệu được nạp đầy đủ lịch sử 3 năm học (lớp 10, lớp 11, lớp 12) của tất cả học sinh mà không bị ghi đè, hãy xóa file DB cũ (nếu có) và khởi tạo lại:

```bash
# Xóa file cũ nếu có (trên Windows PowerShell)
Remove-Item -Path data/students.db -ErrorAction SilentlyContinue

# Khởi tạo và import dữ liệu từ database_master.csv
python init_sqlite_db.py
```
*Sau khi chạy thành công, màn hình sẽ thông báo đã import thành công dữ liệu cho tất cả học sinh (636 dòng vào bảng `students`).*

---

## 🚀 Hướng dẫn Chạy Ứng dụng

Dự án sử dụng **FastAPI** làm máy chủ API và phục vụ giao diện Web ở cổng `8000`.

### 1. Khởi động API Server:
```bash
python server/api.py
```
Màn hình sẽ hiển thị thông báo máy chủ đang chạy:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 2. Trải nghiệm trên Trình duyệt:
Truy cập vào địa chỉ sau trên trình duyệt Web của bạn:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧠 Quy tắc Trải nghiệm Luồng Chatbot Thông minh

Để kiểm tra các luật thông minh về tìm kiếm đa khối lớp học và định dạng điểm tự nhiên:

1. **Chào hỏi**: Gõ `Xin chào` hoặc `Hi` để nhận lời chào từ chatbot.
2. **Tra cứu thiếu thông tin lớp học**:
   - Nhập câu hỏi: `Xem điểm của Lý Duy Giang`
   - Chatbot sẽ yêu cầu xác thực số điện thoại phụ huynh: `Xin vui lòng cung cấp số điện thoại phụ huynh để xác thực trước khi xem điểm.`
   - Nhập số điện thoại: `0990092379`
   - **Luật thông minh hoạt động**: Hệ thống tìm ra phụ huynh này có con học suốt 3 năm (lớp 10, lớp 11, lớp 12). Chatbot sẽ hỏi lại:
     > *Tìm thấy điểm của học sinh Lý Duy Giang ở các lớp: lớp 10, lớp 11, lớp 12. Bạn muốn tìm điểm của học sinh Lý Duy Giang lớp mấy?*
   - Nhập lớp học mong muốn: `lớp 11` (hoặc chỉ cần gõ `11`).
   - Chatbot sẽ trả về bảng điểm chi tiết của lớp 11 của em Lý Duy Giang bằng **ngôn ngữ tự nhiên cực kỳ sinh động**, chi tiết điểm số các môn, GPA tổng hợp, xếp loại hạnh kiểm, điểm rèn luyện và nhận xét của giáo viên chủ nhiệm.
3. **Tra cứu có sẵn thông tin lớp học**:
   - Nhập câu hỏi trực tiếp: `Xem điểm lớp 11 của Lý Duy Giang, sđt 0990092379`
   - Hệ thống sẽ trực tiếp xác thực và xuất ngay bảng điểm lớp 11 mà không cần hỏi lại.

---

## 🧪 Chạy Kiểm thử (Tests)

Bạn có thể chạy các bài test tự động để đảm bảo hệ thống hoạt động ổn định:
```bash
# Chạy bộ test pytest
pytest tests/test_local.py
```
hoặc chạy file test kịch bản tự động:
```bash
python test_fix.py
```
