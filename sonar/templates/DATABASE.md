# DATABASE — {프로젝트명} 데이터베이스 분석

> 생성일: {날짜}  
> 분석 대상: `{타겟 경로}`  
> ORM/데이터 접근: `{JPA / MyBatis / QueryDSL / EF Core / Dapper / Prisma / TypeORM / 복합}`  
> MCP devdb 활용: `{가능 / 불가 — 코드 정적 분석만}`

---

## 1. 데이터 소스 구성

| 항목 | 값 | 근거 |
|:---|:---|:---|
| DB 종류 | `{MySQL / PostgreSQL / MSSQL / Oracle / ...}` | [config: {파일}:{키}] |
| JDBC/연결 URL | `{url (민감정보 마스킹)}` | [config: {파일}:{키}] |
| 연결 풀 | `{HikariCP / DBCP / ...} / max={N}` | [config: {파일}:{키}] |
| 멀티 데이터소스 | `{없음 / 있음 — Primary: {이름}, Secondary: {이름}}` | [code: {파일}:{라인}] |
| Schema/Database | `{스키마명 또는 DB명}` | [config: {파일}:{키}] |

---

## 2. 핵심 ERD

> 이 프로젝트가 직접 소유하거나 주로 사용하는 핵심 엔티티 간 관계도.  
> 전체 시스템 크로스서비스 ER은 `ENTITY-RELATIONSHIP.md` 참조.

```mermaid
erDiagram
    {Entity1} {||--o{} {Entity2} : "{관계 설명}"
    {Entity1} {
        {type} {pk_column} PK
        {type} {column1}
        {type} {column2}
        {type} {fk_column} FK
    }
    {Entity2} {
        {type} {pk_column} PK
        {type} {column1}
        {type} {fk_column} FK
    }
```

> **ERD 근거:** `[code: {Entity 파일 경로}:{라인}]`  
> **⚠️ 확인 필요 항목:** {코드에서 확인 불가한 관계 목록}

---

## 3. 테이블 카탈로그

> 코드에서 확인된 핵심 테이블. MCP devdb 가능 시 실제 스키마로 보완.

### {테이블명 / 엔티티명}

**매핑 클래스:** `{파일 경로}:{라인}` [code]  
**테이블명:** `{실제_테이블명}` (코드 상 `@Table(name="...")` 또는 convention)

| 컬럼명 | 타입 | 제약 | 설명 | 근거 |
|:---|:---|:---|:---|:---|
| `{pk}` | `{VARCHAR/BIGINT/...}` | PK, NOT NULL | {설명} | [code: {파일}:{라인}] |
| `{col}` | `{type}` | NOT NULL | {설명} | [code: {파일}:{라인}] |
| `{fk}` | `{type}` | FK → `{참조테이블.컬럼}` | {설명} | [code: {파일}:{라인}] |

**인덱스:**

| 인덱스명 | 컬럼 | 타입 | 용도 |
|:---|:---|:---|:---|
| `{idx_name}` | `{col1}, {col2}` | {UNIQUE/일반} | {조회 용도} |

---

{테이블 반복}

---

## 4. ORM / 데이터 접근 패턴

### 4-A. ORM 사용 현황

| 패턴 | 사용 여부 | 대표 파일 |
|:---|:---|:---|
| JPA/Hibernate (@Entity) | {✅/❌} | `{파일}` |
| MyBatis (Mapper XML) | {✅/❌} | `{파일}` |
| QueryDSL | {✅/❌} | `{파일}` |
| Spring Data JPA (Repository) | {✅/❌} | `{파일}` |
| JDBC Template (직접 쿼리) | {✅/❌} | `{파일}` |
| Native Query (@Query nativeQuery=true) | {✅/❌} | `{파일}` |

### 4-B. 트랜잭션 경계

| 서비스 / 메서드 | 범위 | 격리 수준 | 비고 |
|:---|:---|:---|:---|
| `{ServiceClass.method()}` | `@Transactional` | {기본/SERIALIZABLE/...} | [code: {파일}:{라인}] |

### 4-C. N+1 리스크

> 코드에서 감지된 잠재적 N+1 쿼리 발생 지점.

| 위치 | 패턴 | 리스크 | 권고 |
|:---|:---|:---|:---|
| `{파일}:{라인}` | `{LazyLoading / findAll() 후 루프}` | {높음/중간} | {FetchJoin / @BatchSize 권고} |

---

## 5. SP / 프로시저 분석

> SP 호출이 없으면 이 섹션은 `> 해당 없음` 으로 표시.

### SP 목록

| SP명 | DB.Schema | 호출 위치 | 용도 |
|:---|:---|:---|:---|
| `{sp_name}` | `{db}.{schema}` | [code: {파일}:{라인}] | {처리 목적} |

### SP 상세: `{sp_name}`

| 항목 | 내용 |
|:---|:---|
| DB / Schema | `{db_name}.{schema_name}` |
| 호출 방식 | `{EXEC / CALL / CommandType.StoredProcedure}` |
| 호출 위치 | [code: {파일}:{라인}] |

**입력 파라미터:**

| 파라미터명 | 타입 | 방향 | 설명 |
|:---|:---|:---|:---|
| `@{param}` | `{type}` | IN | {설명} |

**처리 요약:** {SP 처리 내용 요약. 코드 접근 불가 시 호출부 기준 추정}

> ⚠️ SP 내부 코드: {접근 가능 / 접근 불가 — 호출부 파라미터 기준 추정}

---

## 6. 캐시 전략

| 대상 | 캐시 종류 | TTL | 무효화 조건 | 근거 |
|:---|:---|:---|:---|:---|
| `{엔티티/API}` | `{Redis / Caffeine / @Cacheable}` | `{N초/없음}` | `{이벤트/조건}` | [code: {파일}:{라인}] |

---

## ⚠️ 확인 필요

| 항목 | 이유 |
|:---|:---|
| {항목1} | MCP devdb 없이 코드만으로 확인 불가 |
| {항목2} | SP 내부 로직 접근 불가 |
