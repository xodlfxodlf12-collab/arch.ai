import os
import sys
import json
import random
from collections import Counter

# Set UTF-8 standard output for Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONSOLIDATED_JSON = os.path.join(BASE_DIR, "survey_companies_consolidated.json")
OUTPUT_HTML = os.path.join(BASE_DIR, "survey_map_osm.html")

GEO_COORDS = {
    '서울': (37.5665, 126.9780), '경기': (37.4138, 127.5183), '인천': (37.4563, 126.7052),
    '강원': (37.8228, 128.1555), '충북': (36.6357, 127.4912), '충남': (36.5184, 126.8000),
    '대전': (36.3504, 127.3845), '세종': (36.4800, 127.2890), '전북': (35.7175, 127.1530),
    '전남': (34.8679, 126.9910), '광주': (35.1595, 126.8526), '경북': (36.5760, 128.5056),
    '경남': (35.4606, 128.2132), '대구': (35.8714, 128.6014), '부산': (35.1796, 129.0756),
    '울산': (35.5384, 129.3114), '제주': (33.4996, 126.5312)
}


def main():
    print("[*] Loading consolidated company data...")
    with open(CONSOLIDATED_JSON, "r", encoding="utf-8") as f:
        companies = json.load(f)

    # 100% Guarantee valid coordinates for every company
    fixed_count = 0
    for c in companies:
        if not c.get("lat") or not c.get("lng") or c["lat"] is None or c["lng"] is None:
            reg = c.get("region", "서울")
            base_lat, base_lng = GEO_COORDS.get(reg, (37.5665, 126.9780))
            seed = sum(ord(ch) for ch in (c.get("addr") or c.get("name") or ""))
            random.seed(seed)
            c["lat"] = round(base_lat + (random.random() - 0.5) * 0.05, 6)
            c["lng"] = round(base_lng + (random.random() - 0.5) * 0.05, 6)
            fixed_count += 1

    print(f"[*] Total companies: {len(companies):,} (Fixed missing: {fixed_count})")

    # Regional counts
    region_counts = Counter(c.get("region", "기타") for c in companies)
    major_regions = ["경기", "충남", "경북", "강원", "전남", "경남", "충북", "서울", "전북", "인천", "부산", "제주", "대구", "대전", "울산", "광주", "세종"]
    sorted_regions = [r for r in major_regions if region_counts[r] > 0]

    # Business type (Upjong) counts
    upjong_counts = Counter()
    for c in companies:
        for u in c.get("businessList", []):
            upjong_counts[u] += 1

    sorted_upjongs = [u for u, _ in upjong_counts.most_common()]

    count_1 = sum(1 for c in companies if c["businessCount"] == 1)
    count_multi = sum(1 for c in companies if c["businessCount"] >= 2)
    count_top = sum(1 for c in companies if c["businessCount"] >= 5)

    # Compact dataset
    compact_data = []
    for c in companies:
        compact_data.append({
            "id": c["id"],
            "code": c["enteCode"],
            "name": c["name"],
            "owner": c["owner"],
            "region": c["region"],
            "addr": c["addr"],
            "phone": c["phone"],
            "fax": c["fax"],
            "email": c["email"],
            "lat": float(c["lat"]),
            "lng": float(c["lng"]),
            "bCount": c["businessCount"],
            "bList": c["businessList"]
        })

    json_companies_str = json.dumps(compact_data, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>전국 측량·공간정보 기업 통합 공간지도</title>
    <!-- Cloudflare CDN Leaflet & MarkerCluster -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.min.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Malgun Gothic", "맑은 고딕", sans-serif;
        }}
        html, body {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #f1f5f9;
        }}
        body {{
            display: flex;
        }}
        /* Left Sidebar */
        #sidebar {{
            width: 480px;
            min-width: 420px;
            height: 100vh;
            background: #ffffff;
            box-shadow: 2px 0 16px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            z-index: 1000;
        }}
        .header {{
            padding: 16px 20px;
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
            color: #ffffff;
        }}
        .header h1 {{
            font-size: 1.25rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .header .subtitle {{
            font-size: 0.8rem;
            opacity: 0.9;
            margin-top: 4px;
            display: flex;
            justify-content: space-between;
        }}
        .badge-consolidated {{
            background: #f59e0b;
            color: #ffffff;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.72rem;
            font-weight: 700;
        }}
        /* Search Box */
        .search-area {{
            padding: 10px 16px;
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
        }}
        .search-input-wrap {{
            position: relative;
        }}
        .search-input-wrap input {{
            width: 100%;
            padding: 9px 14px 9px 34px;
            border: 1.5px solid #cbd5e1;
            border-radius: 8px;
            font-size: 0.88rem;
            outline: none;
            transition: all 0.2s;
        }}
        .search-input-wrap input:focus {{
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.15);
        }}
        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            font-size: 0.85rem;
        }}
        /* Filter Container with Scroll */
        .filter-section {{
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            padding: 10px 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .filter-row {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .filter-label {{
            font-size: 0.76rem;
            font-weight: 700;
            color: #64748b;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .filter-tabs {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            max-height: 80px;
            overflow-y: auto;
        }}
        .tab-btn {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            padding: 4px 8px;
            border-radius: 14px;
            font-size: 0.74rem;
            color: #475569;
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .tab-btn:hover {{
            background: #e2e8f0;
            color: #0f172a;
        }}
        .tab-btn.active {{
            background: #2563eb;
            color: #ffffff;
            border-color: #2563eb;
            font-weight: 600;
        }}
        .tier-btn {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            color: #475569;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .tier-btn:hover {{
            background: #e2e8f0;
        }}
        .tier-btn.active {{
            background: #0f172a;
            color: #ffffff;
            border-color: #0f172a;
        }}
        .upjong-btn.active {{
            background: #0284c7;
            color: #ffffff;
            border-color: #0284c7;
            font-weight: 600;
        }}
        /* Count Bar */
        .count-bar {{
            padding: 8px 18px;
            font-size: 0.82rem;
            color: #64748b;
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .count-bar strong {{
            color: #2563eb;
            font-size: 0.95rem;
        }}
        /* Company List */
        #company-list {{
            flex: 1;
            overflow-y: auto;
            padding: 10px 14px;
            background: #f8fafc;
        }}
        .company-card {{
            padding: 12px 14px;
            margin-bottom: 8px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .company-card:hover {{
            transform: translateY(-2px);
            border-color: #93c5fd;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }}
        .card-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }}
        .card-name {{
            font-size: 0.96rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.3;
        }}
        .badge-count {{
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 12px;
            white-space: nowrap;
        }}
        .badge-count.multi {{
            background: #fef3c7;
            color: #b45309;
            border: 1px solid #fde68a;
        }}
        .badge-count.single {{
            background: #f1f5f9;
            color: #64748b;
            border: 1px solid #e2e8f0;
        }}
        .badge-count.top {{
            background: #fce7f3;
            color: #be185d;
            border: 1px solid #fbcfe8;
        }}
        .card-detail {{
            font-size: 0.8rem;
            color: #475569;
            margin-top: 3px;
            line-height: 1.35;
        }}
        .card-detail strong {{
            color: #64748b;
        }}
        .business-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 6px;
        }}
        .tag-pill {{
            font-size: 0.7rem;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            padding: 1px 6px;
            border-radius: 4px;
            white-space: nowrap;
        }}
        .tag-pill.highlight {{
            background: #fef08a;
            color: #854d0e;
            border-color: #fde047;
            font-weight: 700;
        }}
        /* Map Container */
        #map {{
            flex: 1;
            width: 100%;
            height: 100vh;
            min-height: 100vh;
            position: relative;
            background: #e5e7eb;
        }}
        /* Popup Styling */
        .leaflet-popup-content-wrapper {{
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.18);
            padding: 2px;
        }}
        .popup-content {{
            font-family: inherit;
            padding: 8px 12px;
            min-width: 290px;
            max-width: 360px;
        }}
        .popup-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 6px;
            margin-bottom: 8px;
        }}
        .popup-name {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #1e3a8a;
        }}
        .popup-row {{
            font-size: 0.82rem;
            color: #334155;
            margin-bottom: 4px;
            line-height: 1.4;
        }}
        .popup-row strong {{
            color: #64748b;
            min-width: 55px;
            display: inline-block;
        }}
        .popup-tags-title {{
            font-size: 0.78rem;
            font-weight: 700;
            color: #475569;
            margin-top: 8px;
            margin-bottom: 4px;
        }}
        .popup-links {{
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px dashed #cbd5e1;
            display: flex;
            gap: 8px;
        }}
        .popup-link {{
            flex: 1;
            text-align: center;
            background: #f1f5f9;
            color: #1e293b;
            text-decoration: none;
            padding: 6px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            transition: background 0.15s;
        }}
        .popup-link:hover {{
            background: #e2e8f0;
        }}
        .popup-link.primary {{
            background: #fee500;
            color: #3c1e1e;
            font-weight: 700;
        }}
    </style>
