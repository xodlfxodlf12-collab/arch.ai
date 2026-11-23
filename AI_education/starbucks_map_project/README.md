# ☕ 스타벅스 전국 매장 크롤러 & 인터랙티브 지도 (Starbucks Map)

웹에서 스타벅스 전국 매장 데이터를 수집하고, 브라우저에서 바로 열 수 있는 대화형 인터랙티브 지도를 제작하는 프로젝트입니다.

---

## 📁 프로젝트 구조

```
starbucks_map_project/
├── crawler.py          # [1일차] 스타벅스 전국 17개 시도 매장 크롤러 (starbucks.csv 생성)
├── visualize_map.py    # [2일차] 고급 Leaflet.js 인터랙티브 지도 생성기 (검색, 필터, 팝업)
├── folium_map.py       # [2일차 대체] 파이썬 Folium 초간단 실습용 지도 생성기
├── map.html            # 최종 생성된 인터랙티브 지도 웹페이지
├── starbucks.csv       # 수집된 전국 매장 데이터 (이름, 주소, 위경도, 전화번호)
└── README.md           # 실습 가이드
```

---

## 🚀 빠른 시작

### 1. 필수 라이브러리 설치
```bash
pip install requests pandas folium
```

### 2. 실행 순서

#### [1단계] 크롤러 실행 (데이터 수집)
```bash
python crawler.py
```
* 스타벅스 전국 1,900+ 매장 정보를 수집하여 `starbucks.csv`로 저장합니다.

#### [2단계] 지도 생성 스크립트 실행
```bash
python visualize_map.py
# 또는 초간단 Folium 버전: python folium_map.py
```
* 실행 후 생성된 `map.html` 파일을 더블클릭하여 웹 브라우저에서 확인합니다.

---

## 💡 수업 핵심 포인트: "지도가 하얗게 깨질 때의 대처법"

* **문제 상황**: 브라우저에서 `map.html`을 열었을 때 마커만 뜨고 배경 지도가 하얗게 나오지 않는 경우
* **원인**: 네이버/카카오/VWorld 등 국내 지도 타일이 로컬 파일(`file://`) 프로토콜이나 API 인증 차단으로 인해 로딩이 막히는 현상
* **해결 지침**:
  * AI에게 프롬프트를 줄 때 **`tiles='OpenStreetMap'`** 또는 **`CartoDB Positron`**을 명시하도록 지도합니다.
  * 오픈소스 글로벌 타일을 사용하면 별도 API 키 없이 로컬에서도 100% 정상 출력됩니다.
