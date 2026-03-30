# OpenAI API 호출 래퍼
# utils/gpt_client.py
import json
from openai import AsyncOpenAI
from app.core.config import settings
from typing import Optional
from app.core.enums import Category
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def get_insight_instruction(mode: str = "general", category_id: int = None, keyword_list: list = None) -> Optional[str]:
    """카테고리에 따른 맞춤형 인사이트 프롬프트 생성 (정치, 경제, IT/과학 한정)"""
    
    # 1. 브리핑 모드 지침
    if mode == "briefing" and keyword_list:
        keywords_str = ", ".join(keyword_list)
        return (
            f"오늘의 주요 키워드({keywords_str})를 중심으로 "
            "전체 뉴스를 관통하는 핵심 흐름과 시사점을 한 줄의 인사이트로 정리하세요."
        )
    
    # 2. 인사이트 추출 대상 카테고리 정의 (Enum 사용)
    # 만약 category_id가 DB에서 꺼낸 숫자라면, Category(category_id)로 변환해서 비교하는 것이 안전합니다.
    TARGET_CATEGORIES = [Category.POLITICS, Category.ECONOMY, Category.TECH_SCIENCE]
    
    # 입력받은 id가 Enum에 정의된 값인지 확인 (타입에 따라 변환이 필요할 수 있음)
    try:
        current_cat = Category(category_id)
    except ValueError:
        return None

    # 인사이트 대상 카테고리가 아니면 무조건 None 반환
    if current_cat not in TARGET_CATEGORIES:
        return None
    

    
    # 3. 개별 기사 요약 기본 지침
    base_instr = "기사의 핵심 내용을 파악하여 향후 전망이나 독자가 주목해야 할 포인트를 한 문장의 '인사이트'로 제시하세요."
    
    # 4. 대상 카테고리별 특화 지침 (숫자 대신 Enum으로 비교)
    if current_cat == Category.ECONOMY:
        return f"{base_instr} 시장의 변동성이나 투자자 관점의 시사점을 포함하세요."
    elif current_cat == Category.POLITICS:
        return f"{base_instr} 정당 간의 이해관계나 향후 정국에 미칠 파급력을 분석하세요."
    elif current_cat == Category.TECH_SCIENCE:
        return f"{base_instr} 해당 기술의 상용화 가능성이나 산업 지형도 변화를 분석하세요."
    
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