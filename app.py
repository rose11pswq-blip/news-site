import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# -------------------------------
# 🔐 비밀번호 인증
# -------------------------------
PASSWORD = "duddjqqhsqn1!"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 뉴스 대시보드 로그인")

    pw = st.text_input("비밀번호 입력", type="password")

    if st.button("로그인"):
        if pw == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ 비밀번호 틀림")

    st.stop()

# -------------------------------
# 기본 설정
# -------------------------------
st.set_page_config(page_title="뉴스 인사이트", layout="wide")

# -------------------------------
# GPT 요약 (테스트용 기본)
# -------------------------------
def gpt_summary(title):
    return f"""
📌 요약
- {title}
- 산업/시장 관련 주요 이슈
- 향후 영향 가능성 존재

📌 선정 이유
- 시장/기업 영향 가능성 있는 뉴스

📌 인사이트
- 관련 산업 흐름 및 투자 판단 참고 필요
"""

# 👉 실제 GPT 쓰려면 이걸로 교체
"""
def gpt_summary(title):
    import openai
    openai.api_key = "YOUR_API_KEY"

    prompt = f'''
    뉴스 제목 기반으로 아래 작성:
    1. 3줄 요약
    2. 선정 이유
    3. 인사이트

    뉴스: {title}
    '''

    res = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )

    return res.choices[0].message.content
"""
# -------------------------------
# 중요도 점수 (필터 ❌ → 정렬용)
# -------------------------------
def importance_score(title):
    keywords = [
        "시장","경쟁","규제","투자","인수","합병",
        "삼성","LG","애플","테슬라",
        "AI","반도체","금리","환율","배터리"
    ]

    score = 0
    for k in keywords:
        if k in title:
            score += 1

    return score

# -------------------------------
# 네이버 크롤링
# -------------------------------
@st.cache_data(ttl=300)
def crawl_naver(url, category_name):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://news.naver.com/"
    }

    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        articles = soup.select("li.sa_item, div.sa_item")

        news_list = []

        for article in articles:
            try:
                title = article.select_one(".sa_text_title").text.strip()
                link = article.select_one("a")["href"]

                img_tag = article.select_one("img")
                img_url = img_tag.get("src") if img_tag else None

                time_tag = article.select_one(".sa_text_datetime")
                time_text = time_tag.text.strip() if time_tag else ""

                news_list.append({
                    "title": title,
                    "link": link,
                    "img": img_url,
                    "time": time_text,
                    "category": category_name
                })
            except:
                continue

        return news_list

    except:
        return []

# -------------------------------
# 카테고리
# -------------------------------
category_dict = {
    "전체": "ALL",
    "정치": "https://news.naver.com/section/100",
    "경제": "https://news.naver.com/section/101",
    "사회": "https://news.naver.com/section/102",
    "생활/문화": "https://news.naver.com/section/103",
    "세계": "https://news.naver.com/section/104",
    "IT/과학": "https://news.naver.com/section/105"
}

# -------------------------------
# 사이드바
# -------------------------------
st.sidebar.title("⚙️ 설정")

category = st.sidebar.selectbox("카테고리", list(category_dict.keys()))
keyword_input = st.sidebar.text_input("키워드")
time_value = st.sidebar.slider("시간 필터", 0, 48, 0)

# -------------------------------
# 데이터 가져오기
# -------------------------------
with st.spinner("뉴스 불러오는 중..."):

    news_data = []

    if category == "전체":
        for cat, url in category_dict.items():
            if cat == "전체":
                continue
            news_data.extend(crawl_naver(url, cat))
    else:
        news_data = crawl_naver(category_dict[category], category)

# -------------------------------
# 키워드 필터
# -------------------------------
if keyword_input:
    news_data = [n for n in news_data if keyword_input in n["title"]]

# -------------------------------
# 중요도 정렬 (핵심)
# -------------------------------
news_data.sort(key=lambda x: importance_score(x["title"]), reverse=True)

# -------------------------------
# 중복 제거
# -------------------------------
seen = set()
unique_news = []

for n in news_data:
    if n["title"] not in seen:
        unique_news.append(n)
        seen.add(n["title"])

news_data = unique_news[:30]

# -------------------------------
# UI 출력
# -------------------------------
st.title("🧠 전략형 뉴스 인사이트")

if not news_data:
    st.error("❌ 뉴스 없음 (조건 줄여보세요)")
else:
    for news in news_data:

        st.markdown("---")

        col1, col2 = st.columns([1, 3])

        with col1:
            if news["img"]:
                st.image(news["img"], width=120)

        with col2:
            st.markdown(f"### {news['title']}")
            st.caption(f"{news['category']} | {news['time']}")
            st.markdown(f"[👉 기사 보기]({news['link']})")

            with st.expander("🤖 AI 분석 보기"):
                st.write(gpt_summary(news["title"]))

# -------------------------------
# 데이터 테이블
# -------------------------------
with st.expander("📊 데이터"):
    st.dataframe(pd.DataFrame(news_data))
