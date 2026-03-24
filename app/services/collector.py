# RSS 수집, newspaper3k 원문 추출
import feedparser
from newspaper import Article as NewsArticle
from sqlalchemy.orm import Session
from datetime import datetime
from calendar import timegm
import time
from newspaper import Config

from app.models.common.common_detail import CommonDetail
from app.models.article import Article
from app.models.news_summary import NewsSummary
from app.core.enums import CodeGroup, Status 
from app.utils.cleaner import clean_text

def fetch_rss_feeds(db: Session):
    # DB에서 RSS URL 목록 가져오기
    return db.query(CommonDetail).filter(
        CommonDetail.GROUP_ID == CodeGroup.RSS_FEED.value
    ).limit(5).all()

def get_category_id(feed_id: str) -> str:
    #  ID에서 카테고리 코드 추출
    parts = feed_id.split("_", 1) # 첫 번째 "_"에서만 자름
    if len(parts) > 1:
        raw_category = parts[1] 
    else:
        raw_category = "SOCIETY"
    return f"CAT_{raw_category}"

def get_published_at(entry, news_obj) -> datetime:
    # RSS entry 또는 뉴스 본문에서 발행일 추출
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime.fromtimestamp(timegm(entry.published_parsed))
    # RSS에 없으면 newspaper3k 추출값, 그것도 없으면 현재시간
    return news_obj.publish_date or datetime.now()

def process_article(db: Session, entry, feed_info, config) -> str:
    # 단일 기사를 다운로드하고 DB에 저장
    article_url = entry.link
    
    # 중복 체크
    if db.query(Article).filter(Article.URL == article_url).first():
        return "skipped"

    try:
        # 뉴스 추출 (config 전달 확인!)
        news = NewsArticle(article_url, language='ko', config=config)
        news.download()
        news.parse()

        cleaned_content = news.text # 필요시 clean_text(news.text) 사용
        
        if len(cleaned_content) < 100:
            return "failed"

        # 데이터 매핑
        new_article = Article(
            ORIGINAL_TITLE=entry.title,
            URL=article_url,
            CONTENT=cleaned_content,
            MEDIA_ID=feed_info.ID,
            CATEGORY_ID=get_category_id(feed_info.ID),
            PUBLISHED_AT=get_published_at(entry, news),
            SCRAPED_AT=datetime.now(),
            STATUS_CODE=Status.PUBLISHED.value,
            IS_SUMMARIZED=False
        )
        db.add(new_article)
        return "success"
        
    except Exception as e:
        print(f"  [!] 수집 실패 ({article_url}): {e}")
        return "failed"
    
def collect_news_task(db: Session):
    start_time = time.time()
    stats = {"total_feeds": 0, "new_articles": 0, "skipped_articles": 0, "failed_articles": 0}

    rss_feeds = fetch_rss_feeds(db)
    stats["total_feeds"] = len(rss_feeds)
    
    config = Config()
    config.browser_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    for feed_info in rss_feeds:
        print(f"[*] 수집 시작: {feed_info.NAME}")
        parsed_feed = feedparser.parse(feed_info.CODE_VALUE)
        
        for entry in parsed_feed.entries:
            # 개별 기사 처리 호출
            result = process_article(db, entry, feed_info, config)
            
            # 결과 통계 업데이트
            if result == "success":
                stats["new_articles"] += 1
                time.sleep(2.0) # 성공했을 때만 대기하여 효율성 증대
            elif result == "skipped":
                stats["skipped_articles"] += 1
            else:
                stats["failed_articles"] += 1
        
        db.commit() # 피드 단위 커밋

    duration = round(time.time() - start_time, 2)
    print_summary(stats, duration) # 요약 출력 함수(선택사항) 분리 가능
    
    return {**stats, "duration": duration}


def print_summary(stats: dict, duration: float):
    # 수집 결과를 터미널에 표 형태로 출력
    print("\n" + "="*40)
    print(f"       🏁 [뉴스 수집 작업 완료]       ")
    print("-" * 40)
    print(f" ⏱  총 소요 시간  : {duration}초")
    print(f" 📁 대상 피드 수  : {stats['total_feeds']}개")
    print("-" * 40)
    print(f" ✅ 신규 수집     : {stats['new_articles']}건")
    print(f" ⏭  중복 스킵     : {stats['skipped_articles']}건")
    print(f" ❌ 수집 실패     : {stats['failed_articles']}건")
    print("=" * 40 + "\n")