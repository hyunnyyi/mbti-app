"""대학생 MBTI 검사 - Streamlit 앱

실행 방법 (mbti_app 폴더에서):
    streamlit run app.py
"""

import json

import streamlit as st

from mbti_logic import calculate_type, check_data, load_questions, load_results
from stats import save_result

# 페이지 설정은 반드시 가장 먼저 실행해야 해요.
st.set_page_config(page_title="대학생 MBTI 검사", page_icon="🎓", layout="centered")


# ─────────────────────────────────────────────
# 디자인 (4단계 ③ CSS 층)
# ─────────────────────────────────────────────

# 지표별 파스텔 색 (4단계 4-2)
DIM_COLORS = {"EI": "#FFC8DD", "SN": "#BDE0FE", "TF": "#B9E4D4", "JP": "#FFF1B5"}

CSS = """
<style>
@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");

:root {
  --lavender: #C8B6FF;
  --lavender-dark: #9D8DF1;
  --text: #3D3A4B;
  --text-sub: #6E6A7C;
}

/* 글꼴: 아이콘 글꼴은 건드리지 않아요 */
html, body, [data-testid="stAppViewContainer"] *:not([data-testid="stIconMaterial"]) {
  font-family: "Pretendard", -apple-system, "Malgun Gothic", sans-serif;
}

/* Streamlit 기본 메뉴, 상단 바, 하단 문구 숨기기 */
#MainMenu, footer, [data-testid="stHeader"] { display: none; }

/* 콘텐츠 최대 너비 480px, 가운데 정렬 */
[data-testid="stMainBlockContainer"], .block-container {
  max-width: 480px;
  padding: 2.5rem 1rem 3rem;
}

/* 모든 버튼: 누르기 쉬운 크기, 둥근 모서리 */
.stButton button {
  min-height: 48px;
  border-radius: 16px;
}

/* 강조 버튼: 연한 라벤더 위에 흰 글자는 잘 안 읽혀서 진회색으로 */
.stButton button[kind="primary"],
.stButton button[kind="primary"] p {
  color: var(--text);
  font-weight: 700;
}
.stButton button[kind="primary"]:hover {
  background-color: #B9A3FF;
  border-color: #B9A3FF;
}

/* 질문 카드 등장 효과 */
@keyframes rise {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
[class*="st-key-question_"] { animation: rise 0.3s ease-out; }

/* 선택지 버튼: 흰 카드, 왼쪽 정렬, 긴 문장 줄바꿈 */
[class*="st-key-question_"] .stButton button {
  min-height: 64px;
  padding: 14px 18px;
  justify-content: flex-start;
  text-align: left;
  background-color: #FFFFFF;
  border: 2px solid #EDE7FF;
  box-shadow: 0 2px 8px rgba(157, 141, 241, 0.12);
}
[class*="st-key-question_"] .stButton button > div {
  justify-content: flex-start;
}
[class*="st-key-question_"] .stButton button p {
  text-align: left;
  white-space: normal;
  font-size: 16px;
  line-height: 1.5;
}
[class*="st-key-question_"] .stButton button:hover {
  border-color: var(--lavender);
  color: var(--text);
}
/* 전에 고른 답 강조 */
[class*="st-key-question_"] .stButton button[kind="primary"] {
  background-color: #F3EEFF;
  border-color: var(--lavender-dark);
}

/* 공통 텍스트 */
.center { text-align: center; }
.sub { color: var(--text-sub); font-size: 15px; }
.title { font-size: 28px; font-weight: 800; margin: 8px 0 12px; }
.question { font-size: 20px; font-weight: 700; line-height: 1.5; margin: 4px 0 16px; }

/* 지표 태그 */
.tag {
  display: inline-block;
  padding: 2px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}

/* 결과 유형 글자 */
.type-letters { display: flex; justify-content: center; gap: 8px; margin: 8px 0; }
.type-letters span {
  width: 56px; height: 64px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 16px;
  font-size: 40px; font-weight: 800;
}
.nickname { font-size: 20px; font-weight: 700; }
.summary-card {
  margin: 16px 0 8px;
  padding: 14px 16px;
  text-align: center;
  background-color: #FFFFFF;
  border: 1px solid #EDE7FF;
  border-radius: 16px;
}

/* 지표 비율 막대 */
.ratio { display: flex; align-items: center; gap: 10px; margin: 10px 0; font-size: 15px; }
.ratio .letter { width: 52px; }
.ratio .letter.right { text-align: right; }
.ratio .win { font-weight: 800; }
.ratio .bar {
  flex: 1; height: 12px;
  border-radius: 999px;
  background-color: #EEEAF3;
  overflow: hidden;
}
.ratio .fill { height: 100%; border-radius: 999px; }

@media (min-width: 768px) {
  .question { font-size: 24px; }
  .type-letters span { width: 72px; height: 80px; font-size: 52px; }
}
</style>
"""


