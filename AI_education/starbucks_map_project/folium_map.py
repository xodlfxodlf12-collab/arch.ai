"""
스타벅스 매장 지도 시각화 - Folium 입문용 실습 코드 (folium_map.py)
문법 오류 없이 20줄로 끝내는 초간단 지도 생성기
"""

import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "starbucks.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "folium_map.html")

def create_folium_map():
    if not os.path.exists(CSV_PATH):
        print("[!] starbucks.csv 파일이 없습니다. crawler.py를 먼저 실행하세요.")
        return

    # 1. 데이터 읽기
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig").dropna(subset=["lat", "lng"])

    # 2. 지도 생성 (OpenStreetMap 타일 명시 -> 로컬에서도 100% 정상 로딩)
    # 서울 시청 중심 좌표
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles="OpenStreetMap"
    )

    # 3. 마커 클러스터 추가 (수천 개 매장 최적화)
    marker_cluster = MarkerCluster().add_to(m)

    # 4. 상위 매장 마커 찍기 (실습 속도를 위해 서울/경기 중심 또는 전체)
    for _, row in df.iterrows():
        name = row["store_name"]
        addr = row["address"]
        lat = row["lat"]
        lng = row["lng"]

        popup_html = f"<b>{name}</b><br>{addr}"
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=name,
            icon=folium.Icon(color="green", icon="coffee", prefix="fa")
        ).add_to(marker_cluster)

    # 5. HTML로 저장
    m.save(OUTPUT_HTML)
    print(f"[OK] Folium 지도 완성: {OUTPUT_HTML}")
    print("[OK] 브라우저에서 'folium_map.html'을 열어보세요!")

if __name__ == "__main__":
    create_folium_map()

