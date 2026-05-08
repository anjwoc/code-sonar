---
name: github-source-scanner
description: "GitHub MCP/gh/local git 근거를 수집하여 Code-Sonar 분석에 연결합니다."
---

# GitHub Source Scanner

`SONAR_GITHUB_ENABLED=true`일 때 GitHub MCP, `gh`, local git 순서로 repository, PR, commit, workflow 근거를 수집한다.

## 규칙

1. provider가 `auto`이면 GitHub MCP → `gh` → local git 순서로 시도한다.
2. token 값은 문서에 쓰지 않는다.
3. `SONAR_GITHUB_REPOS`가 없으면 `SONAR_TARGET_DIR` 하위 git remote에서 repository를 추론한다.
4. 출력은 `_github/GITHUB-SOURCE-INDEX.md`와 `_github/{repo}/Repository.md`로 저장한다.
5. GitHub 근거는 변경 이력과 운영 맥락이다. 현재 구현 사실은 code/config 근거를 우선한다.
