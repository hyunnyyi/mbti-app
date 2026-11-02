"""검사 결과를 Google 스프레드시트에 한 줄씩 저장해요 (익명 통계)

필요한 비밀 정보는 .streamlit/secrets.toml (배포 앱은 Streamlit Cloud의 Secrets)에 있어요.
    [stats]                  sheet_url = 시트 주소
    [gcp_service_account]    서비스 계정 키 내용
"""

from datetime import datetime, timedelta, timezone

import gspread
import streamlit as st

from mbti_logic import DIMENSIONS

# 시트 1행 제목: 이 순서대로 값을 채워 넣어요.
HEADER = ["시간", "유형", "E", "I", "S", "N", "T", "F", "J", "P", "답변"]

# 배포 서버는 한국 시간이 아니라서 직접 +9시간을 붙여요.
KST = timezone(timedelta(hours=9))


def make_row(mbti, ratios, answers):
    """시트에 넣을 한 줄을 HEADER 순서대로 만들어요.

    예: ["2026-11-02 14:03:05", "INFP", 33, 67, 33, 67, 0, 100, 33, 67, "I,N,F,..."]
    """
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    percents = [ratios[dim][letter] for dim in DIMENSIONS for letter in dim]
    # 1번 문항부터 순서대로 고른 글자
    picked = ",".join(answers[number] for number in sorted(answers))
    return [now, mbti, *percents, picked]


@st.cache_resource
def get_worksheet():
    """시트 연결은 한 번만 만들고 재사용해요."""
    info = dict(st.secrets["gcp_service_account"])
    client = gspread.service_account_from_dict(info)
    return client.open_by_url(st.secrets["stats"]["sheet_url"]).sheet1


def save_result(mbti, ratios, answers):
    """결과를 저장하고 (성공 여부, 메시지)를 돌려줘요. 실패해도 앱은 멈추지 않아요."""
    try:
        sheet = get_worksheet()
    except Exception:
        return False, "통계 저장소에 연결하지 못했어요."

    try:
        # 제목 순서가 다르면 칸이 어긋나므로 저장하지 않아요.
        if sheet.row_values(1) != HEADER:
            return False, "통계 시트의 1행 제목이 약속한 순서와 달라서 저장하지 않았어요."
        sheet.append_row(make_row(mbti, ratios, answers), value_input_option="USER_ENTERED")
    except Exception:
        return False, "통계를 저장하지 못했어요."

    return True, "저장했어요."
