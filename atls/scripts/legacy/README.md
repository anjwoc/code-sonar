# Legacy Scripts

이 디렉토리는 `atls`로 아직 완전히 흡수되지 않은 단독 유틸리티를 보관한다.

- `jira_issue_viewer.py`
- `jira_worklog_manager.py`
- `confluence_wiki_manager.py`

원칙:

- 신규 기능은 가능하면 `src/atls/cli.py` 또는 `src/atls/analysis/*`에 구현한다.
- 반복 사용되는 legacy 스크립트는 검증 후 `atls` 고수준 명령으로 승격한다.
