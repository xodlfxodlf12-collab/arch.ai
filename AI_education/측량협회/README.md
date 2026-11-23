# 전국 측량·공간정보 기업 통합 공간정보 지도 (Korea Surveying & Geospatial Companies Map)

대한민국 공간정보산업협회(KASM) 등록 측량업체 전수 데이터를 수집하고 정제하여 구축한 대화형 웹 지도 시스템입니다.

## 📌 주요 특징
1. **기업 단위 통합 (4,447개사)**
   - 6,628개 개별 사업 면허 데이터를 고유 기업 기준으로 통합하여 동일 위치 핀 중복 제거.
   - 단일 기업이 보유한 모든 사업 분야(최대 10개)를 뱃지 및 태그로 구조화.
2. **카카오 고정밀 지오코딩 (95.9%)**
   - 카카오 로컬 API를 통해 도로명 주소 기반 실제 건물 단위 위도/경도 좌표 부여.
3. **3중 멀티 필터링**
   - **17대 광역시·도 필터**: 서울, 경기, 부산, 강원, 제주 등 지역별 이동 및 필터링.
   - **기업 규모 필터**: 단독 기업(1개 분야), 복합 기업(2개 이상 분야, 786개사), 종합 대형기업(5개 이상 분야, 197개사).
   - **13대 사업 분야 필터**: 영상처리업(289개사), 항공촬영업(21개사), 수치지도제작(688개사), 지하시설물측량(639개사), 공공측량(1,113개사) 등 원클릭 추출.
4. **대화형 검색 및 스마트 클러스터링**
   - 상호명, 대표자명, 주소, 업종 실시간 검색.
   - 수천 개 마커의 시각적 과밀을 방지하는 마커 클러스터링(Leaflet MarkerCluster) 탑재.
   - 마커 및 카드 클릭 시 카카오맵 상세 보기 및 길찾기 연동.

## 🗂 파일 구성
- `index.html` / `survey_map_osm.html`: OpenStreetMap 기반 대화형 웹 지도 (GitHub Pages 지원)
- `survey_companies_consolidated.json`: 기업별 통합 및 정제 완료된 공간정보 데이터 (JSON)
- `survey_companies_consolidated.csv`: 기업별 통합 데이터 (CSV, UTF-8 BOM)
- `survey_companies_geocoded.json`: 카카오 정밀 좌표 포함 원본 면허 데이터
- `collect_survey_companies.py`: 공간정보산업협회 663개 페이지 전량 수집기
- `geocode_with_kakao.py`: 카카오 REST API 고정밀 지오코딩 스크립트
- `consolidate_companies.py`: 기업별 다중 사업 통합 및 행정구역 정규화 스크립트
- `build_osm_map.py`: 지도 웹 페이지 빌더
- `run_map_server.bat`: 로컬 웹서버 실행 배치 파일

## 🌐 GitHub Pages 서비스
저장소 설정(Settings > Pages)에서 `main` 브랜치를 활성화하면 전 세계 어디서나 웹 브라우저로 접속할 수 있습니다.
- 데모 URL: `https://horey205.github.io/surveying_companies/`