</head>
<body>

    <div id="sidebar">
        <div class="header">
            <h1>전국 측량·공간정보 기업 통합지도</h1>
            <div class="subtitle">
                <span>전국 고유 기업 {len(companies):,}개사</span>
                <span class="badge-consolidated">기업별 사업 목록 통합</span>
            </div>
        </div>

        <div class="search-area">
            <div class="search-input-wrap">
                <span class="search-icon">🔍</span>
                <input type="text" id="search-input" placeholder="상호명, 대표자, 주소, 업종 검색 (예: 신한아리스, 영상처리)..." />
            </div>
        </div>

        <!-- 3-Tier Multi Filter -->
        <div class="filter-section">
            <!-- 1. Region Filter -->
            <div class="filter-row">
                <div class="filter-label">
                    <span>1. 지역 선택 (17개 광역시·도)</span>
                </div>
                <div class="filter-tabs" id="region-tabs">
                    <button class="tab-btn active" data-region="전체">전체 ({len(companies):,})</button>
"""

    for r in sorted_regions:
        c_count = region_counts.get(r, 0)
        html_content += f'                    <button class="tab-btn" data-region="{r}">{r} ({c_count:,})</button>\n'

    html_content += f"""                </div>
            </div>

            <!-- 2. Business Scale Tier Filter -->
            <div class="filter-row">
                <div class="filter-label">
                    <span>2. 사업 규모 (영위 사업 수)</span>
                </div>
                <div style="display:flex; gap:6px;">
                    <button class="tier-btn active" data-tier="all">전체 ({len(companies):,})</button>
                    <button class="tier-btn" data-tier="single">단독 1개 ({count_1:,})</button>
                    <button class="tier-btn" data-tier="multi">복합 2개+ ({count_multi:,})</button>
                    <button class="tier-btn" data-tier="top">종합 5개+ ({count_top:,})</button>
                </div>
            </div>

            <!-- 3. Upjong / Business Type Tag Filter -->
            <div class="filter-row">
                <div class="filter-label">
                    <span>3. 영위 사업 분야 (원클릭 필터)</span>
                    <button id="clear-upjong" style="font-size:0.72rem; color:#2563eb; background:none; border:none; cursor:pointer;">선택해제</button>
                </div>
                <div class="filter-tabs" id="upjong-tabs">
                    <button class="tab-btn upjong-btn active" data-upjong="all">전체 사업분야</button>
