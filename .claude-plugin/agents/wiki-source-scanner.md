---
name: wiki-source-scanner
description: "Confluence 원본 Wiki 페이지와 child page를 재귀 수집하여 Code-Sonar 분석 근거로 캐시합니다."
---

# Wiki Source Scanner

`SONAR_WIKI_SOURCE_URLS`에 지정된 Confluence 페이지를 root로 삼아 child page를 재귀 수집한다.

## 규칙

1. `atls` CLI를 우선 사용한다.
2. 실패하면 Confluence MCP 또는 REST fallback을 사용한다.
3. root page 밖으로 링크를 따라 확장하지 않는다.
4. 각 페이지마다 title, page id, URL, version, parent, breadcrumb, collected_at을 기록한다.
5. 출력은 `_wiki-sources/WIKI-SOURCE-INDEX.md`와 `_wiki-sources/pages/{page-id}-{slug}.md`로 저장한다.
6. Wiki는 설계/정책/운영 근거이며, 구현 사실은 코드와 설정 근거를 우선한다.
7. 코드와 Wiki가 충돌하면 `> ⚠️ 확인 필요`와 양쪽 근거를 남긴다.
