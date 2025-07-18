import os
import smtplib
from email.message import EmailMessage

# GitHub Secrets를 통해 전달된 환경 변수에서 이메일 정보 가져오기
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# 이메일 내용 설정
subject = "자동화된 이메일 알림입니다 📬"
body = """
안녕하세요!

이 이메일은 GitHub Actions에 의해 자동 발송되었습니다.
스케줄에 따라 성공적으로 작업이 실행되었습니다.

좋은 하루 보내세요!
"""

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
except Exception as e:
    print(f"이메일 발송 실패: {e}") 