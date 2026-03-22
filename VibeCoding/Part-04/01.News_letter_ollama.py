"""
Ollama Gemma 3:4b를 이용한 대화형 챗봇 스크립트
"""

import requests
import sys

class OllamaChatbot:
    """Ollama를 사용한 대화형 챗봇 클래스"""
    
    def __init__(self, model: str = "gemma3:4b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        self.conversation_history = []
        self.system_prompt = """당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 
사용자의 질문에 자연스럽고 명확하게 답변해주세요.
한국어로 대화하며, 긴 답변은 적절히 줄을 나누어 읽기 쉽게 표현해주세요."""
    
    def build_prompt(self, user_message: str) -> str:
        """이전 대화 맥락을 포함한 전체 프롬프트 생성"""
        prompt = self.system_prompt + "\n\n"
        
        # 최근 6개의 메시지만 포함하여 대화 이력 유지
        for message in self.conversation_history[-6:]:
            role = message["role"]
            content = message["content"]
            if role == "user":
                prompt += f"사용자: {content}\n\n"
            else:
                prompt += f"어시스턴트: {content}\n\n"
        
        # 현재 사용자 메시지 추가
        prompt += f"사용자: {user_message}\n\n어시스턴트:"
        
        return prompt
    
    def get_response(self, user_message: str) -> str:
        """Ollama API를 통해 인공지능 응답 생성"""
        prompt = self.build_prompt(user_message)
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "응답을 생성할 수 없습니다.").strip()
            else:
                return f"오류: 상태 코드 {response.status_code}"
        
        except requests.exceptions.Timeout:
            return "오류: 요청 시간 초과. 다시 시도해주세요."
        except requests.exceptions.ConnectionError:
            return "오류: Ollama 서버에 연결할 수 없습니다. 프로그램 실행 여부를 확인하세요."
        except Exception as e:
            return f"오류: {str(e)}"
    
    def chat(self, user_message: str) -> str:
        """사용자 메시지 처리 및 대화 이력 저장"""
        self.conversation_history.append({"role": "user", "content": user_message})
        
        ai_response = self.get_response(user_message)
        
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response
    
    def clear_history(self) -> None:
        """대화 내용 초기화"""
        self.conversation_history = []
        print("대화 이력이 초기화되었습니다.\n")
    
    def show_help(self) -> None:
        """사용 가능한 명령어 표시"""
        help_text = """
╔════════════════════════════════════════════════════════════╗
║              Ollama 대화형 챗봇 - 명령어                   ║
╚════════════════════════════════════════════════════════════╝

명령어:
  /help      - 이 도움말 표시
  /clear     - 대화 이력 초기화
  /history   - 지금까지의 대화 이력 보기
  /exit      - 프로그램 종료
"""
        print(help_text)
    
    def show_history(self) -> None:
        """저장된 대화 이력 출력"""
        if not self.conversation_history:
            print("대화 이력이 없습니다.\n")
            return
       
        print("\n" + "="*25 + " 대화 이력 " + "="*25)
        for i, message in enumerate(self.conversation_history, 1):
            role = "사용자" if message["role"] == "user" else "어시스턴트"
            print(f"[{i}] {role}: {message['content']}\n")
        print("="*60 + "\n")
    
    def run(self) -> None:
        """메인 대화 루프 실행"""
        print("\n" + "="*60)
        print("🤖 Ollama Gemma 3:4b 대화형 챗봇 실행 중")
        print("="*60)
        print("자유롭게 대화하세요. 종료하려면 '/exit'를 입력하세요.\n")
        
        while True:
            try:
                user_input = input("당신: ").strip()
                if not user_input: continue
               
                if user_input.lower() == "/help":
                    self.show_help(); continue
                if user_input.lower() == "/clear":
                    self.clear_history(); continue
                if user_input.lower() == "/history":
                    self.show_history(); continue
                if user_input.lower() == "/exit":
                    print("\n👋 대화를 종료합니다. 안녕히 가세요!"); break
                
                print("\n(생각 중...)", end="", flush=True)
                response = self.chat(user_input)
                print("\r" + " " * 12 + "\r", end="") 
                
                print(f"어시스턴트: {response}\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 프로그램을 종료합니다."); break
            except Exception as e:
                print(f"오류 발생: {e}\n")

def main():
    """프로그램 시작점 및 연결 확인"""
    print("Ollama 엔진 연결 확인 중...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama 서버 연결 성공!\n")
            chatbot = OllamaChatbot()
            chatbot.run()
        else:
            print("✗ Ollama 서버 상태 이상")
    except requests.exceptions.ConnectionError:
        print("✗ 오류: Ollama가 실행 중이지 않습니다. 프로그램을 켜주세요.")

if __name__ == "__main__":
    main()
