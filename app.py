import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser

# -------------------------------
# 기본 설정 (SaaS 스타일)
# -------------------------------
st.set_page_config(
    page_title="News Intelligence",
    layout="wide"
)

# -------------------------------
# CSS (맥킨지 스타일)
# -------------------------------
st.markdown("""
<style>
body {
    background-color: #f7f9fc;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    transition: 0.2s;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.1);
}
.title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 8px;
}
.meta {
    font-size: 13px;
    color: gray;
}
.header {
    font-size: 32px;
    font-weight: 700;
}
.sub {
    color: gray;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Google News 크롤링
# -------------------------------
@st.cache_data(ttl=300)
def get_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "xml")

    items = soup.find_all("item")

    news_list = []
    for item in items:
        title = item.title.text
        link = item.link.text
        pub_date = parser.parse(item.pubDate.text)

        news_list.append({
            "title": title,
            "link": link,
            "time": pub_date
        })

    return news_list

# -------------------------------
# 시간 필터
# -------------------------------
def filter_time(news, hours):
    if hours == 0:
        return news

    now = datetime.utcnow()
    filtered = [
        n for n in news
        if (now - n["time"]) <= timedelta(hours=hours)
    ]
    return filtered

# -------------------------------
# UI - 헤더
# -------------------------------
st.markdown('<div class="header">🧠 News Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">실시간 키워드 기반 뉴스 분석 시스템</div>', unsafe_allow_html=True)

# -------------------------------
# 입력 영역
# -------------------------------
col1, col2, col3 = st.columns([3,1,1])

with col1:
    keyword = st.text_input("🔍 키워드 입력 (쉼표로 여러 개)", placeholder="예: AI, 금리, 부동산")

with col2:
    hours = st.number_input("⏱ 시간(시간)", 0, 48, 0)

with col3:
    refresh = st.button("🔄 Refresh")

if refresh:
    st.cache_data.clear()

# -------------------------------
# 데이터 처리
# -------------------------------
if keyword:
    keywords = [k.strip() for k in keyword.split(",")]

    all_news = []

    for k in keywords:
        try:
            all_news.extend(get_news(k))
        except:
            pass

    # 중복 제거
    seen = set()
    unique_news = []
    for n in all_news:
        if n["title"] not in seen:
            unique_news.append(n)
            seen.add(n["title"])

    # 시간 필터
    news_data = filter_time(unique_news, hours)

    # 최신순 정렬
    news_data = sorted(news_data, key=lambda x: x["time"], reverse=True)

    # 상위 20개
    news_data = news_data[:20]

    # -------------------------------
    # KPI
    # -------------------------------
    st.markdown(f"### 📊 총 뉴스 수: {len(news_data)}")

    # -------------------------------
    # 카드 UI 출력
    # -------------------------------
    for news in news_data:
        time_str = news["time"].strftime("%Y-%m-%d %H:%M")

        st.markdown(f"""
        <div class="card">
            <div class="title">{news['title']}</div>
            <div class="meta">🕒 {time_str}</div>
            <br>
            <a href="{news['link']}" target="_blank">👉 기사 원문 보기</a>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------
    # 데이터 테이블
    # -------------------------------
    with st.expander("📊 데이터 보기"):
        df = pd.DataFrame(news_data)
        st.dataframe(df)

else:
    st.info("키워드를 입력하세요.")
