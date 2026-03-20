from fastapi import FastAPI
import yaml

from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "This Easy News API is running!"}

@app.get("/news/summary")
def get_summary():
    """뉴스 수집 및 요약을 수행하여 결과를 반환하는 API 엔드포인트"""
    # 1. 설정 로드
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    results = []
    
    # 2. 뉴스 수집 및 분석 루프
    for name, url in config['rss_feeds'].items():
        news_list = fetch_news_links(url, limit=1) # 테스트용으로 1개만
        
        for news in news_list:
            content = extract_article_content(news['link'])
            if content:
                analysis = get_ai_insight(content)
                results.append({
                    "source": name,
                    "title": news['title'],
                    "link": news['link'],
                    "analysis": analysis
                })
                
    return {"status": "success", "data": results}