#!/usr/bin/env python3
"""
AI Daily Digest — HackerNews + arXiv + YouTube + Threads + X 수집 후 Slack 전송
"""
import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("/Users/seonjin/ai_research/.env")

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")

AI_KEYWORDS = ["AI", "LLM", "GPT", "Claude", "machine learning", "deep learning",
               "transformer", "agent", "RAG", "fine-tuning", "multimodal"]

YOUTUBE_CHANNELS = [
    {"name": "Matt Wolfe",       "id": "UChpleBmo18P08aKCIgti38g"},
    {"name": "Fireship",         "id": "UCsBjURrPoezykLs9EqgamOA"},
    {"name": "corbin",           "id": "UCJFMlSxcvlZg5yZUYJT0Pug"},
    {"name": "Andrej Karpathy",  "id": "UCPk8m_r6fkUSYmvgCBwq-sw"},
]

THREADS_ACCOUNTS = ["choi.openai"]

X_ACCOUNTS = ["karpathy", "sama", "goodside", "AnthropicAI", "OpenAI"]


def get_hn_ai_posts(n=5):
    yesterday = int((datetime.now() - timedelta(days=1)).timestamp())
    url = (
        "https://hn.algolia.com/api/v1/search"
        "?query=AI+LLM+language+model&tags=story"
        f"&numericFilters=created_at_i>{yesterday}&hitsPerPage=20"
    )
    r = requests.get(url, timeout=10)
    hits = r.json().get("hits", [])

    results = []
    for h in hits:
        title = h.get("title", "")
        if any(kw.lower() in title.lower() for kw in AI_KEYWORDS):
            story_url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
            results.append({"title": title, "url": story_url})
        if len(results) >= n:
            break
    return results


def get_arxiv_papers(n=5):
    url = (
        "https://export.arxiv.org/api/query"
        "?search_query=cat:cs.AI"
        "&sortBy=submittedDate&sortOrder=descending&max_results=10"
    )
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []
        for entry in root.findall("atom:entry", ns)[:n]:
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            summary = summary[:120] + "..." if len(summary) > 120 else summary
            link = entry.find("atom:id", ns).text.strip()
            papers.append({"title": title, "summary": summary, "url": link})
        return papers
    except Exception as e:
        print(f"arXiv 수집 실패 (무시): {e}")
        return []


def get_youtube_videos():
    """각 채널에서 가장 최근 영상 1개씩 수집."""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results = []
    for ch in YOUTUBE_CHANNELS:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            r = requests.get(url, timeout=10)
            root = ET.fromstring(r.content)
            entry = root.find("atom:entry", ns)
            if entry is None:
                continue
            title = entry.find("atom:title", ns).text
            link = entry.find("atom:link", ns).get("href")
            results.append({"title": title, "url": link, "channel": ch["name"]})
        except Exception as e:
            print(f"YouTube {ch['name']} 수집 실패 (무시): {e}")
    return results


def get_threads_posts():
    """Threads 공개 프로필에서 OG 메타 태그로 최신 내용 추출 (best-effort)."""
    posts = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    }
    for account in THREADS_ACCOUNTS:
        url = f"https://www.threads.net/@{account}"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            match = re.search(r'<meta property="og:description" content="([^"]+)"', r.text)
            if match:
                text = match.group(1)[:200]
                posts.append({"text": text, "account": f"@{account}", "url": url})
        except Exception as e:
            print(f"Threads @{account} 수집 실패 (무시): {e}")
    return posts


def get_x_posts(n=5):
    """Twitter API v2로 지정 계정 최신 트윗 수집. TWITTER_BEARER_TOKEN 없으면 스킵."""
    if not TWITTER_BEARER_TOKEN:
        return []
    query = f"({' OR '.join(f'from:{a}' for a in X_ACCOUNTS)}) -is:retweet lang:en"
    params = {
        "query": query,
        "max_results": min(n * 3, 100),
        "tweet.fields": "text,author_id",
        "expansions": "author_id",
        "user.fields": "username",
    }
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    try:
        r = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            headers=headers, params=params, timeout=10,
        )
        data = r.json()
        users = {u["id"]: u["username"] for u in data.get("includes", {}).get("users", [])}
        results = []
        for tweet in data.get("data", [])[:n]:
            username = users.get(tweet["author_id"], "unknown")
            tweet_url = f"https://x.com/{username}/status/{tweet['id']}"
            results.append({"text": tweet["text"][:200], "account": f"@{username}", "url": tweet_url})
        return results
    except Exception as e:
        print(f"X 수집 실패 (무시): {e}")
        return []


def translate_items(items: list[dict], key: str) -> list[dict]:
    """items 리스트의 특정 key 값을 일괄 한국어 번역."""
    texts = [item[key] for item in items]
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    msg = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": (
                "다음 AI/기술 텍스트를 한국어로 자연스럽게 번역해줘. "
                "번호는 그대로 유지하고, 번역문만 출력해.\n\n" + numbered
            ),
        }],
        max_tokens=1000,
    )
    translated = msg.choices[0].message.content.strip().split("\n")
    result = []
    for i, item in enumerate(items):
        kr = translated[i].lstrip("0123456789. ").strip() if i < len(translated) else item[key]
        result.append({**item, key: kr})
    return result


def send_to_slack(message: str):
    r = requests.post(SLACK_WEBHOOK_URL, json={"text": message}, timeout=10)
    if r.text != "ok":
        raise RuntimeError(f"Slack 전송 실패: {r.text}")


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"[{today}] 수집 시작...")

    hn_posts = get_hn_ai_posts()
    arxiv_papers = get_arxiv_papers()
    yt_videos = get_youtube_videos()
    threads_posts = get_threads_posts()
    x_posts = get_x_posts()

    print(f"[{today}] 번역 중...")
    hn_posts = translate_items(hn_posts, "title")
    if arxiv_papers:
        arxiv_papers = translate_items(arxiv_papers, "title")
        arxiv_papers = translate_items(arxiv_papers, "summary")
    if yt_videos:
        yt_videos = translate_items(yt_videos, "title")

    lines = [f"🤖 *AI Daily Digest — {today}*\n"]

    lines.append("*📰 HackerNews*")
    for p in hn_posts:
        lines.append(f"• <{p['url']}|{p['title']}>")

    if arxiv_papers:
        lines.append("\n*📄 arXiv 논문*")
        for p in arxiv_papers:
            lines.append(f"• <{p['url']}|{p['title']}> — {p['summary']}")

    if yt_videos:
        lines.append("\n*▶️ YouTube 최신 영상*")
        for v in yt_videos:
            lines.append(f"• [{v['channel']}] <{v['url']}|{v['title']}>")

    if threads_posts:
        lines.append("\n*🧵 Threads*")
        for p in threads_posts:
            lines.append(f"• <{p['url']}|{p['account']}> — {p['text']}")

    if x_posts:
        lines.append("\n*🐦 X (Twitter)*")
        for p in x_posts:
            lines.append(f"• <{p['url']}|{p['account']}> — {p['text']}")

    send_to_slack("\n".join(lines))
    print(f"[{today}] Slack 전송 완료")


if __name__ == "__main__":
    main()
