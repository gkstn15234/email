import os
import smtplib
import feedparser
import requests
from email.message import EmailMessage
from datetime import datetime
import json
import pytz

# GitHub Secrets를 통해 전달된 환경 변수에서 정보 가져오기
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenAI 모델 선택 (기본값: gpt-3.5-turbo)
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 사용 가능한 모델들과 설정
MODEL_CONFIGS = {
    'gpt-3.5-turbo': {
        'max_tokens': 300,
        'temperature': 0.7,
        'description': '빠르고 효율적인 모델'
    },
    'gpt-4': {
        'max_tokens': 400,
        'temperature': 0.6,
        'description': '더 정확하고 상세한 분석'
    },
    'gpt-4-turbo': {
        'max_tokens': 500,
        'temperature': 0.7,
        'description': '최신 GPT-4 터보 모델'
    },
    'gpt-4o': {
        'max_tokens': 500,
        'temperature': 0.7,
        'description': '최신 GPT-4o 모델'
    },
    'gpt-4o-mini': {
        'max_tokens': 300,
        'temperature': 0.7,
        'description': '경제적인 GPT-4o 미니 모델'
    }
}

def get_google_news():
    """Google 뉴스 RSS에서 최신 뉴스 가져오기"""
    try:
        # Google 뉴스 RSS URL (한국 뉴스)
        rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(rss_url)
        
        news_items = []
        # 상위 10개 뉴스만 가져오기
        for entry in feed.entries[:10]:
            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'summary': entry.summary if hasattr(entry, 'summary') else ''
            })
        
        return news_items
    except Exception as e:
        print(f"뉴스 가져오기 실패: {e}")
        return []

def summarize_news_with_openai(news_items):
    """OpenAI API를 사용해서 뉴스 요약하기"""
    try:
        # 뉴스 제목들을 하나의 텍스트로 합치기
        news_text = "\n".join([f"- {item['title']}" for item in news_items])
        
        # 선택된 모델의 설정 가져오기
        model_config = MODEL_CONFIGS.get(OPENAI_MODEL, MODEL_CONFIGS['gpt-3.5-turbo'])
        
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': OPENAI_MODEL,
            'messages': [
                {
                    'role': 'system',
                    'content': '당신은 뉴스 요약 전문가입니다. 주요 뉴스들을 간결하고 이해하기 쉽게 요약해주세요. 중요한 키워드와 핵심 내용을 포함하여 독자가 빠르게 파악할 수 있도록 작성해주세요.'
                },
                {
                    'role': 'user',
                    'content': f'다음 뉴스 제목들을 바탕으로 오늘의 주요 뉴스를 3-4줄로 요약해주세요. 각 주요 분야별로 정리해주세요:\n\n{news_text}'
                }
            ],
            'max_tokens': model_config['max_tokens'],
            'temperature': model_config['temperature']
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"OpenAI API 오류: {response.status_code}")
            return "뉴스 요약을 가져올 수 없습니다."
            
    except Exception as e:
        print(f"OpenAI API 호출 실패: {e}")
        return "뉴스 요약을 가져올 수 없습니다."

def create_email_content():
    """이메일 내용 생성"""
    # 한국 시간으로 현재 시간 가져오기
    current_time = datetime.now(KST).strftime("%Y년 %m월 %d일 %H시 %M분 (KST)")
    
    # 뉴스 가져오기
    news_items = get_google_news()
    
    if news_items and OPENAI_API_KEY:
        # OpenAI로 뉴스 요약
        news_summary = summarize_news_with_openai(news_items)
        
        # 상위 5개 뉴스 링크 포함
        top_news_links = "\n".join([
            f"• {item['title']}\n  {item['link']}\n"
            for item in news_items[:5]
        ])
        
        # 사용된 모델 정보
        model_info = MODEL_CONFIGS.get(OPENAI_MODEL, MODEL_CONFIGS['gpt-3.5-turbo'])
        
        body = f"""
🌅 좋은 아침입니다!

📅 {current_time}

🤖 AI가 요약한 오늘의 주요 뉴스 ({OPENAI_MODEL}):
{news_summary}

📰 상위 뉴스 링크:
{top_news_links}

좋은 하루 보내세요! 💪

---
🔧 사용된 AI 모델: {OPENAI_MODEL} ({model_info['description']})
자동 발송 시스템 by n8n + GitHub Actions
        """
    else:
        body = f"""
🌅 좋은 아침입니다!

📅 {current_time}

이 이메일은 n8n과 GitHub Actions에 의해 자동 발송되었습니다.
스케줄에 따라 성공적으로 작업이 실행되었습니다.

좋은 하루 보내세요! 💪

---
자동 발송 시스템 by n8n + GitHub Actions
        """
    
    return body

# 이메일 내용 생성
subject = "🌅 오늘의 뉴스 브리핑 - 자동 발송"
body = create_email_content()

# 이메일 메시지 객체 생성
msg = EmailMessage()
msg['Subject'] = subject
msg['From'] = SENDER_EMAIL
msg['To'] = RECIPIENT_EMAIL
msg.set_content(body)

# Gmail SMTP 서버에 연결하여 이메일 발송
try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
    print("이메일 발송 성공!")
    print(f"사용된 모델: {OPENAI_MODEL}")
    print(f"발송 시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')}")
except Exception as e:
    print(f"이메일 발송 실패: {e}") 