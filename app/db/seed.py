import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.common.common_group import CommonGroup
from app.models.common.common_detail import CommonDetail
from app.core.enums import CodeGroup, Status, Category, Media

def seed_data():
    db = SessionLocal()
    try:
        # 1. common_group 데이터 정의
        groups = [
            (CodeGroup.STATUS.value, "공통 상태 관리"),
            (CodeGroup.CATEGORY.value, "뉴스 카테고리"),
            (CodeGroup.MEDIA.value, "언론사 관리"),
            (CodeGroup.RSS_FEED.value, "언론사 RSS 피드 관리"),
        ]

        for g_id, g_name in groups:
            # ID -> id로 변경
            exists = db.query(CommonGroup).filter(CommonGroup.id == g_id).first()
            if not exists:
                # 인자값을 모두 소문자로 변경
                db.add(CommonGroup(id=g_id, name=g_name, status_code="PUBLISHED"))
                print(f"그룹 생성: {g_id}")
        db.flush()

        # 2. common_detail 데이터 정의 (상태, 카테고리, 언론사)
        status = [
            (Status.DRAFT.value, CodeGroup.STATUS.value, "임시", None), 
            (Status.PUBLISHED.value, CodeGroup.STATUS.value, "게시", None), 
            (Status.DELETED.value, CodeGroup.STATUS.value, "삭제", None), 
            (Status.RUNNING.value, CodeGroup.STATUS.value, "실행중", None), 
            (Status.SUCCESS.value, CodeGroup.STATUS.value, "성공", None), 
            (Status.PARTIAL_SUCCESS.value, CodeGroup.STATUS.value, "부분성공", None), 
            (Status.FAIL.value, CodeGroup.STATUS.value, "실패", None)
        ]
        category = [
            (Category.POLITICS.value, CodeGroup.CATEGORY.value, "정치", None), 
            (Category.ECONOMY.value, CodeGroup.CATEGORY.value, "경제", None), 
            (Category.SOCIETY.value, CodeGroup.CATEGORY.value, "사회", None), 
            (Category.INTERNATIONAL.value, CodeGroup.CATEGORY.value, "국제", None), 
            (Category.SPORTS.value, CodeGroup.CATEGORY.value, "스포츠", None), 
            (Category.CULTURE.value, CodeGroup.CATEGORY.value, "문화", None), 
            (Category.ENTERTAINMENT.value, CodeGroup.CATEGORY.value, "연예", None), 
            (Category.TECH_SCIENCE.value, CodeGroup.CATEGORY.value, "IT·과학", None)
        ]
        media = [
            (Media.CHOSUN.value, CodeGroup.MEDIA.value, "조선일보", None), 
            (Media.MK.value, CodeGroup.MEDIA.value, "매일경제", None), 
            (Media.HANKYUNG.value, CodeGroup.MEDIA.value, "한국경제", None), 
            (Media.KHAN.value, CodeGroup.MEDIA.value, "경향신문", None), 
            (Media.SBS.value, CodeGroup.MEDIA.value, "SBS", None)
        ]

        # 3. RSS 상세 데이터 (RSS_FEED 그룹)
        rss_feeds = [
            ("CHOSUN_POLITICS", CodeGroup.RSS_FEED.value, "조선일보 정치", "https://www.chosun.com/arc/outboundfeeds/rss/category/politics/?outputType=xml"),
            ("CHOSUN_ECONOMY", CodeGroup.RSS_FEED.value, "조선일보 경제", "https://www.chosun.com/arc/outboundfeeds/rss/category/economy/?outputType=xml"),
            ("CHOSUN_SOCIETY", CodeGroup.RSS_FEED.value, "조선일보 사회", "https://www.chosun.com/arc/outboundfeeds/rss/category/national/?outputType=xml"),
            ("CHOSUN_INTERNATIONAL", CodeGroup.RSS_FEED.value, "조선일보 국제", "https://www.chosun.com/arc/outboundfeeds/rss/category/international/?outputType=xml"),
            ("CHOSUN_SPORTS", CodeGroup.RSS_FEED.value, "조선일보 스포츠", "https://www.chosun.com/arc/outboundfeeds/rss/category/sports/?outputType=xml"),
            ("CHOSUN_CULTURE", CodeGroup.RSS_FEED.value, "조선일보 문화", "https://www.chosun.com/arc/outboundfeeds/rss/category/culture-life/?outputType=xml"),
            ("CHOSUN_ENTERTAINMENT", CodeGroup.RSS_FEED.value, "조선일보 연예", "https://www.chosun.com/arc/outboundfeeds/rss/category/entertainments/?outputType=xml"),
            ("MK_POLITICS", CodeGroup.RSS_FEED.value, "매일경제 정치", "https://www.mk.co.kr/rss/30200030/"),
            ("MK_ECONOMY", CodeGroup.RSS_FEED.value, "매일경제 경제", "https://www.mk.co.kr/rss/30100041/"),
            ("MK_SOCIETY", CodeGroup.RSS_FEED.value, "매일경제 사회", "https://www.mk.co.kr/rss/50400012/"),
            ("MK_INTERNATIONAL", CodeGroup.RSS_FEED.value, "매일경제 국제", "https://www.mk.co.kr/rss/30300018/"),
            ("MK_SPORTS", CodeGroup.RSS_FEED.value, "매일경제 스포츠", "https://www.mk.co.kr/rss/71000001/"),
            ("MK_CULTURE", CodeGroup.RSS_FEED.value, "매일경제 문화", "https://www.mk.co.kr/rss/30000023/"),
            ("HANKYUNG_POLITICS", CodeGroup.RSS_FEED.value, "한국경제 정치", "https://www.hankyung.com/feed/politics"),
            ("HANKYUNG_ECONOMY", CodeGroup.RSS_FEED.value, "한국경제 경제", "https://www.hankyung.com/feed/economy"),
            ("HANKYUNG_SOCIETY", CodeGroup.RSS_FEED.value, "한국경제 사회", "https://www.hankyung.com/feed/society"),
            ("HANKYUNG_INTERNATIONAL", CodeGroup.RSS_FEED.value, "한국경제 국제", "https://www.hankyung.com/feed/international"),
            ("HANKYUNG_SPORTS", CodeGroup.RSS_FEED.value, "한국경제 스포츠", "https://www.hankyung.com/feed/sports"),
            ("HANKYUNG_CULTURE", CodeGroup.RSS_FEED.value, "한국경제 문화", "https://www.hankyung.com/feed/life"),
            ("HANKYUNG_ENTERTAINMENT", CodeGroup.RSS_FEED.value, "한국경제 연예", "https://www.hankyung.com/feed/entertainment"),
            ("HANKYUNG_TECH_SCIENCE", CodeGroup.RSS_FEED.value, "한국경제 IT·과학", "https://www.hankyung.com/feed/it"),
            ("KHAN_POLITICS", CodeGroup.RSS_FEED.value, "경향신문 정치", "https://www.khan.co.kr/rss/rssdata/politic_news.xml"),
            ("KHAN_ECONOMY", CodeGroup.RSS_FEED.value, "경향신문 경제", "https://www.khan.co.kr/rss/rssdata/economy_news.xml"),
            ("KHAN_SOCIETY", CodeGroup.RSS_FEED.value, "경향신문 사회", "https://www.khan.co.kr/rss/rssdata/society_news.xml"),
            ("KHAN_INTERNATIONAL", CodeGroup.RSS_FEED.value, "경향신문 국제", "https://www.khan.co.kr/rss/rssdata/kh_world.xml"),
            ("KHAN_SPORTS", CodeGroup.RSS_FEED.value, "경향신문 스포츠", "http://www.khan.co.kr/rss/rssdata/kh_sports.xml"),
            ("KHAN_CULTURE", CodeGroup.RSS_FEED.value, "경향신문 문화", "https://www.khan.co.kr/rss/rssdata/culture_news.xml"),
            ("KHAN_TECH_SCIENCE", CodeGroup.RSS_FEED.value, "경향신문 IT·과학", "https://www.khan.co.kr/rss/rssdata/science_news.xml"),
            ("SBS_POLITICS", CodeGroup.RSS_FEED.value, "SBS 정치", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01&plink=RSSREADERR"),
            ("SBS_ECONOMY", CodeGroup.RSS_FEED.value, "SBS 경제", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER"),
            ("SBS_SOCIETY", CodeGroup.RSS_FEED.value, "SBS 사회", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=03&plink=RSSREADER"),
            ("SBS_INTERNATIONAL", CodeGroup.RSS_FEED.value, "SBS 국제", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=07&plink=RSSREADER"),
            ("SBS_SPORTS", CodeGroup.RSS_FEED.value, "SBS 스포츠", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=09&plink=RSSREADER"),
            ("SBS_CULTURE", CodeGroup.RSS_FEED.value, "SBS 문화", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=08&plink=RSSREADER"),
            ("SBS_ENTERTAINMENT", CodeGroup.RSS_FEED.value, "SBS 연예", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=14&plink=RSSREADER"),
        ]

        # 4. 상세 데이터 일괄 삽입
        final_details = status + category + media + rss_feeds

        for d_id, g_id, d_name, d_val in final_details:
            # ID -> id로 변경
            exists = db.query(CommonDetail).filter(CommonDetail.id == d_id).first()
            if not exists:
                # 인자값을 모두 소문자로 변경
                db.add(CommonDetail(
                    id=d_id, 
                    group_id=g_id, 
                    name=d_name, 
                    code_value=d_val, 
                    status_code="PUBLISHED"
                ))
                print(f"상세 코드 추가: {d_name} ({d_id})")

        db.commit()
        print("\n✅ 모든 초기 데이터 주입 완료")

    except Exception as e:
        db.rollback()
        print(f"❌ 에러 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()