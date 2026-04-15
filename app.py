import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

# -------------------------------
# 기본 설정
# -------------------------------
st.set_page_config(
    page_title="실시간 뉴스 사이트",
    page_icon="📰",
    layout="wide"
)

# -------------------------------
# 크롤링 함수
# -------------------------------
@st.cache_data(ttl=300)
def crawl_news(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news_list = []
    articles = soup.select(".sa_item")

    for article in articles:
        try:
            title = article.select_one(".sa_text_title").text.strip()
            link = article.select_one("a")["href"]

            # 이미지
            img_tag = article.select_one("img")
            img_url = None
            if img_tag:
                img_url = img_tag.get("data-src") or img_tag.get("src")

            # 시간
            time_tag = article.select_one(".sa_text_datetime")
            time_text = time_tag.text.strip() if time_tag else ""

            news_list.append({
                "title": title,
                "link": link,
                "img": img_url,
                "time": time_text
            })
        except:
            continue

    return news_list

# -------------------------------
# 시간 필터 함수
# -------------------------------
def is_recent(news_time, hours):
    try:
        if "분 전" in news_time:
            minutes = int(news_time.replace("분 전", ""))
            return minutes <= hours * 60
        elif "시간 전" in news_time:
            h = int(news_time.replace("시간 전", ""))
            return h <= hours
        elif "일 전" in news_time:
            return False
    except:
        return True
    return True

# -------------------------------
# 카테고리
# -------------------------------
category_dict = {
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

keyword_input = st.sidebar.text_input("키워드 (쉼표로 구분)")

time_value = st.sidebar.number_input(
    "몇 시간 이내 뉴스 (0 = 전체)",
    min_value=0,
    max_value=48,
    value=0,
    step=1
)

refresh = st.sidebar.button("🔄 새로고침")

# -------------------------------
# 데이터 가져오기
# -------------------------------
if refresh:
    st.cache_data.clear()

news_data = crawl_news(category_dict[category])

# -------------------------------
# 키워드 필터
# -------------------------------
if keyword_input:
    keywords = [k.strip().lower() for k in keyword_input.split(",")]

    news_data = [
        n for n in news_data
        if any(k in n["title"].lower() for k in keywords)
    ]

# -------------------------------
# 시간 필터
# -------------------------------
if time_value > 0:
    news_data = [
        n for n in news_data
        if is_recent(n["time"], time_value)
    ]

# -------------------------------
# 중복 제거
# -------------------------------
seen_titles = set()
unique_news = []

for n in news_data:
    if n["title"] not in seen_titles:
        unique_news.append(n)
        seen_titles.add(n["title"])

# -------------------------------
# 20개 제한
# -------------------------------
news_data = unique_news[:20]

# -------------------------------
# UI 출력
# -------------------------------
st.title("📰 실시간 뉴스")

if time_value > 0:
    st.write(f"⏱ 최근 {time_value}시간 이내 뉴스")

for news in news_data:
    col1, col2 = st.columns([1, 3])  # 이미지 영역 줄임

    with col1:
        if news["img"]:
            st.markdown(
                f'<img src="{news["img"]}" style="width:33%; border-radius:8px;">',
                unsafe_allow_html=True
            )

    with col2:
        st.markdown(f"### {news['title']}")
        st.markdown(f"[👉 기사 보러가기]({news['link']})")
        if news["time"]:
            st.caption(f"⏱ {news['time']}")

# -------------------------------
# 데이터 테이블
# -------------------------------
with st.expander("📊 데이터 보기"):
    df = pd.DataFrame(news_data)
    st.dataframe(df)
