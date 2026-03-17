import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import html

def fetch_news(keyword=None, max_items=5):
    """
    Google News RSS를 사용해 뉴스 기사를 가져오는 함수
    
    Args:
        keyword (str, optional): 검색할 키워드. None이면 국내 주요 헤드라인
        max_items (int): 가져올 최대 기사 수 (기본값: 5)
    
    Returns:
        list: 성공 시 뉴스 기사 리스트, 실패 시 None
        [
            {
                'title': str,       # 기사 제목
                'link': str,        # 기사 링크
                'published': str,   # 발행일시
                'source': str,      # 뉴스 소스
                'summary': str      # 기사 요약
            },
            ...
        ]
    """
    try:
        # Google News RSS URL 구성
        if keyword:
            # 키워드 검색 시
            encoded_keyword = requests.utils.quote(keyword)
            url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
        else:
            # 국내 주요 헤드라인
            url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
        
        # RSS 피드 요청
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # XML 파싱
        root = ET.fromstring(response.content)
        
        # 뉴스 기사 추출
        items = root.findall('.//item')
        
        if not items:
            print("검색 결과가 없습니다.")
            return None
        
        news_list = []
        
        for item in items[:max_items]:
            try:
                # 기본 정보 추출
                title = item.find('title').text if item.find('title') is not None else "제목 없음"
                link = item.find('link').text if item.find('link') is not None else ""
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                
                # HTML 엔티티 디코딩
                title = html.unescape(title)
                
                # 뉴스 소스 추출 (제목에서 " - 소스명" 형태로 추출)
                source_match = re.search(r' - (.+)$', title)
                if source_match:
                    source = source_match.group(1)
                    title = title.replace(f' - {source}', '')
                else:
                    source = "알 수 없는 소스"
                
                # 요약 생성 (제목을 기반으로 간단한 요약)
                summary = generate_summary(title)
                
                # 발행일시 포맷팅
                formatted_date = format_pub_date(pub_date)
                
                news_item = {
                    'title': title.strip(),
                    'link': link,
                    'published': formatted_date,
                    'source': source,
                    'summary': summary
                }
                
                news_list.append(news_item)
                
            except Exception as e:
                print(f"기사 파싱 중 오류: {e}")
                continue
        
        return news_list if news_list else None
        
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류: {e}")
        return None
    except ET.ParseError as e:
        print(f"XML 파싱 오류: {e}")
        return None
    except Exception as e:
        print(f"예기치 못한 오류: {e}")
        return None

def generate_summary(title):
    """
    제목을 기반으로 간단한 요약 생성
    """
    # 제목이 너무 긴 경우 적절히 요약
    if len(title) > 50:
        # 문장을 나누고 첫 번째 문장 또는 주요 부분만 사용
        sentences = re.split(r'[.!?]', title)
        if len(sentences) > 1 and len(sentences[0]) > 20:
            return sentences[0].strip() + "..."
        else:
            return title[:47] + "..."
    else:
        return title

def format_pub_date(pub_date_str):
    """
    발행일시를 읽기 쉬운 형태로 포맷팅
    """
    if not pub_date_str:
        return "날짜 정보 없음"
    
    try:
        # RFC 2822 형식 파싱 시도
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(pub_date_str)
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        # 파싱 실패 시 원본 반환
        return pub_date_str

def print_news_item(index, news_item):
    """
    뉴스 기사를 보기 좋게 출력하는 함수
    """
    print(f"\n📰 [{index}] {news_item['title']}")
    print(f"📅 {news_item['published']} | 📺 {news_item['source']}")
    print(f"📝 {news_item['summary']}")
    print(f"🔗 {news_item['link']}")
    print("-" * 80)

def main():
    """
    메인 함수: 사용자 입력을 받아 뉴스를 조회하고 출력
    """
    print("=== 뉴스 요약기 ===")
    
    # 기본값 설정
    default_keyword = None  # None이면 국내 주요 헤드라인
    keyword = default_keyword
    
    try:
        # 키워드 입력받기
        user_input = input("검색할 키워드를 입력하세요 (없으면 Enter로 국내 헤드라인): ").strip()
        if user_input:
            keyword = user_input
    
    except Exception as e:
        print(f"입력 오류: {e}")
        print("국내 주요 헤드라인을 조회합니다.")
        keyword = default_keyword
    
    # 검색 정보 출력
    if keyword:
        print(f"\n'{keyword}' 관련 뉴스를 검색 중...")
    else:
        print(f"\n국내 주요 헤드라인을 조회 중...")
    
    # 뉴스 조회
    news_list = fetch_news(keyword, max_items=5)
    
    # 조회 실패 시 기본 피드로 재시도
    if news_list is None:
        if keyword is not None:
            print(f"\n'{keyword}' 관련 뉴스 조회에 실패했습니다. 국내 주요 헤드라인으로 재시도합니다.")
            print("\n국내 주요 헤드라인을 조회 중...")
            news_list = fetch_news(None, max_items=5)
            keyword = None
        
        if news_list is None:
            print(f"\n뉴스 정보를 가져오는데 실패했습니다.")
            print("인터넷 연결을 확인하거나 나중에 다시 시도해주세요.")
            return
    
    # 결과 출력
    search_type = f"'{keyword}' 검색 결과" if keyword else "국내 주요 헤드라인"
    print(f"\n=== {search_type} ===")
    print(f"총 {len(news_list)}개의 기사를 찾았습니다.")
    
    for i, news_item in enumerate(news_list, 1):
        print_news_item(i, news_item)
    
    # 현재 시간 표시
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n📅 조회 시간: {current_time}")
    print("\n📖 더 자세한 내용은 링크를 클릭하세요!")

if __name__ == "__main__":
    main()
