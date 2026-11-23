import os
import sys
import glob
import zipfile
from PIL import Image, ImageDraw, ImageFont

# 현재 스크립트 위치 기준 상대 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_emoticons")
ZIP_PATH = os.path.join(BASE_DIR, "대학생_16종_이모티콘팩.zip")

CAPTIONS = [
    ("01_hello", "안뇽!"),
    ("02_thanks", "감사합니다!"),
    ("03_agree", "인정!"),
    ("04_nice", "나이스~"),
    ("05_help_me", "살려줘..."),
    ("06_homework", "과제 폭탄"),
    ("07_faint", "기절..."),
    ("08_despair", "F각이다"),
    ("09_late", "지각이다!"),
    ("10_eat", "밥 먹자"),
    ("11_cheers", "적셔~"),
    ("12_poor", "거지..."),
    ("13_fighting", "가보자고!"),
    ("14_perfect", "완벽해"),
    ("15_vacation", "종강이다!!"),
    ("16_escape", "칼퇴!!"),
]

def find_sheet_image():
    """사용자가 인자로 넘겼거나, 현재 폴더 내 시트 이미지를 자동 탐색"""
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        return sys.argv[1]
    
    # 프로젝트 폴더 내 후보 파일 탐색
    candidates = [
        os.path.join(BASE_DIR, "sheet.png"),
        os.path.join(BASE_DIR, "sheet.jpg"),
        os.path.join(BASE_DIR, "emoticon_sheet.png"),
        os.path.join(BASE_DIR, "emoticon_sheet.jpg"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
            
    # 확장자 검색 (png, jpg, webp)
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        found = glob.glob(os.path.join(BASE_DIR, ext))
        if found:
            return found[0]
            
    return None

def get_font(font_size=38):
    """OS별 지원 한글 폰트 탐색 및 로드"""
    font_candidates = [
        "C:/Windows/Fonts/malgunbd.ttf",      # Windows 맑은고딕 볼드
        "C:/Windows/Fonts/malgun.ttf",        # Windows 맑은고딕
        "C:/Windows/Fonts/NanumGothicBold.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc", # macOS
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf", # Linux
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, font_size)
            except Exception:
                continue
    return ImageFont.load_default()

def make_emoticons(sheet_path=None):
    if not sheet_path:
        sheet_path = find_sheet_image()

    if not sheet_path or not os.path.exists(sheet_path):
        print(f"[오류] 4x4 캐릭터 시트 이미지를 찾을 수 없습니다.")
        print(f"사용법: python generate_pack.py [시트_이미지_경로.png/jpg]")
        print(f"또는 프로젝트 폴더({BASE_DIR})에 'sheet.png' 파일을 넣어주세요.")
        return False

    print(f"시트 이미지 로드: {sheet_path}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    sheet = Image.open(sheet_path).convert("RGBA")
    w, h = sheet.size
    
    cell_w = w / 4.0
    cell_h = h / 4.0
    font = get_font(38)

    generated_files = []

    for idx, (filename, caption) in enumerate(CAPTIONS):
        row = idx // 4
        col = idx % 4

        # 그리드 셀 좌표 계산
        left = int(col * cell_w)
        top = int(row * cell_h)
        right = int((col + 1) * cell_w)
        bottom = int((row + 1) * cell_h)

        crop_img = sheet.crop((left, top, right, bottom))

        # 카카오톡 규격: 360x360 캔버스
        target_size = (360, 360)
        emoticon = crop_img.resize(target_size, Image.Resampling.LANCZOS)
        
        # 텍스트 오버레이 (카톡 스타일 볼드 폰트 + 외곽선 스트로크)
        draw = ImageDraw.Draw(emoticon)
        bbox = draw.textbbox((0, 0), caption, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # 텍스트 위치: 하단 중앙
        text_x = (360 - text_w) // 2
        text_y = 360 - text_h - 22

        # 텍스트 외곽선 (두꺼운 흰색 테두리 + 어두운 본문)
        stroke_width = 4
        draw.text((text_x, text_y), caption, font=font, fill="#222222", 
                  stroke_width=stroke_width, stroke_fill="#FFFFFF")

        file_path = os.path.join(OUTPUT_DIR, f"{filename}.png")
        emoticon.save(file_path, "PNG")
        generated_files.append(file_path)

    # ZIP 압축 (index.html에서 바로 다운로드 가능하도록 프로젝트 루트에 저장)
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in generated_files:
            zipf.write(file, os.path.basename(file))

    print(f"[OK] 16종 이모티콘 생성 완료! ({OUTPUT_DIR})")
    print(f"[OK] ZIP 압축 완료: {ZIP_PATH}")
    print(f"[OK] index.html 파일을 브라우저로 열어 카카오톡 뷰어를 확인하세요!")
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    make_emoticons(target)
