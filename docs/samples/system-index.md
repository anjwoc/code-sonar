# Index

## System Overview

Commerce Platform은 외부 사용자 요청, 관리자 작업, API 처리, 이벤트 처리, 배치 정산, 저장소 접근을 여러 프로젝트가 나누어 처리하는 예시 시스템이다.

```mermaid
flowchart LR
  EXT["외부 사용자<br/>Browser / App / Open API"]

  subgraph ADMIN_LAYER["어드민 계층"]
    AW["commerce-admin-web"]
    AA["commerce-admin-api"]
  end

  subgraph FRONT_LAYER["프론트엔드 계층"]
    WEB["commerce-web<br/>고객 포털"]
  end

  subgraph GATEWAY_LAYER["게이트웨이 계층"]
    GW["commerce-gateway-api<br/>Spring Cloud Gateway"]
  end

  subgraph CORE_LAYER["백엔드 핵심 계층"]
    BFF["commerce-bff-api<br/>BFF / WebFlux"]
    API["commerce-api<br/>도메인 API"]
    POST["commerce-postback-api<br/>후속 처리"]
  end

  subgraph EVENT_LAYER["이벤트 계층 / Kafka"]
    PRODUCER["inflow-producer"]
    KAFKA["Kafka<br/>Central Broker"]
    CONSUMER["Consumers<br/>order / payment / refund"]
  end

  subgraph BATCH_LAYER["배치 계층"]
    BATCH["Settlement / Messaging<br/>Retention Batch"]
  end

  subgraph STORAGE_LAYER["저장소"]
    ORACLE[("Oracle<br/>COMMERCE")]
    REDIS[("Redis")]
    MONGO[("MongoDB")]
    ES[("Elasticsearch")]
  end

  EXT -->|HTTPS| WEB
  EXT -->|HTTPS| GW
  AW -->|Feign| AA
  AA -->|Feign| BFF
  WEB -->|Feign| BFF
  GW -->|Route| BFF
  BFF -->|WebClient| API
  PRODUCER -->|publish| KAFKA
  KAFKA -->|subscribe| CONSUMER
  CONSUMER -->|HTTP| POST
  API -->|JDBC/JPA| ORACLE
  API -->|Spring Data| MONGO
  API -->|Redis| REDIS
  POST -->|Redis| REDIS
  POST -->|Elasticsearch| ES
  BATCH -->|JDBC/JPA| ORACLE
  BATCH -->|index/read| ES
```

## Project Map

| Project | Responsibility | Main Evidence |
| --- | --- | --- |
| commerce-admin | 운영자 화면과 관리자 API | `commerce-admin/Backend API.md` |
| commerce-api | 핵심 도메인 처리와 저장소 접근 | `commerce-api/Business Logic.md` |
| commerce-gateway | 외부 요청 라우팅과 보안 정책 | `commerce-gateway/Routing & Security.md` |
| commerce-batch | 일별 집계와 월별 정산 배치 | `commerce-batch/Batch Jobs.md` |

## Operations Inventory

| Item | Value | Evidence |
| --- | --- | --- |
| API domain | `api.example.com` | Wiki source `WIKI-001` |
| Admin domain | `admin.example.com` | config `application-prod.yml` |
| Redis usage | rate limit, temporary state, token cache | code `RedisRateLimiter` |
| Secret values | redacted | policy |
