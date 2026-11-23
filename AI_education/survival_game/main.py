"""
텍스트 인터랙티브 생존 게임: 학점 수호 & 칼퇴 챌린지
- 턴제 시뮬레이션 게임
- 대학생 모드 (F학점 피하기) / 직장인 모드 (칼퇴 & 생존기)
"""

import os
import sys
import time
import random

# 콘솔 화면 지우기 및 ANSI 색상 설정
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# 색상 유틸리티
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

def print_slow(text, delay=0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def press_enter():
    input(f"\n{Color.YELLOW}[Enter 키를 누르면 계속 진행합니다...]{Color.RESET}")

# ==========================================
# 1. 대학생 모드: "F학점을 피하는 방법 (기말고사 D-7)"
# ==========================================
def play_student_mode():
    day = 7
    mental = 100
    grade = 3.5  # 최대 4.5, 최소 0.0
    passed_days = 0

    events = [
        {
            "day": 7,
            "title": "D-7 기말고사 1주일 전",
            "desc": "시험 일주일 전, 밀린 인강이 무려 28개나 밀려있다. 오늘 뭐부터 할까?",
            "choices": [
                {"text": "하루 8시간 인강 정주행 (2배속)", "mental": -25, "grade": +0.3, "msg": "머리가 깨질 것 같지만 핵심 개념을 채워넣었습니다."},
                {"text": "족보부터 구하러 과방/단톡방을 기웃거린다", "mental": -10, "grade": +0.2, "msg": "선배가 남겨준 3년 전 족보를 입수했습니다!"},
                {"text": "일단 마음의 안정을 위해 침대에서 유튜브 시청", "mental": +20, "grade": -0.3, "msg": "쇼츠 보다가 5시간이 순삭되었습니다..."}
            ]
        },
        {
            "day": 6,
            "title": "D-6 팀플의 저주",
            "desc": "기말 대체 팀플 과제 제출일이 다가왔는데, 조원 2명이 연락두절 상태다.",
            "choices": [
                {"text": "내가 다 총대 메고 밤샘 하드캐리한다", "mental": -35, "grade": +0.5, "msg": "피눈물 흘리며 제출 완료. 점수는 지켰지만 영혼이 가출했습니다."},
                {"text": "교수님께 무임승차 조원 명단을 고발 메일로 보낸다", "mental": -10, "grade": +0.2, "special_chance": 0.3, "msg": "교수님이 정의구현 해주셨으나 약간의 후폭풍이 있습니다."},
                {"text": "될 대로 되라며 조원들이 낸 분량 그대로 합쳐서 제출", "mental": +10, "grade": -0.4, "msg": "개판 오분 전 과제물이 제출되었습니다. 교수님의 한숨이 들립니다."}
            ]
        },
        {
            "day": 5,
            "title": "D-5 전공 서적과의 사투",
            "desc": "도서관 열람실. 책을 펴자마자 쏟아지는 졸음... 시험 범위가 무려 400페이지다.",
            "choices": [
                {"text": "고카페인 몬스터 음료 원샷하고 스퍼트", "mental": -20, "grade": +0.3, "msg": "심장이 터질 것 같지만 200페이지를 독파했습니다."},
                {"text": "스터디 카페 친구들과 서로 퀴즈 내주며 복습", "mental": -5, "grade": +0.25, "msg": "서로 격려하며 효율적으로 외웠습니다."},
                {"text": "책 덮고 도서관 앞 잔디밭에서 캔맥주 한 캔", "mental": +25, "grade": -0.4, "msg": "낭만은 챙겼으나 기억 속에 남은 공식은 0개입니다."}
            ]
        },
        {
            "day": 4,
            "title": "D-4 악마의 유혹",
            "desc": "저녁 9시, 고등학교 절친에게서 전화가 왔다.\n'야, 오늘 족발에 소맥 한잔각인데 나올래? 오늘 안 나오면 절교다.'",
            "choices": [
                {"text": "칼같이 차단하고 독서실에 남는다", "mental": -20, "grade": +0.3, "msg": "의리의 배신자 소리를 들었지만, 기말 예상문제를 다 풀었습니다."},
                {"text": "이건 못 참지! 바로 뛰어나가 새벽까지 달린다", "mental": +35, "grade": -0.6, "msg": "족발은 맛있었고, 다음 날 점심까지 시체처럼 잤습니다."},
                {"text": "딱 1시간만 먹고 오겠다고 타협한다", "gamble": True, "success_rate": 0.5,
                 "success_msg": "정확히 1시간 만에 칼퇴장하여 공부 복귀에 성공!", "success_m": +15, "success_g": +0.1,
                 "fail_msg": "분위기에 휩쓸려 3차 노래방까지 끌려갔습니다...", "fail_m": -20, "fail_g": -0.5}
            ]
        },
        {
            "day": 3,
            "title": "D-3 교수님의 기습 공지",
            "desc": "e-캠퍼스에 기습 공지 등록: '중간고사 평균이 높아 기말 서술형 5문항 난이도를 대폭 상향합니다.'",
            "choices": [
                {"text": "멘붕을 딛고 논문과 심화 자료까지 찾아 분석한다", "mental": -30, "grade": +0.4, "msg": "교수님의 의도를 파악하고 심화 문제까지 대비했습니다."},
                {"text": "교수님 연구실에 찾아가 질문 폭격을 날린다", "mental": -15, "grade": +0.3, "msg": "교수님이 '자네 눈빛이 마음에 드는군' 하며 힌트를 주셨습니다!"},
                {"text": "에브리타임(커뮤니티)에 들어가서 교수님 성토글 작성", "mental": +15, "grade": -0.2, "msg": "댓글로 공감은 많이 받았으나 학점은 구제받지 못했습니다."}
            ]
        },
        {
            "day": 2,
            "title": "D-2 밤샘 벼락치기 데이",
            "desc": "이제 남은 시간 48시간. 핏발 선 눈으로 책상을 지키고 있다.",
            "choices": [
                {"text": "오늘 밤은 샌다! 밤샘 올나잇 풀가동", "mental": -35, "grade": +0.45, "msg": "신체 리듬은 파괴되었지만 전 범위 1회독을 마쳤습니다."},
                {"text": "컨디션 관리를 위해 6시간 푹 자고 맑은 정신으로 승부", "mental": +15, "grade": +0.1, "msg": "몸은 상쾌하지만 안 본 챕터가 자꾸 눈에 밟힙니다."},
                {"text": "시험에 나올 것 같은 단원만 찍어서 집중 공략", "gamble": True, "success_rate": 0.6,
                 "success_msg": "적중률 대박! 찍은 곳에서 요약본 완성!", "success_m": +10, "success_g": +0.35,
                 "fail_msg": "안 찍은 단원에서 중요 공식이 대거 발견되었습니다...", "fail_m": -25, "fail_g": -0.2}
            ]
        },
        {
            "day": 1,
            "title": "D-1 결전 전야 (마지막 선택)",
            "desc": "내일 아침 9시 1교시부터 전공 기말고사 시작이다.",
            "choices": [
                {"text": "오답노트와 요점정리 최종 훑어보기", "mental": -15, "grade": +0.25, "msg": "마지막 한 끗 차이를 채웠습니다."},
                {"text": "알람 5개 맞추고 일찍 잠자리에 들기", "mental": +20, "grade": +0.1, "msg": "최상의 컨디션으로 시험장에 들어갈 준비 완료!"},
                {"text": "불안해서 새벽 5시까지 전전긍긍 폰 보기", "mental": -25, "grade": -0.2, "msg": "잠도 못 자고 공부도 안 된 최악의 결전 전야..."}
            ]
        }
    ]

    for ev in events:
        clear_screen()
        print(f"{Color.CYAN}===================================================={Color.RESET}")
        print(f"{Color.BOLD}🎓 대학생 모드: F학점을 피하는 방법 (기말고사 D-{ev['day']}){Color.RESET}")
        print(f"{Color.CYAN}===================================================={Color.RESET}")
        
        # 스탯 표시 바
        m_color = Color.GREEN if mental >= 60 else (Color.YELLOW if mental >= 30 else Color.RED)
        g_color = Color.GREEN if grade >= 3.5 else (Color.YELLOW if grade >= 2.5 else Color.RED)
        print(f"📊 [현재 상태] 남은 시간: {Color.BOLD}D-{ev['day']}{Color.RESET} | 멘탈: {m_color}{mental}/100{Color.RESET} | 예상 학점: {g_color}{grade:.2f}/4.5{Color.RESET}")
        print(f"{Color.CYAN}----------------------------------------------------{Color.RESET}\n")

        print(f"{Color.YELLOW}📌 [{ev['title']}]{Color.RESET}")
        print_slow(f"{ev['desc']}\n")

        print(f"{Color.WHITE}당신의 선택은?{Color.RESET}")
        for idx, ch in enumerate(ev['choices'], 1):
            print(f"  {Color.BOLD}{idx}. {ch['text']}{Color.RESET}")

        while True:
            sel = input(f"\n{Color.CYAN}선택지 번호 입력 (1-3): {Color.RESET}").strip()
            if sel in ["1", "2", "3"]:
                choice = ev['choices'][int(sel) - 1]
                break
            print(f"{Color.RED}1, 2, 3 번 중 하나를 선택해 주세요.{Color.RESET}")

        print("\n" + "-"*50)
        # 선택 결과 처리
        if choice.get("gamble"):
            if random.random() < choice["success_rate"]:
                print(f"{Color.GREEN}✨ [성공!] {choice['success_msg']}{Color.RESET}")
                mental += choice["success_m"]
                grade += choice["success_g"]
            else:
                print(f"{Color.RED}💥 [실패...] {choice['fail_msg']}{Color.RESET}")
                mental += choice["fail_m"]
                grade += choice["fail_g"]
        else:
            print(f"{Color.CYAN}▶ {choice['msg']}{Color.RESET}")
            mental += choice["mental"]
            grade += choice["grade"]

        # 값 보정
        mental = max(0, min(100, mental))
        grade = max(0.0, min(4.5, grade))

        # 중간 게임 오버 체크 (멘탈 0 도달)
        if mental <= 0:
            print(f"\n{Color.RED}{Color.BOLD}🚨 [경고] 멘탈이 0 이하로 바닥났습니다! 극심한 번아웃 발생!{Color.RESET}")
            print(f"{Color.RED}기말고사를 치르지 못하고 조기 휴학계를 제출했습니다...{Color.RESET}")
            press_enter()
            show_student_ending(mental, grade, is_burnout=True)
            return

        press_enter()

    # 7일 모두 생존 후 최종 엔딩
    show_student_ending(mental, grade, is_burnout=False)


def show_student_ending(mental, grade, is_burnout=False):
    clear_screen()
    print(f"{Color.CYAN}===================================================={Color.RESET}")
    print(f"{Color.BOLD}📜 [기말고사 최종 성적표 & 엔딩 발표]{Color.RESET}")
    print(f"{Color.CYAN}===================================================={Color.RESET}\n")

    print(f"• 최종 멘탈: {mental}/100")
    print(f"• 최종 누적 학점: {Color.BOLD}{grade:.2f} / 4.5{Color.RESET}\n")

    if is_burnout:
        print(f"{Color.RED}{Color.BOLD}🛑 [엔딩 1: '몸과 마음의 쉼표, 눈물의 휴학원']{Color.RESET}")
        print("과도한 스트레스와 밤샘으로 몸과 마음에 무리가 왔습니다.")
        print("이번 학기는 아쉽게 쉬어가지만, 건강이 최우선입니다!")
    elif grade >= 4.2:
        print(f"{Color.GREEN}{Color.BOLD}🏆 [엔딩 2: '수석의 영예, 전액 장학금의 신화']{Color.RESET}")
        print("교수님들도 감탄한 완벽한 시험 답안지!")
        print("등록금 0원 고지서와 함께 과탑의 자리에 올랐습니다. 축하합니다!")
    elif grade >= 3.5:
        print(f"{Color.CYAN}{Color.BOLD}✨ [엔딩 3: '우등생의 밸런스, 성적 장학금 수령']{Color.RESET}")
        print("멘탈도 챙기고 학점도 훌륭하게 방어했습니다.")
        print("취업 준비와 대학 생활 모두 청신호가 켜졌습니다!")
    elif grade >= 2.5:
        print(f"{Color.YELLOW}{Color.BOLD}😐 [엔딩 4: '생존 성공! 평범한 대학생의 일상']{Color.RESET}")
        print("F학점의 늪은 무사히 피했습니다. 재수강 몇 개만 하면 무난한 졸업 가능!")
        print("종강의 기쁨을 누리며 방학 동안 재충전하세요.")
    elif grade >= 1.5:
        print(f"{Color.MAGENTA}{Color.BOLD}⚠️ [엔딩 5: '계절학기 확정, 재수강의 굴레']{Color.RESET}")
        print("전공 2과목 F를 맞으며 방학 넷플릭스 계획은 날아갔습니다.")
        print("뜨거운 여름/겨울, 계절학기 강의실에서 다시 만나요...")
    else:
        print(f"{Color.RED}{Color.BOLD}💀 [엔딩 6: '학사경고 통지서 도착']{Color.RESET}")
        print("집으로 날아온 빨간 딱지 학사경고...")
        print("부모님의 등짝 스매싱과 함께 강제 면담이 예약되었습니다.")

    print(f"\n{Color.CYAN}===================================================={Color.RESET}")
    press_enter()


# ==========================================
# 2. 직장인 모드: "오늘도 무사히 칼퇴 챌린지 (월~금)"
# ==========================================
def play_worker_mode():
    days = ["월요일", "화요일", "수요일", "목요일", "금요일"]
    stamina = 100   # 체력
    reputation = 70 # 사내 평판 (100점 만점)
    overtime_count = 0

    work_events = [
        {
            "day": "월요일",
            "title": "월요병과 오전 전체 주간회의",
            "desc": "한 주의 시작, 부서 주간 회의에서 갑자기 아무도 안 맡으려는 새 프로젝트 담당자를 찾는다.",
            "choices": [
                {"text": "눈을 피하고 조용히 엑셀 문서에 집중하는 척한다", "stamina": -10, "rep": -5, "msg": "무사히 타겟을 벗어났습니다. 옆자리 박대리가 끌려갔습니다."},
                {"text": "'제가 한번 해보겠습니다!' 패기 있게 자원한다", "stamina": -30, "rep": +25, "msg": "부장님의 입꼬리가 승천했습니다! (하지만 이번 주 야근 확정 느낌...)"},
                {"text": "화장실 간 척 타이밍 맞춰 자리 비우기", "stamina": +5, "rep": -10, "msg": "위기는 넘겼으나 부장님이 묘한 눈빛으로 쳐다봅니다."}
            ]
        },
        {
            "day": "화요일",
            "title": "메일함 폭탄과 협력사 클레임",
            "desc": "오후 2시, 협력사에서 데이터 포맷이 안 맞는다며 기습 클레임 메일이 도착했다.",
            "choices": [
                {"text": "전화 걸어서 조목조목 설명하고 우아하게 해결한다", "stamina": -20, "rep": +15, "msg": "커뮤니케이션 능력 인정! 협력사도 수긍했습니다."},
                {"text": "'담당자 외근 중' 메일 자동회신 걸고 메신저 오프라인", "stamina": +10, "rep": -15, "msg": "잠시 평화로웠으나 내일 2배로 터질 예정입니다."},
                {"text": "사수에게 슬쩍 토스하며 헬프를 요청한다", "stamina": -5, "rep": +5, "msg": "커피 한 잔 사드리고 안전하게 위기를 넘겼습니다."}
            ]
        },
        {
            "day": "수요일",
            "title": "가정의 날, 17시 50분의 기습",
            "desc": "정시 퇴근 10분 전, 부장님이 슥 다가오더니 '김대리, 오늘 약속 있나?'를 시전하셨다.",
            "choices": [
                {"text": "'네, 병원 예약이 있습니다!' 칼같은 정시 퇴근", "stamina": +25, "rep": -10, "msg": "저녁 6시 칼퇴 완료! 집에서 치맥을 즐겼습니다."},
                {"text": "'아닙니다, 부장님! 무슨 일 있으십니까?' 삼겹살 회식 참여", "stamina": -25, "rep": +20, "msg": "새벽까지 소폭 제조... 부장님의 총애를 듬뿍 받았습니다."},
                {"text": "'약속은 없는데... 혹시 업무 때문이신가요?'", "gamble": True, "success_rate": 0.5,
                 "success_msg": "부장님이 빵 사주고 가셨습니다! 럭키!", "success_s": +10, "success_r": +10,
                 "fail_msg": "'마침 잘됐네, 이 보고서 수정 좀 해줘' 야근 당첨...", "fail_s": -25, "fail_r": +5}
            ]
        },
        {
            "day": "목요일",
            "title": "기획서 발표 D-1",
            "desc": "내일 임원 보고용 PPT를 정리해야 한다. 집중력이 한계에 달했다.",
            "choices": [
                {"text": "카페인 음료 2캔 때려붓고 밤 10시까지 야근 완성", "stamina": -35, "rep": +20, "overtime": True, "msg": "퀄리티 극상의 보고서 탄생! 하지만 다크서클이 턱까지 내려옴."},
                {"text": "템플릿 다운받아 적당히 그럴듯하게 2시간 만에 컷", "stamina": -10, "rep": +5, "msg": "가성비 좋게 마무리하고 퇴근했습니다."},
                {"text": "생성형 AI에게 초안 작성을 부탁하고 검토만 한다", "gamble": True, "success_rate": 0.7,
                 "success_msg": "AI가 고퀄리티 요약본을 3분 만에 뽑아줬습니다!", "success_s": +15, "success_r": +15,
                 "fail_msg": "엉뚱한 할루시네이션 데이터가 섞여 다시 수정하느라 진땀을 뺐습니다.", "fail_s": -20, "fail_r": 0}
            ]
        },
        {
            "day": "금요일",
            "title": "불금, 운명의 18시",
            "desc": "금요일 17시 45분, 갑자기 전사 시스템 오류 알림이 떴다!",
            "choices": [
                {"text": "책임감 있게 자리 지키며 원인 분석 후 퇴근", "stamina": -30, "rep": +25, "overtime": True, "msg": "영웅 소리를 들으며 금요일 밤 10시에 퇴근했습니다."},
                {"text": "시스템 팀 소관이라 생각하고 정시 가방 챙기기", "stamina": +20, "rep": -15, "msg": "주말 시작! 내 일 아니면 일단 튄다!"},
                {"text": "단톡방에 '퇴근길에 원격으로 모니터링하겠습니다' 선언", "stamina": -10, "rep": +10, "msg": "센스 있는 처신으로 평판과 퇴근을 모두 챙겼습니다."}
            ]
        }
    ]

    for ev in work_events:
        clear_screen()
        print(f"{Color.BLUE}===================================================={Color.RESET}")
        print(f"{Color.BOLD}💼 직장인 모드: 오늘도 무사히 칼퇴 챌린지 ({ev['day']}){Color.RESET}")
        print(f"{Color.BLUE}===================================================={Color.RESET}")

        s_color = Color.GREEN if stamina >= 60 else (Color.YELLOW if stamina >= 30 else Color.RED)
        r_color = Color.GREEN if reputation >= 70 else (Color.YELLOW if reputation >= 40 else Color.RED)
        print(f"📊 [현재 상태] 요일: {Color.BOLD}{ev['day']}{Color.RESET} | 체력: {s_color}{stamina}/100{Color.RESET} | 사내 평판: {r_color}{reputation}/100{Color.RESET} | 이번 주 야근: {overtime_count}회")
        print(f"{Color.BLUE}----------------------------------------------------{Color.RESET}\n")

        print(f"{Color.YELLOW}📌 [{ev['title']}]{Color.RESET}")
        print_slow(f"{ev['desc']}\n")

        print(f"{Color.WHITE}당신의 처신은?{Color.RESET}")
        for idx, ch in enumerate(ev['choices'], 1):
            print(f"  {Color.BOLD}{idx}. {ch['text']}{Color.RESET}")

        while True:
            sel = input(f"\n{Color.CYAN}선택지 번호 입력 (1-3): {Color.RESET}").strip()
            if sel in ["1", "2", "3"]:
                choice = ev['choices'][int(sel) - 1]
                break
            print(f"{Color.RED}1, 2, 3 번 중 하나를 선택해 주세요.{Color.RESET}")

        print("\n" + "-"*50)
        if choice.get("gamble"):
            if random.random() < choice["success_rate"]:
                print(f"{Color.GREEN}✨ [성공!] {choice['success_msg']}{Color.RESET}")
                stamina += choice["success_s"]
                reputation += choice["success_r"]
            else:
                print(f"{Color.RED}💥 [실패...] {choice['fail_msg']}{Color.RESET}")
                stamina += choice["fail_s"]
                reputation += choice["fail_r"]
        else:
            print(f"{Color.CYAN}▶ {choice['msg']}{Color.RESET}")
            stamina += choice["stamina"]
            reputation += choice["rep"]
            if choice.get("overtime"):
                overtime_count += 1

        stamina = max(0, min(100, stamina))
        reputation = max(0, min(100, reputation))

        if stamina <= 0:
            print(f"\n{Color.RED}{Color.BOLD}🚨 [응급] 체력이 완전히 방전되어 과로로 병원에 입원했습니다!{Color.RESET}")
            press_enter()
            show_worker_ending(stamina, reputation, overtime_count, is_hospitalized=True)
            return

        press_enter()

    show_worker_ending(stamina, reputation, overtime_count, is_hospitalized=False)


def show_worker_ending(stamina, reputation, overtime_count, is_hospitalized=False):
    clear_screen()
    print(f"{Color.BLUE}===================================================={Color.RESET}")
    print(f"{Color.BOLD}📜 [이번 주 업무 평가서 & 직장인 엔딩 발표]{Color.RESET}")
    print(f"{Color.BLUE}===================================================={Color.RESET}\n")

    print(f"• 최종 잔여 체력: {stamina}/100")
    print(f"• 사내 평판 점수: {reputation}/100")
    print(f"• 이번 주 야근 횟수: {overtime_count}회\n")

    if is_hospitalized:
        print(f"{Color.RED}{Color.BOLD}🏥 [엔딩 1: '과로와 링거 투혼 엔딩']{Color.RESET}")
        print("회사는 당신의 건강을 책임져주지 않습니다.")
        print("병실 침대에서 워라밸의 중요성을 절실히 깨닫습니다.")
    elif reputation >= 85 and stamina >= 50:
        print(f"{Color.GREEN}{Color.BOLD}🌟 [엔딩 2: '사내 에이스 & 고속 승진 코스']{Color.RESET}")
        print("일도 똑부러지게 해내고 체력 관리까지 완벽한 사내 특급 인재!")
        print("부서장들의 스카우트 제의가 쏟아집니다.")
    elif overtime_count == 0 and reputation >= 50:
        print(f"{Color.CYAN}{Color.BOLD}🏃 [엔딩 3: '칼퇴의 지배자, 워라밸 마스터']{Color.RESET}")
        print("단 한 번의 야근 없이 평판도 훌륭하게 방어했습니다.")
        print("저녁이 있는 삶을 완벽하게 누리는 진정한 승리자입니다!")
    elif reputation < 40:
        print(f"{Color.MAGENTA}{Color.BOLD}🌪️ [엔딩 4: '투명인간 혹은 사내 빌런(?)']{Color.RESET}")
        print("몸은 편했으나 팀원들과 부장님의 눈총이 따갑습니다.")
        print("다음 인사평가 시즌에 각별한 주의가 필요합니다...")
    else:
        print(f"{Color.YELLOW}{Color.BOLD}☕ [엔딩 5: '평범하지만 위대한 K-직장인의 생존']{Color.RESET}")
        print("이번 주도 큰 사고 없이 무사히 버텨냈습니다.")
        print("월급날을 손꼽아 기다리며 금요일 퇴근길 맥주 한잔의 여유를 즐깁니다.")

    print(f"\n{Color.BLUE}===================================================={Color.RESET}")
    press_enter()


# ==========================================
# 메인 메뉴
# ==========================================
def main():
    while True:
        clear_screen()
        print(f"{Color.MAGENTA}╔════════════════════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.MAGENTA}║ {Color.BOLD}{Color.WHITE}     🎮 텍스트 인터랙티브 생존 어드벤처 챌린지     {Color.MAGENTA}║{Color.RESET}")
        print(f"{Color.MAGENTA}╚════════════════════════════════════════════════════╝{Color.RESET}")
        print(f"  {Color.CYAN}조건문 · 자원 관리 · 확률 기반 멀티 엔딩 시뮬레이터{Color.RESET}\n")

        print(f"  {Color.BOLD}1. 🎓 대학생 모드: 'F학점을 피하는 방법 (기말고사 D-7)'{Color.RESET}")
        print(f"  {Color.BOLD}2. 💼 직장인 모드: '오늘도 무사히 칼퇴 챌린지 (월~금)'{Color.RESET}")
        print(f"  {Color.BOLD}3. ❌ 게임 종료{Color.RESET}")

        mode = input(f"\n{Color.YELLOW}플레이할 모드를 선택하세요 (1-3): {Color.RESET}").strip()

        if mode == "1":
            play_student_mode()
        elif mode == "2":
            play_worker_mode()
        elif mode == "3":
            print(f"\n{Color.GREEN}게임을 종료합니다. 플레이해 주셔서 감사합니다!{Color.RESET}")
            break
        else:
            print(f"\n{Color.RED}잘못된 입력입니다. 1, 2, 3 중 하나를 입력하세요.{Color.RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}게임을 중단했습니다.{Color.RESET}")
