"""MBTI 계산 로직 (Streamlit 없이 순수 파이썬)

이 파일만 실행하면 데이터 검사와 테스트 케이스를 확인할 수 있어요.
    python mbti_logic.py
"""

import json
import sys
from pathlib import Path

# 터미널 위치와 상관없이 항상 이 파일 기준으로 data 폴더를 찾아요.
DATA_DIR = Path(__file__).parent / "data"
QUESTIONS_PATH = DATA_DIR / "questions.json"
RESULTS_PATH = DATA_DIR / "results.json"

# 지표 순서는 결과 4글자의 순서와 같아요.
DIMENSIONS = ["EI", "SN", "TF", "JP"]


def load_questions(path=QUESTIONS_PATH):
    """questions.json을 읽어 질문 목록으로 돌려줘요."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_results(path=RESULTS_PATH):
    """results.json을 읽어 {유형: 설명} 사전으로 돌려줘요."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def calculate_type(answers):
    """답 사전으로 MBTI 유형과 지표별 비율을 계산해요.

    answers 예: {1: "E", 2: "N", 3: "T", ...}
    돌려주는 값 예:
        ("ENTP", {"EI": {"E": 67, "I": 33}, "SN": {"S": 33, "N": 67}, ...})
    """
    # ① 8개 글자의 개수를 0으로 시작
    counts = {letter: 0 for dim in DIMENSIONS for letter in dim}

    # ② 답을 하나씩 보며 해당 글자 +1
    for letter in answers.values():
        counts[letter] += 1

    mbti = ""
    ratios = {}
    for dim in DIMENSIONS:
        first, second = dim[0], dim[1]

        # ③ 두 글자 중 많은 쪽 선택 (지표마다 3문항이라 동점 없음)
        if counts[first] >= counts[second]:
            mbti += first
        else:
            mbti += second

        # 비율(%) 계산
        total = counts[first] + counts[second]
        if total == 0:
            first_pct = 50
        else:
            first_pct = round(counts[first] / total * 100)
        ratios[dim] = {first: first_pct, second: 100 - first_pct}

    # ④ 4글자 완성
    return mbti, ratios


def check_data(questions, results):
    """데이터 규칙(2-3, 5-5)을 지키는지 검사하고, 문제 목록을 돌려줘요."""
    problems = []

    if len(questions) != 12:
        problems.append(f"질문이 12개가 아니라 {len(questions)}개예요.")

    for dim in DIMENSIONS:
        n = sum(1 for q in questions if q["dimension"] == dim)
        if n != 3:
            problems.append(f"{dim} 질문이 3개가 아니라 {n}개예요.")

    for q in questions:
        scores = sorted(c["score"] for c in q["choices"])
        if len(q["choices"]) != 2 or scores != sorted(q["dimension"]):
            problems.append(f"{q['id']}번 질문의 선택지가 규칙에 맞지 않아요.")

    if len(results) != 16:
        problems.append(f"결과 유형이 16개가 아니라 {len(results)}개예요.")

    fields = ["emoji", "nickname", "summary", "strengths", "cautions", "campus"]
    for mbti, info in results.items():
        for field in fields:
            if not info.get(field):
                problems.append(f"{mbti}의 '{field}' 항목이 비어 있어요.")

    return problems


if __name__ == "__main__":
    # Windows 터미널에서 한글·이모지가 깨지지 않게 해요.
    sys.stdout.reconfigure(encoding="utf-8")

    questions = load_questions()
    results = load_results()

    print("[데이터 검사]")
    problems = check_data(questions, results)
    if problems:
        for p in problems:
            print(" ❌", p)
    else:
        print(" ✅ 질문 12개, 유형 16개 모두 정상")

    # 3-8 테스트 케이스: 지표별 글자 3개씩을 답으로 만들어 계산해요.
    print("\n[테스트 케이스]")
    cases = [
        ("ESTJ", "EEE" + "SSS" + "TTT" + "JJJ"),
        ("INFP", "III" + "NNN" + "FFF" + "PPP"),
        ("ENTP", "EEI" + "SNN" + "TTF" + "JPP"),
    ]
    for expected, letters in cases:
        answers = {i + 1: letter for i, letter in enumerate(letters)}
        mbti, ratios = calculate_type(answers)
        mark = "✅" if mbti == expected else "❌"
        print(f" {mark} 기대 {expected} → 결과 {mbti}  {ratios}")
