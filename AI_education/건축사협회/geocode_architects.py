import os
import sys
import csv
import json
import time
import ssl
import re
import shutil
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SURVEY_DIR = os.path.join(os.path.dirname(BASE_DIR), "측량협회")

CSV_PATH = os.path.join(BASE_DIR, "건축사사무소_전체목록.csv")
BACKUP_PATH = os.path.join(BASE_DIR, "건축사사무소_전체목록_backup.csv")
CACHE_FILE = os.path.join(BASE_DIR, "geocode_cache.json")
SURVEY_GEOCODED = os.path.join(SURVEY_DIR, "survey_companies_geocoded.json")

KAKAO_REST_KEY = "8be27458478ba6ac0638c390d1459b02"
ADDR_API_URL = "https://dapi.kakao.com/v2/local/search/address.json"
KEYWORD_API_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"

CTX = ssl.create_default_context()


def clean_address(addr):
    if not addr:
        return ""
    addr = re.sub(r'\(.*?\)', '', addr)
    addr = re.sub(r'\b\d+층\b', '', addr)
    addr = re.sub(r'\b\d+호\b', '', addr)
    addr = re.sub(r'\b지하\s*\d+층\b', '', addr)
    addr = re.sub(r'[,~]', ' ', addr)
    return " ".join(addr.split()).strip()


def query_kakao(target_url, query_str, max_retries=2):
    encoded = urllib.parse.quote(query_str)
    url = f"{target_url}?query={encoded}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"KakaoAK {KAKAO_REST_KEY}",
        "User-Agent": "Mozilla/5.0"
    })
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                docs = data.get("documents", [])
                if docs:
                    lng = float(docs[0]["x"])
                    lat = float(docs[0]["y"])
                    return round(lat, 7), round(lng, 7)
            break
        except Exception:
            time.sleep(0.2)
    return None, None


def geocode_address(address):
    if not address or not address.strip():
        return None, None

    cleaned = clean_address(address)
    candidates = []
    if cleaned:
        candidates.append((ADDR_API_URL, cleaned))
    candidates.append((ADDR_API_URL, address))

    if "전남광주통합특별시" in address:
        candidates.append((ADDR_API_URL, cleaned.replace("전남광주통합특별시", "광주광역시")))
        candidates.append((ADDR_API_URL, cleaned.replace("전남광주통합특별시", "전라남도")))
        candidates.append((ADDR_API_URL, cleaned.replace("전남광주통합특별시", "").strip()))

    parts = cleaned.split()
    if len(parts) >= 3:
        candidates.append((ADDR_API_URL, " ".join(parts[:4])))
        candidates.append((KEYWORD_API_URL, " ".join(parts[:4])))

    seen = set()
    for api_url, q in candidates:
        q = q.strip()
        if not q or (api_url, q) in seen:
            continue
        seen.add((api_url, q))
        lat, lng = query_kakao(api_url, q)
        if lat is not None and lng is not None:
            return lat, lng

    return None, None


def main():
    print("[*] Starting Geocoding for 건축사사무소_전체목록.csv...")

    # Load cache from 측량협회 if available
    cache = {}
    if os.path.exists(SURVEY_GEOCODED):
        try:
            with open(SURVEY_GEOCODED, "r", encoding="utf-8") as f:
                survey_data = json.load(f)
                for item in survey_data:
                    addr = item.get("addr", "").strip()
                    if addr and item.get("lat") and item.get("lng"):
                        cache[addr] = (item["lat"], item["lng"])
            print(f"[*] Loaded {len(cache)} entries from survey_companies_geocoded.json.")
        except Exception as e:
            print(f"[!] Warning reading survey cache: {e}")

    # Load existing local cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                local_cache = json.load(f)
                cache.update(local_cache)
            print(f"[*] Total cache entries after reading {CACHE_FILE}: {len(cache)}")
        except Exception as e:
            print(f"[!] Warning reading local cache: {e}")

    # Read CSV
    print(f"[*] Reading CSV: {CSV_PATH}")
    rows = []
    fieldnames = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        for row in reader:
            rows.append(row)

    print(f"[*] Total rows in CSV: {len(rows)}")

    # Backup original CSV if not already backed up
    if not os.path.exists(BACKUP_PATH):
        print(f"[*] Creating backup: {BACKUP_PATH}")
        shutil.copy2(CSV_PATH, BACKUP_PATH)

    # Collect unique addresses to geocode
    unique_addrs = set()
    for r in rows:
        addr = r.get("주소", "").strip()
        if addr and addr not in cache:
            unique_addrs.add(addr)

    print(f"[*] Unique addresses needing geocoding: {len(unique_addrs)}")

    # Multi-threaded geocoding
    if unique_addrs:
        processed_count = 0
        success_count = 0
        total_unique = len(unique_addrs)
        start_time = time.time()
        last_save_time = time.time()

        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_addr = {executor.submit(geocode_address, addr): addr for addr in unique_addrs}
            for future in as_completed(future_to_addr):
                addr = future_to_addr[future]
                try:
                    lat, lng = future.result()
                    if lat is not None and lng is not None:
                        cache[addr] = (lat, lng)
                        success_count += 1
                    else:
                        cache[addr] = (None, None)
                except Exception as e:
                    cache[addr] = (None, None)

                processed_count += 1
                if processed_count % 500 == 0 or processed_count == total_unique:
                    elapsed = time.time() - start_time
                    rate = processed_count / elapsed if elapsed > 0 else 0
                    print(f"[*] Progress: {processed_count}/{total_unique} ({processed_count*100/total_unique:.1f}%) | Success: {success_count} | Speed: {rate:.1f} req/s")

                # Periodic save cache every 30 seconds
                if time.time() - last_save_time > 30:
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(cache, f, ensure_ascii=False)
                    last_save_time = time.time()

        # Final cache save
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
        print(f"[*] Geocoding completed. Cache saved to {CACHE_FILE}.")

    # Update rows with 위도, 경도
    out_fields = [f for f in fieldnames if f not in ("위도", "경도", "lat", "lng")]
    out_fields.extend(["위도", "경도"])

    matched_count = 0
    for r in rows:
        addr = r.get("주소", "").strip()
        coords = cache.get(addr, (None, None))
        if coords and coords[0] is not None and coords[1] is not None:
            r["위도"] = coords[0]
            r["경도"] = coords[1]
            matched_count += 1
        else:
            r["위도"] = ""
            r["경도"] = ""

    print(f"[*] Matching Summary: {matched_count}/{len(rows)} rows successfully geocoded ({matched_count*100/len(rows):.2f}%).")

    # Write back to CSV with UTF-8 BOM
    print(f"[*] Writing updated data to: {CSV_PATH}")
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

    print("[OK] All tasks completed successfully.")


if __name__ == "__main__":
    main()

