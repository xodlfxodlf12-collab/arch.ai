"""
1일차: 유튜브 트렌드 데이터 크롤러 (crawler.py)
복잡한 구글 API 키 없이 유튜브 웹 페이지의 ytInitialData를 분석하여
인기 동영상 순위, 제목, 채널명, 조회수, 링크, 썸네일 정보를 수집하고 CSV로 저장합니다.
"""

import sys
import io
import re
import json
import csv
from typing import List, Dict
import urllib.parse
import requests

# Windows 콘솔 utf-8 인코딩 대응
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cookie": "PREF=hl=ko&gl=KR;"
}

# 정렬 필터 파라미터 (유튜브 sp 파라미터)
# CAM%3D : 조회수순 (View count)
# CAI%3D : 업로드 날짜순 (Upload date)
SORT_PARAMS = {
    "relevance": "",
    "view_count": "CAM%253D",
    "date": "CAI%253D"
}


def fetch_youtube_data(query: str = "인기 급상승 동영상", sort_by: str = "relevance") -> List[Dict]:
    """
    유튜브에서 특정 키워드의 영상 목록을 크롤링하여 딕셔너리 리스트로 반환합니다.
    """
    params = {"search_query": query}
    if sort_by in SORT_PARAMS and SORT_PARAMS[sort_by]:
        params["sp"] = urllib.parse.unquote(SORT_PARAMS[sort_by])

    print(f"[*] 유튜브 데이터 수집 중: '{query}' (정렬: {sort_by})...")
    try:
        response = requests.get(YOUTUBE_SEARCH_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[!] 요청 실패: {e}")
        return []

    html = response.text

    # ytInitialData 추출
    match = re.search(r'var ytInitialData\s*=\s*({.+?});</script>', html)
    if not match:
        match = re.search(r'ytInitialData\s*=\s*({.+?});', html)

    if not match:
        print("[!] ytInitialData 데이터를 찾을 수 없습니다.")
        return []

    try:
        data = json.loads(match.group(1))
    except Exception as e:
        print(f"[!] JSON 파싱 오류: {e}")
        return []

    videos = []
    seen_ids = set()

    def recursive_extract(node):
        if isinstance(node, dict):
            if "videoRenderer" in node:
                v = node["videoRenderer"]
                video_id = v.get("videoId", "")
                if video_id and video_id not in seen_ids:
                    seen_ids.add(video_id)
                    title = v.get("title", {}).get("runs", [{}])[0].get("text", "")
                    
                    # 채널명
                    channel = ""
                    owner = v.get("ownerText", {}).get("runs", [])
                    if owner:
                        channel = owner[0].get("text", "")
                    if not channel:
                        byline = v.get("longBylineText", {}).get("runs", [])
                        if byline:
                            channel = byline[0].get("text", "")

                    # 조회수
                    views = v.get("viewCountText", {}).get("simpleText", "")
                    if not views:
                        views = v.get("shortViewCountText", {}).get("simpleText", "조회수 정보 없음")

                    # 업로드 시간
                    published = v.get("publishedTimeText", {}).get("simpleText", "최근")

                    # 영상 길이
                    length = v.get("lengthText", {}).get("simpleText", "")

                    # 썸네일
                    thumbs = v.get("thumbnail", {}).get("thumbnails", [])
                    thumb_url = thumbs[-1].get("url", "") if thumbs else ""

                    if title:
                        videos.append({
                            "rank": len(videos) + 1,
                            "title": title,
                            "channel": channel,
                            "views": views,
                            "published": published,
                            "length": length,
                            "video_id": video_id,
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "thumbnail": thumb_url
                        })
            else:
                for val in node.values():
                    recursive_extract(val)
        elif isinstance(node, list):
            for item in node:
                recursive_extract(item)

    recursive_extract(data)
    return videos


def save_to_csv(videos: List[Dict], filepath: str = "trending.csv") -> bool:
    """수집된 비디오 목록을 CSV 파일로 저장합니다."""
    if not videos:
        print("[!] 저장할 데이터가 없습니다.")
        return False

    fieldnames = ["rank", "title", "channel", "views", "published", "length", "video_id", "url", "thumbnail"]
    try:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for v in videos:
                writer.writerow(v)
        print(f"[+] 성공: {len(videos)}개의 데이터를 '{filepath}'에 저장했습니다.")
        return True
    except Exception as e:
        print(f"[!] CSV 저장 실패: {e}")
        return False


def get_trending_keywords(videos: List[Dict], top_n: int = 5) -> List[str]:
    """영상 제목들에서 자주 등장하는 핵심 단어 TOP N을 산출합니다."""
    from collections import Counter
    words = []
    # 제외할 불용어 (조사, 특수문자, 일반 단어)
    stopwords = {"이", "그", "저", "의", "를", "을", "에", "가", "은", "는", "과", "와", "로", "으로", 
                 "vs", "ep", "선공개", "풀버전", "공식", "teaser", "mv", "shorts", "쇼츠", "모음", "동영상", "인기", "급상승"}
    
    for v in videos:
        title = v.get("title", "")
        # 한글, 영문, 숫자 단어 추출 (2글자 이상)
        tokens = re.findall(r'[가-힣a-zA-Z0-9]{2,}', title)
        for token in tokens:
            lower = token.lower()
            if lower not in stopwords:
                words.append(token)

    counts = Counter(words)
    return [word for word, _ in counts.most_common(top_n)]


if __name__ == "__main__":
    # 1일차 단독 실행 테스트: 기본 인기 급상승 동영상 수집 및 CSV 저장
    results = fetch_youtube_data("인기 급상승 동영상", sort_by="relevance")
    if results:
        save_to_csv(results, "d:/Temp/youtube_trending_board/trending.csv")
        keywords = get_trending_keywords(results, 5)
        print(f"[+] 실시간 키워드 TOP 5: {', '.join(keywords)}")
