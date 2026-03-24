# 불필요 텍스트 제거 로직
import re

def clean_text(text: str) -> str:
    """기사 본문에서 불필요한 텍스트 제거"""
    if not text:
        return ""
    
    # 1. 기자 이메일 제거 (예: abc@chosun.com)
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
    
    # 2. 사진/이미지 설명 제거 (보통 [ ] 또는 ( ) 안에 들어감)
    text = re.sub(r'[\[\(].*?(사진|출처|그래픽|제공).*?[\]\)]', '', text)
    
    # 3. 불필요한 공백 및 줄바꿈 정리
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text