import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# -------------------------------
# 기본 설정
# -------------------------------
st.set_page_config(layout="wide")

# -------------------------------
# 비밀번호 인증
# -------------------------------
PASSWORD = "duddjqqhsqn1!"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("## 🔐 Strategic Intelligence Access")
    pw = st.text_input("비밀번호", type="password")
    if st.button("입장"):
        if pw == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
    st.stop()

# -------------------------------
# CSS (맥킨지 스타일)
# -------------------------------
st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}
.header {
    font-size: 34px;
    font-weight: 700;
}
.sub {
    color: #6b7280;
    margin-bottom: 20px;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    transition: 0.2s;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}
.title {
    font-size: 18px;
    font-weight: 600;
}
.meta {
    font-size: 12px;
    color: gray;
}
.link {
    font-size: 14px;
    color: #2563eb;
}
.kpi {
    font-size: 22px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 네이버 뉴스 크롤링 (개선 버전)
# -------------------------------
@st.cache_data(ttl=300)
def crawl_naver_news():
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news_list = []

    articles = soup.select("ul.type06_headline li, ul.type06 li")

    for article in articles:
        try:
            a_tag = article.select_one("a")
            title = a_tag.text.strip()
            link = a_tag["href"]

            # 네이버 상대경로 대응
            if link.startswith("/"):
                link = "https://news.naver.com" + link

            img_tag = article.select_one("img")
            img = img_tag["src"] if img_tag else None

            news_list.append({
                "title": title,
                "link": link,
                "img": img,
                "time": datetime.now().strftime("%H:%M")
            })

        except:
            continue

    return news_list

# -------------------------------
# UI 헤더
# -------------------------------
st.markdown('<div class="header">🧠 Strategic Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Real-time News Monitoring System</div>', unsafe_allow_html=True)

# -------------------------------
# 입력 영역
# -------------------------------
col1, col2, col3 = st.columns([3,1,1])

with col1:
    keyword = st.text_input("🔍 키워드 (쉼표 구분)", value="경제")

with col2:
    limit = st.number_input("📊 뉴스 개수", 1, 50, 20)

with col3:
    refresh = st.button("🔄 Refresh")

if refresh:
    st.cache_data.clear()

# -------------------------------
# 데이터 처리
# -------------------------------
raw_news = crawl_naver_news()

keywords = [k.strip().lower() for k in keyword.split(",")]

filtered = [
    n for n in raw_news
    if any(k in n["title"].lower() for k in keywords)
]

# 중복 제거
seen = set()
result = []

for n in filtered:
    if n["title"] not in seen:
        result.append(n)
        seen.add(n["title"])

result = result[:limit]

# -------------------------------
# KPI 영역
# -------------------------------
st.markdown(f'<div class="kpi">📊 뉴스 {len(result)}건 분석 중</div>', unsafe_allow_html=True)

# -------------------------------
# 카드 UI 출력
# -------------------------------
for n in result:
    st.markdown(f"""
    <div class="card">
        <div class="title">{n['title']}</div>
        <div class="meta">🕒 {n['time']}</div>
        <br>
        <a class="link" href="{n['link']}" target="_blank">👉 기사 보기</a>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# 데이터 테이블
# -------------------------------
with st.expander("📊 데이터 보기"):
    df = pd.DataFrame(result)
    st.dataframe(df)
