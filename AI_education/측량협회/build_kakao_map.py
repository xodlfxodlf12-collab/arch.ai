import os
import sys
import json

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOCODED_JSON = os.path.join(BASE_DIR, "survey_companies_geocoded.json")
OUTPUT_HTML = os.path.join(BASE_DIR, "survey_map_kakao.html")

# Existing corona_Map JavaScript Key (with free Kakao Maps quota enabled)
KAKAO_JS_KEY = "e28ae09bdab5800d10021c4a246eeb30"


def main():
    print(f"[*] Reading: {GEOCODED_JSON}")
    with open(GEOCODED_JSON, "r", encoding="utf-8") as f:
        companies = json.load(f)

    valid_companies = [c for c in companies if c.get("lat") and c.get("lng")]
    print(f"[*] Valid companies: {len(valid_companies):,} / {len(companies):,}")

    region_counts = {}
    for c in valid_companies:
        r = c.get("region", "기타")
        region_counts[r] = region_counts.get(r, 0) + 1

    major_regions = ["경기", "충남", "경북", "강원", "전남", "경남", "충북", "서울", "전북", "인천", "부산", "제주", "대구", "대전", "울산", "광주", "세종"]
    other_regions = [r for r in region_counts.keys() if r not in major_regions]
    sorted_regions = major_regions + other_regions

    compact_data = []
    for c in valid_companies:
        compact_data.append({
            "id": c.get("rn"),
            "name": c.get("enteHang", ""),
            "owner": c.get("deleHang", ""),
            "type": c.get("upJongName", ""),
            "regNo": c.get("upRegiNumb", ""),
            "phone": c.get("tellNumb", ""),
            "fax": c.get("faxNumb", ""),
            "email": c.get("eMail", ""),
            "addr": c.get("addr", ""),
            "region": c.get("region", ""),
            "lat": c["lat"],
            "lng": c["lng"]
        })

    json_str = json.dumps(compact_data, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>전국 측량업체 공간정보 지도 (카카오맵)</title>
    <!-- Kakao Maps SDK with autoload=false -->
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}&libraries=clusterer&autoload=false"></script>
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
            background: #f8fafc;
        }}
        body {{
            display: flex;
        }}
        #sidebar {{
            width: 440px;
            min-width: 380px;
            height: 100vh;
            background: #ffffff;
            box-shadow: 2px 0 16px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            z-index: 1000;
        }}
        .header {{
            padding: 18px 20px;
            background: linear-gradient(135deg, #fee500 0%, #facc15 100%);
            color: #1e1e1e;
        }}
        .header h1 {{
            font-size: 1.25rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 8px;
            color: #111827;
        }}
        .header .subtitle {{
            font-size: 0.82rem;
            color: #4b5563;
            margin-top: 5px;
            display: flex;
            justify-content: space-between;
        }}
        .badge-kakaomap {{
            background: #ffffff;
            color: #b45309;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .search-area {{
            padding: 12px 16px;
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
        }}
        .search-input-wrap {{
            position: relative;
        }}
        .search-input-wrap input {{
            width: 100%;
            padding: 10px 14px 10px 36px;
            border: 1.5px solid #cbd5e1;
            border-radius: 8px;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        .search-input-wrap input:focus {{
            border-color: #eab308;
            box-shadow: 0 0 0 3px rgba(234,179,8,0.2);
        }}
        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            font-size: 0.9rem;
        }}
        .region-tabs-container {{
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            padding: 10px 14px;
        }}
        .region-tabs {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            max-height: 105px;
            overflow-y: auto;
        }}
        .tab-btn {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            padding: 5px 9px;
            border-radius: 16px;
            font-size: 0.78rem;
            color: #475569;
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .tab-btn:hover {{
            background: #fef08a;
            color: #854d0e;
        }}
        .tab-btn.active {{
            background: #eab308;
            color: #ffffff;
            border-color: #ca8a04;
            font-weight: 700;
        }}
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
            color: #d97706;
        }}
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
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .company-card:hover {{
            transform: translateY(-2px);
            border-color: #fde047;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        }}
        .card-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 4px;
        }}
        .card-name {{
            font-size: 0.93rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.3;
        }}
        .card-badge {{
            font-size: 0.7rem;
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
            padding: 2px 6px;
            border-radius: 4px;
            white-space: nowrap;
            margin-left: 6px;
        }}
        .card-detail {{
            font-size: 0.79rem;
            color: #475569;
            margin-top: 3px;
            line-height: 1.35;
        }}
        .card-detail strong {{
            color: #64748b;
        }}
        #map {{
            flex: 1;
            width: 100%;
            height: 100vh;
            min-height: 100vh;
            position: relative;
            background: #e5e7eb;
        }}
        .map-type-ctrl {{
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 10;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            display: flex;
            overflow: hidden;
            border: 1px solid #cbd5e1;
        }}
        .map-type-btn {{
            padding: 8px 14px;
            font-size: 0.82rem;
            font-weight: 600;
            background: #ffffff;
            color: #475569;
            border: none;
            cursor: pointer;
            transition: background 0.15s;
        }}
        .map-type-btn.active {{
            background: #2563eb;
            color: #ffffff;
        }}
        .custom-infowindow {{
            width: 320px;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
            padding: 14px 16px;
            font-family: inherit;
        }}
        .info-title {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #1e3a8a;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 6px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .info-badge {{
            font-size: 0.7rem;
            background: #fee500;
            color: #371a1a;
            padding: 2px 7px;
            border-radius: 10px;
            font-weight: 700;
        }}
        .info-row {{
            font-size: 0.8rem;
            color: #334155;
            margin-bottom: 4px;
            line-height: 1.4;
        }}
        .info-row strong {{
            color: #64748b;
            min-width: 50px;
            display: inline-block;
        }}
        .info-buttons {{
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px dashed #cbd5e1;
            display: flex;
            gap: 6px;
        }}
        .info-btn {{
            flex: 1;
            text-align: center;
            background: #f1f5f9;
            color: #1e293b;
            text-decoration: none;
            padding: 6px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            transition: background 0.15s;
        }}
        .info-btn.kakao {{
            background: #fee500;
            color: #371a1a;
        }}
        .info-btn:hover {{
            opacity: 0.9;
        }}
    </style>
