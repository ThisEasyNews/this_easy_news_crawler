import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.common.common_group import CommonGroup
from app.models.common.common_detail import CommonDetail

def seed_data():
    db = SessionLocal()
    try:
        # 1. COMMON_GROUP 데이터 정의
        groups = [
            ("STATUS", "공통 상태 관리"),
            ("CATEGORY", "뉴스 카테고리"),
            ("MEDIA", "언론사 관리"),
            ("RSS_FEED", "언론사 RSS 피드 관리")
        ]

        for g_id, g_name in groups:
            exists = db.query(CommonGroup).filter(CommonGroup.ID == g_id).first()
            if not exists:
                db.add(CommonGroup(ID=g_id, NAME=g_name, STATUS_CODE="PUBLISHED"))
                print(f"그룹 생성: {g_id}")
        db.flush()

        # 2. COMMON_DETAIL 데이터 정의 (상태, 카테고리, 언론사)
        status = [
            ("DRAFT", "STATUS", "임시", None), 
            ("PUBLISHED", "STATUS", "게시", None), 
            ("DELETED", "STATUS", "삭제", None), 
            ("RUNNING", "STATUS", "실행중", None), 
            ("SUCCESS", "STATUS", "성공", None), 
            ("PARTIAL_SUCCESS", "STATUS", "부분성공", None), 
            ("FAIL", "STATUS", "실패", None)
        ]
        category = [
            ("CAT_POLITICS", "CATEGORY", "정치", None), 
            ("CAT_ECONOMY", "CATEGORY", "경제", None), 
            ("CAT_SOCIETY", "CATEGORY", "사회", None), 
            ("CAT_INTERNATIONAL", "CATEGORY", "국제", None), 
            ("CAT_SPORTS", "CATEGORY", "스포츠", None), 
            ("CAT_CULTURE", "CATEGORY", "문화", None), 
            ("CAT_ENTERTAINMENT", "CATEGORY", "연예", None), 
            ("CAT_TECH_SCIENCE", "CATEGORY", "IT·과학", None)
        ]
        media = [
            ("MED_CHOSUN", "MEDIA", "조선일보", None), 
            ("MED_MK", "MEDIA", "매일경제", None), 
            ("MED_HANKYUNG", "MEDIA", "한국경제", None), 
            ("MED_KHAN", "MEDIA", "경향신문", None), 
            ("MED_SBS", "MEDIA", "SBS", None)
        ]

        # 3. RSS 상세 데이터 (RSS_FEED 그룹)
        rss_feeds = [
            ("CHOSUN_POLITICS", "RSS_FEED", "조선일보 정치", "https://www.chosun.com/arc/outboundfeeds/rss/category/politics/?outputType=xml"),
            ("CHOSUN_ECONOMY", "RSS_FEED", "조선일보 경제", "https://www.chosun.com/arc/outboundfeeds/rss/category/economy/?outputType=xml"),
            ("CHOSUN_SOCIETY", "RSS_FEED", "조선일보 사회", "https://www.chosun.com/arc/outboundfeeds/rss/category/national/?outputType=xml"),
            ("CHOSUN_INTERNATIONAL", "RSS_FEED", "조선일보 국제", "https://www.chosun.com/arc/outboundfeeds/rss/category/international/?outputType=xml"),
            ("CHOSUN_SPORTS", "RSS_FEED", "조선일보 스포츠", "https://www.chosun.com/arc/outboundfeeds/rss/category/sports/?outputType=xml"),
            ("CHOSUN_CULTURE", "RSS_FEED", "조선일보 문화", "https://www.chosun.com/arc/outboundfeeds/rss/category/culture-life/?outputType=xml"),
            ("CHOSUN_ENTERTAINMENT", "RSS_FEED", "조선일보 연예", "https://www.chosun.com/arc/outboundfeeds/rss/category/entertainments/?outputType=xml"),
            ("MK_POLITICS", "RSS_FEED", "매일경제 정치", "https://www.mk.co.kr/rss/30200030/"),
            ("MK_ECONOMY", "RSS_FEED", "매일경제 경제", "https://www.mk.co.kr/rss/30100041/"),
            ("MK_SOCIETY", "RSS_FEED", "매일경제 사회", "https://www.mk.co.kr/rss/50400012/"),
            ("MK_INTERNATIONAL", "RSS_FEED", "매일경제 국제", "https://www.mk.co.kr/rss/30300018/"),
            ("MK_SPORTS", "RSS_FEED", "매일경제 스포츠", "https://www.mk.co.kr/rss/71000001/"),
            ("MK_CULTURE", "RSS_FEED", "매일경제 문화", "https://www.mk.co.kr/rss/30000023/"),
            ("HANKYUNG_POLITICS", "RSS_FEED", "한국경제 정치", "https://www.hankyung.com/feed/politics"),
            ("HANKYUNG_ECONOMY", "RSS_FEED", "한국경제 경제", "https://www.hankyung.com/feed/economy"),
            ("HANKYUNG_SOCIETY", "RSS_FEED", "한국경제 사회", "https://www.hankyung.com/feed/society"),
            ("HANKYUNG_INTERNATIONAL", "RSS_FEED", "한국경제 국제", "https://www.hankyung.com/feed/international"),
            ("HANKYUNG_SPORTS", "RSS_FEED", "한국경제 스포츠", "https://www.hankyung.com/feed/sports"),
            ("HANKYUNG_CULTURE", "RSS_FEED", "한국경제 문화", "https://www.hankyung.com/feed/life"),
            ("HANKYUNG_ENTERTAINMENT", "RSS_FEED", "한국경제 연예", "https://www.hankyung.com/feed/entertainment"),
            ("HANKYUNG_TECH_SCIENCE", "RSS_FEED", "한국경제 IT·과학", "https://www.hankyung.com/feed/it"),
            ("KHAN_POLITICS", "RSS_FEED", "경향신문 정치", "https://www.khan.co.kr/rss/rssdata/politic_news.xml"),
            ("KHAN_ECONOMY", "RSS_FEED", "경향신문 경제", "https://www.khan.co.kr/rss/rssdata/economy_news.xml"),
            ("KHAN_SOCIETY", "RSS_FEED", "경향신문 사회", "https://www.khan.co.kr/rss/rssdata/society_news.xml"),
            ("KHAN_INTERNATIONAL", "RSS_FEED", "경향신문 국제", "https://www.khan.co.kr/rss/rssdata/kh_world.xml"),
            ("KHAN_SPORTS", "RSS_FEED", "경향신문 스포츠", "http://www.khan.co.kr/rss/rssdata/kh_sports.xml"),
            ("KHAN_CULTURE", "RSS_FEED", "경향신문 문화", "https://www.khan.co.kr/rss/rssdata/culture_news.xml"),
            ("KHAN_TECH_SCIENCE", "RSS_FEED", "경향신문 IT·과학", "https://www.khan.co.kr/rss/rssdata/science_news.xml"),
            ("SBS_POLITICS", "RSS_FEED", "SBS 정치", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01&plink=RSSREADERR"),
            ("SBS_ECONOMY", "RSS_FEED", "SBS 경제", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER"),
            ("SBS_SOCIETY", "RSS_FEED", "SBS 사회", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=03&plink=RSSREADER"),
            ("SBS_INTERNATIONAL", "RSS_FEED", "SBS 국제", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=07&plink=RSSREADER"),
            ("SBS_SPORTS", "RSS_FEED", "SBS 스포츠", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=09&plink=RSSREADER"),
            ("SBS_CULTURE", "RSS_FEED", "SBS 문화", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=08&plink=RSSREADER"),
            ("SBS_ENTERTAINMENT", "RSS_FEED", "SBS 연예", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=14&plink=RSSREADER"),
        ]

        # 4. 상세 데이터 일괄 삽입
        final_details = status + category + media + rss_feeds

        for d_id, g_id, d_name, d_val in final_details:
            exists = db.query(CommonDetail).filter(CommonDetail.ID == d_id).first()
            if not exists:
                db.add(CommonDetail(
                    ID=d_id, 
                    GROUP_ID=g_id, 
                    NAME=d_name, 
                    CODE_VALUE=d_val, 
                    STATUS_CODE="PUBLISHED"
                ))
                print(f"상세 코드 추가: {d_name} ({d_id})")

        db.commit()
        print("\n모든 초기 데이터 주입 완료")

    except Exception as e:
        db.rollback()
        print(f"❌ 에러 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()