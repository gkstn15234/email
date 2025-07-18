# n8n 웹훅으로 GitHub Actions 트리거하기

## 1. GitHub Personal Access Token 생성

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" 클릭
3. 권한 선택:
   - `repo` (전체 리포지토리 권한)
   - `workflow` (GitHub Actions 워크플로우 권한)
4. 생성된 토큰 복사 (한 번만 보여짐)

## 2. n8n 워크플로우 설정

### Step 1: Cron 노드 (스케줄러)
```
노드: Cron
설정:
- Mode: Every X Minutes
- Value: 10 (10분마다)
- 또는 특정 시간 설정 가능
```

### Step 2: HTTP Request 노드 (GitHub API 호출)
```
노드: HTTP Request
설정:
- Method: POST
- URL: https://api.github.com/repos/gkstn15234/email/dispatches
- Headers:
  - Authorization: Bearer YOUR_GITHUB_TOKEN
  - Accept: application/vnd.github.v3+json
  - Content-Type: application/json
- Body (JSON):
{
  "event_type": "send-email",
  "client_payload": {
    "data": "n8n에서 트리거됨",
    "timestamp": "{{ $now }}"
  }
}
```

## 3. 고급 설정 (옵션)

### 조건부 실행
```
노드: IF
조건: 특정 시간대에만 실행
- 오전 9시~오후 6시 사이에만 실행
- 주중에만 실행
```

### 여러 번 실행
```
노드: Loop Over Items
설정: 3번 반복 실행 (10분 간격)
```

### 에러 처리
```
노드: Error Trigger
실패 시 알림 발송
```

## 4. 실행 방법

1. n8n 워크플로우 활성화
2. GitHub Actions가 자동으로 트리거됨
3. 이메일 발송 완료

## 5. 장점

- **유연한 스케줄링**: cron보다 더 복잡한 조건 설정 가능
- **실시간 제어**: 언제든지 워크플로우 수정 가능
- **조건부 실행**: 날씨, API 응답 등에 따른 조건부 실행
- **에러 처리**: 실패 시 재시도, 알림 등
- **데이터 전달**: 웹훅을 통해 추가 데이터 전달 가능

## 6. 예시 시나리오

### 시나리오 1: 10분 간격 3회 발송
```
1. Cron (10분 간격)
2. Counter (3회까지)
3. HTTP Request (GitHub API)
```

### 시나리오 2: 조건부 발송
```
1. Cron (매일 오전 9시)
2. Weather API (날씨 확인)
3. IF (맑은 날씨일 때만)
4. HTTP Request (GitHub API)
```

### 시나리오 3: 수동 트리거
```
1. Webhook (외부에서 호출)
2. HTTP Request (GitHub API)
``` 