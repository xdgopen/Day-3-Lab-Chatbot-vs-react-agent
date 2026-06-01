# Individual Report: Lab 3 — Chatbot vs ReAct Agent

- **Student Name:** [Vũ Ngọc Vinh]
- **Student ID:** [2A202600864]
- **Date:** 2026-06-01
- **Project:** Hệ thống Tra cứu & Quản lý Điểm số Học Sinh
- **Tech Stack:** React · TypeScript · Vite · Tailwind CSS v4 · Lucide React

---

## I. Technical Contribution (15 Points)

### Modules Implemented

| File | Role |
|------|------|
| `src/App.tsx` | Main component — UI, state management, search engine, GPA logic |
| `src/types.ts` | TypeScript interface definitions (`StudentData`, `SubjectScoreData`) |
| `src/data.ts` | Data layer — initial dataset, GPA calculation functions |
| `vite.config.ts` | Build config — Tailwind CSS v4 plugin integration |

### Code Highlights

**1. Natural Language Search Engine (`src/App.tsx`)**

Hệ thống phân tích câu lệnh tiếng Việt tự nhiên để tra cứu học sinh. Sử dụng Unicode normalization loại bỏ dấu khi so sánh:

```typescript
const normalizedQuery = query
  .normalize("NFD")
  .replace(/[\u0300-\u036f]/g, "")
  .replace(/đ/g, "d")
  .toLowerCase();

for (const s of students) {
  const normalizedName = s.name.normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d")
    .toLowerCase();
  const lastName = normalizedName.split(/\s+/).pop();
  if (normalizedQuery.includes(normalizedName) || normalizedQuery.includes(lastName)) {
    matchedStudent = s;
    break;
  }
}
```

**2. GPA Calculator (`src/data.ts`)**

Tính điểm trung bình môn theo đúng trọng số chuẩn Bộ Giáo dục Việt Nam (hệ số 1, 2, 3):

```typescript
export const calculateSubjectGpa = (subject: SubjectScoreData): number => {
  const sum1 = subject.factor_1.reduce((a, b) => a + b, 0);          // weight × 1
  const sum2 = subject.factor_2.reduce((a, b) => a + b, 0) * 2;      // weight × 2
  const sum3 = subject.factor_3 * 3;                                   // weight × 3
  const total = subject.factor_1.length + subject.factor_2.length * 2 + 3;
  return (sum1 + sum2 + sum3) / total;
};
```

**3. TypeScript Type Definitions (`src/types.ts`)**

```typescript
export interface SubjectScoreData {
  id: string;
  name: string;
  englishName: string;
  factor_1: number[];   // Điểm miệng / 15 phút
  factor_2: number[];   // Điểm 45 phút / giữa kỳ
  factor_3: number;     // Điểm cuối kỳ
  teacherName: string;
}

export interface StudentData {
  stt: number;
  studentId: string;
  name: string;
  classId: string;
  avatarUrl: string;
  subjects: SubjectScoreData[];
}
```

### Documentation — How Code Interacts with the ReAct Loop

Trong kiến trúc của lab, `App.tsx` đóng vai trò **Tool** trong vòng lặp ReAct:

- **Observation**: UI nhận input từ phụ huynh (câu lệnh tự nhiên hoặc số STT).
- **Action**: Search engine parse input, gọi `getOrGenerateStudent()` để lấy hoặc tạo mới bản ghi học sinh.
- **Result**: State được cập nhật, React re-render hiển thị kết quả — đây là "Observation" được trả về cho agent ở bước tiếp theo.

Toàn bộ luồng dữ liệu: `User Input → NL Parser → State Update → UI Render → User Observes` phản ánh đúng vòng lặp `Thought → Action → Observation` của ReAct.

---

## II. Debugging Case Study (10 Points)

### Problem Description

Sau khi chạy `npm run dev` thành công (Vite báo `ready in 283ms`, Local: `http://localhost:5173/`), trình duyệt Edge và Cốc Cốc đều trả về lỗi:

```
HTTP ERROR 404 — This localhost page can't be found
ERR_CONNECTION_REFUSED
```

Agent đã đề xuất nhiều giải pháp liên tiếp (đổi trình duyệt, tắt firewall, thêm rule `netsh`) nhưng đều không có tác dụng — đây là trường hợp agent bị "loop" chẩn đoán sai do thiếu dữ liệu quan sát chính xác từ môi trường.

### Log Source

Output từ lệnh `netstat -ano | findstr :5173`:

```
TCP    [::1]:5173    [::]:0    LISTENING    28752
```

Đây là telemetry quan trọng nhất của toàn bộ quá trình debug — một dòng log đã xác định chính xác root cause mà nhiều vòng suy luận trước đó không tìm ra được.

### Diagnosis

**Tại sao LLM/Agent chẩn đoán sai ban đầu?**

Agent đã rơi vào pattern suy luận mặc định: `localhost không kết nối được → firewall`. Đây là lỗi reasoning do **thiếu observation từ môi trường thực**. Agent không có khả năng tự chạy `netstat` trên máy người dùng, nên phải dựa vào người dùng cung cấp output — tạo ra độ trễ lớn trong vòng lặp Observe-Act.