def apply_style():
    st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 데이터 불러오기 (처음 한 번만 읽고 캐시)
# ─────────────────────────────────────────────

@st.cache_data
def get_data():
    return load_questions(), load_results()


def get_question(questions, number):
    """번호(id)에 맞는 질문을 찾아줘요."""
    for q in questions:
        if q["id"] == number:
            return q
    return None


# ─────────────────────────────────────────────
# session_state 초기화 (없을 때만!)
# ─────────────────────────────────────────────

def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "start"
    if "current" not in st.session_state:
        st.session_state.current = 1
    if "answers" not in st.session_state:
        st.session_state.answers = {}


# ─────────────────────────────────────────────
# 콜백 함수 (버튼을 누르면 실행, 끝나면 자동으로 화면을 다시 그림)
# ─────────────────────────────────────────────

def start_quiz():
    st.session_state.answers = {}
    st.session_state.current = 1
    st.session_state.saved = False
    st.session_state.page = "quiz"


def choose(number, choice_index):
    questions, _ = get_data()
    question = get_question(questions, number)

    # 선택지 번호로 알파벳을 직접 찾아 저장 (이미 답한 문항이면 덮어쓰기)
    st.session_state.answers[number] = question["choices"][choice_index]["score"]

    if number == len(questions):
        st.session_state.page = "result"
    else:
        st.session_state.current = number + 1


def go_prev():
    st.session_state.current -= 1


def restart():
    st.session_state.page = "start"


# ─────────────────────────────────────────────
# 화면 ① 시작
# ─────────────────────────────────────────────

