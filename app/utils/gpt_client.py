# OpenAI API 호출 래퍼
# utils/gpt_client.py
import json
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def get_insight_instruction(mode: str = "general", category_id: int = None, keyword_list: list = None) -> str:
    """카테고리에 따른 맞춤형 인사이트 프롬프트 생성"""
    # 기본 지침 (유저님의 '핵심 키워드' 스타일 반영)
    if mode == "briefing" and keyword_list:
        keywords_str = ", ".join(keyword_list)
        return (
            f"오늘의 주요 키워드({keywords_str})를 중심으로 "
            "전체 뉴스를 관통하는 핵심 흐름과 시사점을 한 줄의 인사이트로 정리하세요."
        )
    
    base_instr = "기사의 핵심 내용을 파악하여 향후 전망이나 독자가 주목해야 할 포인트를 한 문장의 '인사이트'로 제시하세요."
    
    if category_id == 1: # 예: 경제
        return f"{base_instr} 시장의 변동성이나 투자자 관점의 시사점을 포함하세요."
    elif category_id == 2: # 예: 스포츠/야구
        return f"{base_instr} 선수의 기록이나 팀 순위 경쟁에 미치는 영향을 분석하세요."
    
    return base_instr

async def get_gpt_analysis(title: str, content: str, instruction: str):
    """GPT API를 호출하여 제목, 요약, 인사이트, 키워드 추출"""
    prompt = f"""
    아래 뉴스 기사를 분석해서 JSON 형식으로 응답해줘.
    
    [지침]
    1. 제목: 기사 원제보다 더 매력적이고 직관적인 제목으로 수정
    2. 요약: 전체 내용을 3줄 이내로 핵심만 요약
    3. 인사이트: {instruction}
    4. 키워드: 기사와 관련된 핵심 단어 3~5개를 리스트로 추출
    
    [기사 제목]: {title}
    [기사 내용]: {content}
    
    응답 형식:
    {{
        "title": "수정된 제목",
        "summary": "요약 내용",
        "insight": "인사이트 내용",
        "keywords": ["키워드1", "키워드2", ...]
    }}
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)