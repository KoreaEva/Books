import json
import os
from datetime import datetime, date
import uuid

# 할일 데이터 파일 경로
TODO_FILE = "todos.json"

def load_todos():
    """
    JSON 파일에서 할일 목록을 불러오는 함수
    
    Returns:
        list: 할일 목록 (파일이 없거나 오류 시 빈 리스트)
    """
    try:
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"파일 읽기 오류: {e}")
        print("빈 할일 목록으로 시작합니다.")
        return []

def save_todos(todos):
    """
    할일 목록을 JSON 파일에 저장하는 함수
    
    Args:
        todos (list): 저장할 할일 목록
    
    Returns:
        bool: 저장 성공 여부
    """
    try:
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"파일 저장 오류: {e}")
        return False

def get_next_id(todos):
    """
    다음 할일 ID를 생성하는 함수
    
    Args:
        todos (list): 기존 할일 목록
    
    Returns:
        int: 다음 할일 ID
    """
    if not todos:
        return 1
    return max(todo['id'] for todo in todos) + 1

def validate_date(date_str):
    """
    날짜 문자열의 유효성을 검증하는 함수
    
    Args:
        date_str (str): 날짜 문자열 (YYYY-MM-DD 형식)
    
    Returns:
        bool: 유효한 날짜인지 여부
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_priority(priority_str):
    """
    우선순위의 유효성을 검증하는 함수
    
    Args:
        priority_str (str): 우선순위 문자열
    
    Returns:
        tuple: (유효성, 우선순위 값)
    """
    try:
        priority = int(priority_str)
        if 1 <= priority <= 5:
            return True, priority
        return False, None
    except ValueError:
        return False, None

def get_priority_emoji(priority):
    """
    우선순위에 따른 이모지 반환
    
    Args:
        priority (int): 우선순위 (1-5)
    
    Returns:
        str: 우선순위 이모지
    """
    emojis = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🔵"}
    return emojis.get(priority, "⚪")

def format_date(date_str):
    """
    날짜 문자열을 읽기 쉬운 형식으로 포맷팅
    
    Args:
        date_str (str): 날짜 문자열
    
    Returns:
        str: 포맷된 날짜 문자열
    """
    if not date_str:
        return ""
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str

def add_todo(todos):
    """
    새로운 할일을 추가하는 함수
    
    Args:
        todos (list): 할일 목록
    
    Returns:
        bool: 추가 성공 여부
    """
    print("\n=== 새 할일 추가 ===")
    
    # 할일 내용 입력
    text = input("할일 내용을 입력하세요: ").strip()
    if not text:
        print("❌ 할일 내용을 입력해야 합니다.")
        return False
    
    # 마감일 입력 (선택사항)
    due = None
    due_input = input("마감일을 입력하세요 (YYYY-MM-DD, 없으면 Enter): ").strip()
    if due_input:
        if validate_date(due_input):
            due = due_input
        else:
            print("❌ 올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)")
            return False
    
    # 우선순위 입력 (선택사항)
    priority = 3  # 기본값
    priority_input = input("우선순위를 입력하세요 (1-5, 기본값 3): ").strip()
    if priority_input:
        valid, priority_value = validate_priority(priority_input)
        if valid:
            priority = priority_value
        else:
            print("❌ 우선순위는 1~5 사이의 숫자여야 합니다.")
            return False
    
    # 새 할일 생성
    new_todo = {
        'id': get_next_id(todos),
        'text': text,
        'created_at': datetime.now().isoformat(),
        'due': due,
        'priority': priority,
        'done': False,
        'done_at': None
    }
    
    todos.append(new_todo)
    
    if save_todos(todos):
        priority_emoji = get_priority_emoji(priority)
        print(f"✅ 할일이 추가되었습니다! (ID: {new_todo['id']}) {priority_emoji}")
        return True
    else:
        print("❌ 할일 저장에 실패했습니다.")
        return False

def list_todos(todos):
    """
    할일 목록을 출력하는 함수
    
    Args:
        todos (list): 할일 목록
    """
    if not todos:
        print("\n📝 등록된 할일이 없습니다.")
        return
    
    print("\n=== 필터 옵션 ===")
    print("1. 전체 할일")
    print("2. 미완료 할일")
    print("3. 완료된 할일")
    
    try:
        choice = input("선택하세요 (1-3, 기본값 1): ").strip()
        if not choice:
            choice = "1"
        
        filter_option = int(choice)
        if filter_option not in [1, 2, 3]:
            raise ValueError
    except ValueError:
        print("❌ 올바른 옵션을 선택해주세요.")
        return
    
    # 필터링
    if filter_option == 1:
        filtered_todos = todos
        title = "전체 할일"
    elif filter_option == 2:
        filtered_todos = [todo for todo in todos if not todo['done']]
        title = "미완료 할일"
    else:
        filtered_todos = [todo for todo in todos if todo['done']]
        title = "완료된 할일"
    
    if not filtered_todos:
        print(f"\n📝 {title}이 없습니다.")
        return
    
    # 우선순위와 마감일 순으로 정렬
    filtered_todos.sort(key=lambda x: (x['done'], -x['priority'], x['due'] or '9999-12-31'))
    
    print(f"\n=== {title} ({len(filtered_todos)}개) ===")
    print("-" * 80)
    
    for todo in filtered_todos:
        status = "✅" if todo['done'] else "⭕"
        priority_emoji = get_priority_emoji(todo['priority'])
        
        # 기본 정보
        print(f"{status} [{todo['id']:2d}] {todo['text']}")
        
        # 상세 정보
        details = []
        details.append(f"우선순위: {priority_emoji} {todo['priority']}")
        
        if todo['due']:
            details.append(f"마감일: 📅 {todo['due']}")
        
        details.append(f"생성: 📝 {format_date(todo['created_at'])}")
        
        if todo['done'] and todo['done_at']:
            details.append(f"완료: ✅ {format_date(todo['done_at'])}")
        
        print(f"    {' | '.join(details)}")
        print("-" * 80)

def complete_todo(todos):
    """
    할일을 완료 처리하는 함수
    
    Args:
        todos (list): 할일 목록
    
    Returns:
        bool: 완료 처리 성공 여부
    """
    incomplete_todos = [todo for todo in todos if not todo['done']]
    
    if not incomplete_todos:
        print("\n📝 완료할 수 있는 할일이 없습니다.")
        return False
    
    print("\n=== 미완료 할일 목록 ===")
    for todo in incomplete_todos:
        priority_emoji = get_priority_emoji(todo['priority'])
        due_info = f" (마감: {todo['due']})" if todo['due'] else ""
        print(f"[{todo['id']:2d}] {todo['text']}{due_info} {priority_emoji}")
    
    try:
        todo_id = int(input("\n완료할 할일 번호를 입력하세요: "))
        
        # 해당 ID의 할일 찾기
        for todo in todos:
            if todo['id'] == todo_id:
                if todo['done']:
                    print("❌ 이미 완료된 할일입니다.")
                    return False
                
                # 완료 처리
                todo['done'] = True
                todo['done_at'] = datetime.now().isoformat()
                
                if save_todos(todos):
                    print(f"✅ 할일 '{todo['text']}'이(가) 완료되었습니다!")
                    return True
                else:
                    print("❌ 할일 저장에 실패했습니다.")
                    return False
        
        print("❌ 해당 번호의 할일을 찾을 수 없습니다.")
        return False
        
    except ValueError:
        print("❌ 올바른 번호를 입력해주세요.")
        return False

def delete_todo(todos):
    """
    할일을 삭제하는 함수
    
    Args:
        todos (list): 할일 목록
    
    Returns:
        bool: 삭제 성공 여부
    """
    if not todos:
        print("\n📝 삭제할 할일이 없습니다.")
        return False
    
    print("\n=== 전체 할일 목록 ===")
    for todo in todos:
        status = "✅" if todo['done'] else "⭕"
        priority_emoji = get_priority_emoji(todo['priority'])
        print(f"{status} [{todo['id']:2d}] {todo['text']} {priority_emoji}")
    
    try:
        todo_id = int(input("\n삭제할 할일 번호를 입력하세요: "))
        
        # 해당 ID의 할일 찾기
        for i, todo in enumerate(todos):
            if todo['id'] == todo_id:
                # 삭제 확인
                confirm = input(f"정말로 '{todo['text']}'을(를) 삭제하시겠습니까? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    deleted_todo = todos.pop(i)
                    
                    if save_todos(todos):
                        print(f"🗑️  할일 '{deleted_todo['text']}'이(가) 삭제되었습니다.")
                        return True
                    else:
                        print("❌ 할일 저장에 실패했습니다.")
                        todos.insert(i, deleted_todo)  # 원복
                        return False
                else:
                    print("❌ 삭제가 취소되었습니다.")
                    return False
        
        print("❌ 해당 번호의 할일을 찾을 수 없습니다.")
        return False
        
    except ValueError:
        print("❌ 올바른 번호를 입력해주세요.")
        return False

def clear_done_todos(todos):
    """
    완료된 할일을 일괄 삭제하는 함수
    
    Args:
        todos (list): 할일 목록
    
    Returns:
        bool: 삭제 성공 여부
    """
    done_todos = [todo for todo in todos if todo['done']]
    
    if not done_todos:
        print("\n📝 완료된 할일이 없습니다.")
        return False
    
    print(f"\n=== 완료된 할일 ({len(done_todos)}개) ===")
    for todo in done_todos:
        print(f"✅ [{todo['id']:2d}] {todo['text']}")
    
    confirm = input(f"\n정말로 완료된 할일 {len(done_todos)}개를 모두 삭제하시겠습니까? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        remaining_todos = [todo for todo in todos if not todo['done']]
        
        if save_todos(remaining_todos):
            print(f"🗑️  완료된 할일 {len(done_todos)}개가 삭제되었습니다.")
            todos.clear()
            todos.extend(remaining_todos)
            return True
        else:
            print("❌ 할일 저장에 실패했습니다.")
            return False
    else:
        print("❌ 삭제가 취소되었습니다.")
        return False

def show_menu():
    """메뉴를 출력하는 함수"""
    print("\n" + "="*50)
    print("📋 To-Do Manager")
    print("="*50)
    print("1. ➕ 할일 추가 (Add)")
    print("2. 📝 할일 조회 (List)")
    print("3. ✅ 할일 완료 (Complete)")
    print("4. 🗑️  할일 삭제 (Delete)")
    print("5. 🧹 완료된 할일 정리 (Clear Done)")
    print("6. 🚪 종료 (Exit)")
    print("="*50)

def main():
    """
    메인 함수: 사용자 인터페이스 제공
    """
    print("🎉 To-Do Manager에 오신 것을 환영합니다!")
    
    # 할일 목록 로드
    todos = load_todos()
    print(f"📂 {len(todos)}개의 할일을 불러왔습니다.")
    
    while True:
        show_menu()
        
        try:
            choice = input("메뉴를 선택하세요 (1-6): ").strip()
            
            if choice == '1':
                add_todo(todos)
            elif choice == '2':
                list_todos(todos)
            elif choice == '3':
                complete_todo(todos)
            elif choice == '4':
                delete_todo(todos)
            elif choice == '5':
                clear_done_todos(todos)
            elif choice == '6':
                print("\n👋 To-Do Manager를 종료합니다. 좋은 하루 되세요!")
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