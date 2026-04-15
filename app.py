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
    st.markdown("## 🔐 Secure Access")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if pw == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid password")

    st.stop()

# -------------------------------
# 기본 설정
# -------------------------------
st.set_page_config(page_title="Insight Dashboard", layout="wide")

# -------------------------------
# 🎨 SaaS 스타일 UI
# -------------------------------
st.markdown("""
<style>
.main-title {
    font-size:28px;
    font-weight:700;
}
.card {
    padding:20px;
    border-radius:12px;
    background-color:#111;
    margin-bottom:15px;
}
.summary {
    font-size:14px;
    color:#aaa;
}
.meta {
    font-size:12px;
    color:#888;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Insight Intelligence Dashboard</div>', unsafe_allow_html=True)

# -------------------------------
# 📄 기사 본문 크롤링
# -------------------------------
def get_article_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        content = soup.select_one("#dic_area")
        if content:
            return content.text.strip()

        return ""
    except:
        return ""

# -------------------------------
# 🤖 GPT 요약 (본문 기반 / 2줄)
# 👉 코드 숨김 (노출 안됨)
# -------------------------------
def gpt_summary(content):
    try:
        import openai
        openai.api_key = "YOUR_API_KEY"

        prompt = f"""
        아래 뉴스 본문을 2줄로 핵심 요약해줘:

        {content[:1500]}
        """

        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        return res.choices[0].message.content.strip()

    except:
        return "요약 생성 실패"

# -------------------------------
# 중요도 점수
# -------------------------------
def importance_score(title):
    keywords = [
        "시장","경쟁","규제","투자","인수","합병",
        "AI","반도체","금리","환율","배터리"
    ]
    return sum(1 for k in keywords if k in title)

# -------------------------------
# 네이버 크롤링
# -------------------------------
@st.cache_data(ttl=300)
def crawl_naver(url, category_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

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

# -------------------------------
# 카테고리
# -------------------------------
category_dict = {
    "전체": "ALL",
    "정치": "https://news.naver.com/section/100",
    "경제": "https://news.naver.com/section/101",
    "사회": "https://news.naver.com/section/102",
    "세계": "https://news.naver.com/section/104",
    "IT": "https://news.naver.com/section/105"
}

# -------------------------------
# 사이드바
# -------------------------------
st.sidebar.title("Settings")

category = st.sidebar.selectbox("Category", list(category_dict.keys()))
keyword = st.sidebar.text_input("Keyword")

# -------------------------------
# 데이터 가져오기
# -------------------------------
news_data = []

if category == "전체":
    for cat, url in category_dict.items():
        if cat == "전체":
            continue
        news_data.extend(crawl_naver(url, cat))
else:
    news_data = crawl_naver(category_dict[category], category)

# 키워드 필터
if keyword:
    news_data = [n for n in news_data if keyword in n["title"]]

# 중요도 정렬
news_data.sort(key=lambda x: importance_score(x["title"]), reverse=True)

news_data = news_data[:15]

# -------------------------------
# UI 출력 (SaaS 카드형)
# -------------------------------
for news in news_data:

    content = get_article_content(news["link"])
    summary = gpt_summary(content) if content else "본문 없음"

    st.markdown(f"""
    <div class="card">
        <div><b>{news['title']}</b></div>
        <div class="summary">{summary}</div>
        <div class="meta">{news['category']} | {news['time']}</div>
        <a href="{news['link']}" target="_blank">기사 보기</a>
    </div>
    """, unsafe_allow_html=True)
