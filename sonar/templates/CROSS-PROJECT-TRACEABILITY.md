# Cross Project Traceability

> 단순 프로젝트 매핑표가 아니라 업무 질문별 추적 가이드입니다. 운영자/기획자/개발자가 특정 업무 문제를 받았을 때 어떤 근거를 어떤 순서로 확인해야 하는지 정리합니다.

## Business Question Trace Guide

| Question | When to use | Check order | Evidence | Decision | Next action |
|:---|:---|:---|:---|:---|:---|
| 왜 특정 주문이 정산 제외됐나? | 주문/회원 문의, 월지급 전 정합성 확인 | 1. 주문 매핑 여부 → 2. 환불/배송/취소 상태 → 3. 정산 제외 조건 → 4. 배치 결과 |  |  |  |
| 왜 postback이 안 갔나? | 매체사 전송 누락 문의 | 1. 이벤트 수신 → 2. 매체사 정책 → 3. Redis/ES/로그 → 4. 재시도/실패 이력 |  |  |  |
| 어떤 링크가 잘못 유입됐나? | LAST_TARGET_URL, sub-id, service-code 오류 | 1. 유입 URL → 2. token/cookie → 3. 정책/target URL → 4. redirect 결과 |  |  |  |
| 왜 주문-유입 매핑이 실패했나? | 주문 이벤트 수신 후 제휴 주문 미생성 | 1. token 존재 → 2. 주문 이벤트 payload → 3. consumer 처리 → 4. 재처리 배치 |  |  |  |
| 왜 월지급 전 정합성 검증이 실패했나? | 월 집계/송금 전 운영 점검 | 1. 일집계 → 2. 월집계 → 3. 지급 대상 → 4. 회계/SAP 요청 |  |  |  |
| 왜 Open API token 검증이 실패했나? | 외부 API client 인증 오류 | 1. Gateway filter → 2. token/auth table → 3. API log → 4. client 권한/만료 |  |  |  |

## Evidence Source Boundaries

| Evidence type | 사용 가능 범위 | 주의 |
|:---|:---|:---|
| code/config | 현재 구현 동작, 라우팅, 배치 job/step, consumer 처리 | 라인/파일 근거가 없으면 확정 표현 금지 |
| wiki | 설계 의도, 정책, 운영 절차, 배경 맥락 | 구현 사실처럼 단정 금지 |
| db | 테이블/컬럼/프로시저/조회 기준 | 실제 schema 근거 우선 |
| github | 변경 이력, 운영 맥락, 리뷰 히스토리 | 현재 동작의 단독 근거로 사용 금지 |
| inferred | 여러 근거 조합 추론 | “추정”, “확인 필요” 표현 필수 |

## Conflict Matrix

| 항목 | Code/Config 근거 | Wiki 근거 | 판단 | 후속 조치 |
|:---|:---|:---|:---|:---|
|  |  |  |  |  |
