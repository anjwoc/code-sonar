# Build Schema Skill

이 스킬은 단일 프로젝트 또는 멀티 프로젝트 분석 결과에서  
**데이터베이스 스키마 + ERD + 크로스서비스 엔티티 관계 + 비즈니스 플로우별 엔티티 상태 생명주기**를 생성하는 파이프라인입니다.

analyze-project 스킬과 함께 또는 독립 실행 가능합니다.

---

## 진입 조건

- `/sonar:schema` 커맨드 실행
- `analyze-project` SKILL의 STEP 2에서 백엔드 프로젝트 감지 시 자동 스폰

`.env` 관련 설정:
```
SONAR_DB_ANALYSIS=true               # 기본값. false면 스킵
SONAR_MCP_DEEP_SCAN=ask              # true/false/ask — MCP devdb 활용 여부
SONAR_LIFECYCLE_ANALYSIS=true        # 기본값. false면 Phase 3 (엔티티 생명주기) 스킵
```

---

## 파이프라인

### Phase 0 — 대상 프로젝트 확인

1. `SONAR_TARGET_DIR` 또는 인자로 전달된 프로젝트 경로를 사용한다.
2. 이미 `analyze-project`가 실행됐으면 `{output_dir}/{project}/Architecture & Dependencies.md` 에서 기술 스택 정보를 재활용한다.
3. `SONAR_MCP_DEEP_SCAN` 설정에 따라 MCP devdb 활성화 여부를 결정한다.

---

### Phase 1 — 프로젝트별 DB 스키마 분석 (병렬)

각 프로젝트에 대해 `sonar/agents/db-schema-analyst.md` 에이전트를 **병렬** 스폰한다.

에이전트 입력:
```
- 타겟 경로: {project_path}
- ORM 힌트: {analyze-project 결과에서 추출된 tech_stack}
- MCP 가용: {true/false}
- 출력 경로: {output_dir}/{project}/Database & Schema.md
```

에이전트 출력:
- `{output_dir}/{project}/Database & Schema.md` (DATABASE.md 템플릿)
- 집계용 `entity_ownership` 객체 (서비스명 → 소유 테이블 목록)

---

### Phase 2 — 크로스서비스 ER 다이어그램 생성

Phase 1 결과를 취합하여 시스템 전체 `ENTITY-RELATIONSHIP.md` 를 생성한다.

**처리 규칙:**
1. 모든 프로젝트의 `entity_ownership` 를 병합
2. 동일 테이블명이 2개 이상 서비스에서 발견되면 → 공유 패턴으로 표시
3. 이벤트(Kafka/MQ) 토픽을 통한 간접 연결도 포함
4. 서비스-테이블 오너십 flowchart + 핵심 시스템 erDiagram 생성

**출력:**
- `{output_dir}/ENTITY-RELATIONSHIP.md`

---

### Phase 3 — 엔티티 상태 생명주기 분석 (병렬)

`SONAR_LIFECYCLE_ANALYSIS=false` 가 아닌 한 각 프로젝트에 대해  
`sonar/agents/entity-lifecycle-analyst.md` 에이전트를 **Phase 1과 병렬** 스폰한다.

에이전트 입력:
```
- 타겟 경로: {project_path}
- 엔티티 힌트: Phase 1의 db-schema-analyst 결과 (이미 추출된 엔티티 목록)
- 출력 경로: {output_dir}/{project}/Entity State Lifecycle.md
```

에이전트 출력:
- `{output_dir}/{project}/Entity State Lifecycle.md` (ENTITY-STATE-LIFECYCLE.md 템플릿)
- `entity_state_map` 객체: {엔티티명 → 상태 필드 → 전이 트리거 목록}

**`entity_state_map` 활용:**
- `business-workflow-analyst`에게 전달 → `_business/Business Workflow.md`의 업무 상태 섹션 강화
- `ENTITY-RELATIONSHIP.md` 생성 시 엔티티별 상태 필드 포함

---

### Phase 4 — 크로스서비스 ER 다이어그램 생성

Phase 1 + Phase 3 결과를 취합하여 시스템 전체 `ENTITY-RELATIONSHIP.md` 를 생성한다.

**처리 규칙:**
1. 모든 프로젝트의 `entity_ownership` 를 병합
2. 동일 테이블명이 2개 이상 서비스에서 발견되면 → 공유 패턴으로 표시
3. 이벤트(Kafka/MQ) 토픽을 통한 간접 연결도 포함
4. Phase 3의 `entity_state_map`에서 크로스 엔티티 상태 연동 정보 추가
5. 서비스-테이블 오너십 flowchart + 핵심 시스템 erDiagram 생성

**출력:**
- `{output_dir}/ENTITY-RELATIONSHIP.md`

---

### Phase 5 — Index 연결

`{output_dir}/Index.md` 에 DB 분석 섹션을 추가한다:

```markdown
## 데이터베이스 & 엔티티 관계

| 문서 | 내용 |
|:---|:---|
| [ENTITY-RELATIONSHIP.md](./ENTITY-RELATIONSHIP.md) | 서비스 간 테이블 오너십 + 시스템 전체 ERD |
| [{project}/Database & Schema.md](./{project}/Database & Schema.md) | {project} DB 스키마 + ERD + SP |
| [{project}/Entity State Lifecycle.md](./{project}/Entity State Lifecycle.md) | {project} 엔티티별 비즈니스 플로우 × 상태 변화 |
```

---

### Phase 6 — Evidence 및 QA

- `evidence-auditor`: 모든 테이블명·컬럼명에 코드 근거 확인
- `qa-reviewer`: ERD 관계선 cardinality와 코드 일치 여부 확인

---

## 품질 기준

| 항목 | 기준 |
|:---|:---|
| ERD 존재 | 엔티티 3개 이상 발견 시 Mermaid erDiagram 필수 |
| 테이블 카탈로그 | 핵심 테이블의 PK, FK, NOT NULL 컬럼 코드 근거 포함 |
| 오너십 매핑 | 멀티 프로젝트 분석 시 서비스-테이블 매핑 표 존재 |
| 근거 태그 | 모든 테이블/컬럼 항목에 `[code:]` 또는 `[db:]` 태그 |
| SP 인벤토리 | SP 호출 감지 시 섹션 5 필수 작성 |
| 상태 생명주기 | 상태 필드 보유 엔티티의 `Entity State Lifecycle.md` 생성 |
| 비즈니스 트리거 | 각 상태 전이의 트리거(API/이벤트/배치) 코드 근거 포함 |
| 크로스 엔티티 연동 | 상태 변화가 다른 엔티티에 영향 주는 연쇄 관계 표시 |
| ⚠️ 명시 | 확인 불가 항목은 `⚠️ 확인 필요` 로 명시 |
