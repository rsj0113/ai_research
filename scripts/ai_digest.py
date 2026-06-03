#!/usr/bin/env python3
"""
AI Daily Digest — HackerNews + arXiv 뉴스 수집 후 Slack 전송
"""
import os
import sys
import time
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("/Users/seonjin/ai_research/.env")

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

AI_KEYWORDS = ["AI", "LLM", "GPT", "Claude", "machine learning", "deep learning",
               "transformer", "agent", "RAG", "fine-tuning", "multimodal"]


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

    print(f"[{today}] 번역 중...")
    hn_posts = translate_items(hn_posts, "title")
    if arxiv_papers:
        arxiv_papers = translate_items(arxiv_papers, "title")
        arxiv_papers = translate_items(arxiv_papers, "summary")

    lines = [f"🤖 *AI Daily Digest — {today}*\n"]

    lines.append("*📰 HackerNews*")
    for p in hn_posts:
        lines.append(f"• <{p['url']}|{p['title']}>")

    if arxiv_papers:
        lines.append("\n*📄 arXiv 논문*")
        for p in arxiv_papers:
            lines.append(f"• <{p['url']}|{p['title']}> — {p['summary']}")

    send_to_slack("\n".join(lines))
    print(f"[{today}] Slack 전송 완료")


if __name__ == "__main__":
    main()
