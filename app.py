import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="뉴스 사이트", layout="wide")

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

            img_tag = article.select_one("img")
            img_url = img_tag["data-src"] if img_tag and "data-src" in img_tag.attrs else img_tag["src"]

            news_list.append({
                "title": title,
                "link": link,
                "img": img_url
            })
        except:
            continue

    return news_list

category_dict = {
    "정치": "https://news.naver.com/section/100",
    "경제": "https://news.naver.com/section/101",
    "사회": "https://news.naver.com/section/102"
}

st.sidebar.title("설정")
category = st.sidebar.selectbox("카테고리", list(category_dict.keys()))
keyword = st.sidebar.text_input("검색어")

news_data = crawl_news(category_dict[category])

if keyword:
    news_data = [n for n in news_data if keyword.lower() in n["title"].lower()]

st.title("📰 뉴스 사이트")

for news in news_data:
    col1, col2 = st.columns([1,2])

    with col1:
        st.image(news["img"], use_container_width=True)

    with col2:
        st.markdown(f"### {news['title']}")
        st.markdown(f"[기사 보러가기]({news['link']})")
