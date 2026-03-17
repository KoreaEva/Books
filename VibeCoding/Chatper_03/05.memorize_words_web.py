import json
import os
import random
from datetime import datetime, date, timedelta
import streamlit as st

# 단어장 데이터 파일
VOCAB_FILE = "vocab.json"

# Leitner 시스템: box별 복습 주기 (일)
LEITNER_INTERVALS = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}


def load_vocab():
    try:
        if os.path.exists(VOCAB_FILE):
            with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError):
        return []


def save_vocab(vocab_list):
    try:
        with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
            json.dump(vocab_list, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def get_next_id(vocab_list):
    if not vocab_list:
        return 1
    return max(w['id'] for w in vocab_list) + 1


def calculate_next_review(box_level):
    days_to_add = LEITNER_INTERVALS.get(box_level, 1)
    return (date.today() + timedelta(days=days_to_add)).isoformat()


def is_due_for_review(word):
    if not word.get('last_review'):
        return True
    if not word.get('next_review'):
        return True
    try:
        return date.today() >= datetime.fromisoformat(word['next_review']).date()
    except Exception:
        return True


def get_box_emoji(box_level):
    return {1: '📦', 2: '📋', 3: '📚', 4: '🎯', 5: '🏆'}.get(box_level, '❓')


def check_answer(correct_meaning, user_answer):
    if not user_answer:
        return False
    correct = correct_meaning.replace(' ', '').replace(',', '').replace('，', '').lower()
    user = user_answer.replace(' ', '').replace(',', '').replace('，', '').lower()
    if correct == user:
        return True
    if correct in user or user in correct:
        return True
    if ',' in correct_meaning or '，' in correct_meaning:
        parts = correct_meaning.replace('，', ',').split(',')
        for p in parts:
            pclean = p.strip().replace(' ', '').lower()
            if pclean == user or pclean in user or user in pclean:
                return True
    return False


def add_word_action(vocab_list, word, meaning, example):
    word = (word or '').strip().lower()
    meaning = (meaning or '').strip()
    example = (example or '').strip() or None
    if not word or not meaning:
        return False, '단어와 뜻을 입력하세요.'
    for w in vocab_list:
        if w['word'].lower() == word:
            return False, '이미 등록된 단어입니다.'
    new_word = {
        'id': get_next_id(vocab_list),
        'word': word,
        'meaning': meaning,
        'example': example,
        'box': 1,
        'created_at': datetime.now().isoformat(),
        'last_review': None,
        'next_review': None,
        'correct_streak': 0,
        'wrong_streak': 0,
    }
    vocab_list.append(new_word)
    if save_vocab(vocab_list):
        return True, '단어가 추가되었습니다. 새 단어는 바로 퀴즈에 출제됩니다.'
    return False, '단어 저장에 실패했습니다.'


def mark_answer(vocab_list, word_id, is_correct):
    for w in vocab_list:
        if w['id'] == word_id:
            if is_correct:
                w['correct_streak'] = w.get('correct_streak', 0) + 1
                w['wrong_streak'] = 0
                w['box'] = min(w.get('box', 1) + 1, 5)
            else:
                w['wrong_streak'] = w.get('wrong_streak', 0) + 1
                w['correct_streak'] = 0
                w['box'] = 1
            w['last_review'] = datetime.now().isoformat()
            w['next_review'] = calculate_next_review(w['box'])
            return save_vocab(vocab_list)
    return False


def delete_word_by_id(vocab_list, word_id):
    for i, w in enumerate(vocab_list):
        if w['id'] == word_id:
            deleted = vocab_list.pop(i)
            if save_vocab(vocab_list):
                return True, f"삭제되었습니다: {deleted['word']}"
            vocab_list.insert(i, deleted)
            return False, '삭제 중 오류 발생'
    return False, '해당 ID를 찾을 수 없습니다.'


def clear_session_quiz():
    for k in list(st.session_state.keys()):
        if k.startswith('quiz_'):
            del st.session_state[k]


def main():
    st.set_page_config(page_title='단어 암기장 (Leitner)', layout='wide')
    st.title('📚 영어 단어 암기장 (Leitner System)')

    if 'vocab' not in st.session_state:
        st.session_state.vocab = load_vocab()

    vocab = st.session_state.vocab

    # Sidebar for actions
    st.sidebar.header('Actions')
    action = st.sidebar.selectbox('기능 선택', options=['학습(Quiz)', '단어 추가', '단어 목록', '단어 삭제', '통계'])
    st.sidebar.markdown('---')
    if st.sidebar.button('저장된 파일 새로고침'):
        st.session_state.vocab = load_vocab()
        st.experimental_rerun()

    # Layout: main area
    if action == '단어 추가':
        st.header('➕ 단어 추가')
        with st.form('add_word'):
            word = st.text_input('영어 단어')
            meaning = st.text_input('한국어 뜻')
            example = st.text_input('예문 (선택)')
            submitted = st.form_submit_button('추가')
            if submitted:
                ok, msg = add_word_action(vocab, word, meaning, example)
                if ok:
                    st.success(msg)
                    st.session_state.vocab = vocab
                    clear_session_quiz()
                else:
                    st.error(msg)

    elif action == '단어 목록':
        st.header('📝 단어 목록')
        view = st.radio('보기', options=['전체', '오늘 복습할 단어'], index=1, horizontal=True)
        if view == '전체':
            filtered = sorted(vocab, key=lambda x: (x.get('box', 1), x['id']))
        else:
            filtered = [w for w in vocab if is_due_for_review(w)]

        st.write(f'총 {len(filtered)}개')
        for w in filtered:
            cols = st.columns([0.02, 0.7, 0.28])
            cols[0].markdown(get_box_emoji(w.get('box', 1)))
            title = f"**{w.get('word','').upper()}** — {w.get('meaning','')}"
            meta = f"박스: {w.get('box',1)} | 정답: {w.get('correct_streak',0)} | 오답: {w.get('wrong_streak',0)}"
            if w.get('next_review'):
                meta += f" | 다음복습: {w.get('next_review')[:10]}"
            cols[1].markdown(title + "\n\n" + (w.get('example') or ''))
            cols[2].markdown(meta)
            st.markdown('---')

    elif action == '단어 삭제':
        st.header('🗑️ 단어 삭제')
        if not vocab:
            st.info('단어장이 비어 있습니다.')
        else:
            options = [f"{w['id']}: {w['word']} - {w['meaning']}" for w in vocab]
            selection = st.selectbox('삭제할 단어 선택', options=options)
            if st.button('삭제'):
                word_id = int(selection.split(':', 1)[0])
                ok, msg = delete_word_by_id(vocab, word_id)
                if ok:
                    st.success(msg)
                    st.session_state.vocab = vocab
                    clear_session_quiz()
                    st.experimental_rerun()
                else:
                    st.error(msg)

    elif action == '통계':
        st.header('📊 통계')
        total = len(vocab)
        due = len([w for w in vocab if is_due_for_review(w)])
        new = len([w for w in vocab if not w.get('last_review')])
        st.write(f'총 단어: {total}개')
        st.write(f'오늘 복습할 단어: {due}개')
        st.write(f'새 단어: {new}개')

        # box distribution
        box_counts = {i: 0 for i in range(1, 6)}
        for w in vocab:
            box_counts[w.get('box', 1)] += 1
        st.bar_chart(list(box_counts.values()))
        for b, c in box_counts.items():
            st.write(f"{get_box_emoji(b)} 박스 {b}: {c}개")

    else:  # Quiz
        st.header('🎯 단어 퀴즈')
        due_words = [w for w in vocab if is_due_for_review(w)]
        if not due_words:
            st.info('🎉 오늘 복습할 단어가 없습니다! 단어를 추가하세요.')
        else:
            # initialize quiz session
            if 'quiz_list' not in st.session_state:
                qlist = due_words.copy()
                random.shuffle(qlist)
                st.session_state.quiz_list = qlist
                st.session_state.quiz_idx = 0
                st.session_state.quiz_correct = 0
                st.session_state.quiz_total = 0

            idx = st.session_state.quiz_idx
            if idx >= len(st.session_state.quiz_list):
                st.success(f"퀴즈 완료! 정답: {st.session_state.quiz_correct}/{st.session_state.quiz_total}")
                if st.button('다시 시작'):
                    clear_session_quiz()
                    st.experimental_rerun()
            else:
                current = st.session_state.quiz_list[idx]
                st.subheader(f"문제 {idx+1}/{len(st.session_state.quiz_list)}")
                st.write(f"단어: **{current['word'].upper()}**")
                if current.get('example'):
                    st.write(f"예문: {current['example']}")

                answer = st.text_input('뜻을 입력하세요', key=f'answer_{current["id"]}')
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button('제출', key=f'submit_{current["id"]}'):
                        st.session_state.quiz_total += 1
                        is_corr = check_answer(current['meaning'], answer)
                        if is_corr:
                            st.session_state.quiz_correct += 1
                            st.success('정답입니다!')
                        else:
                            st.error(f"오답입니다. 정답: {current['meaning']}")
                        mark_answer(vocab, current['id'], is_corr)
                        st.session_state.quiz_idx += 1
                        st.session_state.vocab = vocab
                        st.experimental_rerun()
                with col2:
                    if st.button('포기 (정답 보기)', key=f'skip_{current["id"]}'):
                        st.session_state.quiz_total += 1
                        st.error(f"정답: {current['meaning']}")
                        mark_answer(vocab, current['id'], False)
                        st.session_state.quiz_idx += 1
                        st.session_state.vocab = vocab
                        st.experimental_rerun()
                with col3:
                    if st.button('퀴즈 종료', key='quit_quiz'):
                        st.info('퀴즈를 종료합니다.')
                        clear_session_quiz()


if __name__ == '__main__':
    main()
