import streamlit as st
from rag_engine import generate_answer

st.title("🏍️ 機車保險知識型助手 (RAG)")

query = st.text_input("請輸入你的問題：")

if st.button("詢問"):
    if query.strip() != "":
        with st.spinner("AI 正在思考..."):
            answer = generate_answer(query)
        st.markdown("**回答:**")
        st.write(answer)
    else:
        st.warning("請輸入問題！")
