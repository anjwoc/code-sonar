# Business Workflow

이 문서는 시스템 컴포넌트가 아니라 업무 판단 상태를 기준으로 작성한다.

```mermaid
flowchart LR
  S1["S1: 유입 생성<br/>업무 질문: 어떤 링크로 들어왔나"]
  S2["S2: 정책 검증<br/>업무 질문: 유효한 token인가"]
  S3["S3: 주문 매핑<br/>업무 질문: 어떤 주문과 연결됐나"]
  S4["S4: 정산 대상 판정<br/>업무 질문: 지급 대상인가"]
  S5["S5: 지급 상태 확정<br/>업무 질문: 보류인가 완료인가"]
  S6["S6: 운영 대응<br/>업무 질문: 어디서 재처리하나"]

  LOG[("유입 로그")]
  SETTLE[("정산 데이터")]
  DASH["운영 대시보드"]

  S1 --> S2
  S2 --> S3
  S3 --> S4
  S4 --> S5
  S5 --> S6
  LOG -.-> S3
  SETTLE -.-> S4
  DASH -.-> S6
```

## 업무 단계별 판단

| Step | 업무 질문 | 판정 조건 | 담당 프로젝트 | 확인 근거 | 운영 확인 위치 |
| --- | --- | --- | --- | --- | --- |
| S1 | 어떤 링크로 유입됐나 | target URL과 tracking token 존재 | commerce-web | `TrackingController` | 유입 로그 |
| S2 | 유효한 token인가 | 만료, 정책, rate limit 통과 | commerce-api | `TokenPolicyService` | Redis key |
| S3 | 주문과 연결됐나 | 주문 번호와 유입 키 매칭 | commerce-event | `OrderConsumer` | mapping table |
| S4 | 지급 대상인가 | 취소, 환불, 중복 제외 | commerce-batch | `SettlementJob` | settlement table |
| S5 | 지급 완료인가 | lock date 이후 상태 확정 | commerce-batch | `PayoutService` | monthly settlement |
| S6 | 운영 조치가 필요한가 | 실패 건 존재 또는 재처리 요청 | commerce-admin | `AdminRetryController` | admin page |
