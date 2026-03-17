"""
Ollama Gemma3:4b를 이용한 대화형 챗봇
"""

import requests
import sys


class OllamaChatbot:
    """Ollama를 사용한 대화형 챗봇"""
    
    def __init__(self, model: str = "gemma3:4b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        self.conversation_history = []
        self.system_prompt = """당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 
사용자의 질문에 자연스럽고 명확하게 답변해주세요.
한국어로 대화하며, 긴 답변은 적절히 줄을 나누어 읽기 쉽게 표현해주세요."""
    
    def build_prompt(self, user_message: str) -> str:
        """대화 컨텍스트를 포함한 프롬프트 생성"""
        prompt = self.system_prompt + "\n\n"
        
        # 대화 이력 추가
        for message in self.conversation_history[-6:]:  # 최근 6개 메시지만 포함
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
        """Ollama API를 통해 응답 생성 (스트리밍)"""
        prompt = self.build_prompt(user_message)
        full_response = ""
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": 0.7
                },
                timeout=60,
                stream=True
            )
            
            if response.status_code == 200:
                # 스트리밍 응답 처리
                for line in response.iter_lines():
                    if line:
                        try:
                            import json
                            chunk = json.loads(line)
                            token = chunk.get("response", "")
                            if token:
                                print(token, end="", flush=True)
                                full_response += token
                        except json.JSONDecodeError:
                            continue
                
                print()  # 줄바꿈
                return full_response.strip()
            else:
                return f"오류: 상태 코드 {response.status_code}"
        
        except requests.exceptions.Timeout:
            return "오류: 요청 시간 초과. 다시 시도해주세요."
        except requests.exceptions.ConnectionError:
            return "오류: Ollama 서버에 연결할 수 없습니다."
        except Exception as e:
            return f"오류: {str(e)}"
    
    def chat(self, user_message: str) -> str:
        """사용자 메시지를 처리하고 응답 반환"""
        # 사용자 메시지 저장
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # AI 응답 생성
        ai_response = self.get_response(user_message)
        
        # AI 응답 저장
        self.conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
        
        return ai_response
    
    def clear_history(self) -> None:
        """대화 이력 초기화"""
        self.conversation_history = []
        print("대화 이력이 초기화되었습니다.\n")
    
    def show_help(self) -> None:
        """도움말 표시"""
        help_text = """
╔════════════════════════════════════════════════════════════╗
║              Ollama 대화형 챗봇 - 명령어                   ║
╚════════════════════════════════════════════════════════════╝

명령어:
  /help      - 이 도움말 표시
  /clear     - 대화 이력 초기화
  /history   - 대화 이력 표시
  /exit      - 프로그램 종료

다른 모든 입력은 AI와의 자유로운 대화로 처리됩니다.
"""
        print(help_text)
    
    def show_history(self) -> None:
        """대화 이력 표시"""
        if not self.conversation_history:
            print("대화 이력이 없습니다.\n")
            return
        
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║                      대화 이력                            ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        
        for i, message in enumerate(self.conversation_history, 1):
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                print(f"[{i}] 사용자: {content}\n")
            else:
                print(f"[{i}] 어시스턴트: {content}\n")
                print("-" * 60 + "\n")
    
    def run(self) -> None:
        """대화형 챗봇 실행"""
        print("\n" + "="*60)
        print("🤖 Ollama Gemma3:4b 대화형 챗봇")
        print("="*60)
        print("자유롭게 대화해주세요. '/help'를 입력하면 명령어를 확인할 수 있습니다.\n")
        
        while True:
            try:
                user_input = input("당신: ").strip()
                
                if not user_input:
                    continue
                
                # 명령어 처리
                if user_input.lower() == "/help":
                    self.show_help()
                    continue
                
                if user_input.lower() == "/clear":
                    self.clear_history()
                    continue
                
                if user_input.lower() == "/history":
                    self.show_history()
                    continue
                
                if user_input.lower() == "/exit":
                    print("\n👋 대화를 종료합니다. 안녕히 가세요!")
                    break
                
                # 일반 대화 처리
                print("\n어시스턴트: ", end="", flush=True)
                response = self.chat(user_input)
                print()  # 줄바꿈
            
            except KeyboardInterrupt:
                print("\n\n👋 대화를 종료합니다. 안녕히 가세요!")
                break
            except Exception as e:
                print(f"오류 발생: {e}\n")


def main():
    """메인 함수"""
    print("Ollama 연결 확인 중...")
    
    try:
        # Ollama 연결 테스트
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("✗ Ollama 서버 연결 실패")
            return
        
        models = response.json().get("models", [])
        model_names = [m.get("name", "").split(":")[0] for m in models]
        
        if "gemma3" not in model_names:
            print("✗ gemma3:4b 모델이 설치되어 있지 않습니다.")
            print(f"설치된 모델: {', '.join(set(model_names))}")
            return
        
        print("✓ Ollama 연결 성공!\n")
        
        # 챗봇 시작
        chatbot = OllamaChatbot()
        chatbot.run()
    
    except requests.exceptions.ConnectionError:
        print("✗ Ollama 서버에 연결할 수 없습니다.")
        print("Ollama가 실행되고 있는지 확인해주세요.")
        print("기본 주소: http://localhost:11434")
    except Exception as e:
        print(f"✗ 오류: {e}")


if __name__ == "__main__":
    main()
