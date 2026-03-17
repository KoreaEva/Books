import streamlit as st

st.title("Hello, Streamlit!")
st.write("이것은 Streamlit으로 만든 아주 간단한 웹앱이다.")

name = st.text_input("이름을 입력해 주세요:", value="홍길동")

if st.button("인사하기"):
   st.success(f"{name}님, 또 오셨네요 반가워요!")