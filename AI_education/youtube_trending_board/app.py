"""
2일차: 실시간 유튜브 인급동 랭킹 전광판 데스크톱 앱 (app.py)
Tkinter와 PIL을 활용한 프리미엄 유튜브 다크 모드 GUI
- 멜론 차트 스타일 순위표 & 썸네일 렌더링
- 더블클릭 시 웹 브라우저에서 유튜브 영상 즉시 재생
- 실시간 키워드 전광판 (워드클라우드 태그 칩 클릭 시 즉시 검색)
- 백그라운드 스레드 크롤링 & 실시간 로컬 필터링 검색
"""

import os
import sys
import csv
import io
import threading
import webbrowser
from typing import List, Dict
import urllib.request

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# 크롤러 모듈 임포트
from crawler import fetch_youtube_data, save_to_csv, get_trending_keywords

# 색상 테마 정의 (유튜브 프리미엄 다크 스타일)
THEME = {
    "bg_root": "#0F0F0F",
    "bg_header": "#181818",
    "bg_card": "#212121",
    "bg_card_hover": "#2A2A2A",
    "bg_card_select": "#383838",
    "accent_red": "#FF0000",
    "accent_red_hover": "#CC0000",
    "text_white": "#FFFFFF",
    "text_gray": "#AAAAAA",
    "text_muted": "#717171",
    "border": "#303030",
    "chip_bg": "#272727",
    "chip_active": "#FF0000",
    "gold": "#F59E0B"
}

CSV_PATH = os.path.join(os.path.dirname(__file__), "trending.csv")


class YouTubeTrendingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔥 실시간 유튜브 인급동 랭킹 전광판 (Trending Top 20)")
        self.geometry("960x780")
        self.minsize(800, 600)
        self.configure(bg=THEME["bg_root"])

        self.videos: List[Dict] = []
        self.filtered_videos: List[Dict] = []
        self.thumb_cache = {}
        self.current_query = "인기 급상승 동영상"
        self.current_sort = "relevance"
        self.selected_video = None

        self._init_styles()
        self._build_ui()

        # 화면 중앙 배치 및 맨 앞으로 띄우기
        self.update_idletasks()
        w, h = 960, 780
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.lift()
        self.attributes('-topmost', True)
        self.after(500, lambda: self.attributes('-topmost', False))
        self.focus_force()

        # 어제 저장한 CSV가 있으면 우선 로드, 없으면 실시간 크롤링 시작
        if os.path.exists(CSV_PATH):
            self.load_from_csv(CSV_PATH)
        else:
            self.refresh_data_async(self.current_query)

    def _init_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # 스크롤바 스타일
        style.configure("Vertical.TScrollbar", 
                        gripcount=0, 
                        background="#333333", 
                        darkcolor="#222222", 
                        lightcolor="#444444", 
                        troughcolor=THEME["bg_root"], 
                        bordercolor=THEME["bg_root"], 
                        arrowcolor=THEME["text_gray"])

    def _build_ui(self):
        # 1. 최상단 헤더
        header_frame = tk.Frame(self, bg=THEME["bg_header"], padx=20, pady=12)
        header_frame.pack(fill="x", side="top")

        # 로고 & 타이틀
        title_box = tk.Frame(header_frame, bg=THEME["bg_header"])
        title_box.pack(side="left")

        logo_label = tk.Label(title_box, text="▶", font=("Helvetica", 18, "bold"), 
                              fg=THEME["accent_red"], bg=THEME["bg_header"])
        logo_label.pack(side="left", padx=(0, 8))

        main_title = tk.Label(title_box, text="YOUTUBE TRENDING", font=("Impact", 18), 
                              fg=THEME["text_white"], bg=THEME["bg_header"])
        main_title.pack(side="left")

        sub_title = tk.Label(title_box, text="실시간 인급동 전광판", font=("Malgun Gothic", 11, "bold"), 
                             fg=THEME["text_gray"], bg=THEME["bg_header"])
        sub_title.pack(side="left", padx=(8, 0), pady=(3, 0))

        # 새로고침 & 로딩 상태 표시
        ctrl_box = tk.Frame(header_frame, bg=THEME["bg_header"])
        ctrl_box.pack(side="right")

        self.status_label = tk.Label(ctrl_box, text="준비 완료", font=("Malgun Gothic", 9), 
                                     fg=THEME["text_gray"], bg=THEME["bg_header"])
        self.status_label.pack(side="left", padx=10)

        self.btn_refresh = tk.Button(ctrl_box, text="🔄 새로고침", font=("Malgun Gothic", 9, "bold"),
                                     bg=THEME["accent_red"], fg=THEME["text_white"],
                                     activebackground=THEME["accent_red_hover"], activeforeground="white",
                                     relief="flat", padx=12, pady=4, cursor="hand2",
                                     command=lambda: self.refresh_data_async(self.current_query))
        self.btn_refresh.pack(side="right")

        # 2. 실시간 키워드 전광판 바 (워드클라우드 핫 키워드 TOP 5)
        self.ticker_frame = tk.Frame(self, bg="#1B1B1B", padx=20, pady=6)
        self.ticker_frame.pack(fill="x")

        ticker_title = tk.Label(self.ticker_frame, text="⚡ 지금 핫한 키워드 :", 
                                font=("Malgun Gothic", 9, "bold"), fg=THEME["gold"], bg="#1B1B1B")
        ticker_title.pack(side="left", padx=(0, 10))

        self.keywords_container = tk.Frame(self.ticker_frame, bg="#1B1B1B")
        self.keywords_container.pack(side="left", fill="x", expand=True)

        # 3. 검색 & 테마 퀵 칩 바
        filter_bar = tk.Frame(self, bg=THEME["bg_root"], padx=20, pady=10)
        filter_bar.pack(fill="x")

        # 테마 바로가기 칩 버튼
        quick_chips = [
            ("🔥 인급동 TOP", "인기 급상승 동영상"),
            ("📱 쇼츠 챌린지", "쇼츠 밈 챌린지"),
            ("🎓 대학생 브이로그", "대학생 브이로그"),
            ("💻 코딩/IT", "개발자 IT 테크 트렌드"),
            ("🎵 인기 음악", "인기 음악 차트")
        ]
        chips_frame = tk.Frame(filter_bar, bg=THEME["bg_root"])
        chips_frame.pack(side="left")

        for label, q in quick_chips:
            btn = tk.Button(chips_frame, text=label, font=("Malgun Gothic", 9),
                            bg=THEME["chip_bg"], fg=THEME["text_white"],
                            activebackground=THEME["accent_red"], activeforeground="white",
                            relief="flat", padx=9, pady=3, cursor="hand2",
                            command=lambda target_q=q: self.refresh_data_async(target_q))
            btn.pack(side="left", padx=3)

        # 우측 검색창
        search_box = tk.Frame(filter_bar, bg=THEME["bg_root"])
        search_box.pack(side="right")

        self.search_entry = tk.Entry(search_box, font=("Malgun Gothic", 10), bg="#212121", 
                                     fg=THEME["text_white"], insertbackground="white", 
                                     relief="flat", width=20)
        self.search_entry.pack(side="left", ipady=4, padx=(0, 4))
        self.search_entry.bind("<KeyRelease>", self.on_search_key)
        self.search_entry.bind("<Return>", lambda e: self.refresh_data_async(self.search_entry.get().strip()))

        btn_search = tk.Button(search_box, text="🔍 검색", font=("Malgun Gothic", 9, "bold"),
                               bg="#333333", fg=THEME["text_white"],
                               activebackground="#444444", activeforeground="white",
                               relief="flat", padx=10, pady=4, cursor="hand2",
                               command=lambda: self.refresh_data_async(self.search_entry.get().strip()))
        btn_search.pack(side="left")

        # 4. 메인 컨텐츠 영역 (스크롤 리스트)
        main_content = tk.Frame(self, bg=THEME["bg_root"], padx=20, pady=5)
        main_content.pack(fill="both", expand=True)

        # 캔버스 + 스크롤바 구성
        self.canvas = tk.Canvas(main_content, bg=THEME["bg_root"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_content, orient="vertical", command=self.canvas.yview)
        self.list_container = tk.Frame(self.canvas, bg=THEME["bg_root"])

        self.list_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_container, anchor="nw")
        self.canvas.configure(xscrollcommand="", yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        # 마우스 휠 스크롤 연동
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 5. 하단 액션 & 상태바
        bottom_bar = tk.Frame(self, bg=THEME["bg_header"], padx=20, pady=10)
        bottom_bar.pack(fill="x", side="bottom")

        self.info_label = tk.Label(bottom_bar, text="💡 목록의 영상을 더블클릭하면 즉시 유튜브에서 재생됩니다.", 
                                   font=("Malgun Gothic", 9), fg=THEME["text_gray"], bg=THEME["bg_header"])
        self.info_label.pack(side="left")

        btn_csv_export = tk.Button(bottom_bar, text="📁 CSV 다시 저장", font=("Malgun Gothic", 9),
                                   bg="#2B2B2B", fg=THEME["text_white"], relief="flat", padx=10, pady=3,
                                   cursor="hand2", command=self.export_csv)
        btn_csv_export.pack(side="right", padx=(8, 0))

        self.btn_open = tk.Button(bottom_bar, text="▶ 선택 영상 재생", font=("Malgun Gothic", 9, "bold"),
                                  bg=THEME["accent_red"], fg=THEME["text_white"],
                                  activebackground=THEME["accent_red_hover"], activeforeground="white",
                                  relief="flat", padx=14, pady=3, cursor="hand2",
                                  command=self.open_selected_video)
        self.btn_open.pack(side="right")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def update_keywords_ticker(self, keywords: List[str]):
        """상단 키워드 태그 전광판 업데이트"""
        for widget in self.keywords_container.winfo_children():
            widget.destroy()

        if not keywords:
            lbl = tk.Label(self.keywords_container, text="데이터 수집 중...", font=("Malgun Gothic", 9),
                           fg=THEME["text_muted"], bg="#1B1B1B")
            lbl.pack(side="left")
            return

        for idx, kw in enumerate(keywords, 1):
            btn = tk.Button(self.keywords_container, text=f"#{kw}", font=("Malgun Gothic", 9, "bold"),
                            bg="#2D2D2D", fg="#60A5FA", activebackground="#3B82F6", activeforeground="white",
                            relief="flat", padx=6, pady=1, cursor="hand2",
                            command=lambda target=kw: self.refresh_data_async(target))
            btn.pack(side="left", padx=3)

    def render_video_cards(self, video_list: List[Dict]):
        """멜론 차트 스타일의 비디오 카드 리스트 렌더링"""
        # 기존 카드들 제거
        for widget in self.list_container.winfo_children():
            widget.destroy()

        if not video_list:
            empty_box = tk.Frame(self.list_container, bg=THEME["bg_root"], pady=60)
            empty_box.pack(fill="x")
            tk.Label(empty_box, text="검색 결과가 없습니다.", font=("Malgun Gothic", 12), 
                     fg=THEME["text_gray"], bg=THEME["bg_root"]).pack()
            return

        for i, video in enumerate(video_list):
            card = tk.Frame(self.list_container, bg=THEME["bg_card"], bd=0, padx=12, pady=10)
            card.pack(fill="x", pady=4)

            # 카드 데이터 바인딩
            card.video_data = video

            # 1) 순위 배지 (1~3위는 골드/포인트 컬러)
            rank = video.get("rank", i + 1)
            rank_color = THEME["accent_red"] if rank <= 3 else THEME["text_gray"]
            rank_label = tk.Label(card, text=f"{rank:02d}", font=("Impact", 20), 
                                  fg=rank_color, bg=THEME["bg_card"], width=3)
            rank_label.pack(side="left", padx=(0, 10))

            # 2) 썸네일 미리보기 영역
            thumb_label = tk.Label(card, text="🎬", font=("Segoe UI Emoji", 18), 
                                   bg="#141414", fg=THEME["text_muted"], width=10, height=3)
            thumb_label.pack(side="left", padx=(0, 12))

            # 비동기로 썸네일 다운로드 후 주입
            thumb_url = video.get("thumbnail", "")
            if thumb_url:
                self._load_thumbnail_async(thumb_url, thumb_label)

            # 3) 비디오 정보 (제목, 채널명, 조회수, 업로드일)
            info_frame = tk.Frame(card, bg=THEME["bg_card"])
            info_frame.pack(side="left", fill="both", expand=True)

            title_text = video.get("title", "")
            title_lbl = tk.Label(info_frame, text=title_text, font=("Malgun Gothic", 11, "bold"), 
                                 fg=THEME["text_white"], bg=THEME["bg_card"], anchor="w", justify="left")
            title_lbl.pack(fill="x", pady=(0, 4))

            meta_text = f"👤 {video.get('channel', '알 수 없음')}   •   👁 {video.get('views', '조회수 정보 없음')}   •   🕒 {video.get('published', '최근')}"
            if video.get("length"):
                meta_text += f"   •   ⏱ {video.get('length')}"
            meta_lbl = tk.Label(info_frame, text=meta_text, font=("Malgun Gothic", 9), 
                                fg=THEME["text_gray"], bg=THEME["bg_card"], anchor="w")
            meta_lbl.pack(fill="x")

            # 4) 우측 바로 재생 버튼
            play_btn = tk.Button(card, text="▶ 재생", font=("Malgun Gothic", 9, "bold"),
                                 bg="#333333", fg=THEME["text_white"],
                                 activebackground=THEME["accent_red"], activeforeground="white",
                                 relief="flat", padx=10, pady=5, cursor="hand2",
                                 command=lambda u=video.get("url"): self.open_url(u))
            play_btn.pack(side="right", padx=(10, 0))

            # 이벤트 바인딩 (더블클릭 즉시 재생, 단일클릭 선택, 마우스 호버 효과)
            self._bind_card_events(card, [card, rank_label, thumb_label, info_frame, title_lbl, meta_lbl], video)

    def _bind_card_events(self, card, widgets, video):
        def on_enter(e):
            if self.selected_video != video:
                card.configure(bg=THEME["bg_card_hover"])
                for w in widgets:
                    try:
                        w.configure(bg=THEME["bg_card_hover"])
                    except:
                        pass

        def on_leave(e):
            if self.selected_video != video:
                card.configure(bg=THEME["bg_card"])
                for w in widgets:
                    try:
                        w.configure(bg=THEME["bg_card"])
                    except:
                        pass

        def on_click(e):
            self.selected_video = video
            # 모든 카드의 배경 초기화
            for c in self.list_container.winfo_children():
                if hasattr(c, "video_data"):
                    c.configure(bg=THEME["bg_card"])
                    for child in c.winfo_children():
                        try:
                            child.configure(bg=THEME["bg_card"])
                        except:
                            pass
            # 선택된 카드 하이라이트
            card.configure(bg=THEME["bg_card_select"])
            for w in widgets:
                try:
                    w.configure(bg=THEME["bg_card_select"])
                except:
                    pass
            self.info_label.configure(text=f"선택됨: [{video.get('channel')}] {video.get('title')[:45]}...")

        def on_double_click(e):
            self.open_url(video.get("url", ""))

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)
            w.bind("<Double-Button-1>", on_double_click)

    def _load_thumbnail_async(self, url: str, label_widget: tk.Label):
        """썸네일을 백그라운드에서 다운받아 카드에 표시"""
        if url in self.thumb_cache:
            img = self.thumb_cache[url]
            label_widget.configure(image=img, text="", width=120, height=68)
            label_widget.image = img
            return

        def fetch():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    raw_data = resp.read()
                pil_img = Image.open(io.BytesIO(raw_data))
                pil_img = pil_img.resize((120, 68), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                self.thumb_cache[url] = tk_img

                # 메인 UI 스레드에서 이미지 적용
                self.after(0, lambda: self._apply_thumb(label_widget, tk_img))
            except Exception:
                pass

        threading.Thread(target=fetch, daemon=True).start()

    def _apply_thumb(self, label_widget: tk.Label, tk_img):
        if label_widget.winfo_exists():
            label_widget.configure(image=tk_img, text="", width=120, height=68)
            label_widget.image = tk_img

    def on_search_key(self, event):
        """검색창 실시간 로컬 필터링"""
        query = self.search_entry.get().strip().lower()
        if not query:
            self.filtered_videos = self.videos
        else:
            self.filtered_videos = [
                v for v in self.videos
                if query in v.get("title", "").lower() or query in v.get("channel", "").lower()
            ]
        self.render_video_cards(self.filtered_videos)

    def refresh_data_async(self, query: str = "인기 급상승 동영상"):
        """백그라운드 스레드에서 크롤링 수행"""
        if not query:
            query = "인기 급상승 동영상"
        self.current_query = query

        self.btn_refresh.configure(state="disabled", text="⏳ 수집 중...")
        self.status_label.configure(text=f"'{query}' 최신 데이터 수집 중...")

        def worker():
            results = fetch_youtube_data(query, sort_by=self.current_sort)
            self.after(0, lambda: self._on_crawl_finished(results, query))

        threading.Thread(target=worker, daemon=True).start()

    def _on_crawl_finished(self, results: List[Dict], query: str):
        self.btn_refresh.configure(state="normal", text="🔄 새로고침")
        if not results:
            self.status_label.configure(text="수집 실패 (네트워크를 확인하세요)")
            messagebox.showwarning("수집 알림", f"'{query}'에 대한 동영상 데이터를 가져오지 못했습니다.")
            return

        self.videos = results
        self.filtered_videos = results
        self.status_label.configure(text=f"업데이트 완료 ({len(results)}개 영상)")

        # 키워드 전광판 갱신
        top_keywords = get_trending_keywords(results, 5)
        self.update_keywords_ticker(top_keywords)

        # 멜론 차트 카드 렌더링
        self.render_video_cards(self.filtered_videos)

        # CSV 자동 저장
        save_to_csv(results, CSV_PATH)

    def load_from_csv(self, filepath: str):
        """저장된 CSV 파일로부터 데이터 불러오기"""
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                loaded = list(reader)
                for i, row in enumerate(loaded):
                    row["rank"] = int(row.get("rank", i + 1))
                self.videos = loaded
                self.filtered_videos = loaded

            top_keywords = get_trending_keywords(self.videos, 5)
            self.update_keywords_ticker(top_keywords)
            self.render_video_cards(self.filtered_videos)
            self.status_label.configure(text=f"CSV 로드 완료 ({len(loaded)}개)")
        except Exception as e:
            print(f"CSV 로드 실패: {e}")
            self.refresh_data_async()

    def open_url(self, url: str):
        """기본 브라우저에서 유튜브 영상 열기"""
        if url:
            webbrowser.open(url)

    def open_selected_video(self):
        if self.selected_video and self.selected_video.get("url"):
            self.open_url(self.selected_video["url"])
        else:
            messagebox.showinfo("안내", "목록에서 재생할 영상을 먼저 선택해 주세요.")

    def export_csv(self):
        if self.videos:
            save_to_csv(self.videos, CSV_PATH)
            messagebox.showinfo("완료", f"현재 데이터 {len(self.videos)}개가 trending.csv로 성공적으로 저장되었습니다.")


if __name__ == "__main__":
    app = YouTubeTrendingApp()
    app.mainloop()
