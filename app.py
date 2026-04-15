import streamlit as st
import requests
from bs4 import BeautifulSoup

# -------------------------------
# 페이지 설정
# -------------------------------
st.set_page_config(
    page_title="Strategic Intelligence",
    page_icon="🧠",
    layout="wide"
)

# -------------------------------
# UI 스타일 (유지)
# -------------------------------
st.markdown("""
<style>
body { background-color: #f4f6f9; }

.main-title {
    font-size: 34px;
    font-weight: 700;
    color: #1a2a4f;
}

.sub-title {
    color: #6b7a99;
    font-size: 13px;
}

.search-box {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.news-card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 비밀번호
# -------------------------------
PASSWORD = "duddjqqhsqn1!"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("## 🔐 Private Access")
    pw = st.text_input("비밀번호", type="password")

    if st.button("입장"):
        if pw == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("비밀번호 오류")

    st.stop()

# -------------------------------
# 네이버 뉴스
# -------------------------------
def crawl_naver(keyword):
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news = []
    items = soup.select(".news_area")

    for item in items:
        try:
            title = item.select_one(".news_tit").text
            link = item.select_one(".news_tit")["href"]

            img_tag = item.select_one("img")
            img_url = img_tag["src"] if img_tag else None

            news.append({
                "title": title,
                "link": link,
                "img": img_url,
                "source": "NAVER"
            })
        except:
            continue

    return news

# -------------------------------
# 구글 뉴스
# -------------------------------
def crawl_google(keyword):
    url = f"https://news.google.com/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news = []
    items = soup.select("article")

    for item in items:
        try:
            title = item.select_one("h3").text
            link = "https://news.google.com" + item.select_one("a")["href"][1:]

            news.append({
                "title": title,
                "link": link,
                "img": None,
                "source": "GOOGLE"
            })
        except:
            continue

    return news

# -------------------------------
# 분석
# -------------------------------
def analyze(title):
    if "시장" in title:
        return "시장 구조 변화", "시장 재편 가능성"
    if "경쟁" in title:
        return "경쟁사 동향", "경쟁 심화 가능성"
    if "규제" in title:
        return "규제 리스크", "사업 영향 가능"
    if "투자" in title or "M&A" in title:
        return "투자 이벤트", "기업 가치 변화"
    return "핵심 뉴스", "추가 분석 필요"

# -------------------------------
# 상태
# -------------------------------
if "keyword" not in st.session_state:
    st.session_state.keyword = "경제"

# -------------------------------
# UI
# -------------------------------
st.markdown("<div class='main-title'>Strategic Intelligence</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>made by sw.park</div>", unsafe_allow_html=True)

st.markdown("<div class='search-box'>", unsafe_allow_html=True)

keyword = st.text_input("🔍 키워드 (쉼표 가능)", value=st.session_state.keyword)

st.markdown("</div>", unsafe_allow_html=True)

st.session_state.keyword = keyword

# -------------------------------
# 실행
# -------------------------------
keywords = [k.strip() for k in keyword.split(",")]

all_news = []

for kw in keywords:
    all_news.extend(crawl_naver(kw))
    all_news.extend(crawl_google(kw))

# -------------------------------
# 중복 제거
# -------------------------------
seen = set()
result = []

for n in all_news:
    if n["title"] not in seen:
        result.append(n)
        seen.add(n["title"])

result = result[:20]

# -------------------------------
# 출력
# -------------------------------
if result:
    for n in result:
        reason, insight = analyze(n["title"])

        st.markdown("<div class='news-card'>", unsafe_allow_html=True)

        if n["img"]:
            st.image(n["img"], width=150)

        st.markdown(f"### {n['title']}")
        st.markdown(f"[기사 보기]({n['link']})")
        st.caption(f"출처: {n['source']}")

        st.write(f"📌 {reason}")
        st.write(f"💡 {insight}")

        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning("검색 결과가 없습니다.")
