import json
import os
from datetime import datetime
import streamlit as st

# 할일 데이터 파일 경로 (앱 폴더에 저장)
TODO_FILE = "todos.json"


def load_todos():
    """Load todos from JSON file. Returns a list."""
    try:
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError):
        return []


def save_todos(todos):
    """Save todos list to JSON file."""
    try:
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def get_next_id(todos):
    if not todos:
        return 1
    return max(todo['id'] for todo in todos) + 1


def get_priority_emoji(priority):
    emojis = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🔵"}
    return emojis.get(priority, "⚪")


def format_date(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except Exception:
        return date_str


def add_todo_cli_style(todos, text, due, priority):
    new_todo = {
        'id': get_next_id(todos),
        'text': text,
        'created_at': datetime.now().isoformat(),
        'due': due if due else None,
        'priority': priority,
        'done': False,
        'done_at': None,
    }
    todos.append(new_todo)
    saved = save_todos(todos)
    return saved


def mark_complete(todos, todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            if not todo['done']:
                todo['done'] = True
                todo['done_at'] = datetime.now().isoformat()
                return save_todos(todos)
            return False
    return False


def delete_todo_by_id(todos, todo_id):
    for i, todo in enumerate(todos):
        if todo['id'] == todo_id:
            todos.pop(i)
            return save_todos(todos)
    return False


def clear_done_todos_action(todos):
    remaining = [t for t in todos if not t.get('done')]
    if len(remaining) == len(todos):
        return False
    saved = save_todos(remaining)
    if saved:
        todos.clear()
        todos.extend(remaining)
    return saved


def main():
    st.set_page_config(page_title="To-Do Manager", layout="wide")
    st.title("📋 To-Do Manager (Streamlit)")

    # Load todos once into session state
    if 'todos' not in st.session_state:
        st.session_state.todos = load_todos()

    todos = st.session_state.todos

    # Left column: add / actions
    left, right = st.columns([1, 2])

    with left:
        st.header("➕ Add To-Do")
        with st.form(key='add_form'):
            text = st.text_input('할일 내용을 입력하세요')
            due = st.date_input('마감일 (선택)', value=None)
            priority = st.selectbox('우선순위', options=[1,2,3,4,5], index=2, format_func=lambda v: f"{v} {get_priority_emoji(v)}")
            submitted = st.form_submit_button('추가')

            if submitted:
                due_str = None
                # st.date_input returns a date object even if empty in older streamlit; handle when not set
                try:
                    if due:
                        due_str = due.isoformat()
                except Exception:
                    due_str = None

                if not text.strip():
                    st.error('할일 내용을 입력해야 합니다.')
                else:
                    if add_todo_cli_style(todos, text.strip(), due_str, int(priority)):
                        st.success('할일이 추가되었습니다.')
                    else:
                        st.error('할일 저장에 실패했습니다.')

        st.markdown('---')
        st.header('Actions')
        if st.button('완료된 항목 모두 삭제'):
            if clear_done_todos_action(todos):
                st.success('완료된 항목이 모두 삭제되었습니다.')
            else:
                st.info('삭제할 완료된 항목이 없습니다.')

        if st.button('새로고침'):
            st.session_state.todos = load_todos()
            st.experimental_rerun()

    # Right column: list and manage
    with right:
        st.header('📝 To-Do List')

        filter_option = st.radio('Filter', options=['전체', '미완료', '완료'], index=0, horizontal=True)

        if filter_option == '전체':
            filtered = todos
        elif filter_option == '미완료':
            filtered = [t for t in todos if not t.get('done')]
        else:
            filtered = [t for t in todos if t.get('done')]

        # sort: not-done first, higher priority first, earliest due first
        def sort_key(x):
            return (x.get('done', False), -int(x.get('priority', 3)), x.get('due') or '9999-12-31')

        filtered = sorted(filtered, key=sort_key)

        st.write(f'총 {len(filtered)}개')

        for todo in filtered:
            cols = st.columns([0.05, 0.7, 0.25, 0.2])
            done_cb = cols[0].checkbox('', value=todo.get('done', False), key=f'done-{todo["id"]}')

            title = f"{get_priority_emoji(todo.get('priority',3))} {todo.get('text')}"
            meta = f"생성: {format_date(todo.get('created_at'))}"
            if todo.get('due'):
                meta += f" | 마감: {todo.get('due')}"
            if todo.get('done') and todo.get('done_at'):
                meta += f" | 완료: {format_date(todo.get('done_at'))}"

            cols[1].markdown(f"**{title}**\n\n{meta}")

            if cols[2].button('완료', key=f'complete-{todo["id"]}'):
                if mark_complete(todos, todo['id']):
                    st.session_state.todos = todos
                    st.success('할일이 완료 처리되었습니다.')
                    st.experimental_rerun()
                else:
                    st.info('이미 완료되었거나 오류가 발생했습니다.')

            if cols[3].button('삭제', key=f'delete-{todo["id"]}'):
                if delete_todo_by_id(todos, todo['id']):
                    st.session_state.todos = todos
                    st.success('할일이 삭제되었습니다.')
                    st.experimental_rerun()
                else:
                    st.error('삭제에 실패했습니다.')

        st.markdown('---')
        st.caption('우선순위: 1(🔴) - 5(🔵)')


if __name__ == '__main__':
    main()