import streamlit as st
import pandas as pd
import os
from quiz import *

st.set_page_config(
    page_title="KW-oss-quizApp",
    # layout="wide",
    # initial_sidebar_state="expanded"
)

# ========== 로그인 관리 =========

id_pw = {
    'id': 'pw',
    'abcd': '1234',
    'heewoo':'1234'
}

if 'login' not in st.session_state:
    st.session_state['login'] = False

# ========== 로그인 로직 구현 ==========

if not st.session_state['login']:
    # =============================
    # 로그인 상태가 False일 때 화면
    # =============================
    st.title('오픈소스소프트웨어 Streamlit 실습')
    st.markdown('### 2023204065 김희우')

    col1, col2 = st.columns([1, 3])
    with col1:
        id = st.text_input('id를 입력하세요')
        pw = st.text_input('password를 입력하세요')
        login = st.button('로그인')
        
    if login:
        if id in id_pw.keys() and id_pw[id] == pw:
            st.session_state['login'] = True
            st.session_state['user_id'] = id
            st.rerun()
        else:
            st.error('아이디와 비밀번호를 확인해주세요.')
else:
    # ===================================
    # 로그인 상태가 True일 때 화면 - 퀴즈
    # ===================================
    init_session_state()
    
    col1, col2 = st.columns([8,1])
    with col2:
        if st.button('logout'):
            st.session_state['login'] = False
            st.session_state['user_id'] = None
            reset_quiz()
            st.rerun()

    with col1:
        if st.session_state['difficulty'] is None:
            st.title('문제 난이도를 선택해주세요.')
            col1, col2 = st.columns(2)
            with col1:
                if st.button('기본 문제'):
                    st.session_state['difficulty'] = 'basic'
                    st.rerun()
            with col2:
                if st.button('심화 문제'):
                    st.session_state['difficulty'] = 'hard'
                    st.rerun()

            try:
                df_records = pd.read_csv('user_records.csv')
                user_data = df_records[df_records['user_id'] == st.session_state['user_id']]
                if not user_data.empty:
                    st.divider()
                    st.subheader('내 문제 풀이 기록')

                    basic_data = user_data[user_data['difficulty'] == 'basic']['score'].reset_index(drop=True)
                    hard_data = user_data[user_data['difficulty'] == 'hard']['score'].reset_index(drop=True)

                    chart_data = pd.DataFrame({
                        '기본 문제': basic_data,
                        '심화 문제': hard_data
                    })
                    chart_data.index = range(1, len(chart_data) + 1)
                    st.line_chart(chart_data)
            except Exception:
                pass
        else:
            df_questions = load_data(st.session_state['difficulty'])

            if st.session_state['review_mode']:
                show_review(df_questions)
            else:
                start_quiz(st.session_state['difficulty'])