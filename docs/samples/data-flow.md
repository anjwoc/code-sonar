# Data Flow

## Representative Runtime Sequence

```mermaid
sequenceDiagram
  actor User as 사용자
  participant Web as commerce-web
  participant BFF as commerce-bff-api
  participant API as commerce-api
  participant Redis as Redis
  participant DB as Oracle
  participant Kafka as Kafka

  User->>Web: 주문 상세 조회
  Web->>BFF: Feign API 호출
  BFF->>API: WebClient 도메인 API 호출
  API->>Redis: rate limit 및 token 상태 확인
  API->>DB: 주문 및 유입 매핑 조회
  API-->>BFF: 조회 결과 반환
  API->>Kafka: 후속 처리 이벤트 발행
  BFF-->>Web: 화면 표시 데이터 반환
```

## Business Dataflow

```mermaid
flowchart LR
  U["S1: 유입 생성"]
  T["S2: token 정책 검증"]
  O["S3: 주문 이벤트 수신"]
  M["S4: 주문-유입 매핑"]
  S["S5: 정산 대상 판정"]
  P["S6: 지급 상태 반영"]

  LOG[("유입 로그")]
  ORDER[("주문 저장소")]
  SETTLE[("정산 테이블")]
  MON["운영 모니터링"]

  U -->|write| LOG
  T -->|validate| U
  O -->|read| ORDER
  M -->|join| LOG
  M -->|join| ORDER
  M --> S
  S -->|write| SETTLE
  P -->|status update| SETTLE
  MON -.->|check failed mapping| M
```

## 운영 확인 포인트

| Step | 확인 위치 | 실패 시 조치 |
| --- | --- | --- |
| 유입 생성 | 유입 로그 저장소 | token, target URL, policy 확인 |
| 주문 수신 | Kafka consumer lag | 누락 이벤트 재처리 |
| 매핑 | 주문-유입 매핑 테이블 | 키 값과 시간 범위 확인 |
| 정산 판정 | 정산 집계 테이블 | 제외 사유와 보류 상태 확인 |
