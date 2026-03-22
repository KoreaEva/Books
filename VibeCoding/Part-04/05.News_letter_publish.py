import os
import sys
import requests
import json
import re
import html
from typing import List, Dict
from bs4 import BeautifulSoup
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()
DEFAULT_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
DEFAULT_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
ENDPOINT = "https://openapi.naver.com/v1/search/news.json"

def strip_html_tags(text: str) -> str:
    if not text: return ""
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text)

def get_article_content(url: str) -> str:
    """기사 링크에 접속하여 본문 텍스트만 추출합니다."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 일반적인 뉴스 사이트의 본문 태그들 (p, div 등)에서 텍스트 추출
        # 사이트마다 구조가 다르므로 최대한 공통적인 텍스트 요소를 가져옵니다.
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text()])
        
        # 불필요한 공백 및 줄바꿈 정리
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    except:
        return ""  


def summarize_article_with_ollama(text: str, title: str = "", model: str = "gemma3:4b", base_url: str = "http://localhost:11434") -> str:
    """
    로컬 Ollama 서버의 Gemma3:4b 모델을 사용해 기사 본문을 한국어로 자세히 요약합니다.
    간단한 핵심요약, 주요 사실/수치, 배경/맥락, 영향/결론 형식을 포함하도록 요청합니다.
    """
    try:
        api_url = f"{base_url}/api/generate"
        prompt = (
            f"다음 기사를 한국어로 자세히 요약해줘. 각 요약은 핵심요약(2-3문장), 주요 사실/수치, 배경/맥락, 영향/결론을 포함하도록 구성해줘.\n"
            f"제목: {title}\n"
            f"본문:\n{text}\n\n요약:"
        )

        resp = requests.post(
            api_url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.2,
            },
            timeout=120,
        )

        if resp.status_code == 200:
            try:
                j = resp.json()
                return j.get("response", "요약을 생성하지 못했습니다.")
            except Exception:
                return resp.text or "요약 응답을 파싱하지 못했습니다."
        else:
            return f"요약 오류: 상태 코드 {resp.status_code}"

    except requests.exceptions.RequestException as e:
        return f"요약 요청 실패: {e}"
    except Exception as e:
        return f"요약 중 오류: {e}"


def search_news(query: str, display: int = 10) -> List[str]:
    headers = {
        "X-Naver-Client-Id": DEFAULT_CLIENT_ID,
        "X-Naver-Client-Secret": DEFAULT_CLIENT_SECRET,
    }
    params = {"query": query, "display": display, "sort": "date"}
    
    try:
        resp = requests.get(ENDPOINT, headers=headers, params=params)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        # 'originallink'가 있으면 그것을 사용, 없으면 'link' 사용
        results = []
        for it in items:
            link = it.get("originallink") or it.get("link")
            title = re.sub(r"<[^>]+>", "", it.get("title", ""))
            title = html.unescape(title).strip()
            results.append({"title": title, "link": link})
        return results
    except Exception as e:
        print(f"API 요청 오류: {e}")
        return []

def main():
    query = "속보"
    display_count = 10  # 가져올 뉴스 개수
    
    print(f"'{query}' 키워드로 최신 뉴스를 검색하여 본문을 수집합니다...")
    
    # 1. 뉴스 링크(제목 포함) 가져오기
    items = search_news(query, display_count)
    
    if not items:
        print("검색 결과가 없습니다.")
        return

    # 2. 각 링크에서 본문 수집 및 Ollama로 기사별 요약 생성
    summaries = []
    collected_texts = []
    for it in tqdm(items, desc="본문 수집 및 요약 중", unit="article"):
        title = it.get("title", "(제목 없음)")
        link = it.get("link") or ""
        content = ""
        if link:
            content = get_article_content(link)
        if not content:
            summaries.append({"title": title, "link": link, "summary": "본문을 가져오지 못했습니다."})
            continue

        collected_texts.append(content)

        # 요약 생성 (Ollama 로컬 gemma3:4b 사용)
        summary = summarize_article_with_ollama(content, title=title)
        summaries.append({"title": title, "link": link, "summary": summary})

    # 3. 모든 기사별 요약을 하나의 문자열로 결합하여 출력
    print("\n" + "="*80)
    print("[기사별 상세 요약]")
    print("="*80 + "\n")

    combined = []
    for s in summaries:
        header = f"제목: {s.get('title')}\n링크: {s.get('link')}\n"
        body = s.get('summary', '')
        combined.append(header + body + "\n\n")

    final_output = "\n".join(combined).strip()
    if final_output:
        print(final_output)
    else:
        print("요약을 생성하지 못했습니다.")

if __name__ == "__main__":
    main()