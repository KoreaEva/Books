import json
import os
from datetime import datetime, date, timedelta
import random

# 단어장 데이터 파일 경로
VOCAB_FILE = "vocab.json"

# Leitner 시스템: box별 복습 주기 (일)
LEITNER_INTERVALS = {
    1: 1,    # Box 1: 1일 후
    2: 2,    # Box 2: 2일 후
    3: 4,    # Box 3: 4일 후
    4: 7,    # Box 4: 7일 후
    5: 14    # Box 5: 14일 후
}

def load_vocab():
    """
    JSON 파일에서 단어장을 불러오는 함수
    
    Returns:
        list: 단어 목록 (파일이 없거나 오류 시 빈 리스트)
    """
    try:
        if os.path.exists(VOCAB_FILE):
            with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"파일 읽기 오류: {e}")
        print("빈 단어장으로 시작합니다.")
        return []

def save_vocab(vocab_list):
    """
    단어장을 JSON 파일에 저장하는 함수
    
    Args:
        vocab_list (list): 저장할 단어 목록
    
    Returns:
        bool: 저장 성공 여부
    """
    try:
        with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
            json.dump(vocab_list, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"파일 저장 오류: {e}")
        return False

def get_next_id(vocab_list):
    """다음 단어 ID를 생성하는 함수"""
    if not vocab_list:
        return 1
    return max(word['id'] for word in vocab_list) + 1

def calculate_next_review(box_level):
    """다음 복습일을 계산하는 함수"""
    days_to_add = LEITNER_INTERVALS.get(box_level, 1)
    next_date = date.today() + timedelta(days=days_to_add)
    return next_date.isoformat()

def is_due_for_review(word):
    """
    오늘 복습해야 하는 단어인지 확인하는 함수
    오늘 추가된 단어도 바로 퀴즈 대상에 포함
    """
    # 아직 복습한 적이 없는 새 단어는 바로 복습 대상
    if not word.get('last_review'):
        return True
    
    # next_review가 없거나 오늘 이전이면 복습 대상
    if not word.get('next_review'):
        return True
    
    try:
        next_review_date = datetime.fromisoformat(word['next_review']).date()
        return date.today() >= next_review_date
    except:
        return True

def get_box_emoji(box_level):
    """박스 레벨에 따른 이모지 반환"""
    emojis = {1: "📦", 2: "📋", 3: "📚", 4: "🎯", 5: "🏆"}
    return emojis.get(box_level, "❓")

def add_word(vocab_list):
    """새로운 단어를 추가하는 함수"""
    print("\n=== 새 단어 추가 ===")
    
    # 영어 단어 입력
    word = input("영어 단어를 입력하세요: ").strip().lower()
    if not word:
        print("❌ 영어 단어를 입력해야 합니다.")
        return False
    
    # 중복 체크
    for existing_word in vocab_list:
        if existing_word['word'].lower() == word:
            print(f"❌ '{word}'는 이미 등록된 단어입니다.")
            return False
    
    # 한국어 뜻 입력
    meaning = input("한국어 뜻을 입력하세요: ").strip()
    if not meaning:
        print("❌ 한국어 뜻을 입력해야 합니다.")
        return False
    
    # 예문 입력 (선택사항)
    example = input("예문을 입력하세요 (없으면 Enter): ").strip()
    
    # 새 단어 생성
    new_word = {
        'id': get_next_id(vocab_list),
        'word': word,
        'meaning': meaning,
        'example': example if example else None,
        'box': 1,
        'created_at': datetime.now().isoformat(),
        'last_review': None,  # 아직 복습하지 않음
        'next_review': None,  # 바로 퀴즈 대상이 되도록 None으로 설정
        'correct_streak': 0,
        'wrong_streak': 0
    }
    
    vocab_list.append(new_word)
    
    if save_vocab(vocab_list):
        print(f"✅ 단어 '{word}'가 추가되었습니다! (ID: {new_word['id']}) 📦")
        print("💡 새로 추가된 단어는 바로 퀴즈에서 출제됩니다.")
        return True
    else:
        print("❌ 단어 저장에 실패했습니다.")
        return False

