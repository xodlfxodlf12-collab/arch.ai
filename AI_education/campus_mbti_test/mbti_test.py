"""
[트랙 4] 대학생 캠퍼스 MBTI 성향 판독기 - 파이썬 로직 실습 (mbti_test.py)
조건문(if/elif/else), 딕셔너리 점수 누적, 분기 처리를 학습하는 콘솔 버전
"""

def run_campus_mbti():
    print("=" * 50)
    print("🎓 나의 캠퍼스 생존 동물 MBTI 판독기 (Python CLI)")
    print("=" * 50)
    print("질문을 읽고 1번 또는 2번을 입력하세요!\n")

    scores = {"E": 0, "I": 0, "T": 0, "F": 0, "J": 0, "P": 0}

    # 질문 1: E vs I
    print("[Q1] 개강 첫 주말, 당신이 보내고 싶은 완벽한 하루는?")
    print("  1. 동기들과 뒤풀이 & 밤새 수다 떨며 친목 도모")
    print("  2. 방에서 배달음식 시켜놓고 침대 위 넷플릭스 정주행")
    ans1 = input("선택 (1 또는 2): ").strip()
    if ans1 == "1":
        scores["E"] += 1
    else:
        scores["I"] += 1
    print()

    # 질문 2: J vs P
    print("[Q2] 기말고사 시험공부, 당신의 계획 스타일은?")
    print("  1. 시험 3주 전부터 하루 공부 분량을 분 단위로 플래너에 적어둠")
    print("  2. D-2일부터 에너지 드링크 3캔 마시고 벼락치기로 승부")
    ans2 = input("선택 (1 또는 2): ").strip()
    if ans2 == "1":
        scores["J"] += 1
    else:
        scores["P"] += 1
    print()

    # 질문 3: T vs F
    print("[Q3] 친구가 '나 오늘 시험 완전 망쳤어 ㅠㅠ'라며 전화했을 때?")
    print("  1. '무슨 과목인데? 몇 점 깎였어? 평균은 어때?' (원인 분석)")
    print("  2. '헐 어떡해 ㅠㅠ 교수님이 문제 이상하게 낸 거 아님? 술 마시자' (공감 위로)")
    ans3 = input("선택 (1 또는 2): ").strip()
    if ans3 == "1":
        scores["T"] += 1
    else:
        scores["F"] += 1
    print()

    # 최종 결과 판정 로직
    ei = "E" if scores["E"] >= scores["I"] else "I"
    jp = "J" if scores["J"] >= scores["P"] else "P"
    result_key = f"{ei}_{jp}"

    characters = {
        "E_J": ("🦁 팀플 버스기사 사자", "무임승차자를 응징하는 단호한 과대표 스타일!"),
        "E_P": ("🐆 벼락치기 천재 치타", "스릴 중독자이자 즉흥 멘트로 A학점을 쓸어담는 인싸!"),
        "I_J": ("🦉 과탑 플래너 부엉이", "도서관 지정석 지킴이이자 에타 족보 마스터!"),
        "I_P": ("🦥 방구석 힐러 나무늘보", "세상만사 귀찮지만 관심사엔 과몰입하는 평화주의자!")
    }

    title, desc = characters.get(result_key, characters["E_P"])

    print("=" * 50)
    print("✨ [최종 분석 결과] ✨")
    print(f"당신의 캠퍼스 생존 캐릭터는: {title}")
    print(f"성향 특징: {desc}")
    print(f"누적 점수: {scores}")
    print("=" * 50)
    print("웹 브라우저로 'index.html'을 열면 친구들에게 공유할 수 있는 카드 뷰가 열립니다!")

if __name__ == "__main__":
    run_campus_mbti()

