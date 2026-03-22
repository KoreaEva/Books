import os
import sys
import requests
import json
import re
import html
import webbrowser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Defaults
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


def generate_html_newsletter(summaries: List[Dict], title: str = "발빠른 뉴스속보") -> str:
    """뉴스 요약을 HTML 뉴스레터로 생성합니다."""
    now = datetime.now()
    current_date = f"{now.year}년 {now.month}월 {now.day}일"
    
    # HTML 구조 생성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}
        
        .date {{
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .article {{
            margin-bottom: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        
        .article:hover {{
            background: #eef0f7;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        }}
        
        .article-number {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        
        .article-title {{
            font-size: 1.3em;
            font-weight: 700;
            margin-bottom: 12px;
            color: #2c3e50;
            line-height: 1.4;
        }}
        
        .article-link {{
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
            margin-bottom: 15px;
            display: inline-block;
            word-break: break-all;
        }}
        
        .article-link:hover {{
            text-decoration: underline;
        }}
        
        .article-summary {{
            color: #555;
            line-height: 1.8;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #999;
            font-size: 0.9em;
            border-top: 1px solid #eee;
        }}
        
        .footer-text {{
            margin-bottom: 10px;
        }}
        
        .divider {{
            width: 40px;
            height: 2px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            margin: 0 auto 15px;
        }}
        
        @media (max-width: 600px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .article {{
                padding: 15px;
            }}
            
            .article-title {{
                font-size: 1.1em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ {title}</h1>
            <div class="divider" style="margin: 15px auto 0;"></div>
            <p>오늘의 주요 뉴스를 한눈에</p>
            <div class="date">{current_date}</div>
        </div>
        
        <div class="content">
"""
    
    # 각 기사 추가
    for idx, s in enumerate(summaries, 1):
        title_escaped = html.escape(s.get("title", "(제목 없음)"))
        link_escaped = html.escape(s.get("link", ""))
        summary_escaped = html.escape(s.get("summary", "요약을 생성하지 못했습니다."))
        
        html_content += f"""            <div class="article">
                <span class="article-number">뉴스 #{idx}</span>
                <div class="article-title">{title_escaped}</div>
                <a href="{link_escaped}" class="article-link" target="_blank">원문 읽기 →</a>
                <div class="article-summary">{summary_escaped}</div>
            </div>

"""
    
    # 푸터 추가
    html_content += """        </div>
        
        <div class="footer">
            <div class="footer-text">발빠른 뉴스속보</div>
            <div style="font-size: 0.85em; color: #bbb;">자동 생성된 뉴스레터입니다</div>
        </div>
    </div>
</body>
</html>"""
    
    return html_content


def save_html_to_file(html_content: str, filename: str = "newsletter.html") -> str:
    """HTML 내용을 파일로 저장합니다."""
    output_path = Path(filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return str(output_path.absolute())


def display_newsletter_in_browser(html_file_path: str):
    """웹 브라우저에서 HTML 뉴스레터를 표시합니다."""
    try:
        webbrowser.open(f"file:///{html_file_path}")
    except Exception as e:
        print(f"브라우저 열기 실패: {e}")


def get_user_confirmation(message: str = "뉴스레터를 발송하시겠습니까?") -> bool:
    """사용자 확인을 받습니다."""
    while True:
        response = input(f"\n{message} (y/n): ").strip().lower()
        if response in ['y', 'yes', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("'y' 또는 'n'으로 입력해주세요.")


def load_email_list(email_file: str = "email_list.txt") -> List[str]:
    """파일에서 이메일 목록을 로드합니다."""
    if not Path(email_file).exists():
        print(f"경고: {email_file} 파일이 없습니다.")
        return []
    
    emails = []
    try:
        with open(email_file, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and '@' in email:
                    emails.append(email)
    except Exception as e:
        print(f"이메일 파일 읽기 오류: {e}")
    
    return emails


def send_newsletter_email(html_content: str, email_list: List[str], subject: str = "발빠른 뉴스속보", 
                         sender_email: str = None, sender_password: str = None) -> bool:
    """HTML 뉴스레터를 이메일로 발송합니다."""
    if not email_list:
        print("발송할 이메일 주소가 없습니다.")
        return False
    
    # 환경변수에서 이메일 정보 로드 (없으면 입력받기)
    if not sender_email:
        sender_email = os.environ.get("SENDER_EMAIL")
    if not sender_password:
        sender_password = os.environ.get("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        print("\n이메일 발송을 위해 발신자 정보가 필요합니다.")
        print("환경변수 SENDER_EMAIL, SENDER_PASSWORD를 설정하거나 아래에 입력하세요:")
        sender_email = input("발신 이메일 주소: ").strip()
        sender_password = input("이메일 비밀번호 (또는 앱 비밀번호): ").strip()
    
    if not sender_email or not sender_password:
        print("이메일 정보가 없어 발송을 취소했습니다.")
        return False
    
    try:
        # Gmail SMTP 서버 설정 (Gmail 사용 기준)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        print(f"\n이메일 발송 중... (수신자: {len(email_list)}명)")
        
        # 각 이메일 수신자에게 발송
        for recipient_email in email_list:
            try:
                # 서버 연결
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                
                # 이메일 메시지 작성
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = sender_email
                msg['To'] = recipient_email
                
                # HTML 파트 추가
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
                
                # 발송
                server.send_message(msg)
                server.quit()
                
                print(f"  ✓ {recipient_email}에 발송 완료")
            
            except Exception as e:
                print(f"  ✗ {recipient_email} 발송 실패: {e}")
        
        print("\n이메일 발송 완료!")
        return True
    
    except Exception as e:
        print(f"이메일 발송 중 오류: {e}")
        return False

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

    # 3. HTML 뉴스레터 생성
    print("\nHTML 뉴스레터를 생성하는 중입니다...")
    html_newsletter = generate_html_newsletter(summaries, title="발빠른 뉴스속보")
    
    # 4. 뉴스레터를 파일로 저장
    html_file_path = save_html_to_file(html_newsletter, "newsletter.html")
    print(f"✓ 뉴스레터가 저장되었습니다: {html_file_path}")
    
    # 5. 웹 브라우저에서 미리보기
    print("\n웹 브라우저에서 뉴스레터를 표시합니다...")
    display_newsletter_in_browser(html_file_path)
    
    # 6. 사용자 확인 받기
    if not get_user_confirmation("\n뉴스레터를 이메일로 발송하시겠습니까?"):
        print("뉴스레터 발송을 취소했습니다.")
        return
    
    # 7. 이메일 목록 로드
    email_list = load_email_list("email_list.txt")
    
    if not email_list:
        print("\n이메일 목록이 없습니다. 수동으로 입력하시겠습니까?")
        if get_user_confirmation("이메일을 수동으로 입력하시겠습니까?"):
            email_list = []
            while True:
                email = input("이메일 주소 입력 (종료: 엔터 입력): ").strip()
                if not email:
                    break
                if '@' in email:
                    email_list.append(email)
                    print(f"  추가됨: {email}")
                else:
                    print("  유효한 이메일이 아닙니다.")
        
        if not email_list:
            print("발송할 이메일이 없어 종료합니다.")
            return
    
    # 8. 이메일 발송
    send_newsletter_email(html_newsletter, email_list, subject="발빠른 뉴스속보")

if __name__ == "__main__":
    main()