Root cause thực sự: Vite 8.x trên Windows 11 mặc định bind trên **IPv6 loopback** (`[::1]:5173`) thay vì IPv4 (`127.0.0.1:5173`). Trình duyệt resolve `localhost` sang `127.0.0.1` (IPv4), dẫn đến connection refused dù Vite đang chạy bình thường. Đây không phải lỗi prompt, không phải lỗi model — mà là **environment-specific behavior** của Vite trên stack Windows 11 + Node.js v24.

### Solution

Buộc Vite bind trên tất cả network interfaces (bao gồm IPv4):

```bash
npm run dev -- --host 0.0.0.0
```

Kết quả sau khi áp dụng:
```
→ Local:   http://localhost:5173/
→ Network: http://172.16.28.210:5173/
```

Trình duyệt kết nối thành công qua địa chỉ Network IP. Để fix vĩnh viễn, thêm vào `vite.config.ts`:

```typescript
export default defineConfig({
  server: { host: '0.0.0.0' },
  plugins: [react(), tailwindcss()],
})
```

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning — Lợi Ích Của `Thought` Block

Trong lab này, sự khác biệt rõ ràng nhất giữa Chatbot và ReAct Agent nằm ở khả năng **định vị vấn đề theo ngữ cảnh thực tế**. Một Chatbot thuần túy nhận câu hỏi "tại sao localhost không kết nối được?" và trả về danh sách giải pháp tổng quát (firewall, antivirus, port conflict). Ngược lại, ReAct Agent sử dụng `Thought` block để lý luận có cấu trúc:

`Thought` block buộc agent phải **justify hành động tiếp theo**, thay vì đưa ra câu trả lời phản xạ. Điều này tương tự Chain-of-Thought prompting nhưng có vòng phản hồi từ môi trường thực.

### 2. Reliability — Khi Agent Thực Sự Tệ Hơn Chatbot

Tuy nhiên, lab cũng cho thấy rõ giới hạn của ReAct trong môi trường thiếu tool coverage:

- **Latency cao**: Mỗi vòng lặp Observe-Act yêu cầu người dùng chạy lệnh thủ công và copy-paste output. Một Chatbot đơn giản với câu trả lời "dùng `--host 0.0.0.0`" ngay từ đầu sẽ hiệu quả hơn trong trường hợp này.
- **Cascading wrong diagnosis**: Khi thiếu observation chính xác, agent tiếp tục suy luận dựa trên giả định sai (firewall), tạo ra chuỗi hành động vô ích và gây frustration cho người dùng.
- **Over-engineering**: Với các tác vụ đơn giản như "sửa một dòng import TypeScript", agent vẫn đi qua đủ các bước Thought-Action-Observation trong khi một chatbot có thể trả lời trực tiếp trong một message.

### 3. Observation — Ảnh Hưởng Của Environment Feedback

Observation có giá trị nhất trong lab là output của `netstat` — một dòng text đã thay đổi hoàn toàn hướng suy luận của agent. Trước đó, 4-5 vòng lặp debug đều dựa trên assumption sai. Sau khi nhận được observation thực từ môi trường, agent hội tụ về đúng solution trong một bước.

Điều này minh họa nguyên lý cốt lõi của ReAct: **chất lượng của Observation quyết định chất lượng của Action tiếp theo**. Một agent với tool tốt (có thể tự chạy `netstat`) sẽ debug xong trong 1-2 vòng lặp, thay vì 8-10 vòng như trong lab.

---

## IV. Future Improvements (5 Points)

### Scalability

Kiến trúc hiện tại lưu toàn bộ state trong bộ nhớ React — không scale được khi số học sinh tăng lên hàng nghìn. Để production-ready:

- **Asynchronous tool call queue**: Thay vì xử lý tuần tự từng request tra cứu, dùng message queue (ví dụ: BullMQ trên Redis) để agent xử lý nhiều query đồng thời mà không block UI thread.
- **Pagination & Virtual Scrolling**: Hiển thị danh sách học sinh theo trang, chỉ render DOM elements đang visible, tránh render toàn bộ 1000+ rows.
- **Vector Search**: Thay string matching bằng embedding-based search (pgvector) để Natural Language Search hoạt động chính xác hơn với tên tiếng Việt phức tạp.

### Safety

- **Supervisor LLM**: Thêm một LLM layer thứ hai đóng vai "Supervisor" — audit mọi action trước khi thực thi (ví dụ: chặn agent tự động xóa điểm số mà không có xác nhận từ giáo viên).
- **Role-based Access Control**: Phụ huynh chỉ xem được điểm của con mình. Giáo viên chỉ sửa được môn mình dạy. Admin mới có quyền toàn hệ thống.
- **Audit Log**: Ghi lại mọi thay đổi điểm số (ai sửa, lúc nào, giá trị cũ/mới) để đảm bảo trách nhiệm giải trình.

### Performance

- **Vector DB for Tool Retrieval**: Khi hệ thống có nhiều tool (tra cứu điểm, xem lịch học, liên hệ giáo viên...), dùng vector similarity để agent tự chọn đúng tool thay vì liệt kê toàn bộ trong system prompt — giảm token usage và tăng accuracy.
- **Streaming Response**: Tích hợp SSE (Server-Sent Events) để UI cập nhật real-time trong khi agent đang xử lý, thay vì chờ toàn bộ response.
- **Edge Caching**: Cache kết quả GPA computation ở CDN edge (Cloudflare Workers) — điểm số không thay đổi thường xuyên, không cần tính lại mỗi request.

