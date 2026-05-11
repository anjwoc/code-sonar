# Evidence Audit

## Summary

| Area | Status | Notes |
| --- | --- | --- |
| Code evidence | PASS | API, service, repository claims include file references |
| Config evidence | PASS | Redis, Kafka, DB settings reference config keys |
| Wiki evidence | WARN | Some operating policies are Wiki-only |
| GitHub evidence | WARN | GitHub scan is optional and may be disabled |
| Inferred claims | PASS | Inferred items are marked explicitly |

## Claim Checks

| Claim | Evidence Type | Evidence | Result |
| --- | --- | --- | --- |
| Redis rate limit exists | code/config | `RateLimitFilter`, `application.yml` | PASS |
| Order event consumer updates mapping state | code | `OrderConsumer` | PASS |
| Monthly settlement lock date is operational policy | wiki | `WIKI-SETTLEMENT-001` | WARN |
| Elasticsearch is used for dashboard search | code/config | `SearchClient`, `es.index.orders` | PASS |
| GitHub PR changed payout rule | github | `https://github.example.com/org/repo/pull/100` | WARN |

## Required Follow-up

- Wiki-only policies must not be described as implemented behavior unless code evidence exists.
- GitHub-only evidence should be presented as change history or operating context.
- Secret values must remain `redacted`.
