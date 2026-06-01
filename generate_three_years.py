import json
import csv
import os
import random
import re

def remove_accents(txt):
    accents_map = {
        'a': 'áàảãạăắằẳẵặâấầẩẫậ',
        'A': 'ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ',
        'd': 'đ',
        'D': 'Đ',
        'e': 'éèẻẽẹêếềểễệ',
        'E': 'ÉÈẺẼẸÊẾỀỂỄỆ',
        'i': 'íìỉĩị',
        'I': 'ÍÌỈĨỊ',
        'o': 'óòỏõọôốồổỗộơớờởỡợ',
        'O': 'ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ',
        'u': 'úùủũụưứừửữự',
        'U': 'ÚÙỦŨỤƯỨỪỬỮỰ',
        'y': 'ýỳỷỹỵ',
        'Y': 'ÝỲỶỸỴ'
    }
    res = txt
    for char, accented_chars in accents_map.items():
        for acc in accented_chars:
            res = res.replace(acc, char)
    return res

def generate_email(name):
    no_accent = remove_accents(name).lower()
    clean_name = re.sub(r'[^a-z0-9]', '', no_accent)
    return f"{clean_name}@school.edu.vn"

# Nhận xét giáo viên theo hạnh kiểm
REMARKS_EXCELLENT = [
    "Hoc sinh xuat sac toan dien, guong mau, tich cuc trong moi phong trao.",
    "Lop truong guong mau, hoc tot, tac phong nhanh nhen, giup do ban be tot.",
    "Cham ngoan, hoc gioi, co tu duy sang tao tot, tich cuc phat bieu.",
    "Rat nang no, trach nhiem cao trong cong viec chung cua lop, ket qua xuat sac."
]
REMARKS_GOOD = [
    "Cham ngoan, hoc luc kha gioi, di hoc day du va dung gio.",
    "Y thuc hoc tap tot, co tien bo nhieu trong nam hoc, hoa dong voi ban be.",
    "Ngoan ngoan, le phep, hoan thanh tot cac nhiem vu duoc giao.",
    "Co y thuc ky luat tot, tiep thu bai nhanh, can phat huy hon cac mon tu nhien."
]
REMARKS_AVERAGE = [
    "Hoc luc trung binh kha, doi luc con chua tap trung nghe giang.",
    "Ngoan ngoan nhung con tram, it phat bieu, luc hoc o muc trung binh.",
    "Con di hoc muon vai lan, chua hoan thanh day du bai tap ve nha.",
    "Can co gang tap trung hon nua, han che noi chuyen rieng trong lop."
]
REMARKS_WEAK = [
    "Nghi hoc nhieu khong phep, thai do hoc tap chua tot, can gia dinh nhac nho gap.",
    "Thuong xuyen di muon, chua hoan thanh bai tap, can chu y ky luat.",
    "Y thuc to chuc ky luat chua cao, hay noi chuyen rieng, luc hoc yeu kem.",
    "Vi pham quy che lop nhieu lan, nghi hoc vo toi va, can gia dinh phoi hop."
]

def generate_grades_for_year(student_type):
    subjects = ["Math", "Literature", "English", "Physics", "Chemistry", "Biology", "History", "Geography"]
    grades = {}
    for sub in subjects:
        if student_type == "excellent":
            f1 = [round(random.uniform(8.0, 10.0), 1) for _ in range(2)]
            f2 = [round(random.uniform(8.0, 10.0), 1)]
            f3 = round(random.uniform(8.5, 10.0), 1)
        elif student_type == "average":
            f1 = [round(random.uniform(5.5, 8.5), 1) for _ in range(2)]
            f2 = [round(random.uniform(5.0, 8.0), 1)]
            f3 = round(random.uniform(5.0, 8.5), 1)
        else:
            f1 = [round(random.uniform(3.0, 6.5), 1) for _ in range(2)]
            f2 = [round(random.uniform(3.0, 6.0), 1)]
            f3 = round(random.uniform(2.5, 6.0), 1)
        
        grades[sub] = {
            "factor_1": f1,
            "factor_2": f2,
            "factor_3": f3
        }
    return grades

