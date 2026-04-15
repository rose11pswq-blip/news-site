import streamlit as st
import requests
from bs4 import BeautifulSoup

# -------------------------------
# 페이지 설정
# -------------------------------
st.set_page_config(
    page_title="전략 뉴스 큐레이션",
    page_icon="🧠",
    layout="wide"
)

# -------------------------------
# 스타일 (핵심🔥)
# -------------------------------
st.markdown("""
<style>
body {
    background-color: #f5f9ff;
}

.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #1f4fff;
}

.sub-title {
    color: #6c8cff;
    font-size: 14px;
}

.news-card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
}

.reason-box {
    background-color: #e8f0ff;
    padding: 10px;
    border-radius: 8px;
    margin-top: 10px;
}

.insight-box {
    background-color: #eef4ff;
    padding: 10px;
    border-radius: 8px;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 비밀번호
# -------------------------------
PASSWORD = "duddjqqhsqn1!"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# -------------------------------
# 로그인
# -------------------------------
def login_page():
    st.markdown("<h2 class='main-title'>🔐 Access Required</h2>", unsafe_allow_html=True)
    pw = st.text_input("비밀번호 입력", type="password")

    if st.button("접속"):
        if pw == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("비밀번호 오류")

# -------------------------------
# 크롤링
# -------------------------------
@st.cache_data(ttl=300)
def crawl_news():
    url = "https://news.naver.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news_list = []
    articles = soup.select(".sa_item")

    for article in articles:
        try:
            title = article.select_one(".sa_text_title").text.strip()
            link = article.select_one("a")["href"]

            img_tag = article.select_one("img")
            img_url = img_tag.get("data-src") if img_tag else None

            news_list.append({
                "title": title,
                "link": link,
                "img": img_url
            })
        except:
            continue

    return news_list

# -------------------------------
# 전략 키워드
# -------------------------------
strategic_keywords = [
    "시장", "경쟁", "규제", "공급망", "리스크",
    "투자", "M&A", "인수", "합병", "지분",
    "물류", "기술", "AI", "플랫폼"
]

# -------------------------------
# 분석
# -------------------------------
def analyze_news(title):
    reason = []
    insight = []

    if "시장" in title:
        reason.append("시장 구조 변화")
        insight.append("시장 재편 가능성")

    if "경쟁" in title:
        reason.append("경쟁사 동향")
        insight.append("경쟁 심화 가능성")

    if "규제" in title:
        reason.append("규제 이슈")
        insight.append("사업 리스크 증가")

    if "투자" in title or "M&A" in title:
        reason.append("투자 이벤트")
        insight.append("기업 가치 변동 가능")

    if "공급망" in title:
        reason.append("공급망 리스크")
        insight.append("원가 영향 가능")

    if not reason:
        reason.append("핵심 뉴스")
        insight.append("추가 분석 필요")

    return ", ".join(reason), ", ".join(insight)

# -------------------------------
# 메인
# -------------------------------
def main_page():

    st.markdown("<div class='main-title'>🧠 Strategic News Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>made by sw.park</div>", unsafe_allow_html=True)

    keyword_input = st.text_input("🔍 키워드 입력 (쉼표로 구분)")

    news_data = crawl_news()

    # 사용자 키워드 필터
    if keyword_input:
        user_keywords = [k.strip().lower() for k in keyword_input.split(",")]
        news_data = [
            n for n in news_data
            if any(k in n["title"].lower() for k in user_keywords)
        ]

    # 전략 필터
    news_data = [
        n for n in news_data
        if any(k in n["title"] for k in strategic_keywords)
    ]

    # 중복 제거
    seen = set()
    unique = []

    for n in news_data:
        if n["title"] not in seen:
            unique.append(n)
            seen.add(n["title"])

    news_data = unique[:20]

    # 출력
    for news in news_data:
        reason, insight = analyze_news(news["title"])

        st.markdown("<div class='news-card'>", unsafe_allow_html=True)

        if news["img"]:
            st.markdown(
                f'<img src="{news["img"]}" style="width:30%; border-radius:10px;">',
                unsafe_allow_html=True
            )

        st.markdown(f"### {news['title']}")
        st.markdown(f"[👉 기사 보기]({news['link']})")

        st.markdown(f"<div class='reason-box'>📌 {reason}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='insight-box'>💡 {insight}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# 실행
# -------------------------------
if not st.session_state["authenticated"]:
    login_page()
else:
    main_page()