def list_words(vocab_list):
    """단어 목록을 출력하는 함수"""
    if not vocab_list:
        print("\n📝 등록된 단어가 없습니다.")
        return
    
    print("\n=== 목록 옵션 ===")
    print("1. 전체 단어")
    print("2. 오늘 복습할 단어만")
    
    try:
        choice = input("선택하세요 (1-2, 기본값 2): ").strip()
        if not choice:
            choice = "2"
        
        option = int(choice)
        if option not in [1, 2]:
            raise ValueError
    except ValueError:
        print("❌ 올바른 옵션을 선택해주세요.")
        return
    
    # 필터링
    if option == 1:
        filtered_words = vocab_list
        title = "전체 단어"
    else:
        filtered_words = [word for word in vocab_list if is_due_for_review(word)]
        title = "오늘 복습할 단어"
    
    if not filtered_words:
        print(f"\n📝 {title}가 없습니다.")
        return
    
    # 박스 레벨과 ID 순으로 정렬
    filtered_words.sort(key=lambda x: (x['box'], x['id']))
    
    print(f"\n=== {title} ({len(filtered_words)}개) ===")
    print("-" * 90)
    print(f"{'ID':>3} | {'단어':<15} | {'뜻':<20} | {'박스':<4} | {'정답':<4} | {'오답':<4} | {'상태':<10}")
    print("-" * 90)
    
    for word in filtered_words:
        box_emoji = get_box_emoji(word['box'])
        
        # 상태 표시
        if not word.get('last_review'):
            status = "🆕 신규"
        elif is_due_for_review(word):
            status = "🔔 복습예정"
        else:
            next_review = word.get('next_review', '')[:10] if word.get('next_review') else '미정'
            status = f"📅 {next_review}"
        
        print(f"{word['id']:3d} | {word['word']:<15} | {word['meaning']:<20} | "
              f"{box_emoji} {word['box']:<2} | {word['correct_streak']:4d} | "
              f"{word['wrong_streak']:4d} | {status:<10}")
        
        if word.get('example'):
            print(f"     📝 예문: {word['example']}")
    
    print("-" * 90)

def quiz_words(vocab_list):
    """단어 퀴즈를 진행하는 함수"""
    # 오늘 복습할 단어 필터링 (새로 추가된 단어 포함)
    due_words = [word for word in vocab_list if is_due_for_review(word)]
    
    if not due_words:
        print("\n🎉 오늘 복습할 단어가 없습니다! 새로운 단어를 추가해보세요.")
        return False
    
    print(f"\n=== 단어 퀴즈 ({len(due_words)}개 복습 대상) ===")
    print("💡 오늘 추가된 단어도 포함됩니다.")
    print("종료하려면 'quit' 또는 'q'를 입력하세요.\n")
    
    # 단어를 섞어서 출제
    random.shuffle(due_words)
    
    correct_count = 0
    total_count = 0
    
    for word in due_words:
        total_count += 1
        
        # 새 단어 표시
        is_new = not word.get('last_review')
        new_indicator = " 🆕" if is_new else ""
        
        print(f"\n📚 문제 {total_count}/{len(due_words)}{new_indicator}")
        print(f"단어: {word['word'].upper()}")
        
        if word.get('example'):
            print(f"예문: {word['example']}")
        
        # 사용자 답안 입력
        user_answer = input("뜻을 입력하세요: ").strip()
        
        # 종료 체크
        if user_answer.lower() in ['quit', 'q']:
            print("퀴즈를 종료합니다.")
            break
        
        # 정답 체크 (유연한 매칭)
        is_correct = check_answer(word['meaning'], user_answer)
        
        if is_correct:
            print("✅ 정답입니다!")
            correct_count += 1
            
            # 정답 시 처리
            word['correct_streak'] += 1
            word['wrong_streak'] = 0
            word['box'] = min(word['box'] + 1, 5)  # 최대 박스 5
            
        else:
            print(f"❌ 틀렸습니다. 정답: {word['meaning']}")
            
            # 오답 시 처리
            word['wrong_streak'] += 1
            word['correct_streak'] = 0
            word['box'] = 1  # 박스 1로 리셋
        
        # 복습 정보 업데이트
        word['last_review'] = datetime.now().isoformat()
        word['next_review'] = calculate_next_review(word['box'])
        
        box_emoji = get_box_emoji(word['box'])
        next_review_days = LEITNER_INTERVALS[word['box']]
        print(f"📦 박스 레벨: {box_emoji} {word['box']} (다음 복습: {next_review_days}일 후)")
    
    # 결과 저장
    if save_vocab(vocab_list):
        print(f"\n📊 퀴즈 결과: {correct_count}/{total_count} 정답")
        if total_count > 0:
            accuracy = (correct_count / total_count) * 100
            print(f"정답률: {accuracy:.1f}%")
        return True
    else:
        print("❌ 결과 저장에 실패했습니다.")
        return False

def check_answer(correct_meaning, user_answer):
    """답안을 유연하게 체크하는 함수"""
    if not user_answer:
        return False
    
    # 대소문자 무시, 공백 제거, 쉼표/콤마 제거
    correct = correct_meaning.replace(' ', '').replace(',', '').replace('，', '').lower()
    user = user_answer.replace(' ', '').replace(',', '').replace('，', '').lower()
    
    # 완전 일치
    if correct == user:
        return True
    
    # 부분 일치 (정답이 사용자 답안에 포함되거나 그 반대)
    if correct in user or user in correct:
        return True
    
    # 여러 뜻이 있는 경우 하나라도 맞으면 정답
    if ',' in correct_meaning or '，' in correct_meaning:
        meanings = correct_meaning.replace('，', ',').split(',')
        for meaning in meanings:
            clean_meaning = meaning.strip().replace(' ', '').lower()
            if clean_meaning == user or clean_meaning in user or user in clean_meaning:
                return True
    
    return False