def show_start(questions):
    # 결과 화면의 유형 글자처럼 지표별 파스텔 색 칸에 M B T I를 넣어요.
    letters = "".join(
        f'<span style="background-color:{DIM_COLORS[dim]};">{letter}</span>'
        for dim, letter in zip(["EI", "SN", "TF", "JP"], "MBTI")
    )
    st.markdown(
        f"""
<div class="center">
<div class="type-letters">{letters}</div>
<div class="title">나는 어떤 대학생일까?</div>
<p class="sub">{len(questions)}개 질문으로 알아보는<br>나의 MBTI 유형</p>
<p class="sub">⏱ 약 2분 · {len(questions)}문항</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.button("검사 시작하기", type="primary", width="stretch", on_click=start_quiz)


# ─────────────────────────────────────────────
# 화면 ② 질문
# ─────────────────────────────────────────────

def show_quiz(questions):
    number = st.session_state.current
    total = len(questions)
    question = get_question(questions, number)

    # 잘못된 문항 번호면 시작 화면으로
    if question is None:
        st.session_state.page = "start"
        st.rerun()

    st.progress(number / total, text=f"{number} / {total}")

    # key에 문항 번호를 넣어서 문항이 바뀔 때마다 등장 효과가 다시 나와요.
    with st.container(key=f"question_{number}"):
        dim = question["dimension"]
        st.markdown(
            f"""
<span class="tag" style="background-color:{DIM_COLORS[dim]};">{dim}</span>
<div class="question">{question["text"]}</div>
""",
            unsafe_allow_html=True,
        )

        previous = st.session_state.answers.get(number)
        for i, choice in enumerate(question["choices"]):
            label = f"{'AB'[i]}　{choice['text']}"
            is_previous = previous == choice["score"]
            st.button(
                label,
                key=f"q{number}_c{i}",
                type="primary" if is_previous else "secondary",
                width="stretch",
                on_click=choose,
                args=(number, i),
            )

    if number > 1:
        st.write("")
        st.button("← 이전 문항", key="prev", on_click=go_prev)


# ─────────────────────────────────────────────
# 화면 ③ 결과
# ─────────────────────────────────────────────

def ratio_bar_html(dim, ratio):
    first, second = dim[0], dim[1]
    first_pct, second_pct = ratio[first], ratio[second]
    first_cls = "win" if first_pct > second_pct else ""
    second_cls = "win" if second_pct > first_pct else ""
    return f"""
<div class="ratio">
<span class="letter {first_cls}">{first} {first_pct}%</span>
<div class="bar"><div class="fill" style="width:{first_pct}%; background-color:{DIM_COLORS[dim]};"></div></div>
<span class="letter right {second_cls}">{second_pct}% {second}</span>
</div>"""


def show_result(questions, results):
    answers = st.session_state.answers

    # 답이 다 모이지 않았으면 아직 답하지 않은 첫 문항으로
    unanswered = [q["id"] for q in questions if q["id"] not in answers]
    if unanswered:
        st.session_state.current = unanswered[0]
        st.session_state.page = "quiz"
        st.rerun()

    mbti, ratios = calculate_type(answers)
    info = results.get(mbti)

    # 검사 1번에 통계도 1줄만 저장해요 (화면이 다시 그려져도 중복 저장 안 함)
    if not st.session_state.get("saved"):
        st.session_state.saved = True
        ok, message = save_result(mbti, ratios, answers)
        if not ok:
            st.toast(message, icon="⚠️")

    letters = "".join(
        f'<span style="background-color:{DIM_COLORS[dim]};">{letter}</span>'
        for dim, letter in zip(["EI", "SN", "TF", "JP"], mbti)
    )
    st.markdown(
        f"""
<div class="center">
<p class="sub">당신의 유형은</p>
<div class="type-letters">{letters}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if info:
        st.markdown(
            f'<div class="center nickname">{info["emoji"]} {info["nickname"]}</div>',
            unsafe_allow_html=True,
        )
        summary = info["summary"]
    else:
        summary = '<span class="sub">설명을 준비 중이에요</span>'
    st.markdown(f'<div class="summary-card">{summary}</div>', unsafe_allow_html=True)

    st.markdown(
        "".join(ratio_bar_html(dim, ratios[dim]) for dim in ["EI", "SN", "TF", "JP"]),
        unsafe_allow_html=True,
    )

    if info:
        # 2칸 배치: PC에서는 가로 2칸, 휴대폰에서는 자동으로 세로로 쌓여요.
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("**💪 강점**")
                for s in info["strengths"]:
                    st.markdown(f"- {s}")
        with col2:
            with st.container(border=True):
                st.markdown("**⚠️ 주의할 점**")
                for c in info["cautions"]:
                    st.markdown(f"- {c}")
        with st.container(border=True):
            st.markdown("**🎓 이런 대학 생활이 잘 맞아요**")
            st.markdown(info["campus"])

    st.button("다시 검사하기", type="primary", width="stretch", on_click=restart)
    st.caption(
        "이 검사는 재미로 보는 간이 검사이며, 공식 MBTI® 검사가 아닙니다. "
        "검사 결과는 개인정보 없이 익명 통계로 저장돼요."
    )


# ─────────────────────────────────────────────
# 실행: page 값을 보고 화면 하나만 그려요
# ─────────────────────────────────────────────

apply_style()
init_state()

try:
    questions, results = get_data()
except (FileNotFoundError, json.JSONDecodeError):
    st.error("질문 파일을 불러올 수 없어요. data 폴더의 JSON 파일을 확인해 주세요.")
    st.stop()

problems = check_data(questions, results)
if problems:
    st.error("데이터에 문제가 있어요:\n\n" + "\n".join(f"- {p}" for p in problems))
    st.stop()

if st.session_state.page == "quiz":
    show_quiz(questions)
elif st.session_state.page == "result":
    show_result(questions, results)
else:
    show_start(questions)
