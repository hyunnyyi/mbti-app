# 🌷 나는 어떤 대학생일까? - 대학생 MBTI 검사

12개 질문에 답하면 나의 MBTI 유형 4글자와 설명을 보여주는 Streamlit 웹앱이에요.

## 주요 기능

- **시작 → 질문 → 결과** 3개 화면
- 한 문항씩 넘기는 방식 (선택지를 누르면 바로 다음 문항)
- 이전 문항으로 돌아가 답 고치기
- 지표별 비율 막대와 유형별 강점, 주의할 점, 잘 맞는 대학 생활
- 파스텔톤 디자인, 휴대폰에서 보기 좋은 반응형 화면

## 폴더 구조

```
├── app.py               Streamlit 앱 (화면과 버튼)
├── mbti_logic.py        점수 계산과 데이터 검사
├── data/
│   ├── questions.json   질문 12개
│   └── results.json     16개 유형 설명
├── .streamlit/
│   └── config.toml      파스텔 테마
└── requirements.txt     필요한 라이브러리
```

## 내 컴퓨터에서 실행하기

```bash
pip install -r requirements.txt
streamlit run app.py
```

계산 로직만 테스트하기:

```bash
python mbti_logic.py
```

## 질문 데이터 형식

`data/questions.json`의 각 질문은 아래 형태예요.

```json
{
  "id": 1,
  "dimension": "EI",
  "text": "새 학기 첫 수업 후 쉬는 시간, 나는?",
  "choices": [
    { "text": "옆자리 사람에게 먼저 말을 건다", "score": "E" },
    { "text": "휴대폰을 보며 조용히 쉰다", "score": "I" }
  ]
}
```

---

이 검사는 재미로 보는 간이 검사이며, 공식 MBTI® 검사가 아닙니다.
