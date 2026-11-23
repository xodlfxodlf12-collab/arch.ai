import os
import csv
import sys

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def remove_phone_columns(file_path):
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return

    print(f"[*] Processing: {file_path}")
    rows = []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        # Filter out contact columns
        cols_to_remove = ["전화번호", "팩스", "전화", "연락처", "휴대폰", "phone", "fax", "tel"]
        new_fields = [c for c in fields if c not in cols_to_remove]
        for row in reader:
            filtered_row = {k: row[k] for k in new_fields if k in row}
            rows.append(filtered_row)

    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Cleaned {file_path}. New headers: {new_fields}")

if __name__ == "__main__":
    for fname in ["건축사사무소_전체목록.csv", "건축사사무소_전체목록_backup.csv"]:
        target = os.path.join(BASE_DIR, fname)
        remove_phone_columns(target)

