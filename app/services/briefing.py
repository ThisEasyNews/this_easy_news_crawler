from sqlalchemy.orm import Session
from sqlalchemy import desc, exists
from datetime import datetime

# 모델 임포트 (프로젝트 구조에 맞게 경로를 확인하세요)
from app.models.news_summary import NewsSummary
from app.models.news_keyword import NewsKeyword
from app.models.keyword_log import KeywordLog
from app.models.summary_keyword import SummaryKeyword
from app.models.briefing_summary import BriefingSummary 
from app.models.article import Article 
from app.utils.gpt_client import get_gpt_analysis, get_insight_instruction

async def create_daily_briefing(db: Session):
    """
    오늘의 상위 10개 키워드 각각에 대해 개별적인 3분 브리핑 생성 및 저장
    """
    today = datetime.now().date()

    # 1. 오늘 가장 많이 언급된 상위 키워드 10개 추출
    top_keywords_data = (
        db.query(NewsKeyword.id, NewsKeyword.keyword, KeywordLog.mention_count)
        .join(KeywordLog, NewsKeyword.id == KeywordLog.keyword_id)
        .filter(KeywordLog.target_date == today)
        .order_by(desc(KeywordLog.mention_count))
        .limit(10)
        .all()
    )

    if not top_keywords_data:
        print(f"[*] {today}: 브리핑을 생성할 키워드 로그 데이터가 없습니다.")
        return

    print(f"🚀 총 {len(top_keywords_data)}개의 키워드에 대해 브리핑 생성을 시작합니다.")

    # 2. 각 키워드별 개별 브리핑 생성 루프
    for kw_info in top_keywords_data:
        target_kw_id = kw_info.id
        target_kw_text = kw_info.keyword
        
        # [중복 체크] 에러 수정된 버전: 해당 키워드로 오늘 이미 BRIEFING이 생성되었는지 확인
        is_already_briefed = db.query(
            exists().where(
                (NewsSummary.target_date == today) &
                (NewsSummary.summary_type == "BRIEFING") &
                (SummaryKeyword.keyword_id == target_kw_id) &
                (NewsSummary.id == SummaryKeyword.summary_id) # 여기서 조인 조건을 명시
            )
        ).scalar()

        if is_already_briefed:
            print(f"[-] '{target_kw_text}' 키워드 브리핑이 이미 존재합니다. 스킵합니다.")
            continue

        # 3. 해당 키워드와 관련된 최신 뉴스 요약 데이터 5개 수집 (소스 데이터)
        source_summaries = (
            db.query(NewsSummary)
            .join(SummaryKeyword, NewsSummary.id == SummaryKeyword.summary_id)
            .filter(SummaryKeyword.keyword_id == target_kw_id)
            .filter(NewsSummary.summary_type != "BRIEFING")
            .order_by(desc(NewsSummary.created_at))
            .limit(5)
            .all()
        )

        if not source_summaries:
            print(f"[-] '{target_kw_text}' 관련 뉴스 요약 데이터가 없어 브리핑을 생성하지 않습니다.")
            continue

        # 4. 브리핑용 대표 이미지 추출
        representative_article = (
            db.query(Article.image_url)
            .join(SummaryKeyword, Article.summary_id == SummaryKeyword.summary_id)
            .filter(SummaryKeyword.keyword_id == target_kw_id)
            .filter(Article.image_url.isnot(None))
            .order_by(desc(Article.published_at))
            .first()
        )
        final_image_url = representative_article.image_url if representative_article else None

        # 5. GPT 분석 요청
        context_text = "\n\n".join([f"기사제목: {s.title}\n내용요약: {s.summary_content}" for s in source_summaries])
        briefing_instruction = get_insight_instruction(mode="briefing", keyword_list=[target_kw_text])
        briefing_title = f"[{target_kw_text}] 오늘의 3분 핵심 브리핑"

        try:
            res_data = await get_gpt_analysis(
                title=briefing_title,
                content=context_text,
                instruction=briefing_instruction
            )

            # 6. 뉴스 요약 테이블(NewsSummary)에 브리핑 본체 저장
            new_briefing = NewsSummary(
                title=res_data.get('title', briefing_title),
                summary_content=res_data.get('summary'),
                insight=res_data.get('insight'),
                ai_model="gpt-4o-mini",
                top_image_url=final_image_url,
                target_date=today,
                summary_type="BRIEFING",
                created_at=datetime.now()
            )
            db.add(new_briefing)
            db.flush()

            # 7. briefing_summary 저장: 소스 뉴스들 매핑
            for source in source_summaries:
                mapping = BriefingSummary(
                    briefing_id=new_briefing.id, 
                    summary_id=source.id
                )
                db.add(mapping)

            # 8. summary_keyword 저장: 메인 키워드와 연결
            db.add(SummaryKeyword(
                summary_id=new_briefing.id, 
                keyword_id=target_kw_id
            ))

            db.commit()
            print(f"✅ '{target_kw_text}' 브리핑 생성 완료 (ID: {new_briefing.id})")

        except Exception as e:
            db.rollback()
            print(f"❌ '{target_kw_text}' 브리핑 생성 중 오류 발생: {str(e)}")

    print("🏁 모든 키워드에 대한 브리핑 작업이 종료되었습니다.")