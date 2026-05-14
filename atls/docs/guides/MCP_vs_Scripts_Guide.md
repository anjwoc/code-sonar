# Jira & Confluence 관리 유틸리티 및 MCP 연동 가이드

이 폴더에는 사용자가 언제든지 손쉽게 커맨드 환경 및 AI로 호출하여 업무를 자동화할 수 있는 **직접 파이썬(Python) 기반 유틸리티 스크립트**와 `atls` 패키지 자료가 저장되어 있습니다.

## 📁 1. 직접 작성된 유틸리티 파일 목록 (`/Users/jaecjeong/lab/memo/atsl/scripts/legacy/`)

| 파일명 | 기능 설명 | 주요 예시 |
|--------|-----------|-----------|
| `jira_worklog_manager.py` | 특정 지라(Jira) 티켓에 워크로그를 추가하거나, 수정 또는 조회합니다. | `python3 scripts/legacy/jira_worklog_manager.py add --issue GEMINI-1788 --comment "완료" --time "15m"` |
| `confluence_wiki_manager.py` | 개인 위키(Confluence)의 문서를 검색, 하위 문서 생성, 또는 수정 덮어쓰기를 수행합니다. | `python3 scripts/legacy/confluence_wiki_manager.py search --title "New ADCenter"` |
| `jira_issue_viewer.py` | 지라 티켓 번호를 입력하면 제목, 상세 내용, 담당자, 상태를 직관적으로 조회합니다 | `python3 scripts/legacy/jira_issue_viewer.py GEMINI-1234` |

---

## 🤖 2. MCP (`mcp-atlassian`) 도구를 사용해서 "자연어만으로" 쉽게 할 수 있는 작업들

현재 시스템에는 `uvx mcp-atlassian` 혹은 `github` MCP 서버가 환경으로 등록되어 있습니다(*환경변수 자동 로드*). 
위에서 제작한 스크립트 외에, **"AI에게 그냥 자연어로 물어봐서 즉시 가능한 범주"**는 다음과 같습니다.

### ✅ 2.1 지라(Jira) 관련 가능한 자연어 지시사항
* **이슈 내용 요약 요청**
  > *"GEMINI-1788번 이슈 내용이 뭔지 한국어로 짧게 3줄 요약해줘"*
* **이슈 상태 및 담당자 변경 확인**
  > *"현재 내가 담당자(assignee='정재철')로 할당된 상태가 'In Review'인 이슈들을 모두 가져와서 표로 정리해줘"*
* **간단한 코멘트 추가**
  > *"GEMINI-1776 번에 '해당 이슈 프론트 이슈에서 수정 완료했습니다.' 라고 댓글(Comment) 달아줘"* (주의: 워크로그가 아닌 일반 스레드 댓글)
* **새로운 버그(Bug) 이슈 생성**
  > *"이번에 발견한 결함 건으로 '로그인 세션 만료 알럿 오류'라는 제목의 지라 버그 티켓 하나 생성해줘. 디스크립션은 알아서 포맷팅해."*

### ✅ 2.2 컨플루언스(Confluence) 관련 가능한 자연어 지시사항
* **페이지 검색 및 내용 요약 읽기**
  > *"내 개인 스페이스(~jaecjeong)에 있는 'ADCenter API 명세서' 페이지를 찾아서 내용 좀 읽고 주요 목차만 알려줘"*
* **기존 문서 내용 중 일부 추출 정보 확인**
  > *"위키 문서 ID 12345678번에 적혀있는 배포 타임라인이 어떻게 되는지 확인해줘"*

### ⚠️ 제약사항 (왜 커스텀 Python 스크립트가 필요한가?)
* **정밀한 시간 단위 조작 및 일관성:** Worklog(소요 시간, 특정 Start Time 명시 등)의 다량 비동기 생성, 수정 작업 등은 MCP의 순정 툴이 제공하는 파라미터 제약을 넘어서기 마련입니다. 
* **정교한 HTML 레이아웃 업로드:** Confluence 위키 페이지 생성 시 복잡한 HTML 문서 서식이나 템플릿(표, 컬러 배경 등)을 통째로 올리는 작업은 REST API로 직접 `storage` 데이터를 밀어 넣는 방식이 훨씬 안전합니다.

### 🚀 사용 팁
향후 AI와 협업할 때 **"내가 만들어둔 Lab의 python 스크립트들을 활용해서 워크로그 일괄 수정해줘"**라고 지시하시면 AI가 위 스크립트를 재사용하여 즉시 업무를 자동화해 줍니다.
