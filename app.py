import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="실시간 뉴스", layout="wide")

# -------------------------------
# 네이버 뉴스 크롤링
# -------------------------------
@st.cache_data(ttl=300)
def crawl_naver(url, category_name):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://news.naver.com/"
    }

    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code != 200:
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.select("li.sa_item, div.sa_item")

        news_list = []

        for article in articles:
            try:
                title_tag = article.select_one(".sa_text_title")
                if not title_tag:
                    continue

                title = title_tag.text.strip()
                link = article.select_one("a")["href"]

                img_tag = article.select_one("img")
                img_url = None
                if img_tag:
                    img_url = img_tag.get("data-src") or img_tag.get("src")

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
# 구글 뉴스 (fallback)
# -------------------------------
@st.cache_data(ttl=300)
def crawl_google(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"

    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "xml")

        news_list = []

        for item in soup.find_all("item")[:20]:
            news_list.append({
                "title": item.title.text,
                "link": item.link.text,
                "img": None,
                "time": item.pubDate.text,
                "category": "구글뉴스"
            })

        return news_list

    except:
        return []


# -------------------------------
# 시간 필터
# -------------------------------
def is_recent(news_time, hours):
    try:
        if "분 전" in news_time:
            return int(news_time.replace("분 전", "")) <= hours * 60
        elif "시간 전" in news_time:
            return int(news_time.replace("시간 전", "")) <= hours
        elif "일 전" in news_time:
            return False
    except:
        return True
    return True


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
keyword_input = st.sidebar.text_input("키워드 (쉼표 구분)")
time_value = st.sidebar.slider("몇 시간 이내", 0, 48, 0)

# -------------------------------
# 데이터 가져오기
# -------------------------------
with st.spinner("뉴스 불러오는 중..."):

    news_data = []

    if category == "전체":
        for cat, url in category_dict.items():
            if cat == "전체":
                continue
            data = crawl_naver(url, cat)
            news_data.extend(data)
    else:
        news_data = crawl_naver(category_dict[category], category)

    # 네이버 실패 시 fallback
    if len(news_data) == 0:
        st.warning("⚠️ 네이버 뉴스 실패 → 구글 뉴스로 대체")
        search_keyword = keyword_input if keyword_input else "한국"
        news_data = crawl_google(search_keyword)

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
        n for n in news_data if is_recent(n["time"], time_value)
    ]

# -------------------------------
# 중복 제거
# -------------------------------
seen = set()
unique_news = []

for n in news_data:
    if n["title"] not in seen:
        unique_news.append(n)
        seen.add(n["title"])

news_data = unique_news[:30]

# -------------------------------
# UI 출력
# -------------------------------
st.title("📰 실시간 뉴스")

if not news_data:
    st.error("❌ 뉴스 없음 (조건 줄여보세요)")
else:
    for news in news_data:
        col1, col2 = st.columns([1, 3])

        with col1:
            if news["img"]:
                st.image(news["img"], width=100)

        with col2:
            st.markdown(f"### {news['title']}")
            st.markdown(f"[👉 기사 보러가기]({news['link']})")
            st.caption(f"{news['category']} | {news['time']}")

# -------------------------------
# 데이터 테이블
# -------------------------------
with st.expander("📊 데이터 보기"):
    st.dataframe(pd.DataFrame(news_data))
