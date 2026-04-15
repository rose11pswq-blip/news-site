import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Strategic Intelligence", layout="wide")

# -------------------------------
# 로그인
# -------------------------------
PASSWORD = "duddjqqhsqn1!"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pw = st.text_input("비밀번호", type="password")
    if st.button("입장"):
        if pw == PASSWORD:
            st.session_state.auth = True
            st.rerun()
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
            return int(news_time.replace("분 전","")) <= hours*60
        if "시간 전" in news_time:
            return int(news_time.replace("시간 전","")) <= hours
    except:
        return True
    return True

# -------------------------------
# 분석
# -------------------------------
def analyze(title):
    if "시장" in title: return "시장 변화", "시장 재편 가능"
    if "경쟁" in title: return "경쟁 동향", "경쟁 심화 가능"
    if "규제" in title: return "규제 이슈", "리스크 존재"
    return "핵심 뉴스", "추가 분석 필요"

# -------------------------------
# 검색 상태 저장 (핵심🔥)
# -------------------------------
if "search_trigger" not in st.session_state:
    st.session_state.search_trigger = False
    st.session_state.keyword = ""
    st.session_state.time_value = 0

# -------------------------------
# UI
# -------------------------------
st.title("🧠 Strategic Intelligence")
st.caption("made by sw.park")

with st.form("search_form"):
    keyword = st.text_input("키워드 (쉼표 가능)")
    time_value = st.number_input("시간", 0, 48, 0)

    submitted = st.form_submit_button("검색 (엔터 가능)")

    if submitted:
        st.session_state.search_trigger = True
        st.session_state.keyword = keyword
        st.session_state.time_value = time_value

# -------------------------------
# 검색 실행 (항상 session 기준)
# -------------------------------
if st.session_state.search_trigger:

    data = crawl_news()

    keyword = st.session_state.keyword
    time_value = st.session_state.time_value

    # 키워드
    if keyword:
        kws = [k.strip().lower() for k in keyword.split(",")]
        data = [n for n in data if any(k in n["title"].lower() for k in kws)]

    # 시간
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

        st.markdown("---")
        st.markdown(f"### {n['title']}")
        st.markdown(f"[기사 보기]({n['link']})")
        st.write(f"📌 {reason}")
        st.write(f"💡 {insight}")
