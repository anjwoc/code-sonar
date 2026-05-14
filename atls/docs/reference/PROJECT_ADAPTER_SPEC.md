# Project Adapter Spec

## 목적

`project adapter`는 같은 acceptance manifest를 프로젝트별로 실행 가능하게 만드는 설정 계층이다.

`ATLS core`는 요구조건과 케이스 정의를 담당하고, 프로젝트 adapter는 실행 환경 차이를 담당한다.

## 책임

- `base_url`
- 인증 전략
- 테스트 계정 정책
- storageState 경로
- selector policy
- seed data 전략
- API mock / route interception 정책
- CI secret 사용 방식

## 인증 전략 유형

### 1. storageState bootstrap

- 가장 일반적
- `auth.setup.ts`에서 로그인 후 세션 저장
- 이후 테스트는 `storageState` 재사용

### 2. API login

- 로그인 API를 호출하고 cookie / token을 주입
- UI 로그인 플로우가 불안정할 때 유리

### 3. bootstrap route

- 테스트 환경 전용 route에서 세션 생성
- 가장 안정적이지만 서버 지원 필요

### 4. manual credentials

- 권장하지 않음
- 개인 계정 사용 금지

## adcenter 권장안

### 현재 문제

- Playwright 설정은 있으나 `tests/e2e`, `auth.setup.ts`, `.env.e2e`가 실제로 비어 있다.
- 즉 runner는 있으나 인증 하네스가 완성되지 않은 상태다.

### 권장 전략

1. dedicated test account 준비
2. 로컬용 `.env.e2e.local` 사용
3. CI는 GitHub Secret 사용
4. `auth.setup.ts`에서 storageState 생성
5. 가능하면 추후 API login 또는 bootstrap login 도입
6. `adcenter` 테스트 계정은 반드시 `GMKT / G마켓 로그인` 탭으로 로그인한다. `ESMPLUS` 로그인은 기본 하네스 범위에서 제외한다.

## adapter 예시 필드

```json
{
  "project_key": "adcenter",
  "runner": "playwright",
  "base_url": "http://localhost:3000",
  "auth": {
    "strategy": "storage_state_bootstrap",
    "login_provider": "GMKT",
    "login_tab_selector": ".button__tab--gmarket",
    "env_file": ".env.e2e.local",
    "required_env": [
      "E2E_GMARKET_ID",
      "E2E_GMARKET_PASSWORD"
    ],
    "storage_state_path": "tests/.auth/user.json"
  },
  "selectors": {
    "prefer_test_id": true,
    "fallback_order": [
      "data-testid",
      "role",
      "label",
      "text"
    ]
  },
  "artifacts": {
    "html_report_dir": "tests/results/html-report",
    "artifact_dir": "tests/results/artifacts"
  }
}
```

## 보안 원칙

1. 개인 계정 사용 금지
2. 비밀번호를 spec, test code, manifest에 직접 기록하지 않음
3. `.env.e2e.local`은 git ignore
4. CI secret은 최소 권한 테스트 계정만 사용
