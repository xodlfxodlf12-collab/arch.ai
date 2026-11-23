import os
import sys
import json
import time
import ssl
import re
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set UTF-8 output for Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON = os.path.join(BASE_DIR, "survey_companies.json")
OUTPUT_JSON = os.path.join(BASE_DIR, "survey_companies_geocoded.json")

# User's Kakao REST API Key
KAKAO_REST_KEY = "8be27458478ba6ac0638c390d1459b02"
API_URL = "https://dapi.kakao.com/v2/local/search/address.json"

CTX = ssl.create_default_context()


def clean_address(addr):
    """Clean address string to improve geocoding match rate."""
    if not addr:
        return ""
    # Remove floor, room, building parentheses e.g. (구로동, 대명벨리온), 1212호, 3층
    addr = re.sub(r'\(.*?\)', '', addr)
    addr = re.sub(r'\b\d+층\b', '', addr)
    addr = re.sub(r'\b\d+호\b', '', addr)
    addr = re.sub(r'\b지하\s*\d+층\b', '', addr)
    addr = re.sub(r'[,~]', ' ', addr)
    return " ".join(addr.split()).strip()


def query_kakao_geocoding(address, max_retries=2):
    """Query Kakao Local API for lat/lng of an address."""
    if not address:
        return None, None

    cleaned = clean_address(address)
    targets = [cleaned, address]

    for target in targets:
        encoded_query = urllib.parse.quote(target)
        url = f"{API_URL}?query={encoded_query}"
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
                        return round(lat, 6), round(lng, 6)
                break
            except Exception:
                time.sleep(0.3)

    return None, None


def main():
    print("[*] Starting Kakao High-Precision Geocoding for 6,628 companies...")
    print(f"[*] Reading: {INPUT_JSON}")

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        companies = json.load(f)

    # Check for existing cache to support resume
    cache = {}
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
                prev_data = json.load(f)
                for item in prev_data:
                    if item.get("lat") and item.get("lng") and item.get("geo_source") == "kakao":
                        cache[item.get("rn")] = (item["lat"], item["lng"])
            print(f"[*] Found {len(cache)} existing cached Kakao coordinates.")
        except Exception:
            pass

    total = len(companies)
    to_process = []
    for c in companies:
        rn = c.get("rn")
        if rn in cache:
            c["lat"], c["lng"] = cache[rn]
            c["geo_source"] = "kakao"
        else:
            to_process.append(c)

    print(f"[*] Need to geocode {len(to_process)} remaining companies...")

    def worker(item):
        addr = item.get("addr", "") or item.get("addr1", "")
        lat, lng = query_kakao_geocoding(addr)
        return item.get("rn"), lat, lng

    completed = len(cache)
    success_count = len(cache)
    max_workers = 12

    if to_process:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {executor.submit(worker, item): item for item in to_process}

            for future in as_completed(future_to_item):
                rn, lat, lng = future.result()
                completed += 1

                # update in company list
                for c in companies:
                    if c.get("rn") == rn:
                        if lat and lng:
                            c["lat"] = lat
                            c["lng"] = lng
                            c["geo_source"] = "kakao"
                            success_count += 1
                        else:
                            # Keep fallback coordinate if Kakao has no exact match
                            c["geo_source"] = "fallback"
                        break

                if completed % 200 == 0 or completed == total:
                    pct = (completed / total) * 100
                    print(f"[+] Progress: {completed}/{total} ({pct:.1f}%) - Success: {success_count}")

    # Save to geocoded JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Geocoding complete! Total: {total}, Kakao Matched: {success_count} ({success_count/total*100:.1f}%)")
    print(f"[OK] Saved to: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()