</head>
<body>

    <div id="sidebar">
        <div class="header">
            <h1>전국 측량업체 공간정보 지도</h1>
            <div class="subtitle">
                <span>공간정보산업협회 등록 {len(valid_companies):,}개사</span>
                <span class="badge-kakaomap">카카오 지도 공식 API</span>
            </div>
        </div>

        <div class="search-area">
            <div class="search-input-wrap">
                <span class="search-icon">🔍</span>
                <input type="text" id="search-input" placeholder="상호명, 대표자, 주소, 업종 검색..." />
            </div>
        </div>

        <div class="region-tabs-container">
            <div class="region-tabs" id="region-tabs">
                <button class="tab-btn active" data-region="전체">전체 ({len(valid_companies):,})</button>
"""

    for r in sorted_regions:
        c_count = region_counts.get(r, 0)
        if c_count > 0:
            html_content += f'                <button class="tab-btn" data-region="{r}">{r} ({c_count:,})</button>\n'

    html_content += f"""            </div>
        </div>

        <div class="count-bar">
            <span>검색/표시 업체: <strong id="visible-count">{len(valid_companies):,}</strong>개</span>
            <span style="font-size:0.75rem; color:#94a3b8;">목록 클릭 시 지도 이동</span>
        </div>

        <div id="company-list"></div>
    </div>

    <!-- Kakao Map Container -->
    <div id="map">
        <div class="map-type-ctrl">
            <button id="btn-roadmap" class="map-type-btn active" onclick="setMapType('roadmap')">지도</button>
            <button id="btn-skyview" class="map-type-btn" onclick="setMapType('skyview')">스카이뷰(위성)</button>
        </div>
    </div>

    <script>
        const companies = {json_str};

        const REGION_CENTERS = {{
            "전체": {{ lat: 36.3, lng: 127.8, level: 12 }},
            "서울": {{ lat: 37.5665, lng: 126.9780, level: 8 }},
            "경기": {{ lat: 37.4138, lng: 127.5183, level: 9 }},
            "인천": {{ lat: 37.4563, lng: 126.7052, level: 8 }},
            "강원": {{ lat: 37.8228, lng: 128.1555, level: 10 }},
            "충북": {{ lat: 36.6357, lng: 127.4912, level: 9 }},
            "충남": {{ lat: 36.5184, lng: 126.8000, level: 9 }},
            "대전": {{ lat: 36.3504, lng: 127.3845, level: 7 }},
            "세종": {{ lat: 36.4800, lng: 127.2890, level: 7 }},
            "전북": {{ lat: 35.7175, lng: 127.1530, level: 9 }},
            "전남": {{ lat: 34.8679, lng: 126.9910, level: 10 }},
            "광주": {{ lat: 35.1595, lng: 126.8526, level: 7 }},
            "경북": {{ lat: 36.5760, lng: 128.5056, level: 10 }},
            "경남": {{ lat: 35.4606, lng: 128.2132, level: 10 }},
            "대구": {{ lat: 35.8714, lng: 128.6014, level: 7 }},
            "부산": {{ lat: 35.1796, lng: 129.0756, level: 8 }},
            "울산": {{ lat: 35.5384, lng: 129.3114, level: 7 }},
            "제주": {{ lat: 33.4996, lng: 126.5312, level: 9 }}
        }};

        let map, clusterer;
        let currentOverlay = null;
        let markerMap = new Map();
        let currentRegion = '전체';
        let currentKeyword = '';

        function setMapType(maptype) {{
            if (!map) return;
            const btnRoadmap = document.getElementById('btn-roadmap');
            const btnSkyview = document.getElementById('btn-skyview');
            if (maptype === 'roadmap') {{
                map.setMapTypeId(kakao.maps.MapTypeId.ROADMAP);
                btnRoadmap.classList.add('active');
                btnSkyview.classList.remove('active');
            }} else {{
                map.setMapTypeId(kakao.maps.MapTypeId.HYBRID);
                btnSkyview.classList.add('active');
                btnRoadmap.classList.remove('active');
            }}
        }}

        function showCompanyOverlay(c, marker) {{
            if (currentOverlay) {{
                currentOverlay.setMap(null);
            }}

            const kakaoSearchUrl = `https://map.kakao.com/link/search/${{encodeURIComponent(c.name + ' ' + c.addr)}}`;
            const kakaoNavUrl = `https://map.kakao.com/link/to/${{encodeURIComponent(c.name)}},${{c.lat}},${{c.lng}}`;

            const contentHtml = `
                <div class=\"custom-infowindow\">
                    <div class=\"info-title\">
                        <span>${{c.name}}</span>
                        <span class=\"info-badge\">${{c.type || '측량업'}}</span>
                    </div>
                    <div class=\"info-row\"><strong>대표자:</strong> ${{c.owner || '-'}}</div>
                    <div class=\"info-row\"><strong>등록번호:</strong> ${{c.regNo || '-'}}</div>
                    <div class=\"info-row\"><strong>전화번호:</strong> ${{c.phone || '-'}}</div>
                    <div class=\"info-row\"><strong>이메일:</strong> ${{c.email || '-'}}</div>
                    <div class=\"info-row\"><strong>주소:</strong> ${{c.addr}}</div>
                    <div class=\"info-buttons\">
                        <a href=\"${{kakaoSearchUrl}}\" target=\"_blank\" class=\"info-btn kakao\">카카오맵 상세</a>
                        <a href=\"${{kakaoNavUrl}}\" target=\"_blank\" class=\"info-btn\">길찾기</a>
                        <button onclick=\"currentOverlay.setMap(null)\" class=\"info-btn\" style=\"background:#e2e8f0; border:none; cursor:pointer;\">닫기</button>
                    </div>
                </div>
            `;

            currentOverlay = new kakao.maps.CustomOverlay({{
                position: marker.getPosition(),
                content: contentHtml,
                xAnchor: 0.5,
                yAnchor: 1.25,
                zIndex: 100
            }});

            currentOverlay.setMap(map);
        }}

        function applyFilter() {{
            if (!clusterer) return;
            clusterer.clear();
            if (currentOverlay) {{
                currentOverlay.setMap(null);
            }}
            markerMap.clear();

            const query = currentKeyword.toLowerCase();
            const filtered = companies.filter(c => {{
                const matchRegion = (currentRegion === '전체' || c.region === currentRegion);
                const matchQuery = !query || 
                    c.name.toLowerCase().includes(query) ||
                    c.owner.toLowerCase().includes(query) ||
                    c.addr.toLowerCase().includes(query) ||
                    c.type.toLowerCase().includes(query);
                return matchRegion && matchQuery;
            }});

            document.getElementById('visible-count').textContent = filtered.length.toLocaleString();

            const newMarkers = [];
            filtered.forEach(c => {{
                const pos = new kakao.maps.LatLng(c.lat, c.lng);
                const marker = new kakao.maps.Marker({{
                    position: pos
                }});

                kakao.maps.event.addListener(marker, 'click', () => {{
                    showCompanyOverlay(c, marker);
                }});

                newMarkers.push(marker);
                markerMap.set(c.id, {{ marker: marker, data: c }});
            }});

            clusterer.addMarkers(newMarkers);

            const listContainer = document.getElementById('company-list');
            listContainer.innerHTML = '';

            const listItems = filtered.slice(0, 120);
            listItems.forEach(c => {{
                const card = document.createElement('div');
                card.className = 'company-card';
                card.innerHTML = `
                    <div class=\"card-title-row\">
                        <div class=\"card-name\">${{c.name}}</div>
                        <span class=\"card-badge\">${{c.type || '측량업'}}</span>
                    </div>
                    <div class=\"card-detail\">
                        <strong>대표:</strong> ${{c.owner || '-'}} &nbsp;|&nbsp; <strong>전화:</strong> ${{c.phone || '-'}}
                    </div>
                    <div class=\"card-detail\" style=\"margin-top:4px; color:#64748b;\">
                        ${{c.addr}}
                    </div>
                `;

                card.addEventListener('click', () => {{
                    const targetPos = new kakao.maps.LatLng(c.lat, c.lng);
                    map.panTo(targetPos);
                    map.setLevel(4);
                    const item = markerMap.get(c.id);
                    if (item) {{
                        showCompanyOverlay(c, item.marker);
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
                notice.textContent = `외 ${{filtered.length - 120}}개 업체가 지도에 표시되어 있습니다. (검색어 입력 시 좁혀집니다)`;
                listContainer.appendChild(notice);
            }}
        }}

        // Initialize Kakao Map inside official load callback
        if (typeof kakao !== 'undefined' && kakao.maps) {{
            kakao.maps.load(() => {{
                const container = document.getElementById('map');
                const options = {{
                    center: new kakao.maps.LatLng(36.3, 127.8),
                    level: 12
                }};
                map = new kakao.maps.Map(container, options);

                const zoomControl = new kakao.maps.ZoomControl();
                map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);

                clusterer = new kakao.maps.MarkerClusterer({{
                    map: map,
                    averageCenter: true,
                    minLevel: 7,
                    disableClickZoom: false
                }});

                kakao.maps.event.addListener(map, 'click', () => {{
                    if (currentOverlay) {{
                        currentOverlay.setMap(null);
                    }}
                }});

                applyFilter();
            }});
        }} else {{
            console.error('Kakao SDK not loaded');
        }}

        // Region Tab Handler
        document.getElementById('region-tabs').addEventListener('click', (e) => {{
            const btn = e.target.closest('.tab-btn');
            if (!btn) return;

            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            currentRegion = btn.getAttribute('data-region');

            if (map && REGION_CENTERS[currentRegion]) {{
                const cfg = REGION_CENTERS[currentRegion];
                map.panTo(new kakao.maps.LatLng(cfg.lat, cfg.lng));
                map.setLevel(cfg.level);
            }}

            applyFilter();
        }});

        // Search Input Handler
        let searchTimer;
        document.getElementById('search-input').addEventListener('input', (e) => {{
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {{
                currentKeyword = e.target.value.trim();
                applyFilter();
            }}, 200);
        }});
    </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Kakao Map updated with corona_Map key: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
