import os
import pandas as pd
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_interactive_map(csv_path=None, output_html=None):
    if csv_path is None:
        csv_path = os.path.join(BASE_DIR, "starbucks.csv")
    if output_html is None:
        output_html = os.path.join(BASE_DIR, "map.html")
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df = df.dropna(subset=['lat', 'lng'])
    
    # 매장 성격 분류 (리저브/더특화/드라이브스루/일반)
    def classify_store(row):
        name = str(row.get('store_name', ''))
        addr = str(row.get('address', ''))
        
        # 1. 최고 핫플레이스 / 플래그십 (The 특화 매장 & 플래그십 매장)
        super_flagships = ['더종로R', '더양평DTR', '더북한강R', '더북한산', '더여수돌산DT', '더제주송당파크R', '명동', '센트럴시티']
        for sf in super_flagships:
            if sf in name:
                return 'HOT_FLAGSHIP'
        
        # 2. 리저브 프리미엄 매장
        if name.endswith('R') or '리저브' in name:
            return 'RESERVE'
        
        # 3. 드라이브스루 (DT 매장)
        if 'DT' in name:
            return 'DT'
            
        return 'NORMAL'
        
    df['store_type'] = df.apply(classify_store, axis=1)
    
    stores_data = df.to_dict(orient="records")
    stores_json = json.dumps(stores_data, ensure_ascii=False)
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>스타벅스 전국 매장 인터랙티브 맵</title>
  
  <!-- Leaflet CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <!-- Leaflet.markercluster CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>

  <!-- Google Fonts & Phosphor Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700;800&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/@phosphor-icons/web"></script>

  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body, html {{
      height: 100%;
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      overflow: hidden;
      background: #111827;
      color: #1f2937;
    }}
    #map {{
      height: 100%;
      width: 100%;
      z-index: 1;
    }}
    
    /* 플로팅 컨트롤 바 & 검색창 */
    .floating-panel {{
      position: absolute;
      top: 20px;
      left: 20px;
      z-index: 1000;
      width: 370px;
      max-width: calc(100vw - 40px);
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(14px);
      border-radius: 18px;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.18), 0 2px 6px rgba(0,0,0,0.06);
      padding: 18px;
      border: 1px solid rgba(255, 255, 255, 0.7);
    }}

    .brand-header {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .brand-icon {{
      width: 38px;
      height: 38px;
      background: #00704A;
      border-radius: 11px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 22px;
      box-shadow: 0 4px 12px rgba(0, 112, 74, 0.35);
    }}
    .brand-title {{
      font-size: 17px;
      font-weight: 800;
      color: #1e293b;
      letter-spacing: -0.3px;
    }}
    .brand-subtitle {{
      font-size: 12px;
      color: #64748b;
      font-weight: 500;
    }}

    /* 범례 (Legend) 필터 칩 */
    .legend-container {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 12px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e2e8f0;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      user-select: none;
      transition: all 0.2s;
      border: 1.5px solid transparent;
    }}
    .chip-hot {{
      background: #fff1f2;
      color: #e11d48;
      border-color: #fecdd3;
    }}
    .chip-hot.active, .chip-hot:hover {{
      background: #e11d48;
      color: #fff;
    }}
    .chip-reserve {{
      background: #faf5ff;
      color: #9333ea;
      border-color: #e9d5ff;
    }}
    .chip-reserve.active, .chip-reserve:hover {{
      background: #9333ea;
      color: #fff;
    }}
    .chip-dt {{
      background: #eff6ff;
      color: #2563eb;
      border-color: #bfdbfe;
    }}
    .chip-dt.active, .chip-dt:hover {{
      background: #2563eb;
      color: #fff;
    }}
    .chip-normal {{
      background: #f0fdf4;
      color: #00704A;
      border-color: #bbf7d0;
    }}
    .chip-normal.active, .chip-normal:hover {{
      background: #00704A;
      color: #fff;
    }}

    /* 검색 박스 */
    .search-box {{
      position: relative;
      margin-bottom: 12px;
    }}
    .search-box i {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: #94a3b8;
      font-size: 18px;
    }}
    .search-box input {{
      width: 100%;
      padding: 11px 14px 11px 40px;
      border-radius: 10px;
      border: 1.5px solid #e2e8f0;
      outline: none;
      font-size: 13.5px;
      font-weight: 500;
      transition: all 0.2s ease;
      background: #f8fafc;
    }}
    .search-box input:focus {{
      border-color: #00704A;
      background: #ffffff;
      box-shadow: 0 0 0 3px rgba(0, 112, 74, 0.15);
    }}

    /* 상태 뱃지 및 액션 */
    .status-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: #475569;
      font-weight: 600;
    }}
    .btn-reset {{
      background: transparent;
      border: none;
      color: #64748b;
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .btn-reset:hover {{
      color: #00704A;
    }}

    /* 마커 스타일 애니메이션 */
    .pulse-animation {{
      animation: pulse-ring 1.8s infinite cubic-bezier(0.45, 0, 0.2, 1);
    }}
    @keyframes pulse-ring {{
      0% {{ box-shadow: 0 0 0 0 rgba(225, 29, 72, 0.6); }}
      70% {{ box-shadow: 0 0 0 12px rgba(225, 29, 72, 0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(225, 29, 72, 0); }}
    }}

    /* 커스텀 마커 팝업 */
    .leaflet-popup-content-wrapper {{
      border-radius: 14px;
      box-shadow: 0 12px 28px rgba(0,0,0,0.2);
      padding: 4px;
      border: 1px solid #f1f5f9;
    }}
    .custom-popup {{
      padding: 8px 6px;
      min-width: 230px;
    }}
    .popup-badge {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 10px;
      font-weight: 800;
      margin-bottom: 6px;
    }}
    .badge-hot {{ background: #ffe4e6; color: #e11d48; }}
    .badge-reserve {{ background: #f3e8ff; color: #9333ea; }}
    .badge-dt {{ background: #dbeafe; color: #2563eb; }}
    .badge-normal {{ background: #e6f4ea; color: #00704A; }}

    .popup-title {{
      font-size: 15px;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .popup-addr {{
      font-size: 12px;
      color: #475569;
      line-height: 1.45;
      margin-bottom: 6px;
    }}
    .popup-tel {{
      font-size: 12px;
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .popup-actions {{
      margin-top: 10px;
      display: flex;
      gap: 6px;
    }}
    .popup-btn {{
      flex: 1;
      text-align: center;
      background: #00704A;
      color: #fff;
      text-decoration: none;
      font-size: 11px;
      padding: 6px 0;
      border-radius: 6px;
      font-weight: 600;
      transition: background 0.2s;
    }}
    .popup-btn:hover {{
      background: #005638;
    }}

    /* 클러스터 아이콘 그린 테마화 */
    .marker-cluster-small {{
      background-color: rgba(0, 112, 74, 0.4);
    }}
    .marker-cluster-small div {{
      background-color: rgba(0, 112, 74, 0.85);
      color: white;
      font-weight: 700;
    }}
    .marker-cluster-medium {{
      background-color: rgba(0, 98, 65, 0.4);
    }}
    .marker-cluster-medium div {{
      background-color: rgba(0, 98, 65, 0.9);
      color: white;
      font-weight: 700;
    }}
    .marker-cluster-large {{
      background-color: rgba(30, 41, 59, 0.4);
    }}
    .marker-cluster-large div {{
      background-color: rgba(30, 41, 59, 0.95);
      color: white;
      font-weight: 700;
    }}
  </style>
</head>
<body>

  <!-- 플로팅 네비게이션 헤더 -->
  <div class="floating-panel">
    <div class="brand-header">
      <div class="brand-icon">
        <i class="ph-bold ph-coffee"></i>
      </div>
      <div>
        <div class="brand-title">스타벅스 매장 지도</div>
        <div class="brand-subtitle">매장 성격별 차별화 아이콘 & 검색</div>
      </div>
    </div>
    
    <!-- 매장 타입별 필터 칩 범례 -->
    <div class="legend-container">
      <span class="chip chip-hot" data-filter="HOT_FLAGSHIP">🔥 최고 핫플/특화</span>
      <span class="chip chip-reserve" data-filter="RESERVE">⭐ 리저브(R)</span>
      <span class="chip chip-dt" data-filter="DT">🚗 드라이브스루</span>
      <span class="chip chip-normal" data-filter="NORMAL">☕ 일반 매장</span>
    </div>

    <div class="search-box">
      <i class="ph ph-magnifying-glass"></i>
      <input type="text" id="searchInput" placeholder="매장명 또는 지역 검색 (예: 종로, 강남, 양평)" />
    </div>

    <div class="status-bar">
      <span>표시 매장: <strong id="storeCount">0</strong>개</span>
      <button class="btn-reset" id="resetViewBtn">
        <i class="ph ph-arrows-clockwise"></i> 전체 보기
      </button>
    </div>
  </div>

  <!-- 지도 컨테이너 -->
  <div id="map"></div>

  <script>
    const rawStores = {stores_json};

    // 1. Leaflet 지도 초기화 (대한민국 전국 중심)
    const map = L.map('map', {{
      center: [36.2, 127.8],
      zoom: 7,
      zoomControl: false
    }});

    L.control.zoom({{ position: 'bottomright' }}).addTo(map);

    // 1. 표준 OpenStreetMap (안정적인 글로벌 타일)
    const osmLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
      crossOrigin: true
    }}).addTo(map);

    // 2. CartoDB Positron (CORS 차단 없는 초고속 대체 타일)
    const cartoLayer = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{
      attribution: '&copy; CartoDB &copy; OpenStreetMap',
      maxZoom: 19,
      subdomains: 'abcd',
      crossOrigin: true
    }});

    // 지도 타일 전환 컨트롤 (OSM / CartoDB)
    L.control.layers({{
      "OpenStreetMap (기본)": osmLayer,
      "CartoDB 컬러 맵": cartoLayer
    }}, null, {{ position: 'topright' }}).addTo(map);

    // 아이콘 생성기 함수
    function createCustomIcon(type) {{
      if (type === 'HOT_FLAGSHIP') {{
        // 불꽃 레드/골드 펄스 아이콘 (최고 매출/핫플)
        return L.divIcon({{
          className: 'custom-pin-hot',
          html: `
            <div class="pulse-animation" style="
              width: 34px;
              height: 34px;
              background: linear-gradient(135deg, #e11d48, #f59e0b);
              border: 2.5px solid #ffffff;
              border-radius: 50%;
              box-shadow: 0 4px 14px rgba(225, 29, 72, 0.5);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-size: 18px;
            ">
              <i class="ph-fill ph-fire"></i>
            </div>
          `,
          iconSize: [34, 34],
          iconAnchor: [17, 17],
          popupAnchor: [0, -17]
        }});
      }} else if (type === 'RESERVE') {{
        // 리저브 퍼플/블랙 프리미엄 별 아이콘
        return L.divIcon({{
          className: 'custom-pin-reserve',
          html: `
            <div style="
              width: 30px;
              height: 30px;
              background: #1e1b4b;
              border: 2px solid #c084fc;
              border-radius: 50%;
              box-shadow: 0 4px 12px rgba(147, 51, 234, 0.4);
              display: flex;
              align-items: center;
              justify-content: center;
              color: #facc15;
              font-size: 16px;
            ">
              <i class="ph-fill ph-star"></i>
            </div>
          `,
          iconSize: [30, 30],
          iconAnchor: [15, 15],
          popupAnchor: [0, -15]
        }});
      }} else if (type === 'DT') {{
        // 드라이브스루 블루 자동차 아이콘
        return L.divIcon({{
          className: 'custom-pin-dt',
          html: `
            <div style="
              width: 28px;
              height: 28px;
              background: #2563eb;
              border: 2px solid #ffffff;
              border-radius: 50%;
              box-shadow: 0 3px 10px rgba(37, 99, 235, 0.4);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-size: 14px;
            ">
              <i class="ph-bold ph-car"></i>
            </div>
          `,
          iconSize: [28, 28],
          iconAnchor: [14, 14],
          popupAnchor: [0, -14]
        }});
      }} else {{
        // 일반 스타벅스 그린 커피 아이콘
        return L.divIcon({{
          className: 'custom-pin-normal',
          html: `
            <div style="
              width: 26px;
              height: 26px;
              background: #00704A;
              border: 2px solid #ffffff;
              border-radius: 50%;
              box-shadow: 0 3px 8px rgba(0, 112, 74, 0.35);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-size: 13px;
            ">
              <i class="ph-bold ph-coffee"></i>
            </div>
          `,
          iconSize: [26, 26],
          iconAnchor: [13, 13],
          popupAnchor: [0, -13]
        }});
      }}
    }}

    let markerCluster = L.markerClusterGroup({{
      showCoverageOnHover: false,
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true
    }});
    map.addLayer(markerCluster);

    let allMarkers = [];
    let currentFilter = 'ALL';

    function renderMarkers(storeList) {{
      markerCluster.clearLayers();
      allMarkers = [];

      storeList.forEach(store => {{
        if (!store.lat || !store.lng) return;

        let badgeHtml = '<span class="popup-badge badge-normal">☕ 일반 매장</span>';
        if (store.store_type === 'HOT_FLAGSHIP') {{
          badgeHtml = '<span class="popup-badge badge-hot">🔥 전국 핫플 플래그십</span>';
        }} else if (store.store_type === 'RESERVE') {{
          badgeHtml = '<span class="popup-badge badge-reserve">⭐ 스타벅스 리저브</span>';
        }} else if (store.store_type === 'DT') {{
          badgeHtml = '<span class="popup-badge badge-dt">🚗 드라이브스루 (DT)</span>';
        }}

        const popupContent = `
          <div class="custom-popup">
            ${{badgeHtml}}
            <div class="popup-title">
              <span>${{store.store_name}}</span>
            </div>
            <div class="popup-addr">${{store.address || '주소 정보 없음'}}</div>
            <div class="popup-tel">
              <i class="ph ph-phone"></i>
              <span>${{store.tel || '1522-3232'}}</span>
            </div>
            <div class="popup-actions">
              <a href="https://map.kakao.com/link/to/${{encodeURIComponent(store.store_name)}},${{store.lat}},${{store.lng}}" target="_blank" class="popup-btn">
                길찾기
              </a>
            </div>
          </div>
        `;

        const icon = createCustomIcon(store.store_type);
        const marker = L.marker([store.lat, store.lng], {{ icon: icon }})
          .bindPopup(popupContent);

        marker.storeData = store;
        allMarkers.push(marker);
        markerCluster.addLayer(marker);
      }});

      document.getElementById('storeCount').innerText = storeList.length.toLocaleString();
    }}

    // 초기 렌더링
    renderMarkers(rawStores);
    if (allMarkers.length > 0) {{
      const group = L.featureGroup(allMarkers);
      map.fitBounds(group.getBounds().pad(0.08));
    }}

    // 필터링 적용 함수
    function applyFilters() {{
      const query = searchInput.value.toLowerCase().trim();

      const filtered = rawStores.filter(store => {{
        // 1. 타입 필터
        const typeMatch = (currentFilter === 'ALL') || (store.store_type === currentFilter);
        
        // 2. 검색어 필터
        let searchMatch = true;
        if (query) {{
          const nameMatch = store.store_name && store.store_name.toLowerCase().includes(query);
          const addrMatch = store.address && store.address.toLowerCase().includes(query);
          searchMatch = nameMatch || addrMatch;
        }}

        return typeMatch && searchMatch;
      }});

      renderMarkers(filtered);

      if (filtered.length > 0 && query) {{
        const group = L.featureGroup(allMarkers);
        map.fitBounds(group.getBounds().pad(0.2), {{ maxZoom: 16 }});
      }}
    }}

    // 검색창 이벤트
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', applyFilters);

    // 범례 칩 클릭 필터링
    document.querySelectorAll('.chip').forEach(chip => {{
      chip.addEventListener('click', () => {{
        const targetType = chip.getAttribute('data-filter');
        if (chip.classList.contains('active')) {{
          chip.classList.remove('active');
          currentFilter = 'ALL';
        }} else {{
          document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
          chip.classList.add('active');
          currentFilter = targetType;
        }}
        applyFilters();
      }});
    }});

    // 전체 보기 버튼
    document.getElementById('resetViewBtn').addEventListener('click', () => {{
      searchInput.value = '';
      currentFilter = 'ALL';
      document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      renderMarkers(rawStores);
      if (allMarkers.length > 0) {{
        const group = L.featureGroup(allMarkers);
        map.fitBounds(group.getBounds().pad(0.08));
      }}
    }});
  </script>
</body>
</html>
"""
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[+] '{output_html}' 인터랙티브 맵(차별화 아이콘 적용) 생성 완료!")

if __name__ == "__main__":
    generate_interactive_map()
