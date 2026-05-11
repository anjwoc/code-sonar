# Deep Research Skill

이 스킬은 **단일 프로젝트**를 대상으로 도메인, 비즈니스 플로우, 인테그레이션 토폴로지, 환경 매트릭스를 코드 근거 기반으로 완전히 파악하는 심층 분석 파이프라인입니다.

analyze-project 스킬과의 차이:
- **단일 프로젝트에 집중** — 대상 1개, 분석 깊이 최대
- **질문 주입** — 사용자 질문을 분석 디렉티브로 변환해 해당 영역을 우선 탐색
- **크로스레포 추적** — GitHub MCP로 연관 레포를 자동 발견하고 의존성 체인 추적
- **비즈니스 플로우 완전 해석** — 도메인 자동 감지, 상태 머신 추출, 유저 저니 재구성

어떤 도메인(e-commerce, fintech, logistics, auth, CMS...)이든 동일 파이프라인으로 동작합니다.

---

## 진입 조건

다음 중 하나로 실행:
- `/sonar:deep` — config에서 타겟 읽기
- `/sonar:deep <프로젝트경로>` — 경로 직접 지정
- `/sonar:deep <프로젝트경로> --questions <질문파일.md>` — 집중 질문 첨부

`.env` 설정:
```
SONAR_DEEP_TARGET=<프로젝트 경로 또는 이름>
SONAR_DEEP_QUESTIONS=<질문 파일 경로, 선택>
SONAR_DEEP_ENVS=<쉼표 구분 환경명, 선택. 예: mobile,pcweb,mweb>
SONAR_CROSS_REPO_SEARCH=true
SONAR_CROSS_REPO_ORG=<GitHub 조직명, 선택>
```

---

## 파이프라인

### Phase 0 — 초기화 및 질문 파싱

1. `.env`와 `sonar/config/sonar-config.md`를 로드한다.
2. `SONAR_DEEP_TARGET`이 디렉토리면 해당 경로를, 이름이면 `target_dir`에서 매칭한다.
3. `SONAR_DEEP_QUESTIONS` 파일이 있으면 읽어 **질문 디렉티브**를 추출한다.

**질문 디렉티브 추출 규칙:**
- 각 질문에서 핵심 키워드(서비스명, 기술명, 도메인 용어)를 파싱한다.
- 키워드를 두 카테고리로 분류한다:
  - `SEARCH_KEYWORDS`: GitHub MCP 탐색 및 코드 그렙에 사용
  - `FOCUS_AREAS`: 특정 Phase에 집중 디렉티브로 주입 (예: "OAuth", "결제", "정산")
- 질문이 없으면 전 영역을 균등 탐색한다.

---

### Phase 1 — 도메인 감지 및 프로젝트 스니핑

타겟 디렉토리를 스캔하여 다음을 파악한다:

**기술 스택 감지:**
- `package.json`, `build.gradle`, `pom.xml`, `*.csproj`, `Cargo.toml`, `go.mod` 등
- 프레임워크: Spring Boot, NestJS, Django, FastAPI, Rails, Next.js, .NET 등
- 언어: Java, Kotlin, TypeScript, Python, Go, C# 등

**도메인 힌트 수집:**
아래 패턴을 가진 심볼명, 테이블명, API 경로, 설정 키에서 도메인을 유추한다:
- Entity/Model 클래스명 → 핵심 비즈니스 엔티티 목록 추출
- status/state/type/yn 필드 → 비즈니스 상태 후보
- Controller/Router의 URL 패턴 → 서비스 기능 영역
- application.yml / .env 키 → 연동 외부 서비스

**환경 구성 탐지:**
- `application-{profile}.yml`, `*.{env}.ts`, `nginx/*.conf`, `k8s/*.yaml` 등 환경별 설정 파일
- 환경 분기 코드 (`process.env.NODE_ENV`, `@Profile`, `SPRING_PROFILES_ACTIVE`)
- `SONAR_DEEP_ENVS`가 지정된 경우 해당 환경 파일을 우선 수집

**결과:** 도메인 컨텍스트 요약 (에이전트 프롬프트에 주입됨)
```
DOMAIN_CONTEXT:
  type: e-commerce | auth | payment | logistics | cms | ads | ...
  core_entities: [Order, Member, Product, ...]
  tech_stack: [Spring Boot 3.x, Java 17, MySQL, Kafka]
  env_profiles: [local, dev, stg, prd]
  external_integrations: [payment-gateway, sms-provider, ...]
```

---

### Phase 2 — 크로스레포 탐색 (cross-repo-tracer)

`SONAR_CROSS_REPO_SEARCH=true`이고 `SONAR_CROSS_REPO_ORG`가 있으면 실행.

**담당 에이전트:** `sonar/agents/cross-repo-tracer.md`

**탐색 전략:**
1. Phase 0에서 추출한 `SEARCH_KEYWORDS`로 GitHub MCP `search_code` + `search_repositories` 실행
2. 타겟 프로젝트 코드에서 Feign/WebClient/HttpClient/fetch 호출 URL 및 서비스명 추출 → 추가 검색
3. 발견한 연관 레포의 핵심 파일(README, 설정, 인터페이스, 스키마)을 수집
4. 수집한 연관 레포 정보를 Phase 4 `integration-flow-analyst`에 컨텍스트로 전달

**출력:**
- `resources/github/CROSS-REPO-INDEX.md` — 발견 레포 목록 + 연관도 근거
- Phase 4 에이전트 입력으로 전달되는 `cross_repo_context` 객체

---

### Phase 3 — 병렬 심층 분석

