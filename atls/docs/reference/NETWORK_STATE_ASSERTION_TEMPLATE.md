# Network / State Assertion Template

## 목적

이 문서는 E2E에서 `영상만으로는 부족한 부분`을 보강하기 위한 assertion 템플릿을 정의한다.

주요 대상:

- payload mapping
- state persistence
- localStorage / sessionStorage
- query param / route state
- API response branching

## 기본 원칙

1. `network assertion`과 `state assertion`은 UI assertion과 분리한다.
2. 영상은 증거이지만 payload/state 정합성의 판정 기준이 되지 않는다.
3. source가 없는 필드는 assert하지 않는다.
4. exact key/value를 요구하려면 PRD, Jira, OpenAPI, existing API contract 중 하나가 있어야 한다.

## Network Assertion Template

```ts
type NetworkAssertion = {
  assertion_id: string;
  purpose: string;
  trigger_action: string;
  request_match: {
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    url_pattern: string;
  };
  expected_request?: Array<{
    path: string;
    operator: 'equals' | 'contains' | 'not_exists' | 'gte' | 'lte';
    value?: unknown;
    source_ref: string;
  }>;
  expected_response?: Array<{
    path: string;
    operator: 'equals' | 'contains' | 'not_exists' | 'gte' | 'lte';
    value?: unknown;
    source_ref: string;
  }>;
  forbidden_request?: Array<{
    path: string;
    operator: 'exists' | 'equals' | 'contains';
    value?: unknown;
    source_ref: string;
  }>;
  evidence: Array<'request_json' | 'response_json' | 'har' | 'video' | 'screenshot'>;
};
```

## State Assertion Template

```ts
type StateAssertion = {
  assertion_id: string;
  purpose: string;
  checkpoint: 'before_action' | 'after_action' | 'after_reload' | 'after_reentry';
  state_source: 'local_storage' | 'session_storage' | 'url_query' | 'dom' | 'redux_store_like';
  expected: Array<{
    key: string;
    operator: 'equals' | 'contains' | 'not_exists';
    value?: unknown;
    source_ref: string;
  }>;
  forbidden?: Array<{
    key: string;
    operator: 'exists' | 'equals' | 'contains';
    value?: unknown;
    source_ref: string;
  }>;
  evidence: Array<'state_dump' | 'video' | 'screenshot'>;
};
```

## 사용 규칙

### Network Assertion을 써야 하는 경우

- `campaignName` / `campaignGroupName` 분리 전달
- `maxBid`, `firstSlotOverbidRatio` 같은 payload key
- `bidPrice` 생략/포함 조건
- 잘못된 fallback field 전송 여부

### State Assertion을 써야 하는 경우

- 최근 등록 유형 복원
- seller 전환 후 active seller 유지
- 최상단 입찰가 저장값 복원
- 모달/dirty state 유지 여부

## 구현 예시

### 예시 1. payload mapping

```ts
const requestPromise = page.waitForRequest((request) =>
  request.url().includes('/registration/addSolution') && request.method() === 'POST'
);

await page.getByRole('button', { name: '등록하기' }).click();

const request = await requestPromise;
const body = request.postDataJSON();

expect(body.solution.campaignList[0].campaignName).toBe('캠페인-A');
expect(body.solution.campaignList[0].adgroupList[0].itemId).toBeDefined();
expect(body.solution.campaignList[0].campaignGroupName).toBeUndefined();
```

### 예시 2. state persistence

```ts
await page.reload();
await expect(page.locator('#top-bid-input')).toHaveValue('130');

const savedType = await page.evaluate(() => window.localStorage.getItem('LAST_AD_TYPE'));
expect(savedType).toBe('semi-auto');
```

## 증거 부족 시 처리

아래 중 하나라도 없으면 assertion을 추가하지 않는다.

- payload 구조를 보여주는 PRD / OpenAPI / Jira 코멘트
- 상태 저장 키 이름을 보여주는 기존 구현 계약
- exact text나 exact field의 source

이 경우는 manifest에 이렇게 남긴다.

- `assertion_status: blocked_by_missing_evidence`
- `required_material: <사용자가 가져와야 할 자료>`

## 사용자에게 요청해야 하는 자료 예시

- 저장 후 재진입 기대 상태를 설명한 Jira 코멘트
- API request/response 샘플
- exact alert 문구 캡처
- Figma interaction spec
