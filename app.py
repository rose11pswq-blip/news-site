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
# UI 스타일 (고급 유지)
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

.reason {
    background: #eef2ff;
    padding: 8px;
    border-radius: 6px;
    font-size: 13px;
}

.insight {
    background: #f5f7ff;
    padding: 8px;
    border-radius: 6px;
    font-size: 13px;
    margin-top: 5px;
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
# 크롤링
# -------------------------------
@st.cache_data(ttl=300)
def crawl_news():
    url = "https://news.naver.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news = []
    for a in soup.select(".sa_item"):
        try:
            title = a.select_one(".sa_text_title").text.strip()
            link = a.select_one("a")["href"]

            img = a.select_one("img")
            img_url = img.get("data-src") if img else None

            time_tag = a.select_one(".sa_text_datetime")
            time_text = time_tag.text.strip() if time_tag else ""

            news.append({
                "title": title,
                "link": link,
                "img": img_url,
                "time": time_text
            })
        except:
            continue
    return news

# -------------------------------
# 시간 필터
# -------------------------------
def is_recent(news_time, hours):
    try:
        if "분 전" in news_time:
            return int(news_time.replace("분 전","")) <= hours * 60
        elif "시간 전" in news_time:
            return int(news_time.replace("시간 전","")) <= hours
    except:
        return True
    return True

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
    if "공급망" in title:
        return "공급망 리스크", "비용 영향"
    return "핵심 뉴스", "추가 분석 필요"

# -------------------------------
# 상태값 (자동 검색 핵심)
# -------------------------------
if "keyword" not in st.session_state:
    st.session_state.keyword = ""

if "time_value" not in st.session_state:
    st.session_state.time_value = 0

# -------------------------------
# 헤더
# -------------------------------
st.markdown("<div class='main-title'>Strategic Intelligence</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>made by sw.park</div>", unsafe_allow_html=True)

# -------------------------------
# 검색 UI (자동 검색)
# -------------------------------
st.markdown("<div class='search-box'>", unsafe_allow_html=True)

col1, col2 = st.columns([3,1])

with col1:
    keyword = st.text_input(
        "🔍 키워드 입력 (쉼표 가능)",
        value=st.session_state.keyword
    )

with col2:
    time_value = st.number_input(
        "시간",
        0, 48,
        value=st.session_state.time_value
    )

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# 값 변경 감지
# -------------------------------
changed = False

if keyword != st.session_state.keyword:
    st.session_state.keyword = keyword
    changed = True

if time_value != st.session_state.time_value:
    st.session_state.time_value = time_value
    changed = True

# -------------------------------
# 검색 실행
# -------------------------------
if st.session_state.keyword or st.session_state.time_value > 0:

    data = crawl_news()

    keyword = st.session_state.keyword
    time_value = st.session_state.time_value

    # 키워드 필터
    if keyword:
        kws = [k.strip().lower() for k in keyword.split(",")]
        data = [n for n in data if any(k in n["title"].lower() for k in kws)]

    # 시간 필터
    if time_value > 0:
        data = [n for n in data if is_recent(n["time"], time_value)]

    # 중복 제거
    seen = set()
    result = []
    for n in data:
        if n["title"] not in seen:
            result.append(n)
            seen.add(n["title"])

    result = result[:20]

    # 출력
    for n in result:
        reason, insight = analyze(n["title"])

        st.markdown("<div class='news-card'>", unsafe_allow_html=True)

        if n["img"]:
            st.markdown(
                f'<img src="{n["img"]}" style="width:28%; border-radius:8px;">',
                unsafe_allow_html=True
            )

        st.markdown(f"### {n['title']}")
        st.markdown(f"[기사 보기]({n['link']})")

        st.markdown(f"<div class='reason'>📌 {reason}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='insight'>💡 {insight}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
