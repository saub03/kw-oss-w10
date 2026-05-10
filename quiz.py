import streamlit as st
import pandas as pd
import os
from datetime import datetime

@st.cache_data
def load_data(difficulty='basic'):
    if difficulty == 'hard':
        df = pd.read_csv('questions_hard.csv')
    else:
        df = pd.read_csv('questions.csv')
    return df

def init_session_state():
    if 'answered' not in st.session_state:
        st.session_state['answered'] = False
    if 'quiz_id' not in st.session_state:
        st.session_state['quiz_id'] = 0
    if 'score' not in st.session_state:
        st.session_state['score'] = 0
    if 'fail_quiz' not in st.session_state:
        st.session_state['fail_quiz'] = []
    if 'done' not in st.session_state:
        st.session_state['done'] = False
    if 'review_mode' not in st.session_state:
        st.session_state['review_mode'] = False
    if 'record_saved' not in st.session_state:
        st.session_state['record_saved'] = False
    if 'difficulty' not in st.session_state:
        st.session_state['difficulty'] = None

def start_quiz(difficulty):
    df_questions = load_data(difficulty)
    if not st.session_state['done']:
        st.progress(st.session_state['quiz_id']/len(df_questions))

        question = df_questions.iloc[st.session_state.quiz_id]
        st.subheader(f"문제{st.session_state.quiz_id + 1}. {question['question']}")
        if not st.session_state['answered']:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("O"):
                    submit_answer("O", question['answer'], question['id'])
            with col2:
                if st.button("X"):
                    submit_answer("X", question['answer'], question['id'])
        else:
            if st.session_state.get('is_correct'):
                st.success(question['why'])
            else:
                st.error(question['why'])

            if st.button('확인'):
                st.session_state['answered'] = False # 상태 초기화
                if st.session_state['quiz_id'] < len(df_questions) - 1:
                    st.session_state['quiz_id'] += 1
                else:
                    st.session_state['done'] = True
                st.rerun()

    else:
        show_result(len(df_questions), df_questions)

def submit_answer(choice, answer, quiz_id):
    st.session_state['answered'] = True
    if choice == answer:
        st.session_state['score'] += 1
        st.session_state['is_correct'] = True
    else:
        st.session_state['is_correct'] = False
        if quiz_id not in st.session_state['fail_quiz']:
            st.session_state['fail_quiz'].append(quiz_id)
    st.rerun()

def save_record(user_id, score, total, fail_quiz, difficulty):
    record_file = 'user_records.csv'
    fail_quiz_str = ','.join(map(str, fail_quiz)) if fail_quiz else 'None'
    new_record = pd.DataFrame([{
        'user_id': user_id,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'score': score,
        'total': total,
        'fail_quiz': fail_quiz_str,
        'difficulty': difficulty
    }])
    
    if os.path.exists(record_file):
        new_record.to_csv(record_file, mode='a', header=False, index=False)
    else:
        new_record.to_csv(record_file, mode='w', header=True, index=False)

def show_result(df_len, df_questions):
    st.balloons()
    st.header('퀴즈를 모두 풀었습니다!')
    
    score = st.session_state['score']
    st.subheader(f"당신의 점수는: {int(score/df_len * 100)}점 입니다")
    
    if not st.session_state['record_saved']:
        save_record(st.session_state.get('user_id', 'unknown'), score, df_len, st.session_state['fail_quiz'], st.session_state.get('difficulty'))
        st.session_state['record_saved'] = True
    
    if st.session_state['fail_quiz']:
        st.info(f'틀린 문제 {len(st.session_state["fail_quiz"])}개를 복습할 수 있습니다!')
        if st.button('복습하기'):
            st.session_state['review_mode'] = True
            st.rerun()
    else:
        st.info('모든 문제를 맞췄습니다!')
        
    if st.button('처음부터 다시 풀기'):
        reset_quiz()
        st.rerun()

def show_review(df_questions):
    st.title('틀린 문제 복습하기')
    df_wrong = df_questions[df_questions['id'].isin(st.session_state['fail_quiz'])]
    if df_wrong.empty:
        st.info('틀린 문제가 없습니다!')
    else:
        # iterrows()를 사용해 데이터프레임의 행을 하나씩 반복하며 출력
        for idx, question in df_wrong.iterrows():
            with st.expander(f"문제: {question['question']}", expanded=True):
                st.write(f"**정답:** {question['answer']}")
                st.info(f"**해설:** {question['why']}")
    if st.button('처음부터 다시 풀기'):
        reset_quiz()
        st.rerun()


def reset_quiz():
    st.session_state['review_mode'] = False
    st.session_state['quiz_id'] = 0
    st.session_state['score'] = 0
    st.session_state['fail_quiz'] = []
    st.session_state['done'] = False
    st.session_state['record_saved'] = False
    st.session_state['difficulty'] = None