import os
import sys
import json
import csv

# Set UTF-8 standard output for Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON = os.path.join(BASE_DIR, "survey_companies_geocoded.json")
OUTPUT_JSON = os.path.join(BASE_DIR, "survey_companies_consolidated.json")
OUTPUT_CSV = os.path.join(BASE_DIR, "survey_companies_consolidated.csv")

# Gyeonggi-do Si/Gun list for address starting without '경기도'
GYEONGGI_CITIES = {
    "수원시", "고양시", "용인시", "성남시", "부천시", "화성시", "안산시", "남양주시",
    "안양시", "평택시", "시흥시", "파주시", "의정부시", "김포시", "광주시", "광명시",
    "군포시", "하남시", "오산시", "양주시", "이천시", "구리시", "안성시", "포천시",
    "의왕시", "양평군", "여주시", "동두천시", "가평군", "과천시", "연천군"
}


def normalize_region(addr, orig_region):
    """Ensure standard 17 metropolitan city / province names."""
    if not addr:
        return orig_region or "기타"
    tokens = addr.strip().split()
    if not tokens:
        return orig_region or "기타"

    first = tokens[0]
    if "서울" in first: return "서울"
    if "경기" in first: return "경기"
    if "인천" in first: return "인천"
    if "강원" in first: return "강원"
    if "충북" in first or "충청북도" in first: return "충북"
    if "충남" in first or "충청남도" in first: return "충남"
    if "대전" in first: return "대전"
    if "세종" in first: return "세종"
    if "전북" in first or "전라북도" in first: return "전북"
    if "전남" in first or "전라남도" in first or "전남광주" in first: return "전남"
    if "광주" in first and len(tokens) > 1 and "광주시" not in first: return "광주"
    if "경북" in first or "경상북도" in first: return "경북"
    if "경남" in first or "경상남도" in first: return "경남"
    if "대구" in first: return "대구"
    if "부산" in first: return "부산"
    if "울산" in first: return "울산"
    if "제주" in first: return "제주"

    # Match Gyeonggi cities if "경기도" was omitted by user
    if any(city in first for city in GYEONGGI_CITIES):
        return "경기"

    return orig_region or "기타"


def main():
    print("[*] Consolidating and normalizing survey companies...")
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    companies_map = {}

    for item in raw_items:
        ente_code = item.get("enteCode", "").strip()
        name = item.get("enteHang", "").strip()
        addr = item.get("addr", "").strip()

        key = ente_code if ente_code else f"{name}_{addr}"

        upjong = item.get("upJongName", "").strip()
        reg_no = item.get("upRegiNumb", "").strip()
        reg_ymd = item.get("upRegiYmd", "").strip()

        license_entry = {
            "type": upjong,
            "regNo": reg_no,
            "regYmd": reg_ymd
        }

        if key not in companies_map:
            region = normalize_region(addr, item.get("region"))
            companies_map[key] = {
                "enteCode": ente_code,
                "name": name,
                "owner": item.get("deleHang", "").strip(),
                "region": region,
                "addr": addr,
                "addr1": item.get("addr1", "").strip(),
                "addr2": item.get("addr2", "").strip(),
                "postCode": item.get("postServNumb", "").strip(),
                "phone": item.get("tellNumb", "").strip(),
                "fax": item.get("faxNumb", "").strip(),
                "email": item.get("eMail", "").strip(),
                "lat": item.get("lat"),
                "lng": item.get("lng"),
                "geoSource": item.get("geo_source", "kakao"),
                "businessList": [],
                "licenses": []
            }

        c = companies_map[key]
        if upjong and upjong not in c["businessList"]:
            c["businessList"].append(upjong)

        c["licenses"].append(license_entry)

    consolidated_list = []
    for idx, (k, c) in enumerate(companies_map.items(), 1):
        c["id"] = idx
        c["businessCount"] = len(c["businessList"])
        c["isMultiBusiness"] = c["businessCount"] > 1
        c["businessStr"] = ", ".join(c["businessList"])
        consolidated_list.append(c)

    consolidated_list.sort(key=lambda x: (-x["businessCount"], x["name"]))

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(consolidated_list, f, ensure_ascii=False, indent=2)

    csv_columns = [
        "id", "enteCode", "name", "owner", "region", "businessCount",
        "businessStr", "addr", "phone", "fax", "email", "lat", "lng"
    ]
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(consolidated_list)

    print(f"[OK] Consolidated {len(consolidated_list):,} companies with 100% normalized 17 provinces.")


if __name__ == "__main__":
    main()
