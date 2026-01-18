# app1.py
import streamlit as st
import os
import time

# 2026.py에서 체인 생성 함수 임포트
from importlib import import_module

# 숫자로 된 파일명 import 하기 위한 트릭
policy_module = import_module("2026")
create_policy_chain = policy_module.create_policy_chain

# -----------------------------------------------------------------------------
# 0. API 키 설정 (보안)
# -----------------------------------------------------------------------------
if "PPLX_API_KEY" not in os.environ:
    try:
        if "PPLX_API_KEY" in st.secrets:
            os.environ["PPLX_API_KEY"] = st.secrets["PPLX_API_KEY"]
    except FileNotFoundError:
        pass
    except Exception:
        pass

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 CSS (듀오링고 스타일 구현)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="나만의 AI 정책 해결사", page_icon="🦉", layout="wide")

st.markdown(
    """
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
    }
    
    /* 전체 배경 */
    .stApp {
        background-color: #ffffff;
    }
    
    /* 듀오링고 스타일 버튼 (3D 효과) */
    .stButton > button {
        background-color: #58cc02;
        color: white;
        border: none;
        border-radius: 16px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 800;
        border-bottom: 5px solid #46a302;
        transition: all 0.1s;
        width: 100%;
    }
    .stButton > button:active {
        border-bottom: 0px;
        transform: translateY(5px);
    }
    .stButton > button:hover {
        background-color: #61e002;
        color: white;
        border-color: #46a302;
    }

    /* 컨테이너 카드 스타일 */
    .css-card {
        border: 2px solid #e5e5e5;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        background-color: white;
        box-shadow: 0 4px 0 #e5e5e5;
    }
    
    /* 헤더 스타일 */
    .header-box {
        background-color: #1cb0f6;
        color: white;
        padding: 30px;
        border-radius: 20px;
        border-bottom: 6px solid #1899d6;
        margin-bottom: 30px;
        text-align: center;
    }
    
    /* 채팅 메시지 스타일 조정 */
    .stChatMessage {
        background-color: #f7f7f7;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }

    /* 답변 섹션 스타일 */
    .reasoning-box {
        background-color: #fff9c4;
        border: 2px solid #fbc02d;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        color: #5f4306;
    }
    .conclusion-box {
        background-color: #e1f5fe;
        border: 2px solid #039be5;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        color: #014361;
    }
    .contact-box {
        background-color: #fce4ec; /* 연한 분홍 */
        border: 2px solid #f48fb1;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        color: #880e4f;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. 사이드바 (네비게이션 & 정책 용어 사전)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🦉 정책 해결사")

    # API 키 입력
    if not os.environ.get("PPLX_API_KEY"):
        st.warning("Perplexity API 키가 필요합니다.")
        api_key_input = st.text_input("PPLX_API_KEY 입력", type="password")
        if api_key_input:
            os.environ["PPLX_API_KEY"] = api_key_input
            st.success("API 키 저장 완료!")

    st.markdown("---")

    # 정책 용어 사전 기능
    st.subheader("📚 정책 용어 사전")
    st.markdown("모르는 정책 용어가 있나요? 검색해보세요!")

    term_input = st.text_input("용어 입력", placeholder="예: 기회소득, 바우처")

    if st.button("용어 검색"):
        if not term_input:
            st.warning("용어를 입력해주세요.")
        elif not os.environ.get("PPLX_API_KEY"):
            st.error("API 키가 필요합니다.")
        else:
            with st.spinner(f"'{term_input}'의 뜻을 찾는 중..."):
                try:
                    term_chain = create_policy_chain()
                    term_prompt = f"다음 정책 용어의 뜻을 초보자도 이해하기 쉽게 3문장 이내로 명확하게 설명해줘: '{term_input}'"
                    term_definition = term_chain.invoke(
                        {"question": term_prompt, "context": "용어 사전 모드"}
                    )

                    st.success("🔍 검색 결과")
                    st.info(term_definition)
                except Exception as e:
                    st.error(f"검색 중 오류가 발생했습니다: {e}")

# -----------------------------------------------------------------------------
# 3. 메인 화면 레이아웃 (1단 컬럼)
# -----------------------------------------------------------------------------

# 헤더
st.markdown(
    """
    <div class="header-box">
        <h1>🕵️ 정책! 무엇이든 물어보살</h1>
        <p>어려운 정책 용어? 30년 경력의 담당관이 쉽게 알려드립니다!</p>
    </div>
""",
    unsafe_allow_html=True,
)

# 1. 채팅 내역 출력 (상단 위치 고정)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"], unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Context 입력 (중간 배치)
# -----------------------------------------------------------------------------
st.markdown("### 📚 1단계: 참고 자료 입력 (선택사항)")
with st.expander("여기를 눌러 정책 공문이나 자료를 입력하세요", expanded=True):
    # [중요] key를 지정하여 session_state로 참조
    st.text_area(
        "자료 내용",
        height=100,
        key="user_context_key",
        placeholder="예: 정부 공문 내용, 보도자료 텍스트 등을 여기에 붙여넣으세요.",
        help="여기에 내용을 입력하면 AI가 이 내용을 최우선으로 참고합니다.",
        label_visibility="collapsed",
    )

# -----------------------------------------------------------------------------
# 3. 사용자 입력 처리 (st.form을 사용하여 위치 제어)
# -----------------------------------------------------------------------------
st.markdown("### 💬 2단계: 질문하기")

# [수정 핵심] st.chat_input(하단 고정) 대신 st.form 사용
with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([6, 1])

    with col_input:
        user_input = st.text_input(
            "질문 입력",
            placeholder="궁금한 정책을 물어보세요! (예: 올해 육아휴직 급여가 올랐나요?)",
            label_visibility="collapsed",
        )

    with col_btn:
        submit_button = st.form_submit_button("전송 🚀")

# -----------------------------------------------------------------------------
# 4. 답변 생성 로직 (폼 제출 시 실행)
# -----------------------------------------------------------------------------
if submit_button and user_input:
    # API 키 확인
    if not os.environ.get("PPLX_API_KEY"):
        st.error("⚠️ 먼저 사이드바에서 Perplexity API 키를 입력해주세요.")
        st.stop()

    # 사용자 메시지 표시 (즉시 추가)
    st.session_state.messages.append(
        {"role": "user", "content": user_input, "avatar": "👤"}
    )
    # 폼 제출 후 리런되므로 메시지를 다시 그려주는 로직이 위(1번 섹션)에 있어서 자동 반영됨
    # 다만, 즉각적인 반응을 위해 여기서도 한번 그려줄 수 있으나, Streamlit 특성상 리런됨.
    # 여기서는 force-rerun을 하지 않고 자연스럽게 처리.

    # 답변 생성 시작 (빈 박스 생성)
    with st.chat_message("assistant", avatar="🧑‍💼"):
        message_placeholder = st.empty()
        full_response = ""

        with st.spinner("정책 담당관이 관련 법령과 자료를 검토 중입니다... 🧐"):
            try:
                # Backend 연결
                chain = create_policy_chain()

                # Context 가져오기
                user_context_val = st.session_state.get("user_context_key", "")
                final_context = (
                    user_context_val
                    if user_context_val
                    else "제공된 Context 없음. 외부 지식(검색)을 활용하여 답변할 것."
                )

                # 스트리밍 답변
                response_stream = chain.stream(
                    {"question": user_input, "context": final_context}
                )

                for chunk in response_stream:
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")

                # 최종 출력 정리 및 연락처 추가
                if "### 1. 상세 검토" in full_response:
                    parts = full_response.split("### 2. 결론 및 요약")
                    reasoning_part = (
                        parts[0].replace("### 1. 상세 검토 (Reasoning)", "").strip()
                    )
                    conclusion_part = (
                        parts[1].replace("(Conclusion)", "").strip()
                        if len(parts) > 1
                        else ""
                    )

                    formatted_html = f"""
                    <div class="reasoning-box">
                        <strong>🤔 상세 검토 (Reasoning)</strong><br><br>
                        {reasoning_part}
                    </div>
                    <div class="conclusion-box">
                        <strong>💡 결론 및 요약</strong><br><br>
                        {conclusion_part}
                    </div>
                    <div class="contact-box">
                        <strong>📞 추가 문의처</strong><br><br>
                        궁금한 점이 더 있으시다면 아래로 연락주세요.<br>
                        - <strong>정부민원안내 콜센터:</strong> 국번없이 110<br>
                        - <strong>보건복지상담센터:</strong> 국번없이 129<br>
                        <span style="font-size: 0.9em; color: #666;">(상세 부서 연락처는 관련 부처 홈페이지를 참고해주세요)</span>
                    </div>
                    """
                    message_placeholder.markdown(formatted_html, unsafe_allow_html=True)
                    # 세션 저장
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": formatted_html,
                            "avatar": "🧑‍💼",
                        }
                    )
                else:
                    # 형식 불일치 시
                    full_response_with_contact = (
                        full_response
                        + """
                    <br><br>
                    <div class="contact-box">
                        <strong>📞 추가 문의처</strong><br>
                        정부민원안내 콜센터: 110
                    </div>
                    """
                    )
                    message_placeholder.markdown(
                        full_response_with_contact, unsafe_allow_html=True
                    )
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": full_response_with_contact,
                            "avatar": "🧑‍💼",
                        }
                    )

                # 답변 완료 후 페이지 리런하여 대화 내역 갱신 (선택 사항이나 폼 동작 매끄럽게 하기 위함)
                st.rerun()

            except Exception as e:
                error_msg = f"죄송합니다. 오류가 발생했습니다.\n\n`{str(e)}`"
                message_placeholder.error(error_msg)
