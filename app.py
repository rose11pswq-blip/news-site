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
st.set_page_config(page_title="뉴스 인사이트 대시보드", layout="wide")

# -------------------------------
# GPT 요약 (OpenAI API 필요)
# -------------------------------
def gpt_summary(title):
    try:
        import openai

        openai.api_key = "YOUR_API_KEY"

        prompt = f"""
        다음 뉴스 제목을 기반으로:

        1. 3줄 요약
        2. 이 뉴스가 중요한 이유
        3. 얻을 수 있는 인사이트

        뉴스: {title}
        """

        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )

        return res.choices[0].message.content

    except:
        return "⚠️ GPT 요약 실패 (API 키 확인 필요)"


# -------------------------------
# 중요 뉴스 필터 키워드
# -------------------------------
IMPORTANT_KEYWORDS = [
    "유통", "물류", "식품", "택배", "패션", "뷰티",
    "산업재", "소비재", "이커머스", "온라인", "자사몰",
    "쿠팡", "네이버", "소비자", "물가" 
]

def is_important(title):
    return any(k in title for k in IMPORTANT_KEYWORDS)


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
# 중요 뉴스 필터
# -------------------------------
news_data = [n for n in news_data if is_important(n["title"])]

# -------------------------------
# 키워드 필터
# -------------------------------
if keyword_input:
    news_data = [n for n in news_data if keyword_input in n["title"]]

# -------------------------------
# 중복 제거
# -------------------------------
seen = set()
unique_news = []

for n in news_data:
    if n["title"] not in seen:
        unique_news.append(n)
        seen.add(n["title"])

news_data = unique_news[:20]

# -------------------------------
# UI 출력
# -------------------------------
st.title("🧠 전략형 뉴스 인사이트")

if not news_data:
    st.error("❌ 조건에 맞는 뉴스 없음")
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

            # GPT 분석
            with st.expander("🤖 AI 분석 보기"):
                result = gpt_summary(news["title"])
                st.write(result)

# -------------------------------
# 데이터 테이블
# -------------------------------
with st.expander("📊 데이터"):
    st.dataframe(pd.DataFrame(news_data))
