import asyncio
import httpx
import feedparser
import time
from newspaper import Config
from newspaper import Article as NewsArticle
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta

from app.models.common.common_detail import CommonDetail
from app.models.article import Article
from app.core.database import SessionLocal
from app.core.enums import CodeGroup, Status

# 설정: 동시 접속 제한
MAX_CONCURRENT_TASKS = 10 
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

async def fetch_and_parse(url):
    """비동기로 HTML을 가져와서 newspaper3k로 파싱 (추출 최적화)"""
    async with semaphore:
        # 1. 브라우저처럼 보이기 위한 설정 추가
        config = Config()
        config.browser_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        config.request_timeout = 15
        
        timeout_config = httpx.Timeout(15.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout_config, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    news = NewsArticle(url, language='ko', config=config)
                    news.set_html(response.text)
                    news.parse()
                    return news
            except Exception as e:
                return e
            return None

async def process_single_article(db_session: Session, entry, feed_info):
    article_url = entry.link
    
    # 1. 발행일 확인 (오늘 데이터만 수집)
    # feedparser의 published_parsed를 사용하여 날짜 비교
    pub_date = None
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        pub_date = date(*entry.published_parsed[:3]) # (년, 월, 일) 추출
    
    if pub_date not in [date.today(), date.today() - timedelta(days=1)]:
        return "not_today"

    # 2. 중복 체크
    if db_session.query(Article).filter(Article.url == article_url).first():
        return "skipped"

    # 3. 비동기 본문 추출
    result = await fetch_and_parse(article_url)
    
    # 실패 케이스 처리
    if isinstance(result, Exception):
        print(f"    [!] 수집 실패 ({article_url}): {str(result)}")
        return "failed"
    if isinstance(result, Exception) or not result or len(result.text) < 100:
        print(f"    [!] 수집 실패 ({article_url}): 본문 길이 미달 혹은 추출 불가")
        return "failed"

    try:
        id_parts = feed_info.id.split('_', 1) 
        media_code = id_parts[0]            
        category_code = id_parts[1]

        # 4. 데이터 매핑 (요청하신 구조 적용)
        new_article = Article(
            original_title=entry.title,
            url=article_url,
            feedparser_content=result.text,      
            crawler_content=None,               # 현재는 미사용
            description=entry.get('summary', ''),
            image_url=result.top_image,
            media_id=f"MED_{media_code}",
            category_id=f"CAT_{category_code}",
            published_at=result.publish_date or datetime.now(),
            scraped_at=datetime.now(),
            status_code=Status.PUBLISHED.value,
            is_summarized=False
        )
        db_session.add(new_article)
        db_session.commit()
        return "success"
    except Exception as e:
        db_session.rollback()
        print(f"    [!] DB 저장 실패: {str(e)}")
        return "failed"

async def collect_single_feed(db: Session, feed_info):
    print(f"  ▶ [수집 시작] {feed_info.name} ({feed_info.code_value})")
    start_time = time.time()
    
    try:
        # httpx를 사용하여 RSS XML을 직접 가져옴 (feedparser 직접 호출보다 안정적)
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(feed_info.code_value.strip())
            # 조선일보 등 인코딩 이슈 대응을 위해 content(bytes) 사용
            parsed_feed = feedparser.parse(response.content)
            
        if not parsed_feed.entries:
            print(f"    [!] 데이터를 찾을 수 없습니다. (피드가 비어있거나 형식이 잘못됨)")
            return []

        tasks = [process_single_article(db, entry, feed_info) for entry in parsed_feed.entries]
        results = await asyncio.gather(*tasks)
        
        success = results.count("success")
        not_today = results.count("not_today")
        duration = round(time.time() - start_time, 2)
        
        print(f"  ■ [수집 종료] {feed_info.name} | 성공: {success}건 (과거/중복 제외: {not_today + results.count('skipped')}건) | 소요: {duration}초")
        return results

    except Exception as e:
        print(f"    [!] RSS 접속 실패 ({feed_info.name}): {str(e)}")
        return []

async def collect_by_category(category_name: str):
    db = SessionLocal()
    cat_stats = {"total": 0, "success": 0, "skipped": 0, "failed": 0, "not_today": 0}
    
    try:
        feeds = db.query(CommonDetail).filter(
            CommonDetail.group_id == CodeGroup.RSS_FEED.value,
            CommonDetail.id.like(f"%_{category_name}")
        ).all()

        if not feeds:
            return cat_stats

        print(f"\n🚀 === [{category_name}] 카테고리 오늘 뉴스 수집 === ")
        
        feed_tasks = [collect_single_feed(db, feed) for feed in feeds]
        all_feed_results = await asyncio.gather(*feed_tasks)
        
        for feed_result in all_feed_results:
            cat_stats["total"] += len(feed_result)
            cat_stats["success"] += feed_result.count("success")
            cat_stats["skipped"] += feed_result.count("skipped")
            cat_stats["failed"] += feed_result.count("failed")
            cat_stats["not_today"] += feed_result.count("not_today")
        
        return cat_stats
    finally:
        db.close()

async def run_all_categories():
    categories = ["POLITICS", "ECONOMY", "SOCIETY", "INTERNATIONAL", "SPORTS", "CULTURE", "ENTERTAINMENT", "TECH_SCIENCE"]
    total_stats = {"total": 0, "success": 0, "skipped": 0, "failed": 0, "not_today": 0}
    total_start = time.time()
    
    for cat in categories:
        cat_result = await collect_by_category(cat)
        for key in total_stats:
            total_stats[key] += cat_result[key]
    
    duration = round(time.time() - total_start, 2)
    
    print("\n" + "="*50)
    print(f"🏆 [오늘의 뉴스 수집 리포트]")
    print(f"⏱ 총 소요시간: {duration}초")
    print(f"✅ 오늘 신규 저장: {total_stats['success']}건")
    print(f"⏭ 중복 제외: {total_stats['skipped']}건")
    print(f"📅 과거 기사 제외: {total_stats['not_today']}건")
    print(f"❌ 수집 실패: {total_stats['failed']}건")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_all_categories())