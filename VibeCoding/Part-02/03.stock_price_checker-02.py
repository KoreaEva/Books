import yfinance as yf
from datetime import datetime
import time

def fetch_price(ticker):
    """
    주식 종목의 최신 가격을 가져오는 함수
    
    Args:
        ticker (str): 주식 종목 티커 (예: AAPL, MSFT, GOOGL)
    
    Returns:
        dict: 성공 시 {'price': float, 'currency': str, 'name': str, 'date': str}
              실패 시 None
    """
    try:
        # yfinance로 종목 정보 가져오기
        stock = yf.Ticker(ticker.upper())
        
        # 종목 정보 조회
        info = stock.info
        
        # 최근 주가 데이터 조회 (1일)
        hist = stock.history(period="1d")
        
        if hist.empty:
            print(f"오류: '{ticker}' 종목의 데이터를 찾을 수 없습니다.")
            return None
        
        # 가장 최근 종가
        latest_close = hist['Close'].iloc[-1]
        
        # 종목 정보
        company_name = info.get('longName', info.get('shortName', ticker.upper()))
        currency = info.get('currency', 'USD')
        
        # 최근 거래일
        latest_date = hist.index[-1].strftime('%Y-%m-%d')
        
        return {
            'price': latest_close,
            'currency': currency,
            'name': company_name,
            'date': latest_date
        }
        
    except Exception as e:
        print(f"주가 조회 중 오류 발생: {e}")
        return None

def monitor_stock():
    """
    실시간 주가 모니터링 함수
    사용자로부터 티커와 간격을 입력받아 반복적으로 주가를 출력
    """
    print("=== 실시간 주가 모니터링 ===")
    
    # 기본값 설정
    default_ticker = "AAPL"
    default_interval = 30
    
    try:
        # 티커 입력받기
        ticker_input = input("모니터링할 종목 티커를 입력하세요 (기본값: AAPL): ").strip()
        ticker = ticker_input.upper() if ticker_input else default_ticker
        
        # 간격 입력받기
        interval_input = input("갱신 간격(초)을 입력하세요 (기본값: 30): ").strip()
        if interval_input:
            interval = int(interval_input)
            if interval <= 0:
                raise ValueError("간격은 양수여야 합니다.")
        else:
            interval = default_interval
            
    except ValueError as e:
        print(f"잘못된 입력입니다: {e}")
        print(f"기본값을 사용합니다. (티커: {default_ticker}, 간격: {default_interval}초)")
        ticker = default_ticker
        interval = default_interval
    except Exception as e:
        print(f"입력 오류: {e}")
        print(f"기본값을 사용합니다. (티커: {default_ticker}, 간격: {default_interval}초)")
        ticker = default_ticker
        interval = default_interval
    
    print(f"\n{ticker} 종목을 {interval}초 간격으로 모니터링합니다.")
    print("모니터링을 중단하려면 Ctrl+C를 누르세요.\n")
    
    # 첫 번째 조회로 종목 정보 표시
    first_result = fetch_price(ticker)
    if first_result is None:
        print(f"'{ticker}' 종목을 찾을 수 없습니다. 프로그램을 종료합니다.")
        return
    
    # 종목 정보 출력 (한 번만)
    print("=" * 60)
    print(f"종목명: {first_result['name']}")
    print(f"티커: {ticker}")
    print(f"기준일: {first_result['date']}")
    print(f"통화: {first_result['currency']}")
    print("=" * 60)
    print(f"{'순번':>4} | {'시간':>8} | {'가격':>12} | {'변화':>15}")
    print("-" * 60)
    
    # 이전 가격 저장 (변화량 계산용)
    previous_price = None
    update_count = 0
    
    try:
        while True:
            update_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            result = fetch_price(ticker)
            if result:
                current_price = result['price']
                price_str = f"{current_price:,.2f} {result['currency']}"
                
                # 가격 변화 표시
                if previous_price is not None:
                    change = current_price - previous_price
                    change_percent = (change / previous_price) * 100
                    
                    if change > 0:
                        change_str = f"▲ +{change:,.2f} (+{change_percent:.2f}%)"
                    elif change < 0:
                        change_str = f"▼ {change:,.2f} ({change_percent:.2f}%)"
                    else:
                        change_str = "→ 변화없음"
                else:
                    change_str = "첫 조회"
                
                print(f"{update_count:4d} | {current_time:>8} | {price_str:>12} | {change_str:>15}")
                previous_price = current_price
            else:
                print(f"{update_count:4d} | {current_time:>8} | {'조회 실패':>12} | {'':>15}")
            
            # 지정된 간격만큼 대기
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n모니터링이 중단되었습니다. (총 {update_count}회 조회)")
        print("프로그램을 종료합니다.")

def single_lookup():
    """
    단일 주가 조회 함수: 사용자 입력을 받아 주가를 조회하고 출력
    """
    print("=== 주가 조회기 ===")
    
    # 기본값 설정
    default_ticker = "AAPL"
    ticker = default_ticker
    
    try:
        # 종목 티커 입력받기
        user_input = input("조회할 종목 티커를 입력하세요 (기본값: AAPL): ").strip()
        if user_input:
            ticker = user_input.upper()
    
    except Exception as e:
        print(f"입력 오류: {e}")
        print(f"기본값 '{default_ticker}'을 사용합니다.")
        ticker = default_ticker
    
    print(f"\n주가 조회 중... ({ticker})")
    
    # 주가 조회
    result = fetch_price(ticker)
    
    # 조회 실패 시 기본값으로 재시도
    if result is None:
        if ticker != default_ticker:
            print(f"\n'{ticker}' 조회에 실패했습니다. 기본값 '{default_ticker}'로 재시도합니다.")
            print(f"\n주가 조회 중... ({default_ticker})")
            result = fetch_price(default_ticker)
        
        if result is None:
            print(f"\n주가 정보를 가져오는데 실패했습니다.")
            print("인터넷 연결을 확인하거나 나중에 다시 시도해주세요.")
            return
    
    # 결과 출력
    print(f"\n=== 주가 정보 ===")
    print(f"종목명: {result['name']}")
    print(f"티커: {ticker if result else default_ticker}")
    print(f"최근 종가: {result['price']:,.2f} {result['currency']}")
    print(f"기준일: {result['date']}")
    
    # 현재 시간 표시
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"조회 시간: {current_time}")

def main():
    """
    메인 함수: 사용자가 기능을 선택할 수 있는 메뉴 제공
    """
    print("=== 주가 조회 프로그램 ===")
    print("1. 단일 주가 조회")
    print("2. 실시간 주가 모니터링")
    
    try:
        choice = input("\n원하는 기능을 선택하세요 (1 또는 2, 기본값: 1): ").strip()
        
        if choice == "2":
            monitor_stock()
        else:
            single_lookup()
            
    except Exception as e:
        print(f"오류: {e}")
        print("단일 주가 조회를 실행합니다.")
        single_lookup()

if __name__ == "__main__":
    main()
