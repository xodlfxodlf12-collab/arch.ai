import os
import sys
import json
import csv
import time
import ssl
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set UTF-8 standard output for Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_URL = "https://www.kasm.or.kr/mbi/selectEnterpriseList.do"

# Ignore SSL verification for older institutional certs
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.kasm.or.kr/mbi/selectEnterpriseListVw.do"
}


def fetch_page(page_index, max_retries=3):
    """Fetch single page data from KASM API."""
    data = urllib.parse.urlencode({
        "pageIndex": str(page_index),
        "enteHang": "",
        "deleHang": "",
        "cityCode": "",
        "sigunguCode": "",
        "upJongCode": "",
        "addr": ""
    }).encode("utf-8")

    req = urllib.request.Request(API_URL, data=data, headers=HEADERS)

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=15) as resp:
                res_bytes = resp.read()
                data_json = json.loads(res_bytes.decode("utf-8"))
                result_list = data_json.get("resultData", {}).get("resultList", [])
                page_info = data_json.get("page", {})
                return page_index, result_list, page_info
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[ERROR] Page {page_index} failed after {max_retries} attempts: {e}")
                return page_index, [], {}
            time.sleep(1.0)


def extract_city_name(addr):
    """Extract primary city/province from address string."""
    if not addr:
        return "기타"
    tokens = addr.strip().split()
    if not tokens:
        return "기타"
    first = tokens[0]
    if "서울" in first:
        return "서울"
    elif "경기" in first:
        return "경기"
    elif "인천" in first:
        return "인천"
    elif "강원" in first:
        return "강원"
    elif "충청북도" in first or "충북" in first:
        return "충북"
    elif "충청남도" in first or "충남" in first:
        return "충남"
    elif "대전" in first:
        return "대전"
    elif "세종" in first:
        return "세종"
    elif "전라북도" in first or "전북" in first:
        return "전북"
    elif "전라남도" in first or "전남" in first:
        return "전남"
    elif "광주" in first:
        return "광주"
    elif "경상북도" in first or "경북" in first:
        return "경북"
    elif "경상남도" in first or "경남" in first:
        return "경남"
    elif "대구" in first:
        return "대구"
    elif "부산" in first:
        return "부산"
    elif "울산" in first:
        return "울산"
    elif "제주" in first:
        return "제주"
    return first


def main():
    print("[*] Starting survey company data collection...")
    print(f"[*] Target URL: {API_URL}")

    # 1. Fetch first page to get total pages
    _, first_items, page_info = fetch_page(1)
    if not first_items:
        print("[ERROR] Failed to fetch initial page. Exiting.")
        return

    total_pages = page_info.get("totalPages", 663)
    total_elements = page_info.get("totalElements", 6628)
    print(f"[*] Total items to collect: {total_elements} across {total_pages} pages.")

    all_results = {1: first_items}
    completed_pages = 1

    # 2. Concurrently fetch pages 2 to total_pages
    pages_to_fetch = list(range(2, total_pages + 1))
    max_workers = 6

    print(f"[*] Fetching remaining {len(pages_to_fetch)} pages with {max_workers} worker threads...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_page = {executor.submit(fetch_page, p): p for p in pages_to_fetch}

        for future in as_completed(future_to_page):
            p_idx, items, _ = future.result()
            all_results[p_idx] = items
            completed_pages += 1

            if completed_pages % 50 == 0 or completed_pages == total_pages:
                pct = (completed_pages / total_pages) * 100
                print(f"[+] Progress: {completed_pages}/{total_pages} pages ({pct:.1f}%)")

    # 3. Flatten and sort results by original page index and rn
    flat_items = []
    for p in range(1, total_pages + 1):
        for item in all_results.get(p, []):
            item["region"] = extract_city_name(item.get("addr", ""))
            flat_items.append(item)

    print(f"[*] Successfully collected {len(flat_items)} companies.")

    # 4. Save to JSON
    json_path = os.path.join(BASE_DIR, "survey_companies.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(flat_items, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved JSON: {json_path}")

    # 5. Save to CSV
    csv_path = os.path.join(BASE_DIR, "survey_companies.csv")
    csv_columns = [
        "rn", "enteCode", "enteHang", "deleHang", "upJongCode", "upJongName",
        "upRegiNumb", "region", "postServNumb", "addr", "addr1", "addr2",
        "tellNumb", "faxNumb", "eMail", "upRegiYmd", "membKindNm", "membGubunName"
    ]

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat_items)
    print(f"[OK] Saved CSV (with UTF-8 BOM): {csv_path}")

    # 6. Regional summary
    region_counts = {}
    for item in flat_items:
        r = item.get("region", "기타")
        region_counts[r] = region_counts.get(r, 0) + 1

    print("\n[*] Regional Distribution Summary:")
    for r, c in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {r}: {c} 건")

    print("\n[OK] Collection complete!")


if __name__ == "__main__":
    main()

