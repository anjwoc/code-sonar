# Index

## Project Summary

`commerce-api`는 주문, 유입, 정산 대상 판정, 후속 이벤트 발행을 처리하는 도메인 API 예시 프로젝트다.

## Document Map

| Document | Purpose |
| --- | --- |
| Architecture & Dependencies | 모듈 구조, 외부 시스템, 저장소 의존성 |
| Backend API | REST API, 인증, 요청/응답, 오류 |
| Business Logic | 핵심 정책, 예외 처리, 알고리즘 |
| Data Flow | 요청 흐름, 이벤트 흐름, 업무 데이터플로우 |
| Database Schema | 테이블, 인덱스, 데이터 보관 정책 |

## Key Responsibilities

- 외부 요청을 도메인 명령으로 변환한다.
- 주문과 유입 데이터를 매핑한다.
- Redis 기반 유량 제어와 임시 상태를 관리한다.
- Oracle, MongoDB, Redis, Elasticsearch에 목적별로 접근한다.
- 배치와 이벤트 consumer가 재처리할 수 있도록 상태를 남긴다.

## Evidence

| Claim | Evidence |
| --- | --- |
| Redis rate limit을 사용한다 | `src/main/java/example/RateLimitFilter.java` |
| 주문 매핑 실패 상태를 저장한다 | `src/main/java/example/OrderMappingService.java` |
| 일별 정산 조회 API가 있다 | `src/main/java/example/AdminSettlementController.java` |
