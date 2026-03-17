1  import requests
2  import json
3  
4  def ask_gemma(prompt):
5      # Ollama 로컬 API 주소
6      url = "http://localhost:11434/api/chat"
7      
8      # 전달할 데이터 설정 (Gemma 3 4B 모델 사용)
9      payload = {
10         "model": "gemma3:4b",
11         "messages": [
12             {
13                 "role": "user",
14                 "content": prompt
15             }
16         ],
17         "stream": False  # 한 번에 전체 답변을 받기 위해 False로 설정
18     }
19     
20     try:
21         # 인공지능 엔진에게 질문 전달
22         response = requests.post(url, json=payload)
23         response.raise_for_status()
24         
25         # 결과값에서 답변 내용만 추출
26         result = response.json()
27         return result['message']['content']
28         
29     except Exception as e:
30         return f"오류가 발생했습니다: {e}"
31 
32 # 질문 던지기 테스트
33 if __name__ == "__main__":
34     question = "오늘 날씨에 어울리는 점심 메뉴를 추천해줘."
35     print(f"나: {question}")
36     
37     answer = ask_gemma(question)
38     print(f"Gemma 3: {answer}")