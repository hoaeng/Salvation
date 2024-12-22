import streamlit as st
import openai

# secrets.toml에서 API 키 가져오기
api_key = ""#st.secrets["OPENAI_API_KEY"]

# OpenAI API 키 설
openai.api_key = api_key

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

st.title('CONCHURY')
#st.markdown(f'')

# 시스템 메시지 정의
system_message = '''
Your name is ConchuryBot.
You should focus on the differences between Korean culture and other cultures, using any language.
Occasionally, use an emoticon at the end of the sentence.
'''

if "messages" not in st.session_state:
    st.session_state.messages = []

# 초기 메시지 설정
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "system", "content": system_message})



# 이전 메시지 표시
for idx, message in enumerate(st.session_state.messages):
    if idx > 0:  # 시스템 메시지는 제외
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("What is up?"):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GPT 응답 생성 및 스트리밍
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # OpenAI API 호출
        for chunk in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=st.session_state.messages,
            stream=True,  # 스트리밍 활성화
        ):
            chunk_content = chunk["choices"][0]["delta"].get("content", "")
            full_response += chunk_content
            message_placeholder.markdown(full_response + "▌")  # 실시간 표시

        message_placeholder.markdown(full_response)  # 최종 응답 표시

    # 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})
