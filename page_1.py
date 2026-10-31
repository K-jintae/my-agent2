import streamlit as st
import requests
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5.4-mini")

tavily_tool = TavilySearch(
    
    max_results=5,
    topic="general",
)

@tool
def get_exchange_rate(
    base_currency: str,
    target_currency: str,
    amount: float = 1.0,
) -> dict:
    """최신 제공 환율로 금액을 환산한다.
    통화는 USD, KRW, EUR, JPY 같은 영문 코드로 입력한다.
    """
    base = base_currency.strip().upper()
    target = target_currency.strip().upper()

    if amount < 0:
        return {"error": "금액은 0 이상이어야 합니다."}

    if base == target:
        return {
            "base": base,
            "quote": target,
            "rate": 1,
            "amount": amount,
            "converted_amount": amount,
            "note": "동일한 통화이므로 환산이 필요 없습니다.",
        }

    try:
        response = requests.get(
            f"https://api.frankfurter.dev/v2/rate/{base}/{target}",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "base": base,
            "quote": target,
            "rate": data["rate"],
            "amount": amount,
            "converted_amount": amount * data["rate"],
            "date": data["date"],
            "source": "Frankfurter",
        }

    except requests.RequestException:
        return {"error": "환율 조회에 실패했습니다. 통화 코드나 연결을 확인하세요."}
    except (ValueError, KeyError, TypeError):
        return {"error": "환율 API 응답을 해석할 수 없습니다."}

agent = create_agent(
    model,
    tools=[tavily_tool, get_exchange_rate],
    system_prompt=(
        "한국어로 답하세요. "
        "환율 조회나 통화 환산에는 get_exchange_rate 도구를 사용하세요. "
        "통화명은 USD, KRW, EUR, JPY 등의 코드로 변환하세요. "
        "기준 통화나 대상 통화가 불명확하면 사용자에게 확인하세요. "
        "답변에는 환율, 환산 결과, 기준일, 출처를 표시하세요. "
        "일별 참고 환율이므로 실시간 환율이라고 설명하지 마세요. "
        "도구가 오류를 반환하면 환율을 추측하지 말고 오류를 안내하세요."
    ),
)


if "messages" not in st.session_state :
    st.session_state.messages = []

st.title("실시간 챗봇")

prompt = st.chat_input("여기에 입력하시오.")
if prompt:
    response = agent.invoke(
        {"messages" : [{"role" : "user", "content" : prompt}]}
    )
    st.session_state.messages.append({'role' : "user", 'content' : prompt})
    st.session_state.messages.append({'role' : "ai", 'content' : response['messages'][-1].content})

for message in st.session_state.messages :
    with st.chat_message(message['role']) :
        st.write(message['content'])