Phase 1 결과(DOMAIN_CONTEXT)와 Phase 2 결과(cross_repo_context)를 입력으로 다음 에이전트를 **동시** 스폰한다.

#### 3-A. 환경 매트릭스 분석
**담당 에이전트:** `sonar/agents/env-matrix-analyst.md`
**입력:** 타겟 경로, DOMAIN_CONTEXT, `SONAR_DEEP_ENVS`
**출력:** `deep-research/ENV-MATRIX.md`

도메인이 무엇이든 환경별 차이를 매트릭스로 정리:
- 환경별 진입점(URL, 라우팅 규칙, BFF 분기)
- 환경별 활성 설정(Feature Flag, 외부 서비스 엔드포인트, 인증 방식)
- 환경별 비활성 기능 또는 mock 처리 여부

#### 3-B. 인테그레이션 플로우 분석
**담당 에이전트:** `sonar/agents/integration-flow-analyst.md`
**입력:** 타겟 경로, DOMAIN_CONTEXT, cross_repo_context, FOCUS_AREAS
**출력:** `deep-research/INTEGRATION-FLOW.md`

모든 외부/내부 서비스 연동 지점을 코드 레벨로 추적:
- REST/gRPC/GraphQL 아웃바운드 호출 전체
- 이벤트 퍼블리시/컨슘 (Kafka, RabbitMQ, SQS 등)
- 인증/인가 체인 (OAuth2, JWT, API Key, SSO 등)
- 배치/스케줄 작업의 외부 의존
- FOCUS_AREAS에 해당하는 플로우를 최우선 추적

#### 3-C. 비즈니스 상태 머신 추출
**담당 에이전트:** `sonar/agents/business-workflow-analyst.md` (deep 모드)
**입력:** 타겟 경로, DOMAIN_CONTEXT, FOCUS_AREAS
**출력:** `deep-research/BUSINESS-STATE-MACHINE.md`

- 코드에서 status/state/type 필드를 가진 모든 엔티티 발견
- 각 엔티티의 상태 전이(transition)를 코드 근거(파일:라인)와 함께 추출
- 상태 전이를 유발하는 트리거(API 호출, 이벤트, 배치, 시간 조건) 매핑
- 비즈니스 예외(거부, 취소, 롤백) 경로 별도 표시

#### 3-D. 유저 저니 및 API 플로우 추적
**담당 에이전트:** `sonar/agents/analyst-backend.md` (deep 모드)
**입력:** 타겟 경로, DOMAIN_CONTEXT, FOCUS_AREAS
**출력:** `deep-research/USER-JOURNEY.md`

- 모든 공개 엔드포인트(HTTP Controller, Event Consumer, Batch Job) 목록
- 엔드포인트별 Controller → Service → Repository 완전 호출 체인
- 트랜잭션 경계 및 분산 트랜잭션 패턴
- 비동기 처리 흐름 (Async, EventBus, Message Queue)

---

### Phase 4 — 질문 집중 분석 (FOCUS_AREAS 있을 때)

Phase 3 결과와 cross_repo_context를 바탕으로 각 질문에 대한 코드 근거 기반 답변을 생성한다.

**처리 방식:**
1. 각 질문을 독립 태스크로 분리
2. Phase 3 산출물에서 관련 섹션을 찾아 참조
3. 코드 레벨 근거(파일:라인)가 없으면 추가 코드 탐색 실행
4. 발견 불가 시 `> ⚠️ 확인 필요 — 코드에서 근거를 찾지 못했습니다` 명시

**출력:** `deep-research/QUESTION-ANSWER.md`

---

### Phase 5 — Evidence 통합 및 QA

**담당 에이전트:** `sonar/agents/evidence-auditor.md` + `sonar/agents/qa-reviewer.md`

- Phase 3~4 산출물의 모든 클레임에 근거 태그 확인
- `code:파일:라인`, `config:파일:키`, `github:레포:파일`, `wiki:페이지ID` 형식 준수
- 근거 없는 클레임은 `inferred` 태그 또는 `⚠️ 확인 필요`로 처리

---

### Phase 6 — DEEP-RESEARCH.md 통합 출력

`sonar/templates/DEEP-RESEARCH.md` 템플릿으로 최종 문서 생성.

**출력 경로:** `{output_dir}/{project}/deep-research/`

```
deep-research/
├── DEEP-RESEARCH.md          ← 전체 요약 + 색인 (이 파일 하나로 전체 파악 가능)
├── ENV-MATRIX.md             ← 환경별 차이 매트릭스
├── INTEGRATION-FLOW.md       ← 인테그레이션 토폴로지 + 플로우 다이어그램
├── BUSINESS-STATE-MACHINE.md ← 비즈니스 상태 머신
├── USER-JOURNEY.md           ← 유저 저니 + API 플로우
└── QUESTION-ANSWER.md        ← 질문별 코드 근거 기반 답변 (질문 있을 때만)
```

---

## 품질 기준

| 항목 | 기준 |
|:---|:---|
| 도메인 감지 | 타겟 프로젝트의 핵심 엔티티 3개 이상 코드에서 확인 |
| 상태 머신 | status/state 필드 보유 엔티티의 전이 다이어그램 생성 |
| 인테그레이션 | 아웃바운드 호출 전체 목록 (누락 0건) |
| 환경 매트릭스 | SONAR_DEEP_ENVS에 명시된 환경 전체 컬럼 포함 |
| 질문 답변 | 각 질문에 코드 근거(파일:라인) 1개 이상 또는 ⚠️ 명시 |
| Evidence | 모든 핵심 클레임에 근거 태그 |
