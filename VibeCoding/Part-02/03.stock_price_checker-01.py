import yfinance as yf
from datetime import datetime


def fetch_price(ticker):
	"""주식 종목의 최신 가격을 가져오는 함수"""
	try:
		stock = yf.Ticker(ticker.upper())
		hist = stock.history(period="1d")

		if hist.empty:
			print(f"오류: '{ticker}' 종목의 데이터를 찾을 수 없습니다.")
			return None

		info = stock.info
		latest_close = hist["Close"].iloc[-1]
		company_name = info.get("longName", info.get("shortName", ticker.upper()))
		currency = info.get("currency", "USD")
		latest_date = hist.index[-1].strftime("%Y-%m-%d")

		return {
			"price": latest_close,
			"currency": currency,
			"name": company_name,
			"date": latest_date,
		}
	except Exception as e:
		print(f"주가 조회 중 오류 발생: {e}")
		return None


def main():
	# 테스트 실행
	print("=== 주가 조회 테스트 ===")
	test_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]

	for ticker in test_tickers:
		print(f"\n{ticker} 조회 중...")
		result = fetch_price(ticker)
		if result:
			print(f"종목명: {result['name']}")
			print(f"가격: {result['price']:,.2f} {result['currency']}")


if __name__ == "__main__":
	main()