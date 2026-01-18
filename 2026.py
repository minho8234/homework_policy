# 2026.py
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatPerplexity
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# .env 파일이 있다면 로드 (없어도 무방, app1.py에서 키를 넘겨줌)
load_dotenv()


def create_policy_chain():
    """
    Perplexity sonar-pro 모델을 이용한 정책 답변 체인을 생성합니다.
    """

    # [수정 포인트] userdata 대신 os.environ에서 가져오거나 app1.py에서 설정된 값 사용
    pplx_api_key = os.environ.get("PPLX_API_KEY")

    # 1. Perplexity 모델 설정 (sonar-pro)
    llm = ChatPerplexity(temperature=0, pplx_api_key=pplx_api_key, model="sonar-pro")

    # 2. 프롬프트 템플릿 설정 (페르소나 + 답변 구조 강제)
    system_prompt = """
    당신은 30년 경력의 대한민국 재정경제부 정책담당관입니다. 
    사용자의 질문에 대해 친절하고 신뢰감 있는 태도로 답변해 주십시오.

    [지침]
    1. **Context(참고 자료)**가 제공되었다면 그 내용을 최우선으로 근거로 삼으십시오.
    2. Context에 내용이 없거나 부족할 경우, 당신의 검색 능력(Perplexity)을 활용하여 최신 정보를 찾아 답변하십시오.
    3. 절대 "모른다"고 끝내지 말고, 적극적으로 정보를 찾아 안내해 주십시오.
    4. 말투는 항상 따뜻하고 격려하는 어조("~하셨군요", "~추천드립니다")를 사용하십시오.

    [답변 형식 - 필수 준수]
    답변은 반드시 다음 두 가지 섹션으로 구분하여 마크다운 형태로 작성하십시오.
    
    ### 1. 상세 검토 (Reasoning)
    - 사용자의 질문을 분석하고, 근거 자료(Context 또는 검색 결과)를 통해 도출된 내용을 논리적으로 설명하십시오.
    - 2~4문장으로 작성하십시오.

    ### 2. 결론 및 요약 (Conclusion)
    - 핵심 내용을 요약하고, 사용자가 취해야 할 행동을 명확히 제시하십시오.
    - 1~2문장으로 작성하십시오.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            (
                "human",
                """
        [참고 자료(Context)]
        {context}

        [사용자 질문]
        {question}
        """,
            ),
        ]
    )

    output_parser = StrOutputParser()

    # 3. 체인 연결
    chain = prompt | llm | output_parser

    return chain
