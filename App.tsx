import React, { useState, useEffect } from 'react';
import { 
  GraduationCap, 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  RotateCcw, 
  Award, 
  BookOpen, 
  TrendingUp
} from 'lucide-react';
import { StudentData, SubjectScoreData } from './types';
import { INITIAL_STUDENTS, calculateSubjectGpa, calculateOverallGpa } from './data';

export default function App() {
  // Main student records stored in state
  const [students, setStudents] = useState<StudentData[]>(INITIAL_STUDENTS);
  
  // Text search query state (accepts conversational sentences)
  const [searchQuery, setSearchQuery] = useState<string>('hãy cho tôi biết điểm của bạn A');
  const [activeStt, setActiveStt] = useState<number>(1);
  const [searchFeedback, setSearchFeedback] = useState<string>('');
  
  // Selected subject for visualization highlight
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>('math');

  // Auto-generate student details if ordinal number does not exist
  const getOrGenerateStudent = (sttNum: number): StudentData => {
    const existing = students.find(s => s.stt === sttNum);
    if (existing) return existing;

    // Generate a beautiful new mock student dynamically on the fly
    const generatedName = `Học sinh Số thứ tự #${sttNum}`;
    const generated: StudentData = {
      stt: sttNum,
      studentId: `HS-2027-${String(sttNum).padStart(4, '0')}`,
      name: generatedName,
      classId: '8A',
      avatarUrl: `https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&h=150&q=80`,
      subjects: [
        { id: 'math', name: 'Toán', englishName: 'Math', factor_1: [7.0, 8.0], factor_2: [7.5], factor_3: 8.0, teacherName: 'Thầy Trần Minh Hoàng' },
        { id: 'literature', name: 'Ngữ văn', englishName: 'Literature', factor_1: [8.0], factor_2: [7.0, 7.5], factor_3: 7.5, teacherName: 'Cô Lê Thị Kim Chi' },
        { id: 'english', name: 'Tiếng Anh', englishName: 'English', factor_1: [8.5], factor_2: [8.0], factor_3: 8.5, teacherName: 'Ms. Elizabeth Nguyen' },
        { id: 'physics', name: 'Vật lý', englishName: 'Physics', factor_1: [7.5, 8.0], factor_2: [8.0], factor_3: 7.0, teacherName: 'Thầy Nguyễn Văn Đức' },
        { id: 'chemistry', name: 'Hóa học', englishName: 'Chemistry', factor_1: [7.0, 7.5], factor_2: [7.5], factor_3: 7.0, teacherName: 'Cô Hoàng Thanh Thủy' },
        { id: 'biology', name: 'Sinh học', englishName: 'Biology', factor_1: [8.0], factor_2: [7.0], factor_3: 8.0, teacherName: 'Cô Phan Minh Thư' },
        { id: 'history', name: 'Lịch sử', englishName: 'History', factor_1: [7.5, 8.0], factor_2: [8.0], factor_3: 7.5, teacherName: 'Cô Trịnh Lan Vy' },
        { id: 'geography', name: 'Địa lý', englishName: 'Geography', factor_1: [8.0], factor_2: [7.5], factor_3: 8.0, teacherName: 'Cô Vũ Thị Vân' }
      ]
    };

    return generated;
  };

  // Helper to extract a capitalized name from text query for user dynamic generation
  const extractNameFromQuery = (query: string): string | null => {
    const clean = query.replace(/[?.,!]/g, "").trim();
    const words = clean.split(/\s+/);
    
    // Check if there are uppercase words at the end
    let uppercaseWords: string[] = [];
    for (let i = words.length - 1; i >= 0; i--) {
      const w = words[i];
      if (w && w[0] === w[0].toUpperCase() && w[0].toLowerCase() !== w[0].toUpperCase()) {
        uppercaseWords.unshift(w);
      } else {
        if (uppercaseWords.length > 0) break;
      }
    }
    
    if (uppercaseWords.length > 0) {
      return uppercaseWords.join(" ");
    }

    // Fallback: If lowercase, extract the word after key prefixes
    for (let i = 0; i < words.length - 1; i++) {
      const w = words[i].toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      if (w === "ban" || w === "cua" || w === "ten") {
        const nextWord = words[i+1];
        return nextWord.charAt(0).toUpperCase() + nextWord.slice(1);
      }
    }

    return null;
  };

  // The active student object based on the currently chosen STT
  const currentStudent = getOrGenerateStudent(activeStt);

  // If the student records state does not yet contain this student, append them
  useEffect(() => {
    const isSaved = students.some(s => s.stt === activeStt);
    if (!isSaved) {
      setStudents(prev => [...prev, currentStudent]);
    }
  }, [activeStt, students, currentStudent]);

  // Selected subject helper
  const selectedSubject = currentStudent.subjects.find(s => s.id === selectedSubjectId) || currentStudent.subjects[0];

  const getGpaClass = (gpa: number) => {
    if (gpa >= 8.5) return 'text-emerald-700 bg-emerald-50 border-emerald-200';
    if (gpa >= 6.5) return 'text-blue-700 bg-blue-50 border-blue-200';
    if (gpa >= 5.0) return 'text-amber-700 bg-amber-50 border-amber-200';
    return 'text-red-700 bg-red-50 border-red-200';
  };

  const getRankName = (gpa: number) => {
    if (gpa >= 9.0) return { label: 'Xuất sắc', style: 'bg-indigo-600 text-white' };
    if (gpa >= 8.0) return { label: 'Học lực Giỏi', style: 'bg-emerald-600 text-white' };
    if (gpa >= 6.5) return { label: 'Học lực Khá', style: 'bg-blue-600 text-white' };
    if (gpa >= 5.0) return { label: 'Học lực Trung bình', style: 'bg-amber-500 text-white' };
    return { label: 'Học lực Yếu', style: 'bg-red-600 text-white' };
  };

  // Handler: Select student based on text query parsing
  const handleSearchQuerySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (!query) return;

    const normalizedQuery = query.toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/đ/g, "d");

    let matchedStudent: StudentData | undefined = undefined;

    // Check existing names
    for (const s of students) {
      const normalizedName = s.name.toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/đ/g, "d");

      const nameParts = normalizedName.split(/\s+/);
      const lastName = nameParts[nameParts.length - 1]; // e.g. "a", "chi", "nam", "duc", "linh"

      if (
        normalizedQuery.includes(normalizedName) || 
        normalizedQuery.includes(lastName) ||
        (lastName === 'a' && normalizedQuery.match(/\b[aA]\b/))
      ) {
        matchedStudent = s;
        break;
      }
    }

    // Try finding by STT number
    if (!matchedStudent) {
      const numbersInQuery = query.match(/\d+/);
      if (numbersInQuery) {
        const parsedNum = parseInt(numbersInQuery[0]);
        if (parsedNum > 0) {
          matchedStudent = getOrGenerateStudent(parsedNum);
        }
      }
    }

    if (matchedStudent) {
      setActiveStt(matchedStudent.stt);
      setSearchFeedback(`✓ Đã tìm thấy: ${matchedStudent.name} (STT #${matchedStudent.stt})`);
    } else {
      // Dynamic creation of student for unrecognized name query
      const extractedName = extractNameFromQuery(query);
      if (extractedName && extractedName.length > 1) {
        const newStt = students.length + 1;
        const newStudent: StudentData = {
          stt: newStt,
          studentId: `HS-2027-${String(newStt).padStart(4, '0')}`,
          name: extractedName,
          classId: '8A',
          avatarUrl: `https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&h=150&q=80`,
          subjects: [
            { id: 'math', name: 'Toán', englishName: 'Math', factor_1: [8.0, 8.5], factor_2: [8.0], factor_3: 8.5, teacherName: 'Thầy Trần Minh Hoàng' },
            { id: 'literature', name: 'Ngữ văn', englishName: 'Literature', factor_1: [7.5], factor_2: [8.0, 7.5], factor_3: 8.0, teacherName: 'Cô Lê Thị Kim Chi' },
            { id: 'english', name: 'Tiếng Anh', englishName: 'English', factor_1: [8.5], factor_2: [8.5], factor_3: 9.0, teacherName: 'Ms. Elizabeth Nguyen' },
            { id: 'physics', name: 'Vật lý', englishName: 'Physics', factor_1: [8.0], factor_2: [8.0], factor_3: 8.0, teacherName: 'Thầy Nguyễn Văn Đức' },
            { id: 'chemistry', name: 'Hóa học', englishName: 'Chemistry', factor_1: [7.5, 8.0], factor_2: [8.0], factor_3: 8.5, teacherName: 'Cô Hoàng Thanh Thủy' },
            { id: 'biology', name: 'Sinh học', englishName: 'Biology', factor_1: [8.0], factor_2: [8.5], factor_3: 8.0, teacherName: 'Cô Phan Minh Thư' },
            { id: 'history', name: 'Lịch sử', englishName: 'History', factor_1: [8.5], factor_2: [8.0], factor_3: 8.0, teacherName: 'Cô Trịnh Lan Vy' },
            { id: 'geography', name: 'Địa lý', englishName: 'Geography', factor_1: [8.0], factor_2: [8.0], factor_3: 8.5, teacherName: 'Cô Vũ Thị Vân' }
          ]
        };
        setStudents(prev => [...prev, newStudent]);
        setActiveStt(newStt);
        setSearchFeedback(`✓ Đã tự động tạo mới học sinh: ${extractedName} (STT #${newStt})`);
      } else {
        setSearchFeedback(`✗ Không tìm thấy học sinh. Hãy thử nhập: "Học sinh Nguyễn Văn A" hoặc "bạn Chi"`);
      }
    }
  };

  const navigateStt = (direction: 'prev' | 'next') => {
    const nextVal = direction === 'next' ? activeStt + 1 : Math.max(1, activeStt - 1);
    setActiveStt(nextVal);
    const targetStudent = getOrGenerateStudent(nextVal);
    setSearchQuery(`hãy cho tôi biết điểm của bạn ${targetStudent.name.split(' ').pop()}`);
    setSearchFeedback(`Tìm thấy: ${targetStudent.name} (STT #${targetStudent.stt})`);
  };

  // Full default reset
  const handleResetToDefault = () => {
    if (confirm('Bạn có muốn khôi phục điểm số ban đầu của tất cả học sinh không?')) {
      setStudents(INITIAL_STUDENTS);
      setActiveStt(1);
      setSearchQuery('hãy cho tôi biết điểm của bạn A');
      setSearchFeedback('');
      setSelectedSubjectId('math');
    }
  };

  // Calculated overall GPA across all 8 subjects
  const overallGpaValue = calculateOverallGpa(currentStudent);
  const rankInfo = getRankName(overallGpaValue);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans antialiased">
      {/* Header bar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-blue-600 text-white rounded-xl shadow-md shadow-blue-105">
              <GraduationCap size={22} />
            </div>
            <div>
              <h1 className="font-bold text-base sm:text-lg text-slate-900 tracking-tight leading-tight">
                EduCheck Vietnam
              </h1>
              <p className="text-[10px] sm:text-xs text-slate-500 font-semibold uppercase tracking-wider">
                Hệ thống Tra cứu &amp; Quản điểm số tối giản
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleResetToDefault}
              className="px-3 py-1.5 border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 rounded-xl transition flex items-center gap-1.5"
              title="Khôi phục trạng thái ban đầu"
            >
              <RotateCcw size={13} />
              Đặt lại
            </button>
            <span className="hidden sm:inline bg-blue-50 text-blue-800 text-[10px] font-bold px-2.5 py-1 rounded-full border border-blue-100 uppercase tracking-wider">
              Niên khóa: 2024-2027
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* TOP INTERACTIVE WRAPPER: STUDENT INDEX INP & PROFILE SUMMARY */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 sm:p-5 flex flex-col md:flex-row items-stretch justify-between gap-5">
          
          {/* CONVERSATIONAL SEARCH BY NATURAL TEXT COMMAND */}
          <div className="flex-1 flex flex-col justify-between py-1 space-y-3">
            <div>
              <span className="text-[10px] text-blue-600 font-bold uppercase tracking-wider block mb-1">
                Trợ lý tra cứu tự nhiên (Natural Language Search)
              </span>
              <h2 className="text-lg font-bold text-slate-900 tracking-tight">
                Nhập câu hỏi hoặc câu lệnh tra cứu điểm
              </h2>
              <p className="text-xs text-slate-500 leading-relaxed max-w-md font-medium">
                Hệ thống tự động phân tích tên học sinh hoặc số thứ tự từ câu lệnh tiếng Việt của bạn (Ví dụ: &quot;cho tôi biết điểm của bạn A&quot;, &quot;điểm của Chi&quot;, v.v.)
              </p>
            </div>

            {/* Conversation query Input Form */}
            <div className="space-y-3">
              <form onSubmit={handleSearchQuerySubmit} className="flex items-center gap-2 max-w-xl">
                <button
                  type="button"
                  onClick={() => navigateStt('prev')}
                  className="p-2 sm:p-2.5 border border-slate-200 hover:bg-slate-100 rounded-xl transition text-slate-600 shadow-xs shrink-0"
                  title="Học sinh trước"
                >
                  <ChevronLeft size={16} />
                </button>

                <div className="relative flex-1">
                  <input
                    type="text"
                    className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 font-semibold text-xs sm:text-sm rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 text-slate-800 transition"
                    placeholder="Nhập yêu cầu: hãy cho tôi biết điểm của bạn A..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <Search size={14} className="absolute left-3 top-3 text-slate-400" />
                </div>

                <button
                  type="submit"
                  className="px-4 py-2 sm:py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm rounded-xl transition shadow-xs shadow-blue-105 shrink-0"
                >
                  Tra cứu
                </button>

                <button
                  type="button"
                  onClick={() => navigateStt('next')}
                  className="p-2 sm:p-2.5 border border-slate-200 hover:bg-slate-100 rounded-xl transition text-slate-600 shadow-xs shrink-0"
                  title="Học sinh tiếp theo"
                >
                  <ChevronRight size={16} />
                </button>
              </form>

              {/* Status or search feedback message */}
              {searchFeedback && (
                <div className={`text-[11px] font-bold px-3 py-1 rounded-lg inline-block ${
                  searchFeedback.startsWith('✓') 
                    ? 'bg-emerald-50 text-emerald-800 border border-emerald-100' 
                    : 'bg-blue-50 text-blue-800 border border-blue-100'
                }`}>
                  {searchFeedback}
                </div>
              )}

              {/* Conversational Suggestions chips */}
              <div className="space-y-1.5 pt-1">
                <span className="text-slate-400 font-bold text-[10px] uppercase block">Bấm thử các câu lệnh mẫu dưới đây:</span>
                <div className="flex flex-wrap items-center gap-1.5 text-xs">
                  {[
                    'hãy cho tôi biết điểm của bạn A',
                    'xem điểm của Trần Thị Bích Chi',
                    'điểm của học sinh Lê Hoài Nam',
                    'bảng điểm bạn Linh',
                    'tra cứu học sinh số thứ tự 4'
                  ].map((preset, idx) => {
                    const isActive = searchQuery.toLowerCase() === preset.toLowerCase();
                    return (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => {
                          setSearchQuery(preset);
                          // We can evaluate directly
                          const query = preset;
                          const normalizedQuery = query.toLowerCase()
                            .normalize("NFD")
                            .replace(/[\u0300-\u036f]/g, "")
                            .replace(/đ/g, "d");

                          let matchedStudent: StudentData | undefined = undefined;

                          for (const s of students) {
                            const normalizedName = s.name.toLowerCase()
                              .normalize("NFD")
                              .replace(/[\u0300-\u036f]/g, "")
                              .replace(/đ/g, "d");

                            const nameParts = normalizedName.split(/\s+/);
                            const lastName = nameParts[nameParts.length - 1];

                            if (
                              normalizedQuery.includes(normalizedName) || 
                              normalizedQuery.includes(lastName) ||
                              (lastName === 'a' && normalizedQuery.match(/\b[aA]\b/))
                            ) {
                              matchedStudent = s;
                              break;
                            }
                          }

                          if (!matchedStudent) {
                            const numbersInQuery = query.match(/\d+/);
                            if (numbersInQuery) {
                              const parsedNum = parseInt(numbersInQuery[0]);
                              if (parsedNum > 0) {
                                matchedStudent = getOrGenerateStudent(parsedNum);
                              }
                            }
                          }

                          if (matchedStudent) {
                            setActiveStt(matchedStudent.stt);
                            setSearchFeedback(`✓ Đã tìm thấy: ${matchedStudent.name} (STT #${matchedStudent.stt})`);
                          }
                        }}
                        className={`px-2.5 py-1 rounded-lg text-[10px] font-bold border transition duration-150 ${
                          isActive 
                            ? 'bg-blue-600 text-white border-blue-600 shadow-xs' 
                            : 'bg-slate-55 text-slate-600 hover:bg-slate-100 border-slate-200'
                        }`}
                      >
                        &quot;{preset}&quot;
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

          </div>

          {/* ACTIVE STUDENT INFORMATION PROFILE CARD */}
          <div className="w-full md:w-80 bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col justify-between space-y-4">
            
            <div className="flex items-center gap-3">
              <div className="relative shrink-0">
                <img
                  src={currentStudent.avatarUrl}
                  alt={currentStudent.name}
                  referrerPolicy="no-referrer"
                  className="w-12 h-12 rounded-xl object-cover border border-slate-300"
                />
                <span className="absolute -bottom-1 -right-1 bg-blue-600 text-white font-bold font-mono text-[9px] px-1.5 py-0.5 rounded-full border border-white">
                  #{currentStudent.stt}
                </span>
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-sm text-slate-900 truncate">
                  {currentStudent.name}
                </h3>
                <div className="flex items-center gap-2 mt-0.5 text-[10px] text-slate-500 font-semibold uppercase">
                  <span>Lớp: {currentStudent.classId}</span>
                  <span>•</span>
                  <span className="font-mono text-blue-600">{currentStudent.studentId}</span>
                </div>
              </div>
            </div>

            <div className="border-t border-slate-200/80 pt-3 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
                  Điểm GPA trung bình chung
                </span>
                <p className="text-2xl font-black text-slate-900 mt-0.5">
                  {overallGpaValue.toFixed(2)}
                </p>
              </div>
              <span className={`px-2.5 py-1 text-[10px] font-black rounded-lg uppercase tracking-wide shadow-3xs ${rankInfo.style}`}>
                {rankInfo.label}
              </span>
            </div>

          </div>

        </div>

        {/* WORKSPACE DETAILED SECTION: SUBJECT CARDS GRID */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between px-1 gap-2">
            <div>
              <h3 className="font-bold text-sm text-slate-900 tracking-tight flex items-center gap-1.5 uppercase">
                <BookOpen size={16} className="text-blue-600" /> Điểm số đầy đủ 8 môn học
              </h3>
              <p className="text-xs text-slate-500 font-medium">Bảng kết quả học lực định kỳ đã quy về trọng số hệ số 1, hệ số 2 và hệ số 3 chuẩn bộ giáo dục</p>
            </div>
            
            <div className="text-[10px] text-slate-500 font-bold bg-white border border-slate-200 px-2.5 py-1 rounded-lg">
              Tổng số lượng: 8 Môn Học
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {currentStudent.subjects.map((sub) => {
              const gpa = calculateSubjectGpa(sub);
              const isSelected = sub.id === selectedSubjectId;
              
              return (
                <div
                  key={sub.id}
                  onClick={() => setSelectedSubjectId(sub.id)}
                  className={`border rounded-xl p-4 cursor-pointer transition-all duration-200 flex flex-col justify-between space-y-4 bg-white ${
                    isSelected 
                      ? 'border-blue-500 ring-2 ring-blue-500/10 shadow-md shadow-blue-50/50' 
                      : 'border-slate-200 hover:bg-slate-50 hover:border-slate-350'
                  }`}
                >
                  {/* Top: Name & Teacher */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between gap-1">
                      <h4 className="font-bold text-xs sm:text-sm text-slate-900 flex items-center gap-1.5 truncate">
                        <span className={`w-1.5 h-1.5 rounded-full ${isSelected ? 'bg-blue-600' : 'bg-slate-300'}`} />
                        {sub.name}
                        <span className="text-[10px] text-slate-400 font-medium font-mono font-normal">({sub.englishName})</span>
                      </h4>
                      <span className={`inline-block font-mono font-black text-xs px-2 py-0.5 rounded border ${getGpaClass(gpa)}`}>
                        {gpa.toFixed(2)}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-400 font-semibold pl-3">
                      {sub.teacherName}
                    </p>
                  </div>

                  {/* Coefficients Rows (Factor 1, 2, 3) */}
                  <div className="space-y-2.5 text-xs border-t border-slate-100 pt-3">
                    {/* Factor 1 */}
                    <div className="flex justify-between items-start gap-2">
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">HS1 (Miệng/15p):</span>
                      <div className="flex flex-wrap gap-1 justify-end max-w-[65%]">
                        {sub.factor_1.length === 0 ? (
                          <span className="text-[10px] text-slate-400 italic">Trống</span>
                        ) : (
                          sub.factor_1.map((v, i) => (
                            <span key={i} className="px-1.5 py-0.5 text-[9px] font-bold border rounded bg-slate-50 hover:bg-slate-100 text-slate-700 font-mono transition">
                              {v.toFixed(1)}
                            </span>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Factor 2 */}
                    <div className="flex justify-between items-start gap-2">
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">HS2 (Giữa kỳ):</span>
                      <div className="flex flex-wrap gap-1 justify-end max-w-[65%]">
                        {sub.factor_2.length === 0 ? (
                          <span className="text-[10px] text-slate-400 italic">Trống</span>
                        ) : (
                          sub.factor_2.map((v, i) => (
                            <span key={i} className="px-1.5 py-0.5 text-[9px] font-bold border rounded bg-slate-50 hover:bg-slate-100 text-slate-700 font-mono transition">
                              {v.toFixed(1)}
                            </span>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Factor 3 */}
                    <div className="flex justify-between items-center gap-2">
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">HS3 (Cuối kỳ):</span>
                      <span className="px-1.5 py-0.5 text-[9px] font-bold border rounded bg-blue-50/50 text-blue-800 border-blue-200 font-mono">
                        {sub.factor_3.toFixed(1)}
                      </span>
                    </div>
                  </div>


                </div>
              );
            })}
          </div>
        </div>

        {/* BOTTOM SECTION: DETAILED DYNAMIC GRAPH OF THE 8 SUBJECTS */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 sm:p-5 space-y-4">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-150 pb-3">
            <div>
              <h3 className="font-bold text-sm text-slate-900 tracking-tight flex items-center gap-1.5 uppercase">
                <TrendingUp size={15} className="text-blue-600" /> Trực quan hóa điểm GPA 8 môn học
              </h3>
              <p className="text-xs text-slate-500 font-medium">Bản đồ so sánh đối sánh thông tin trực quan giữa các bộ môn đào tạo</p>
            </div>
            
            <span className="text-[10px] text-slate-500 font-bold">Thang đo: 0.0 - 10.0</span>
          </div>

          {/* CUSTOM SVG PANORAMIC BAR CHART */}
          <div className="w-full overflow-x-auto pt-2">
            <div className="min-w-[640px] h-72 relative flex flex-col justify-between">
              
              {/* Background scoring scale coordinates */}
              <div className="absolute inset-0 flex flex-col justify-between pointer-events-none text-[9px] text-slate-300 font-bold font-mono">
                {[10, 8, 6, 4, 2, 0].map((val) => (
                  <div key={val} className="w-full flex items-center gap-2">
                    <span className="w-6 text-right shrink-0">{val.toFixed(1)}</span>
                    <div className="flex-1 border-t border-dashed border-slate-200" />
                  </div>
                ))}
              </div>

              {/* Svg bars section container */}
              <div className="h-60 w-full flex items-end justify-around pl-8 pr-4 relative z-10">
                {currentStudent.subjects.map((sub) => {
                  const gpa = calculateSubjectGpa(sub);
                  const isSelected = sub.id === selectedSubjectId;
                  
                  // Calculate height representation percentage (e.g. 9.5 points / 10 max points = 95%)
                  const barHeightPercent = (gpa / 10) * 100;
                  
                  // Color scale for beautiful bars
                  let barColor = 'bg-blue-500 hover:bg-blue-600';
                  if (gpa >= 8.5) barColor = 'bg-emerald-500 hover:bg-emerald-600';
                  else if (gpa < 5.0) barColor = 'bg-red-500 hover:bg-red-600';
                  
                  if (isSelected) {
                    barColor += ' ring-4 ring-blue-500/30';
                  }

                  return (
                    <div 
                      key={sub.id} 
                      onClick={() => setSelectedSubjectId(sub.id)}
                      className="flex flex-col items-center group cursor-pointer w-14 sm:w-16 transition-all"
                    >
                      {/* Score Value badge */}
                      <span className={`text-[10px] font-black font-mono mb-2 px-1.5 py-0.5 rounded-md border text-slate-800 transition ${
                        isSelected ? 'bg-blue-100 border-blue-300 text-blue-800 font-extrabold' : 'bg-slate-50 border-slate-200'
                      }`}>
                        {gpa.toFixed(2)}
                      </span>

                      {/* Actual Pillar */}
                      <div className="w-8 sm:w-9 bg-slate-100 rounded-t-lg relative h-40 flex items-end">
                        <div 
                          className={`w-full rounded-t-lg transition-all duration-300 shadow-sm ${barColor}`}
                          style={{ height: `${barHeightPercent}%` }}
                        />
                      </div>

                      {/* Label Subject Title under the bar */}
                      <span className={`text-[11px] font-bold mt-2.5 text-center truncate w-full ${
                        isSelected ? 'text-blue-600 font-extrabold' : 'text-slate-600'
                      }`}>
                        {sub.name}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Buffer Bottom footer space */}
              <div className="h-4" />

            </div>
          </div>

          {/* Bar Chart Legends */}
          <div className="flex flex-wrap items-center justify-center gap-5 text-xs text-slate-500/80 font-bold border-t border-slate-100 pt-3">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-emerald-500 block" />
              <span>GPA Đạt Giỏi/Xuất sắc (≥ 8.5)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-blue-500 block" />
              <span>GPA Đạt Khá (6.5 - 8.4)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-red-50 block border border-red-300" />
              <span>GPA Cần Cải thiện (&lt; 5.0)</span>
            </div>
          </div>

          {/* QUICK PERFORMANCE INSIGHTS BANNER */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs font-semibold space-y-2 text-slate-700">
            <h4 className="font-extrabold text-[#111111] uppercase tracking-wide flex items-center gap-1">
              <Award size={13} className="text-amber-500" /> Nhận xét tổng quan học lực:
            </h4>
            <p className="leading-relaxed">
              Dựa trên kết quả {overallGpaValue.toFixed(2)} điểm chung, học sinh <span className="font-black text-slate-900">{currentStudent.name}</span> đang đạt danh hiệu xếp loại <span className="text-blue-700 font-extrabold">{rankInfo.label}</span>. 
              Môn học có kết quả cao nhất là học phần thuộc về bộ môn <span className="font-black text-slate-900">{
                currentStudent.subjects
                  .map(sub => ({ sub, gpa: calculateSubjectGpa(sub) }))
                  .reduce((max, curr) => curr.gpa > max.gpa ? curr : max, { sub: { name: 'Toán' }, gpa: 0 }).sub.name
              }</span>.
            </p>
          </div>

        </div>

      </main>

      {/* FOOTER */}
      <footer className="bg-white border-t border-slate-200 mt-12 py-5 text-xs text-slate-500 font-bold">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-blue-600 font-extrabold">EduCheck Vietnam</span>
            <span className="text-slate-350">•</span>
            <span>© 2026 Hệ thống Sổ điểm điện tử cải tiến.</span>
          </div>
          <div className="flex gap-4">
            <a href="#" className="hover:text-blue-600 transition-colors">Điều khoản</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Bảo mật</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Liên hệ Hỗ trợ</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
