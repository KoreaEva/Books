import requests
import json

def fetch_exchange_rate(base, target):
    """
    환율 정보를 가져오는 함수
    
    Args:
        base (str): 기준 통화 코드 (예: USD, EUR, JPY)
        target (str): 대상 통화 코드 (예: KRW, USD, EUR)
    
    Returns:
        float: 환율 값 (base → target), 실패 시 None
    """
    try:
        # exchangerate-api.com의 무료 API 사용
        url = f"https://api.exchangerate-api.com/v4/latest/{base.upper()}"
        
        # API 호출
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        # JSON 데이터 파싱
        data = response.json()
        
        # 대상 통화의 환율 반환
        rates = data.get('rates', {})
        if target.upper() in rates:
            return rates[target.upper()]
        else:
            print(f"오류: '{target}' 통화를 찾을 수 없습니다.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"데이터 파싱 오류: {e}")
        return None
    except Exception as e:
        print(f"예기치 못한 오류: {e}")
        return None

def main():
    """
    메인 함수: 사용자 입력을 받아 환율을 조회하고 출력
    """
    print("=== 환율 조회기 ===")
    
    # 기본값 설정
    base_currency = "USD"
    target_currency = "KRW"
    
    try:
        # 기준 통화 입력받기
        base_input = input("기준 통화를 입력하세요 (기본값: USD): ").strip()
        if base_input:
            base_currency = base_input.upper()
        
        # 대상 통화 입력받기
        target_input = input("대상 통화를 입력하세요 (기본값: KRW): ").strip()
        if target_input:
            target_currency = target_input.upper()
        
        # 통화 코드 길이 검증 (일반적으로 3자리)
        if len(base_currency) != 3 or len(target_currency) != 3:
            raise ValueError("통화 코드는 3자리여야 합니다 (예: USD, EUR, KRW)")
            
    except Exception as e:
        print(f"잘못된 입력입니다: {e}")
        print("기본값으로 설정합니다. (USD → KRW)")
        base_currency = "USD"
        target_currency = "KRW"
    
    print(f"\n환율 조회 중... ({base_currency} → {target_currency})")
    
    # 환율 조회
    rate = fetch_exchange_rate(base_currency, target_currency)
    
    if rate is not None:
        print(f"\n=== 환율 정보 ===")
        print(f"기준 통화: {base_currency}")
        print(f"대상 통화: {target_currency}")
        print(f"환율: 1 {base_currency} = {rate:,.4f} {target_currency}")
        
        # 예시 계산
        example_amount = 100
        converted = example_amount * rate
        print(f"\n예시: {example_amount} {base_currency} = {converted:,.2f} {target_currency}")
    else:
        print(f"\n환율 정보를 가져오는데 실패했습니다.")
        print("인터넷 연결이나 통화 코드를 확인해주세요.")

if __name__ == "__main__":
    main()