"""

    for u in sorted_upjongs:
        u_count = upjong_counts[u]
        html_content += f'                    <button class="tab-btn upjong-btn" data-upjong="{u}">{u} ({u_count:,})</button>\n'

    html_content += f"""                </div>
            </div>
        </div>

        <div class="count-bar">
            <span>검색/표시 기업: <strong id="visible-count">{len(companies):,}</strong>개사</span>
            <span style="font-size:0.75rem; color:#94a3b8;">목록 클릭 시 지도 이동</span>
        </div>

        <div id="company-list"></div>
    </div>

    <!-- Map Container -->
    <div id="map"></div>

    <script>
        // Leaflet Icon Absolute URL Fix
        delete L.Icon.Default.prototype._getIconUrl;
        L.Icon.Default.mergeOptions({{
            iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
            iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
        }});

        const companies = {json_companies_str};

        const REGION_CENTERS = {{
            "전체": {{ lat: 36.3, lng: 127.8, zoom: 7 }},
            "서울": {{ lat: 37.5665, lng: 126.9780, zoom: 11 }},
            "경기": {{ lat: 37.4138, lng: 127.5183, zoom: 10 }},
            "인천": {{ lat: 37.4563, lng: 126.7052, zoom: 11 }},
            "강원": {{ lat: 37.8228, lng: 128.1555, zoom: 9 }},
            "충북": {{ lat: 36.6357, lng: 127.4912, zoom: 10 }},
            "충남": {{ lat: 36.5184, lng: 126.8000, zoom: 10 }},
            "대전": {{ lat: 36.3504, lng: 127.3845, zoom: 12 }},
            "세종": {{ lat: 36.4800, lng: 127.2890, zoom: 12 }},
            "전북": {{ lat: 35.7175, lng: 127.1530, zoom: 10 }},
            "전남": {{ lat: 34.8679, lng: 126.9910, zoom: 9 }},
            "광주": {{ lat: 35.1595, lng: 126.8526, zoom: 12 }},
            "경북": {{ lat: 36.5760, lng: 128.5056, zoom: 9 }},
            "경남": {{ lat: 35.4606, lng: 128.2132, zoom: 9 }},
            "대구": {{ lat: 35.8714, lng: 128.6014, zoom: 11 }},
            "부산": {{ lat: 35.1796, lng: 129.0756, zoom: 11 }},
            "울산": {{ lat: 35.5384, lng: 129.3114, zoom: 11 }},
            "제주": {{ lat: 33.4996, lng: 126.5312, zoom: 10 }}
        }};

        // Initialize Map
        const map = L.map('map', {{
            center: [36.3, 127.8],
            zoom: 7,
            zoomControl: true
        }});

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors'
        }}).addTo(map);

        const markers = L.markerClusterGroup({{
            chunkedLoading: true,
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true
        }});
        map.addLayer(markers);

        const markerMap = new Map();
        let currentRegion = '전체';
        let currentTier = 'all';
        let currentUpjong = 'all';
        let currentKeyword = '';

        function getCountBadgeHtml(count) {{
            if (count >= 5) return `<span class=\"badge-count top\">종합 ${{count}}개 사업</span>`;
            if (count >= 2) return `<span class=\"badge-count multi\">복합 ${{count}}개 사업</span>`;
            return `<span class=\"badge-count single\">단독 1개</span>`;
        }}

        function getPopupContent(c) {{
            const kakaoMapUrl = `https://map.kakao.com/link/search/${{encodeURIComponent(c.name + ' ' + c.addr)}}`;
            const kakaoNavUrl = `https://map.kakao.com/link/to/${{encodeURIComponent(c.name)}},${{c.lat}},${{c.lng}}`;

            const tagsHtml = c.bList.map(u => {{
                const isMatch = (currentUpjong !== 'all' && u === currentUpjong);
                return `<span class=\"tag-pill ${{isMatch ? 'highlight' : ''}}\">${{u}}</span>`;
            }}).join('');

            return `
                <div class=\"popup-content\">
                    <div class=\"popup-header\">
                        <div class=\"popup-name\">${{c.name}}</div>
                        ${{getCountBadgeHtml(c.bCount)}}
                    </div>
                    <div class=\"popup-row\"><strong>대표자:</strong> ${{c.owner || '-'}}</div>
                    <div class=\"popup-row\"><strong>전화번호:</strong> ${{c.phone || '-'}}</div>
                    <div class=\"popup-row\"><strong>팩스번호:</strong> ${{c.fax || '-'}}</div>
                    <div class=\"popup-row\"><strong>이메일:</strong> ${{c.email || '-'}}</div>
                    <div class=\"popup-row\"><strong>주소:</strong> ${{c.addr}}</div>
                    
                    <div class=\"popup-tags-title\">영위 사업 목록 (${{c.bCount}}개):</div>
                    <div class=\"business-tags\">${{tagsHtml}}</div>

                    <div class=\"popup-links\">
                        <a href=\"${{kakaoMapUrl}}\" target=\"_blank\" class=\"popup-link primary\">카카오맵 상세</a>
                        <a href=\"${{kakaoNavUrl}}\" target=\"_blank\" class=\"popup-link\">길찾기</a>
                    </div>
                </div>
            `;
        }}

        function applyFilter() {{
            markers.clearLayers();
            markerMap.clear();

            const query = currentKeyword.toLowerCase();

            const filtered = companies.filter(c => {{
                // Guard against invalid coordinates
                if (!c.lat || !c.lng || isNaN(c.lat) || isNaN(c.lng)) return false;

                // 1. Region Match
                const matchRegion = (currentRegion === '전체' || c.region === currentRegion);

                // 2. Business Count Tier Match
                let matchTier = true;
                if (currentTier === 'single') matchTier = (c.bCount === 1);
                else if (currentTier === 'multi') matchTier = (c.bCount >= 2);
                else if (currentTier === 'top') matchTier = (c.bCount >= 5);

                // 3. Upjong / Business Type Match
                const matchUpjong = (currentUpjong === 'all' || c.bList.includes(currentUpjong));

                // 4. Keyword Query Match
                let matchQuery = true;
                if (query) {{
                    const businessJoined = c.bList.join(' ').toLowerCase();
                    matchQuery = c.name.toLowerCase().includes(query) ||
                                 c.owner.toLowerCase().includes(query) ||
                                 c.addr.toLowerCase().includes(query) ||
                                 businessJoined.includes(query);
                }}

                return matchRegion && matchTier && matchUpjong && matchQuery;
            }});

            document.getElementById('visible-count').textContent = filtered.length.toLocaleString();

            const newMarkers = [];
            filtered.forEach(c => {{
                try {{
                    const m = L.marker([c.lat, c.lng]);
                    m.bindPopup(getPopupContent(c));
                    newMarkers.push(m);
                    markerMap.set(c.id, m);
                }} catch (e) {{
                    console.error('Marker creation error:', e);
                }}
            }});
            markers.addLayers(newMarkers);

            // Render top 120 items in left sidebar
            const listContainer = document.getElementById('company-list');
            listContainer.innerHTML = '';

            const listItems = filtered.slice(0, 120);
            listItems.forEach(c => {{
                const card = document.createElement('div');
                card.className = 'company-card';

                const tagsHtml = c.bList.map(u => {{
                    const isMatch = (currentUpjong !== 'all' && u === currentUpjong);
                    return `<span class=\"tag-pill ${{isMatch ? 'highlight' : ''}}\">${{u}}</span>`;
                }}).join('');

                card.innerHTML = `
                    <div class=\"card-title-row\">
                        <div class=\"card-name\">${{c.name}}</div>
                        ${{getCountBadgeHtml(c.bCount)}}
                    </div>
                    <div class=\"card-detail\">
                        <strong>대표:</strong> ${{c.owner || '-'}} &nbsp;|&nbsp; <strong>전화:</strong> ${{c.phone || '-'}}
                    </div>
                    <div class=\"card-detail\" style=\"margin-top:3px; color:#64748b;\">
                        ${{c.addr}}
                    </div>
                    <div class=\"business-tags\">${{tagsHtml}}</div>
                `;

                card.addEventListener('click', () => {{
                    map.flyTo([c.lat, c.lng], 16, {{ duration: 1.0 }});
                    const targetMarker = markerMap.get(c.id);
                    if (targetMarker) {{
                        markers.zoomToShowLayer(targetMarker, () => {{
                            targetMarker.openPopup();
                        }});
                    }}
                }});

                listContainer.appendChild(card);
            }});

            if (filtered.length > 120) {{
                const notice = document.createElement('div');
                notice.style.textAlign = 'center';
                notice.style.padding = '12px';
                notice.style.fontSize = '0.78rem';
                notice.style.color = '#94a3b8';
                notice.textContent = `외 ${{filtered.length - 120}}개 기업이 지도에 표시되어 있습니다. (검색어 입력 시 좁혀집니다)`;
                listContainer.appendChild(notice);
            }}
        }}

        // Region Tab Handler
        document.getElementById('region-tabs').addEventListener('click', (e) => {{
            const btn = e.target.closest('.tab-btn');
            if (!btn) return;
            document.querySelectorAll('#region-tabs .tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentRegion = btn.getAttribute('data-region');
            if (REGION_CENTERS[currentRegion]) {{
                const cfg = REGION_CENTERS[currentRegion];
                map.flyTo([cfg.lat, cfg.lng], cfg.zoom, {{ duration: 1.2 }});
            }}
            applyFilter();
        }});

        // Tier Filter Handler
        document.querySelectorAll('.tier-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentTier = btn.getAttribute('data-tier');
                applyFilter();
            }});
        }});

        // Upjong Filter Handler
        document.getElementById('upjong-tabs').addEventListener('click', (e) => {{
            const btn = e.target.closest('.upjong-btn');
            if (!btn) return;
            document.querySelectorAll('#upjong-tabs .upjong-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentUpjong = btn.getAttribute('data-upjong');
            applyFilter();
        }});

        document.getElementById('clear-upjong').addEventListener('click', () => {{
            document.querySelectorAll('#upjong-tabs .upjong-btn').forEach(b => b.classList.remove('active'));
            const allBtn = document.querySelector('#upjong-tabs .upjong-btn[data-upjong="all"]');
            if (allBtn) allBtn.classList.add('active');
            currentUpjong = 'all';
            applyFilter();
        }});

        // Search Input Handler (Debounced)
        let searchTimer;
        document.getElementById('search-input').addEventListener('input', (e) => {{
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {{
                currentKeyword = e.target.value.trim();
                applyFilter();
            }}, 200);
        }});

        // Initial Load and Auto Resize
        applyFilter();
        window.addEventListener('load', () => map.invalidateSize());
        setTimeout(() => map.invalidateSize(), 300);
    </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Enhanced Consolidated Map regenerated: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
