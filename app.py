import streamlit as st
import requests
from bs4 import BeautifulSoup

# -------------------------------
# 🔐 비밀번호 인증
# -------------------------------
PASSWORD = "duddjqqhsqn1!"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("## 🔐 대시보드 로그인")
    pw = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        if pw == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다")

    st.stop()

# -------------------------------
# 기본 설정
# -------------------------------
st.set_page_config(page_title="뉴스 인사이트", layout="wide")

# -------------------------------
# 🎨 한국형 고급 SaaS UI
# -------------------------------
st.markdown("""
<style>
body {
    background-color:#f7f8fa;
}
.title {
    font-size:30px;
    font-weight:800;
    margin-bottom:20px;
}
.card {
    background:white;
    padding:20px;
    border-radius:14px;
    margin-bottom:18px;
    box-shadow:0 4px 12px rgba(0,0,0,0.05);
}
.summary {
    font-size:15px;
    color:#333;
    margin-top:10px;
    line-height:1.5;
}
.meta {
    font-size:12px;
    color:#888;
    margin-top:8px;
}
.link {
    font-size:13px;
    color:#1a73e8;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📊 프리미엄 뉴스 인사이트</div>', unsafe_allow_html=True)

# -------------------------------
# 📄 본문 가져오기
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
# 🤖 GPT 요약 (본문 → 실패시 제목)
# -------------------------------
def gpt_summary(content, title):
    try:
        import openai
        openai.api_key = "YOUR_API_KEY"

        if content:
            prompt = f"""
            아래 뉴스 본문을 핵심 2줄로 요약해줘:

            {content[:1500]}
            """
        else:
            prompt = f"""
            아래 뉴스 제목을 기반으로 핵심 2줄 요약:

            {title}
            """

        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        return res.choices[0].message.content.strip()

    except:
        # GPT 실패 시 기본 fallback
        return f"{title}\n핵심 이슈 중심 뉴스 (요약 실패)"

# -------------------------------
# 중요도 정렬
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
st.sidebar.title("⚙️ 설정")

category = st.sidebar.selectbox("카테고리", list(category_dict.keys()))
keyword = st.sidebar.text_input("키워드")

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
# UI 출력 (이미지 포함 카드형)
# -------------------------------
for news in news_data:

    content = get_article_content(news["link"])
    summary = gpt_summary(content, news["title"])

    col1, col2 = st.columns([1, 4])

    with col1:
        if news["img"]:
            st.image(news["img"], use_container_width=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <div><b>{news['title']}</b></div>
            <div class="summary">{summary}</div>
            <div class="meta">{news['category']} | {news['time']}</div>
            <div class="link"><a href="{news['link']}" target="_blank">기사 보기</a></div>
        </div>
        """, unsafe_allow_html=True)