def delete_word(vocab_list):
    """단어를 삭제하는 함수"""
    if not vocab_list:
        print("\n📝 삭제할 단어가 없습니다.")
        return False
    
    print("\n=== 등록된 단어 목록 ===")
    vocab_list.sort(key=lambda x: x['id'])
    
    for word in vocab_list:
        box_emoji = get_box_emoji(word['box'])
        status = "🆕" if not word.get('last_review') else f"📦{word['box']}"
        print(f"[{word['id']:2d}] {word['word']:<15} - {word['meaning']:<20} {status}")
    
    try:
        word_id = int(input("\n삭제할 단어 번호를 입력하세요: "))
        
        # 해당 ID의 단어 찾기
        for i, word in enumerate(vocab_list):
            if word['id'] == word_id:
                # 삭제 확인
                confirm = input(f"정말로 '{word['word']} - {word['meaning']}'을(를) 삭제하시겠습니까? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    deleted_word = vocab_list.pop(i)
                    
                    if save_vocab(vocab_list):
                        print(f"🗑️  단어 '{deleted_word['word']}'가 삭제되었습니다.")
                        return True
                    else:
                        print("❌ 단어 저장에 실패했습니다.")
                        vocab_list.insert(i, deleted_word)  # 원복
                        return False
                else:
                    print("❌ 삭제가 취소되었습니다.")
                    return False
        
        print("❌ 해당 번호의 단어를 찾을 수 없습니다.")
        return False
        
    except ValueError:
        print("❌ 올바른 번호를 입력해주세요.")
        return False

def show_stats(vocab_list):
    """단어장 통계를 출력하는 함수"""
    if not vocab_list:
        print("\n📊 통계를 표시할 단어가 없습니다.")
        return
    
    total_words = len(vocab_list)
    due_words = len([word for word in vocab_list if is_due_for_review(word)])
    new_words = len([word for word in vocab_list if not word.get('last_review')])
    
    # 박스별 분포
    box_counts = {i: 0 for i in range(1, 6)}
    for word in vocab_list:
        box_counts[word['box']] += 1
    
    print(f"\n📊 단어장 통계")
    print("-" * 40)
    print(f"총 단어 수: {total_words}개")
    print(f"새 단어: {new_words}개 🆕")
    print(f"오늘 복습할 단어: {due_words}개 🔔")
    print("\n박스별 분포:")
    for box, count in box_counts.items():
        emoji = get_box_emoji(box)
        percentage = (count / total_words * 100) if total_words > 0 else 0
        print(f"  {emoji} 박스 {box}: {count}개 ({percentage:.1f}%)")

def show_menu():
    """메뉴를 출력하는 함수"""
    print("\n" + "="*60)
    print("📚 영어 단어 암기장 (Leitner System)")
    print("="*60)
    print("1. ➕ 단어 추가 (Add)")
    print("2. 📝 단어 목록 (List)")
    print("3. 🎯 단어 퀴즈 (Quiz)")
    print("4. 🗑️  단어 삭제 (Delete)")
    print("5. 📊 통계 보기 (Stats)")
    print("6. 🚪 종료 (Exit)")
    print("="*60)

def main():
    """메인 함수: 사용자 인터페이스 제공"""
    print("🎉 영어 단어 암기장에 오신 것을 환영합니다!")
    print("📚 Leitner 시스템으로 효율적인 복습을 도와드립니다.")
    
    # 단어장 로드
    vocab_list = load_vocab()
    total_words = len(vocab_list)
    due_words = len([word for word in vocab_list if is_due_for_review(word)])
    new_words = len([word for word in vocab_list if not word.get('last_review')])
    
    print(f"📂 {total_words}개의 단어를 불러왔습니다.")
    if new_words > 0:
        print(f"🆕 새 단어: {new_words}개")
    if due_words > 0:
        print(f"🔔 오늘 복습할 단어: {due_words}개")
    
    while True:
        show_menu()
        
        try:
            choice = input("메뉴를 선택하세요 (1-6): ").strip()
            
            if choice == '1':
                add_word(vocab_list)
            elif choice == '2':
                list_words(vocab_list)
            elif choice == '3':
                quiz_words(vocab_list)
            elif choice == '4':
                delete_word(vocab_list)
            elif choice == '5':
                show_stats(vocab_list)
            elif choice == '6':
                print("\n👋 영어 단어 암기장을 종료합니다. 꾸준한 학습으로 실력 향상하세요!")
                break
            else:
                print("❌ 올바른 메뉴 번호를 선택해주세요. (1-6)")
        
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 예기치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