def generate_conduct_for_year(student_type):
    if student_type == "excellent":
        excused = random.randint(0, 2)
        unexcused = 0
        behavior_score = random.randint(85, 100)
        conduct_grade = "Tốt"
        remarks = random.choice(REMARKS_EXCELLENT)
    elif student_type == "average":
        excused = random.randint(1, 5)
        unexcused = random.randint(0, 2)
        behavior_score = random.randint(65, 84)
        conduct_grade = "Khá"
        remarks = random.choice(REMARKS_GOOD if behavior_score >= 75 else REMARKS_AVERAGE)
    else:
        excused = random.randint(2, 7)
        unexcused = random.randint(3, 10)
        behavior_score = random.randint(40, 64)
        conduct_grade = "Trung bình" if behavior_score >= 50 else "Yếu"
        remarks = random.choice(REMARKS_WEAK)
        
    return {
        "excused_absences": excused,
        "unexcused_absences": unexcused,
        "behavior_score": behavior_score,
        "conduct_grade": conduct_grade,
        "teacher_remarks": remarks
    }

def main():
    # 1. Tìm đường dẫn file database.json
    paths_to_try = ["database.json", "db.json", "src/data/database.json"]
    json_path = None
    for p in paths_to_try:
        if os.path.exists(p):
            json_path = p
            break
            
    if not json_path:
        print("[ERROR] Khong tim thay file database.json hoac db.json.")
        return
        
    print(f"[INFO] Dang doc du lieu tu: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    # 2. Xây dựng cấu trúc dữ liệu mới hỗ trợ 3 năm học
    # Định nghĩa 3 năm học và các lớp tương ứng cho từng học sinh
    years = [
        {"academic_year": "2023-2024", "grade_level": 10, "class_suffix": "A1"},
        {"academic_year": "2024-2025", "grade_level": 11, "class_suffix": "B1"},
        {"academic_year": "2025-2026", "grade_level": 12, "class_suffix": "C1"}
    ]
    
    new_db = {
        "students": {},
        "history": {}  # Lưu trữ dữ liệu học tập và rèn luyện theo sid và academic_year
    }

    print("[INFO] Dang sinh du lieu hoc tap cho 3 nam hoc (Lop 10 -> Lop 12)...")
    for sid, info in db["students"].items():
        name = info["name"]
        parent = info["parent"]
        parent_phone = info["parent_phone"]
        email = info.get("email", generate_email(name))
        
        # Lưu thông tin học sinh cố định
        new_db["students"][sid] = {
            "name": name,
            "parent": parent,
            "parent_phone": parent_phone,
            "email": email
        }
        
        new_db["history"][sid] = {}
        
        # Xác định ngẫu nhiên loại học lực của học sinh để đồng bộ qua các năm
        stype = random.choices(["excellent", "average", "weak"], weights=[20, 70, 10])[0]
        
        for yr in years:
            acad_yr = yr["academic_year"]
            grade_lvl = yr["grade_level"]
            
            # Đặt tên lớp tương thích, ví dụ: 10A1, 11B1, 12C1
            # Để tạo tính ngẫu nhiên nhẹ, chúng ta cho học sinh thuộc lớp A1 hoặc A2
            suffix = random.choice(["1", "2"]) if grade_lvl != 12 else "1"
            cls_name = f"{grade_lvl}{'A' if grade_lvl==10 else 'B' if grade_lvl==11 else 'C'}{suffix}"
            
            # Sinh điểm và hạnh kiểm cho năm học này
            year_grades = generate_grades_for_year(stype)
            year_conduct = generate_conduct_for_year(stype)
            
            new_db["history"][sid][acad_yr] = {
                "grade_level": grade_lvl,
                "class": cls_name,
                "grades": year_grades,
                "conduct": year_conduct
            }

    # 3. Ghi lại dữ liệu JSON mới cập nhật
    for p in paths_to_try:
        if os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                json.dump(new_db, f, ensure_ascii=False, indent=4)
            print(f"[SUCCESS] Da ghi nhan CSDL 3 nam hoc vao: {p}")

    # 4. Xuất bảng tổng hợp database_master.csv (Hỗ trợ 3 dòng dữ liệu cho mỗi học sinh)
    master_csv_path = "database_master.csv"
    print(f"[INFO] Dang xuat file master CSV moi: {master_csv_path}")
    
    subjects_keys = ["Math", "Literature", "English", "Physics", "Chemistry", "Biology", "History", "Geography"]
    
    # Tạo tiêu đề bảng Master (Có thêm cột academic_year và grade_level)
    headers = ["student_id", "name", "academic_year", "grade_level", "class", "parent", "parent_phone", "email"]
    for sub in subjects_keys:
        headers.extend([f"{sub}_factor_1", f"{sub}_factor_2", f"{sub}_factor_3", f"{sub}_gpa"])
    headers.extend(["excused_absences", "unexcused_absences", "behavior_score", "conduct_grade", "overall_gpa", "teacher_remarks"])
    
    with open(master_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for sid, info in new_db["students"].items():
            for yr in years:
                acad_yr = yr["academic_year"]
                yr_data = new_db["history"][sid][acad_yr]
                grade_lvl = yr_data["grade_level"]
                cls_name = yr_data["class"]
                
                row = [
                    sid, 
                    info["name"], 
                    acad_yr, 
                    str(grade_lvl), 
                    cls_name, 
                    info["parent"], 
                    info["parent_phone"], 
                    info["email"]
                ]
                
                # Tính điểm các môn trong năm học đó
                all_gpas = []
                for sub in subjects_keys:
                    score_info = yr_data["grades"][sub]
                    f1_list = score_info["factor_1"]
                    f2_list = score_info["factor_2"]
                    f3_val = score_info["factor_3"]
                    
                    total_sum = sum(f1_list) + (2 * sum(f2_list)) + (3 * f3_val)
                    total_count = len(f1_list) + (2 * len(f2_list)) + 3
                    gpa = round(total_sum / total_count, 2)
                    all_gpas.append(gpa)
                    
                    row.extend([
                        ";".join(map(str, f1_list)),
                        ";".join(map(str, f2_list)),
                        str(f3_val),
                        str(gpa)
                    ])
                    
                # Điểm trung bình tổng quát chung của năm học
                overall_gpa = round(sum(all_gpas) / len(all_gpas), 2)
                
                cond = yr_data["conduct"]
                row.extend([
                    cond["excused_absences"],
                    cond["unexcused_absences"],
                    cond["behavior_score"],
                    cond["conduct_grade"],
                    overall_gpa,
                    cond["teacher_remarks"]
                ])
                writer.writerow(row)

    # 5. Xuất các file CSV riêng rẽ trong csv_export/
    os.makedirs("csv_export", exist_ok=True)
    
    # 5.1 students.csv (Chỉ giữ 1 dòng/học sinh vì hồ sơ cá nhân là tĩnh)
    students_csv_path = "csv_export/students.csv"
    with open(students_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "name", "parent", "parent_phone", "email"])
        for sid, info in new_db["students"].items():
            writer.writerow([sid, info["name"], info["parent"], info["parent_phone"], info["email"]])
            
    # 5.2 grades.csv (Mỗi học sinh có 8 môn * 3 năm = 24 dòng)
    grades_csv_path = "csv_export/grades.csv"
    with open(grades_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "academic_year", "grade_level", "class", "subject", "factor_1", "factor_2", "factor_3", "gpa"])
        for sid, yr_dict in new_db["history"].items():
            for acad_yr, yr_data in yr_dict.items():
                grade_lvl = yr_data["grade_level"]
                cls_name = yr_data["class"]
                for sub, score_info in yr_data["grades"].items():
                    f1_list = score_info["factor_1"]
                    f2_list = score_info["factor_2"]
                    f3_val = score_info["factor_3"]
                    total_sum = sum(f1_list) + (2 * sum(f2_list)) + (3 * f3_val)
                    total_count = len(f1_list) + (2 * len(f2_list)) + 3
                    gpa = round(total_sum / total_count, 2)
                    writer.writerow([
                        sid, 
                        acad_yr, 
                        str(grade_lvl), 
                        cls_name, 
                        sub, 
                        ";".join(map(str, f1_list)), 
                        ";".join(map(str, f2_list)), 
                        str(f3_val), 
                        str(gpa)
                    ])

    # 5.3 conduct.csv (Mỗi học sinh có 3 năm = 3 dòng)
    conduct_csv_path = "csv_export/conduct.csv"
    with open(conduct_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "academic_year", "grade_level", "class", "excused_absences", "unexcused_absences", "behavior_score", "conduct_grade", "teacher_remarks"])
        for sid, yr_dict in new_db["history"].items():
            for acad_yr, yr_data in yr_dict.items():
                grade_lvl = yr_data["grade_level"]
                cls_name = yr_data["class"]
                cond = yr_data["conduct"]
                writer.writerow([
                    sid, 
                    acad_yr, 
                    str(grade_lvl), 
                    cls_name, 
                    cond["excused_absences"], 
                    cond["unexcused_absences"], 
                    cond["behavior_score"], 
                    cond["conduct_grade"], 
                    cond["teacher_remarks"]
                ])

    print("\n[SUCCESS] Chuyen doi co so du lieu 3 nam hoc hoan tat!")
    print(f"[INFO] 1. Master CSV: {os.path.abspath(master_csv_path)}")
    print(f"[INFO] 2. Thuc muc CSV rieng le: {os.path.abspath('csv_export/')}")

if __name__ == "__main__":
    main()
