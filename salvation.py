import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup

# secrets.toml에서 API 키 가져오기
api_key = ""#st.secrets["OPENAI_API_KEY"]

# OpenAI API 키 설정
openai.api_key = api_key

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

st.title('CONCHURY')
#st.markdown(f'')

#참고 사이트
url = "https://www.visitsuwon.or.kr/base/board/list?boardManagementNo=7&menuLevel=2&menuNo=70"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
page_content = soup.find("div", class_="gallery-board").text
url = "https://www.visitsuwon.or.kr/base/contents/view?contentsNo=13&menuLevel=3&menuNo=21"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
page_content2 = soup.find("div", class_="sub-contents__bottom").text



if "language_selected" not in st.session_state:
    st.session_state.language_selected = False

if not st.session_state.language_selected:
    # 언어 선택을 위한 옵션 목록
    languages = [
        "English", "Korean", "Spanish", "French", "German", "Italian", "Chinese", 
        "Japanese", "Russian", "Arabic", "Portuguese", "Hindi", "Turkish", "Dutch", 
        "Swedish", "Greek", "Polish", "Danish", "Norwegian", "Finnish", "Czech"
    ]

    # 사용자에게 언어 선택을 받음
    selected_language = st.selectbox("Choose your language", languages)

    # 확인 버튼을 누르면 선택된 언어 저장하고 화면 전환
    if st.button("check"):
        # 선택된 언어를 세션 상태에 저장
        st.session_state.selected_language = selected_language
        st.session_state.language_selected = True
        # 언어 선택 후 다른 화면을 보여줍니다.
else:
    #st.markdown(st.session_state.selected_language) #언어 표시
    # 시스템 메시지 정의
    system_message = f'''
    Your name is ConchuryBot.
    You should be able to introduce Hwaseong Haenggung in Suwon to foreign visitors,
    recommending courses or explaining tourist attractions,
    and always respond in {st.session_state.selected_language} no matter what language is used.
    Also, occasionally use an emoticon at the end of the sentence.
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

    #봇 시작 메시지
    response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "user", "content": f"hello! ConchuryBot, Introduce yourself Respond in {st.session_state.selected_language} "}
            ]
        )

    start_message = response["choices"][0]["message"]["content"]

    # 여행 코스 표시
    with st.chat_message("assistant"):
        st.markdown(start_message)

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

    # 여행 코스 짜기 버튼
    if st.session_state.selected_language == "English":
        button_text = "Create Travel Itinerary"
    elif st.session_state.selected_language == "Korean":
        button_text = "여행 코스 짜기"
    # 다른 언어를 추가하려면 여기서 조건을 더 추가
    else:
        button_text = "Create Travel Itinerary"
    if st.button(button_text):
        #with st.chat_message("user"):
        #    st.markdown("여행 코스를 짜주세요!")

        # GPT 요청 메시지 생성
        travel_prompt = f"Create a travel itinerary for Hwaseong Fortress based on {page_content} and {page_content2} First, ask what time slots are available and which one they would like to choose." #

        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": travel_prompt}
            ]
        )

        travel_plan = response["choices"][0]["message"]["content"]

        # 여행 코스 표시
        with st.chat_message("assistant"):
            st.markdown(travel_plan)