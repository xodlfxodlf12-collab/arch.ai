import requests
import pandas as pd
import json
import time

def fetch_all_starbucks_stores():
    """
    스타벅스 전국(17개 시도) 매장 정보 전체 수집 함수
    """
    url = "https://www.starbucks.co.kr/store/getStore.do"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.starbucks.co.kr/store/store_map.do",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    # 스타벅스 17개 시도 코드 목록
    sido_codes = [
        ("01", "서울"), ("08", "경기"), ("03", "대구"), ("04", "인천"),
        ("05", "부산"), ("06", "울산"), ("07", "대전"), ("09", "광주"),
        ("10", "세종/충남"), ("11", "충북"), ("12", "강원"), ("13", "경남"),
        ("14", "경북"), ("15", "전남"), ("16", "전북"), ("17", "제주")
    ]

    all_stores = []
    print("[*] 스타벅스 전국 17개 시도 매장 수집을 시작합니다...")

    for code, name in sido_codes:
        payload = {
            "in_biz_cds": "0",
            "in_scodes": "0",
            "ins_lat": "37.566535",
            "ins_lng": "126.977969",
            "search_date": "",
            "iend": "3000",
            "searchType": "C",
            "set_date": "",
            "s_code": code,
            "p_sido_cd": code,
            "p_gugun_cd": "",
            "isError": "true",
            "in_distance": "0",
            "in_biz_cd": "",
            "gugun_cd": "",
            "sido_cd": code,
            "del_yes": "0",
            "record": "3000"
        }
        try:
            res = requests.post(url, headers=headers, data=payload, timeout=10)
            res.raise_for_status()
            data = res.json()
            raw_list = data.get("list", [])
            
            sido_store_count = 0
            for item in raw_list:
                store_name = item.get("s_name", "").strip()
                address = item.get("doro_address", "").strip() or item.get("addr", "").strip()
                lat = item.get("lat")
                lng = item.get("lot")
                tel = item.get("tel", "")
                sido_name = item.get("sido_name", "").strip() or name

                if lat and lng:
                    all_stores.append({
                        "sido": sido_name,
                        "store_name": store_name,
                        "address": address,
                        "lat": float(lat),
                        "lng": float(lng),
                        "tel": tel
                    })
                    sido_store_count += 1
            print(f"  - [{name} ({code})] {sido_store_count}개 수집 완료")
            time.sleep(0.15)
        except Exception as e:
            print(f"  [!] [{name} ({code})] 수집 실패: {e}")

    print(f"\n[+] 전국 수집 완료! 총 {len(all_stores)}개 매장 데이터를 확보했습니다.")
    return all_stores

def main():
    stores = fetch_all_starbucks_stores()
    if stores:
        df = pd.DataFrame(stores)
        csv_file = "starbucks.csv"
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print(f"[+] '{csv_file}' 전국 매장 저장 완료 ({len(df)}건)")

if __name__ == "__main__":
    main()
