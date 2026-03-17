import requests
import json
from datetime import datetime

def fetch_weather(city):
    """
    OpenWeatherMap API를 사용해 도시의 최신 날씨 정보를 가져오는 함수
    
    Args:
        city (str): 조회할 도시명 (예: Seoul, Tokyo, New York)
    
    Returns:
        dict: 성공 시 날씨 정보 딕셔너리, 실패 시 None
        {
            'city': str,           # 도시명
            'country': str,        # 국가 코드
            'temperature': float,  # 현재 기온 (섭씨)
            'feels_like': float,   # 체감 온도 (섭씨)
            'humidity': int,       # 습도 (%)
            'description': str,    # 날씨 설명
            'weather_main': str,   # 주요 날씨 상태
            'wind_speed': float,   # 풍속 (m/s)
            'pressure': int        # 기압 (hPa)
        }
    """
    # OpenWeatherMap API 키 (무료 버전 사용)
    # 실제 사용 시에는 환경변수나 별도 설정파일에서 관리하는 것이 좋습니다
    API_KEY = "cbca82ab27245d6ada1ed4bef00b01da"
    
    try:
        # OpenWeatherMap API URL
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric',  # 섭씨 온도 사용
            'lang': 'kr'        # 한국어 설명
        }
        
        # API 호출
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        # JSON 데이터 파싱
        data = response.json()
        
        if data.get('cod') != 200:
            print(f"API 오류: {data.get('message', '알 수 없는 오류')}")
            return None
        
        # 날씨 정보 추출
        weather_info = {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'weather_main': data['weather'][0]['main'],
            'wind_speed': data['wind'].get('speed', 0),
            'pressure': data['main']['pressure']
        }
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"데이터 파싱 오류: {e}")
        return None
    except KeyError as e:
        print(f"API 응답 형식 오류: {e}")
        return None
    except Exception as e:
        print(f"예기치 못한 오류: {e}")
        return None

def get_weather_emoji(weather_main):
    """날씨 상태에 따른 이모지 반환"""
    weather_emojis = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Fog': '🌫️',
        'Haze': '🌫️'
    }
    return weather_emojis.get(weather_main, '🌤️')

def main():
    """
    메인 함수: 사용자 입력을 받아 날씨를 조회하고 출력
    """
    print("=== 날씨 알림기 ===")
    
    # 기본값 설정
    default_city = "Seoul"
    city = default_city
    
    try:
        # 도시명 입력받기
        user_input = input("조회할 도시명을 입력하세요 (기본값: Seoul): ").strip()
        if user_input:
            city = user_input.title()  # 첫 글자를 대문자로
    
    except Exception as e:
        print(f"입력 오류: {e}")
        print(f"기본값 '{default_city}'을 사용합니다.")
        city = default_city
    
    print(f"\n날씨 조회 중... ({city})")
    
    # 날씨 조회
    weather = fetch_weather(city)
    
    # 조회 실패 시 기본값으로 재시도
    if weather is None:
        if city.lower() != default_city.lower():
            print(f"\n'{city}' 날씨 조회에 실패했습니다. 기본값 '{default_city}'로 재시도합니다.")
            print(f"\n날씨 조회 중... ({default_city})")
            weather = fetch_weather(default_city)
            city = default_city
        
        if weather is None:
            print(f"\n날씨 정보를 가져오는데 실패했습니다.")
            print("인터넷 연결을 확인하거나 나중에 다시 시도해주세요.")
            return
    
    # 결과 출력
    weather_emoji = get_weather_emoji(weather['weather_main'])
    
    print(f"\n=== {weather['city']}, {weather['country']} 날씨 정보 ===")
    print(f"{weather_emoji} 현재 날씨: {weather['description']}")
    print(f"🌡️  현재 기온: {weather['temperature']:.1f}°C")
    print(f"🤔 체감 온도: {weather['feels_like']:.1f}°C")
    print(f"💧 습도: {weather['humidity']}%")
    print(f"💨 풍속: {weather['wind_speed']:.1f} m/s")
    print(f"📊 기압: {weather['pressure']} hPa")
    
    # 현재 시간 표시
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n📅 조회 시간: {current_time}")
    
    # 간단한 날씨 조언
    temp = weather['temperature']
    if temp >= 30:
        print("\n🔥 매우 더워요! 충분한 수분 섭취와 시원한 곳에서 휴식하세요.")
    elif temp >= 25:
        print("\n☀️ 따뜻한 날씨예요. 가벼운 옷차림이 좋겠어요.")
    elif temp >= 15:
        print("\n🌤️ 쾌적한 날씨네요! 외출하기 좋은 날입니다.")
    elif temp >= 5:
        print("\n🧥 쌀쌀해요. 따뜻한 옷을 챙기세요.")
    else:
        print("\n🧊 매우 추워요! 두꺼운 옷과 목도리를 착용하세요.")

if __name__ == "__main__":
    main()