import streamlit as st

# --- 페이지 설정 ---
st.set_page_config("공식 노트", page_icon='💾')
st.badge(":material/star_shine: New Web Page!", color="blue")
st.title(":material/book_2: 공식 노트")

# --- 세션 상태 초기화 ---
if "subjects" not in st.session_state:
    st.session_state.subjects = ["수학", "화학", "물리"]

if "cards" not in st.session_state or not isinstance(st.session_state.cards, dict):
    st.session_state.cards = {subj: [] for subj in st.session_state.subjects}

if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0

if "highlighted" not in st.session_state:
    st.session_state.highlighted = ""  # 강조 카드 저장

if "active_tab_subject" not in st.session_state:
    st.session_state.active_tab_subject = None  # None이면 모든 탭 표시

# --- CSS: 다크/라이트 모드 강조 카드 스타일 ---
st.markdown("""
<style>
@media (prefers-color-scheme: dark) {
    .highlight-card {
        background-color: #01598f;
        color: white;
        padding: 5px;
        border-radius: 5px;
    }
}
@media (prefers-color-scheme: light) {
    .highlight-card {
        background-color: #FFD700;
        color: black;
        padding: 5px;
        border-radius: 5px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- 입력란 ---
st.subheader(":material/Edit: 공식 입력")
key_front = f"front_{st.session_state.input_counter}"
key_back = f"back_{st.session_state.input_counter}"

front = st.text_input("문제 / 공식 제목", key=key_front)
back = st.text_area("답 / 공식 입력", key=key_back)
use_latex = st.checkbox("LaTeX 사용", value=True)

if back:
    st.caption("미리보기:")
    if use_latex:
        st.latex(back)
    else:
        st.text(back)

# 저장 버튼 + 과목 선택
if st.session_state.subjects:
    selected_subject = st.selectbox("저장할 과목 선택: ", st.session_state.subjects)
    if st.button(":material/note_add: 저장"):
        if front and back:
            st.session_state.cards[selected_subject].append((front, back, use_latex))
            st.success(f"'{front}' 공식이 '{selected_subject}' 과목에 저장되었습니다!")
            st.session_state.input_counter += 1
        else:
            st.warning("저장할 공식이 없습니다. 입력란을 확인하세요.")
else:
    st.warning("과목이 없습니다. 새 과목을 먼저 추가하세요.")

st.divider()

# --- 새 과목 추가 ---
new_subject = st.text_input(":material/add: 새 과목 추가")
if st.button("과목 추가"):
    if new_subject and new_subject not in st.session_state.subjects:
        st.session_state.subjects.append(new_subject)
        st.session_state.cards[new_subject] = []
        st.success(f"'{new_subject}' 과목 추가 완료!")

st.divider()

# --- 사이드바 ---
st.sidebar.header(":material/search: 공식 검색")
search_subject = st.sidebar.selectbox("검색할 과목 선택", ["전체"] + st.session_state.subjects)
search_query = st.sidebar.text_input("검색어 입력")

if search_query:
    st.sidebar.write("검색 결과:")
    found = False
    for subj, cards in st.session_state.cards.items():
        if search_subject != "전체" and subj != search_subject:
            continue
        for idx, (f, b, latex_flag) in enumerate(cards):
            if search_query.lower() in f.lower() or search_query.lower() in b.lower():
                found = True
                st.sidebar.markdown(f"**[{subj}]** {f}")
                if latex_flag:
                    st.sidebar.latex(b)
                else:
                    st.sidebar.text(b)
                # 강조 버튼 (탭 열기 + 강조)
                if st.sidebar.button(":material/search: 찾기", key=f"jump_{subj}_{idx}", type="tertiary"):
                    st.session_state.highlighted = f"{subj} - {f}"      # 강조 카드
                    st.session_state.active_tab_subject = subj           # 해당 탭만 표시
                    st.query_params = {"highlight": f"{subj} - {f}"}    # URL 반영
    if not found:
        st.sidebar.info("검색 결과가 없습니다.")
else:
    st.sidebar.caption("검색어를 입력하면 결과가 여기에 표시됩니다.")

# --- 모든 탭 보기 버튼 ---
if st.session_state.active_tab_subject:
    if st.sidebar.button(":material/view_list: 모든 탭 보기"):
        st.session_state.active_tab_subject = None  # 모든 탭 표시
        st.session_state.highlighted = ""           # 강조 해제
        st.rerun()                    # 페이지 새로고침


# 과목별 카드 개수 요약
st.sidebar.header(":material/Equalizer: 과목별 카드 개수")
if st.session_state.subjects:
    for subj in st.session_state.subjects:
        st.sidebar.write(f"- {subj}: {len(st.session_state.cards[subj])}개")
else:
    st.sidebar.info("등록된 과목이 없습니다.")
st.sidebar.divider()


# --- 탭별 카드 확인 + 삭제 ---
st.subheader(":material/view_list: 저장된 카드 확인")
display_subjects = [st.session_state.active_tab_subject] if st.session_state.active_tab_subject else st.session_state.subjects

tabs = st.tabs(display_subjects)
for tab, subj in zip(tabs, display_subjects):
    with tab:
        col_subject, col_btn = st.columns([0.9, 0.1])
        with col_subject:
            st.write(f":material/book: {subj} 과목")
        with col_btn:
            if st.button(":material/delete:", key=f"del_subject_{subj}", type="tertiary"):
                st.session_state.subjects.remove(subj)
                st.session_state.cards.pop(subj, None)
                st.success(f"'{subj}' 과목이 삭제되었습니다.")
                st.rerun()

        cards = st.session_state.cards.get(subj, [])
        if cards:
            highlight = st.session_state.get("highlighted", "")
            if not highlight:
                highlight = st.query_params.get("highlight", [""])[0]

            for i, (f, b, latex_flag) in enumerate(cards):
                is_highlighted = highlight == f"{subj} - {f}"

                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    if is_highlighted:
                        st.markdown(
                            f"<div class='highlight-card'>{i+1}. {f}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.write(f"{i+1}. {f}")

                    if latex_flag:
                        st.latex(b)
                    else:
                        st.text(b)

                with col2:
                    if st.button(":material/delete:", key=f"del_{subj}_{i}", type="tertiary"):
                        st.session_state.cards[subj].pop(i)
                        st.rerun()


#[theme]
#base="dark"
#primaryColor="#487bd8"
#secondaryBackgroundColor="#393946"
#이거 넣기