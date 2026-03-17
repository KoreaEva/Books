# 발빠른 뉴스속보 - HTML 뉴스레터 시스템

"속보" 키워드로 최신 뉴스를 검색하고, AI로 요약하며, HTML 기반의 아름다운 뉴스레터로 이메일 발송하는 시스템입니다.

## 기능

✅ **뉴스 자동 수집**: 네이버 뉴스 API로 최신 속보 뉴스 10개 검색
✅ **AI 자동 요약**: Ollama의 Gemma3:4b 모델로 한국어 요약
✅ **HTML 뉴스레터**: 아름답게 디자인된 HTML 형식의 뉴스레터 생성
✅ **웹 미리보기**: 생성된 뉴스레터를 웹 브라우저에서 미리 확인
✅ **사용자 확인**: 발송 전 사용자 승인 받기
✅ **이메일 발송**: email_list.txt의 수신자에게 자동 발송

## 필수 요구사항

### Python 패키지
```bash
pip install requests beautifulsoup4 tqdm
```

### 외부 서비스
1. **Ollama**: 로컬에서 실행 중이어야 함
   ```bash
   ollama run gemma3:4b
   ```

2. **Naver API 인증**:
   ```python
   # 환경변수 설정 또는 코드에서 설정
   NAVER_CLIENT_ID = "your_client_id"
   NAVER_CLIENT_SECRET = "your_client_secret"
   ```

3. **이메일 발송** (Gmail 기준):
   - Gmail 앱 비밀번호 생성
   - 환경변수 설정:
     ```
     SENDER_EMAIL=your_email@gmail.com
     SENDER_PASSWORD=your_app_password
     ```

## 사용 방법

### 1. email_list.txt 설정
`VibeCoding/Chapter_04/email_list.txt`에 수신자 이메일 주소 입력:
```
recipient1@example.com
recipient2@example.com
recipient3@example.com
```

### 2. 스크립트 실행
```bash
python 03.News_letter_summary.py
```

### 3. 프로세스

1. **뉴스 검색 및 본문 수집**
   - "속보" 키워드로 10개 기사 검색
   - 각 기사 본문 자동 크롤링

2. **AI 요약**
   - Ollama Gemma3:4b으로 한국어 요약 생성
   - 각 기사마다 상세한 요약 제공

3. **HTML 뉴스레터 생성**
   - 예쁘게 디자인된 HTML 형식으로 변환
   - 제목: "발빠른 뉴스속보"
   - 생성 일시 자동 포함

4. **웹 브라우저 미리보기**
   - 자동으로 브라우저에서 뉴스레터 표시
   - `newsletter.html` 파일로 저장됨

5. **사용자 확인**
   - "뉴스레터를 이메일로 발송하시겠습니까? (y/n)" 질문
   - 사용자 승인 후만 발송 진행

6. **이메일 발송**
   - email_list.txt의 모든 수신자에게 HTML 형식으로 발송
   - 각 발송 완료 상태 표시

## 출력 파일

- **newsletter.html**: 생성된 HTML 뉴스레터 파일

## 주요 기능 설명

### HTML 뉴스레터 디자인
- 그라데이션 배경 (보라색)
- 반응형 디자인 (모바일 지원)
- 카드 형식의 기사 표시
- 원문 링크 포함
- 호버 효과 포함

### 이메일 발송
- Gmail SMTP 지원
- 각 수신자별 개별 발송
- 발송 상태 실시간 표시
- 오류 처리 및 로깅

## 환경변수 예시

```bash
# .env 파일 또는 시스템 환경변수
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

## 주의사항

⚠️ **Ollama 서버 실행 필수**
```bash
ollama run gemma3:4b
```

⚠️ **Gmail 이메일 발송 시**
- Gmail 2단계 인증 활성화 필요
- 앱 비밀번호 사용 (일반 비밀번호 X)

⚠️ **이메일 주소 형식**
- email_list.txt에는 한 줄에 하나의 이메일 주소
- @ 기호가 포함된 유효한 형식이어야 함

## 문제 해결

### 뉴스 검색 실패
- 네이버 API 인증 정보 확인
- 클라이언트 ID와 시크릿 확인

### Ollama 요약 실패
- Ollama 서버 실행 확인: `ollama run gemma3:4b`
- 로컬호스트 11434 포트 확인

### 이메일 발송 실패
- Gmail 앱 비밀번호 확인
- 이메일 주소 형식 확인 (@ 포함)
- SMTP 서버 연결 확인

## 라이센스

이 프로젝트는 교육 목적으로 사용됩니다.
