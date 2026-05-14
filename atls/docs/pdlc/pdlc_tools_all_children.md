# PDLC 플랫폼 - Tools

- Root Page ID: `538918918`
- Total Pages Collected: `18`
- Source URL: https://wiki.gmarket.com/spaces/PDLC/pages/538918918/PDLC+%ED%94%8C%EB%9E%AB%ED%8F%BC+-+Tools

## Page Tree

- PDLC 플랫폼 - Tools (538918918)
  - Roster CLI (538918920)
    - AI 에이전트 사용자 가이드 (AI Agent User Guide) (543086995)
    - CI/CD 배포자 가이드 (CI/CD Deployer Guide) (543086997)
    - Google 관리자 가이드 (Google/GCP Admin Guide) (543087003)
    - JQL 자동 변환 가이드 (JQL Transformation Guide) (543087011)
    - Jira 관리자 가이드 (Jira Admin Guide) (543087005)
    - Roster CLI 설정 가이드 (Strict OAuth 2.0) (543086991)
    - Roster CLI 응용 - org3 수준의 개발 프로젝트 월간 조회 (543066760)
      - (Deprecated)Roster CLI 응용 - org3 수준의 개발 프로젝트 월간 조회 (543087324)
    - Story, Task, Bug type issue로 Epic, Initiative type issue까지 한번에 조회하기 (543086871)
    - console 명령어 사용 가이드 (543086993)
    - 개발자 가이드 (Developer Guide) (543087001)
    - 데이터 엔지니어 가이드 (Data Engineer Guide) (543086999)
    - 리소스 배분(Allocation) 규칙 가이드 (543086989)
    - 비즈니스 활용 시나리오 (Use Cases) (543087007)
    - 일반 사용자 가이드 (User Guide) (543087009)
  - 중요 필드 입력 누락 방지, 입력 독려 (543086919)

## PDLC 플랫폼 - Tools

- Page ID: `538918918`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/538918918/PDLC+%ED%94%8C%EB%9E%AB%ED%8F%BC+-+Tools
- Depth: `0`

_본문 없음 또는 children 매크로만 포함_

---

### Roster CLI

- Page ID: `538918920`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/538918920/Roster+CLI
- Depth: `1`

Project homepage: <https://github.gmarket.com/jseungbum/roster>

Jira 이슈 데이터를 분석하여 프로젝트 및 담당자별 리소스 투입 현황을 계산하고 시각화하는 도구입니다. 일정 데이터를 월별 투입량(days)으로 수치화하여 리소스 현황 파악을 지원합니다.

## 1\. 개요 및 주요 기능

  * **작업별 업무량 및 일정 확인:** 특정 기간 내 프로젝트/담당자별 투입량(days) 조회
  * **계획 대비 실적 분석:** 업무 로그(Worklog) 기반 실제 투입 리소스 조회
  * **데이터 성격 정의:** Epic, Initiative 등 상위 단위는 가이드라인으로 활용하고, 실제 리소스 계산은 하위 실행 공수(Story, Task, Bug)를 기준으로 자동 집계
  * **출력 포맷 다양화:** Console 표, Markdown, CSV, JSON, Google Sheets 내보내기 지원



## 2\. 역할별 가이드 문서

Roster CLI를 사용하는 각 사용자 역할에 맞춰 가이드 문서가 세분화되어 있습니다. 본인에게 해당하는 가이드를 확인해 주세요.

  * 일반 사용자 가이드 (User Guide) (설치 및 실행 방법 안내)
  * AI 에이전트 사용자 가이드 (AI Agent User Guide) (Gemini, Claude 등 LLM과 연동하려는 사용자용)
  * 개발자 가이드 (Developer Guide) (코드를 수정하거나 실행 파일을 배포하려는 개발자용)
  * CI/CD 배포자 가이드 (CI/CD Deployer Guide) (Headless 환경에서 자동화 배치를 구성하려는 담당자용)
  * Jira 관리자 가이드 (Jira Admin Guide) (사내 Jira OAuth 2.0 앱을 생성하려는 관리자용)
  * Google 관리자 가이드 (Google/GCP Admin Guide) (사내 GCP OAuth 2.0 앱을 생성하려는 관리자용)
  * 데이터 엔지니어 가이드 (Data Engineer Guide) (DB 연동 및 BI 대시보드 구축을 담당하는 데이터 엔지니어용)



## 3\. 비즈니스 활용 사례 (Use Cases)

데이터를 바라보는 관점과 목적에 따라 Roster CLI를 어떻게 업무에 활용할 수 있는지 구체적인 시나리오를 제공합니다.

  * 비즈니스 활용 시나리오 (Use Cases) (실무자, 피플 매니저, PM, PMO 관점의 활용법 및 JQL 예시)



## 4\. 기타 세부 문서

  * Roster CLI 설정 가이드 (Strict OAuth 2.0)
  * 리소스 배분(Allocation) 규칙 가이드

---

#### AI 에이전트 사용자 가이드 (AI Agent User Guide)

- Page ID: `543086995`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543086995/AI+%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8+%EC%82%AC%EC%9A%A9%EC%9E%90+%EA%B0%80%EC%9D%B4%EB%93%9C+AI+Agent+User+Guide
- Depth: `2`

이 문서는 Gemini CLI, Claude Desktop, Cursor 등 AI 에이전트(LLM) 환경에서 `roster` 프로그램을 직접 도구(Tool)로 연동하여 사용하려는 사용자를 위한 통합 가이드입니다.

Roster CLI는 AI 에이전트와 연동할 수 있도록 **Gemini Skill** 방식과 범용 **MCP(Model Context Protocol)** 방식 두 가지를 모두 지원합니다.

## 1\. 사전 준비 사항 (공통)

AI 에이전트가 Roster CLI를 대신 실행하려면, 먼저 로컬 환경에서 **Jira 자격 증명 토큰이 정상적으로 발급되어 있어야** 합니다.

  1. 터미널에서 다운로드 받은 프로그램을 1회 실행합니다.
[code]./roster doctor
         
[/code]

  2. 자동으로 열리는 브라우저에서 사내 Jira 계정으로 로그인을 완료합니다.
  3. 인증이 완료되면 `~/.config/roster/jira_token.json` 파일에 접속 권한(Refresh Token)이 저장되며, 이후 에이전트는 사용자의 개입 없이 백그라운드에서 데이터를 가져올 수 있게 됩니다.



## 2\. Gemini Skill 방식 연동 (Gemini CLI 전용)

Gemini CLI 환경을 사용 중이라면 제공되는 스크립트를 통해 원클릭으로 스킬을 등록할 수 있습니다.

### 설치 및 등록

터미널에서 아래 명령을 실행하여 프로젝트를 전역(Global) 환경에 스킬로 등록하세요.

  * **Windows (PowerShell):**
[code]powershell -ExecutionPolicy Bypass -File scripts\install-skill.ps1 --global
        
[/code]

  * **macOS / Linux (Bash):**
[code]bash scripts/install-skill.sh --global
        
[/code]




### 사용 예시

등록이 완료되면 Gemini CLI에서 다음과 같이 자연어로 요청할 수 있습니다.

  * "이번 분기 Payment 팀의 리소스 투입량을 분석해줘."
  * "업무가 과하게 할당된 담당자가 있는지 확인해줘."
  * "A 프로젝트의 공수 비중을 표로 요약해줘."



## 3\. MCP 방식 연동 (Claude Desktop, Cursor 등 범용)

Roster CLI는 MCP(Model Context Protocol) 서버 모드를 지원하여, MCP를 지원하는 모든 AI 클라이언트에서 연동할 수 있습니다. MCP 서버 모드로 동작할 때는 AI가 `get_allocation` 도구를 호출하여 JQL을 기반으로 리소스 현황을 JSON 형태로 직접 받아 분석합니다.

### 3.1. 사전 준비 (Refresh Token 획득)

MCP 환경은 팝업 창을 띄울 수 없는 Headless 환경이므로, 1번 과정에서 저장된 `~/.config/roster/jira_token.json` 파일을 열어 `"refresh_token": "..."` 부분의 문자열 값을 복사합니다.

### 3.2. 클라이언트별 설정 파일 수정

**Claude Desktop 설정** `~/Library/Application Support/Claude/claude_desktop_config.json` 파일을 열고 다음과 같이 추가합니다.
[code]
    {
      "mcpServers": {
        "roster": {
          "command": "/절대경로/bin/roster",
          "args": ["mcp"],
          "env": {
            "JIRA_REFRESH_TOKEN": "여기에-복사한-refresh-token을-붙여넣으세요"
          }
        }
      }
    }
    
[/code]

**Cursor / VS Code 등** 각 클라이언트의 MCP 설정 메뉴에서 다음을 지정합니다.

  * **Command** : `/절대경로/bin/roster mcp`
  * **Environment Variables** : `JIRA_REFRESH_TOKEN=...` 추가



### 3.3. 실행 및 확인

  1. 클라이언트 앱을 재시작하거나 MCP 서버 목록을 새로고침합니다.
  2. 서버 상태가 **Connected** 인지 확인합니다.
  3. 에이전트에게 "Roster 도구를 사용해서 현재 내 프로젝트 할당 현황을 알려줘"라고 요청해 보세요.



## 4\. 문제 해결 (Troubleshooting)

  * **인증 에러 (401 Unauthorized):**
    * 원인: 토큰이 만료되었거나 사내 비밀번호를 변경한 경우 발생할 수 있습니다.
    * 해결: 로컬 터미널에서 다시 `./roster doctor`를 실행하여 새로운 토큰을 발급받으세요. (MCP의 경우 발급받은 Refresh Token 값을 설정 파일에 다시 업데이트해야 합니다.)
  * **명령어를 찾을 수 없음:**
    * 원인: MCP 설정에서 `command` 경로가 잘못되었거나 실행 권한이 없습니다.
    * 해결: Roster 실행 파일의 절대 경로를 정확히 입력하고, 파일에 실행 권한(`chmod +x`)이 있는지 확인하세요.

---

#### CI/CD 배포자 가이드 (CI/CD Deployer Guide)

- Page ID: `543086997`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543086997/CI+CD+%EB%B0%B0%ED%8F%AC%EC%9E%90+%EA%B0%80%EC%9D%B4%EB%93%9C+CI+CD+Deployer+Guide
- Depth: `2`

이 문서는 GitHub Actions, Jenkins, OpenShift 등 CI/CD 파이프라인에서 `roster` 프로그램을 자동화된 배치 작업(Batch Job)으로 실행하려는 배포 담당자를 위한 가이드입니다.

## 1\. Headless 환경의 인증 한계점

`roster` 프로그램은 기본적으로 사용자의 웹 브라우저를 열어 로그인을 수행하는 인터랙티브 OAuth 2.0 방식을 사용합니다. 하지만 CI/CD 컨테이너 환경(Headless)에서는 브라우저를 띄울 수 없으므로, **Refresh Token을 환경 변수로 직접 주입** 하여 브라우저 인증 과정을 우회(Bypass)해야 합니다.

## 2\. Refresh Token 획득 방법 (로컬 사전 작업)

CI/CD 파이프라인에 주입할 "영구 토큰(Refresh Token)"을 얻으려면 배포자(또는 서비스 계정 소유자)의 로컬 PC에서 다음 단계를 선행해야 합니다.

  1. 로컬 터미널에서 아래 명령을 실행하여 브라우저 인증을 완료합니다.
[code]./roster console # Jira 인증 수행
         ./roster sheets  # Google 인증 수행
         
[/code]

  2. 인증이 성공하면 생성된 아래 두 파일을 엽니다.
     * `~/.config/roster/jira_token.json`
     * `~/.config/roster/google_token.json`
  3. JSON 파일 내용 중 `"refresh_token": "..."` 부분의 문자열 값을 각각 복사해 둡니다.



## 3\. 파이프라인 환경 변수 주입 방법

CI/CD 플랫폼의 보안 설정(Secret Management)에 아래 변수들을 등록합니다.

### 필수 등록 환경 변수

  * `JIRA_CLIENT_ID`
  * `JIRA_CLIENT_SECRET`
  * `JIRA_REFRESH_TOKEN` (위 2단계에서 복사한 값)
  * `GOOGLE_CLIENT_ID`
  * `GOOGLE_CLIENT_SECRET`
  * `GOOGLE_REFRESH_TOKEN` (위 2단계에서 복사한 값)



> **참고:** 바이너리에 Client ID/Secret이 이미 내장되어 있다면, `REFRESH_TOKEN` 두 가지만 주입해도 정상 작동합니다. 그러나 보안상 명시적인 주입을 권장합니다.

### GitHub Actions 예시
[code]
    jobs:
      run-roster-batch:
        runs-on: ubuntu-latest
        steps:
          - name: Run Roster to Google Sheets
            env:
              JIRA_REFRESH_TOKEN: ${{ secrets.JIRA_REFRESH_TOKEN }}
              GOOGLE_REFRESH_TOKEN: ${{ secrets.GOOGLE_REFRESH_TOKEN }}
            run: ./roster sheets
    
[/code]

### Jenkins 예시
[code]
    pipeline {
        agent any
        environment {
            JIRA_REFRESH_TOKEN = credentials('roster-jira-refresh-token')
            GOOGLE_REFRESH_TOKEN = credentials('roster-google-refresh-token')
        }
        stages {
            stage('Batch Update') {
                steps {
                    sh "./roster sheets"
                }
            }
        }
    }
    
[/code]

## 4\. 유지보수 및 보안 가이드

  * **토큰 갱신:** Refresh Token은 일반적으로 만료되지 않으나, 계정 비밀번호 변경이나 관리자의 세션 초기화 시 무효화될 수 있습니다. 인증 오류(HTTP 401) 발생 시 로컬에서 2단계 과정을 다시 수행하여 새로운 Refresh Token을 발급받아 교체하세요.
  * **최소 권한:** 가급적 CI/CD 배치 작업을 위한 별도의 서비스 전용 사내 계정(System Account)을 생성하여 해당 계정으로 토큰을 발급받는 것을 권장합니다.

---

#### Google 관리자 가이드 (Google/GCP Admin Guide)

- Page ID: `543087003`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543087003/Google+%EA%B4%80%EB%A6%AC%EC%9E%90+%EA%B0%80%EC%9D%B4%EB%93%9C+Google+GCP+Admin+Guide
- Depth: `2`

이 문서는 사내 GCP(Google Cloud Platform) 프로젝트 관리자가 `roster` 프로그램의 분석 결과를 구글 시트(Google Sheets)로 전송할 수 있도록 OAuth 2.0 애플리케이션을 생성하고 자격 증명을 발급하는 과정을 안내합니다.

## 1\. 프로젝트 및 API 설정

  1. [Google Cloud Console](<https://console.cloud.google.com/>)에 사내 관리자 계정으로 접속합니다.
  2. Roster 연동을 위한 전용 프로젝트를 새로 생성하거나 기존 프로젝트를 선택합니다.
  3. 좌측 메뉴의 **[API 및 서비스] > [라이브러리]**로 이동하여 **"Google Sheets API"**를 검색한 후 **[사용(Enable)]**을 클릭합니다.



## 2\. OAuth 동의 화면 구성

  1. 좌측 메뉴에서 **[API 및 서비스] > [OAuth 동의 화면]**으로 이동합니다.
  2. **User Type** 을 반드시 **[Internal(내부)]**로 설정합니다. (사내 계정인 `@gmarket.com` 등 같은 도메인 소속 사용자만 이 앱을 이용해 로그인할 수 있게 제한하여 보안을 강화합니다.)
  3. 앱 이름(`Roster CLI` 등), 사용자 지원 이메일 등 필수 정보를 입력하고 저장합니다. (범위(Scopes) 추가는 건너뛰어도 됩니다.)



## 3\. OAuth 2.0 클라이언트 ID 생성

  1. 좌측 메뉴에서 **[API 및 서비스] > [사용자 인증 정보]**로 이동합니다.
  2. 상단의 **[+ 사용자 인증 정보 만들기] > [OAuth 클라이언트 ID]**를 선택합니다.
  3. **애플리케이션 유형** 을 **[데스크톱 앱(Desktop app)]**으로 선택합니다. (중요: 웹 애플리케이션이 아닙니다.)
  4. 이름을 입력하고 **[만들기]**를 클릭합니다.



## 4\. 자격 증명(Credentials) 발급 및 전달

생성을 완료하면 아래 두 개의 문자열이 화면에 표시됩니다. (또는 JSON 파일 형태로 다운로드할 수 있습니다.)

  * **Client ID**
  * **Client Secret**



이 두 값을 복사하여 `roster` 프로그램 배포 담당자(개발자)에게 전달하세요. 개발자는 이 정보를 활용하여 일반 사용자가 쓸 수 있는 실행 파일을 빌드(내장)하게 됩니다.

## 5\. 참고 및 보안 사항

  * `Client Secret`은 비밀번호와 같으므로 안전한 채널을 통해 전달해야 합니다.
  * Internal(내부) 앱으로 설정하였으므로 사외 외부인은 설사 `Client ID/Secret`을 알게 되더라도 앱에 로그인하여 접근 권한을 얻을 수 없습니다.

---

#### JQL 자동 변환 가이드 (JQL Transformation Guide)

- Page ID: `543087011`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543087011/JQL+%EC%9E%90%EB%8F%99+%EB%B3%80%ED%99%98+%EA%B0%80%EC%9D%B4%EB%93%9C+JQL+Transformation+Guide
- Depth: `2`

Roster CLI는 사용자가 복잡한 Jira 계층 구조를 일일이 추적하지 않아도 되도록, 입력된 JQL을 내부적으로 자동 확장하고 정제합니다. 이 문서에서는 그 변환 과정을 상세히 설명합니다.

## 1\. 개요

Jira에서 정확한 리소스 공수(Effort)를 산출하려면, 실제 작업 단위(Story, Task 등)뿐만 아니라 이들이 속한 상위 계층(Epic, Initiative, Battle) 정보가 반드시 필요합니다.

사용자가 `assignee = currentUser()`와 같이 짧은 쿼리를 입력하더라도, Roster CLI는 내부적으로 **"하위 이슈 조회 -> 상위 계층 추적 -> 불필요 이슈 제거"**의 과정을 거쳐 가장 정확한 데이터 셋을 만듭니다.

## 2\. 변환 3단계 (Three-Step Transformation)

### 1단계: 기본 필터링 강제 (Mandatory Filtering)

분석의 시작점이 되는 이슈들을 정제합니다. 하위 이슈(Sub-task)나 계층 구조의 중간 단계(Epic 등)가 분석 대상에 직접 포함되어 공수가 중복 계산되는 것을 방지합니다.

  * **추가되는 조건** : `AND issuetype in standardIssueTypes() AND issuetype != Epic`
  * **의도** : Story, Task, Bug 등 '실제 공수가 발생하는 표준 이슈'들만 분석의 뿌리로 삼습니다.



### 2단계: 상위 계층 자동 확장 (Hierarchy Expansion)

Jira의 상위 이슈 추적 함수(`issueFunction`)를 사용하여 계층 구조를 한 번에 가져오도록 쿼리를 래핑합니다.

  * **래핑 구조** :
[code](사용자_JQL) 
        OR issueFunction in epicsOf("사용자_JQL") 
        OR issueFunction in portfolioParentsOf("issueFunction in epicsOf('사용자_JQL')")
        
[/code]

  * **효과** :
    * `epicsOf`: Story/Task가 속한 **Epic** 을 자동으로 가져옵니다.
    * `portfolioParentsOf`: Epic이 속한 **Initiative** 나 **Battle** 을 자동으로 추적합니다.



### 3단계: 쿼리 정규화 (Normalization)

JQL 문법 오류를 방지하기 위해 따옴표 및 이스케이프 처리를 수행합니다.

  * 작은따옴표(`'`)를 큰따옴표(`"`)로 통일하여 함수 중첩 시 발생할 수 있는 문법 오류를 원천 차단합니다.



## 3\. 변환 예시

구분| 사용자 입력 JQL| 최종 변환되어 Jira로 전송되는 JQL  
---|---|---  
**기본**| `assignee = currentUser()`| `((assignee = currentUser()) AND (issuetype in standardIssueTypes() AND issuetype != Epic)) OR issueFunction in epicsOf(...) OR issueFunction in portfolioParentsOf(...)`  
**프로젝트**| `project = "PAYMENT"`| `((project = "PAYMENT") AND (issuetype in standardIssueTypes() AND issuetype != Epic)) OR issueFunction in epicsOf(...) OR ...`  
  
## 4\. 사용자 주의 사항

  * **수동 계층 추적 금지** : 사용자가 직접 `portfolioParentsOf` 등을 쿼리에 넣을 필요가 없습니다. 프로그램이 항상 자동으로 처리하므로, 사용자는 오직 **"내가 분석하고 싶은 실제 작업(Story/Task)들"**만 조회하는 쿼리를 작성하세요.
  * **디버그 확인** : 실제로 어떤 쿼리가 나가는지 궁금하다면 실행 시 `--debug` 플래그를 사용하세요.
[code]./roster console --debug
        
[/code]

---

#### Jira 관리자 가이드 (Jira Admin Guide)

- Page ID: `543087005`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543087005/Jira+%EA%B4%80%EB%A6%AC%EC%9E%90+%EA%B0%80%EC%9D%B4%EB%93%9C+Jira+Admin+Guide
- Depth: `2`

이 문서는 사내 Jira Data Center (또는 Jira Server) 관리자가 `roster` 프로그램에서 사용할 수 있도록 **OAuth 2.0 (Incoming)** 애플리케이션을 생성하고 자격 증명을 발급하는 과정을 안내합니다.

## 1\. Application Links 생성

  1. Jira 관리자 권한으로 로그인합니다.
  2. 상단 톱니바퀴 아이콘 > **[Administration(관리)] > [Applications(애플리케이션)] > [Application Links]** 메뉴로 이동합니다.
  3. **[Create link]** 버튼을 클릭합니다.
  4. **Application Type** 을 `External application`으로 선택합니다.
  5. **Direction** 을 `Incoming`으로 선택하여 생성을 시작합니다.



## 2\. OAuth 2.0 클라이언트 설정

생성 창에서 아래와 같이 입력합니다.

  * **Name** : `Roster CLI` (또는 내부적으로 식별 가능한 이름)
  * **Description** : Roster CLI 리소스 현황 분석 도구
  * **Redirect URL** : `http://localhost:58594`
    *  _중요:_ Jira Data Center의 OAuth 2.0 설정은 `redirect_uri`의 **정확한 문자열 일치** 를 요구합니다. Roster CLI는 기본적으로 `58594` 포트를 사용하므로 반드시 위 주소 그대로 입력해야 합니다.
    * 만약 특정 사유로 포트를 변경해야 한다면, CLI 실행 시 환경 변수 `JIRA_REDIRECT_URL`에도 동일한 값을 지정해야 합니다. (예: `JIRA_REDIRECT_URL=http://localhost:8080`)
  * **Permission (Scopes)** : `Read` 및 `Write` (또는 `api` 스코프)



## 3\. 자격 증명 (Credentials) 발급 및 전달

설정을 완료하면 아래 두 개의 문자열이 발급됩니다.

  * **Client ID**
  * **Client Secret**



발급된 정보를 `roster` 프로그램 배포 담당자(개발자)에게 전달하세요. 개발자는 이 정보를 활용하여 일반 사용자가 쓸 수 있는 실행 파일을 빌드(내장)하게 됩니다.

## 4\. 참고 및 보안 사항

  * `Client Secret`은 비밀번호와 같으므로 사내 메신저나 안전한 채널을 통해 전달해야 합니다.
  * 이 OAuth 애플리케이션은 Public Client(데스크톱 앱) 형태이므로, 만약 `Client Secret`이 외부에 유출되더라도 공격자가 특정 직원의 사내 계정으로 브라우저 로그인을 하지 않는 한 데이터 탈취는 어렵습니다.
  * 단, 주기적인 보안 갱신을 위해 일정 주기마다 `Client Secret`을 재생성(Roll)하는 것을 권장합니다.

---

#### Roster CLI 설정 가이드 (Strict OAuth 2.0)

- Page ID: `543086991`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543086991/Roster+CLI+%EC%84%A4%EC%A0%95+%EA%B0%80%EC%9D%B4%EB%93%9C+Strict+OAuth+2.0
- Depth: `2`

Roster CLI는 보안 강화를 위해 모든 외부 서비스(Jira, Google Sheets)에 대해 **OAuth 2.0 인증 방식만을 지원** 합니다. 기존의 API Token, Basic Auth, Service Account 방식은 더 이상 지원되지 않습니다.

## 설정 우선순위 (Priority)

  1. **CLI Flag** : 실행 시 입력한 플래그
  2. **OS 환경변수** : Jira, Google, Roster 관련 환경변수
  3. **.env 파일** : 프로젝트 루트의 환경변수 파일
  4. **config.yaml 파일** : 로컬 설정 파일
  5. **기본값 (Default)** : 코드 내 정의된 기본값



## 보안 및 인증 정책 (Security Policy)

Roster CLI는 사내 보안 규정을 준수하며, 모든 인증 정보는 안전하게 관리됩니다.

  1. **토큰 저장** : 브라우저 인증을 통해 획득한 토큰은 `~/.config/roster/*.json` 경로에 로컬 저장됩니다.
  2. **CI/CD 지원** : 환경변수로 `REFRESH_TOKEN`을 직접 주입하면 브라우저 인증 없이도 자동 실행이 가능합니다.



## Jira OAuth 2.0 설정

사내 Jira Data Center 환경에서 안전한 인증을 위해 OAuth 2.0을 사용합니다. 설정에 대한 자세한 내용은 다음 가이드를 참고하세요.

  * Jira 관리자 가이드 (Jira Admin Guide)
  * 개발자 가이드 (Developer Guide)



### 1\. 환경 변수 설정 (.env)
[code]
    JIRA_CLIENT_ID=your_client_id
    JIRA_CLIENT_SECRET=your_client_secret
    # (선택) Jira 쿼리 (기본값: 내 할당 이슈 및 상위 링크 포함)
    # JIRA_JQL=assignee = currentUser() OR ...
    # (선택) Jira 서버 주소 (기본값: https://jira.gmarket.com)
    # JIRA_SERVER=https://jira.gmarket.com
    # (선택) CI/CD 환경용
    # JIRA_REFRESH_TOKEN=your_refresh_token
    
[/code]

### 2\. 최초 인증

명령어 실행 시 자동으로 브라우저가 열립니다. Jira 로그인 후 권한을 승인하면 인증이 완료됩니다.

## Google Sheets OAuth 2.0 설정

### 1\. 환경 변수 설정 (.env)
[code]
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    ROSTER_GOOGLE_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/...
    # (선택) CI/CD 환경용
    # GOOGLE_REFRESH_TOKEN=your_refresh_token
    
[/code]

## 시스템 설정 요약

구분| Viper Key| 환경변수명| 비고  
---|---|---|---  
**Jira (필수)**| `jira.client_id`| `JIRA_CLIENT_ID`| (환경변수 필수)  
  
| `jira.client_secret`| `JIRA_CLIENT_SECRET`| (환경변수 필수)  
**Jira (선택)**| `jql`| `JIRA_JQL`| 기본 조회 쿼리 (currentUser 기반 기본값 제공)  
  
| `jira.server`| `JIRA_SERVER`| Jira 서버 URL (기본값: https://jira.gmarket.com)  
__Google (선택_)_*| `google.client_id`| `GOOGLE_CLIENT_ID`| (Sheets 사용 시 필수)  
  
| `google.client_secret`| `GOOGLE_CLIENT_SECRET`| (Sheets 사용 시 필수)  
  
| `google.spreadsheet_url`| `ROSTER_GOOGLE_SPREADSHEET_URL`| 대상 시트 URL  
**기타 (선택)**| `output.format`| `ROSTER_OUTPUT_FORMAT`| table, markdown, csv, json  
  
| `output.layout`| `ROSTER_OUTPUT_LAYOUT`| column, row  
  
| `hours_per_day`| -| 하루 작업 시간 (기본 8.0)  
  
| `holidays_path`| `ROSTER_HOLIDAYS_PATH`| 공휴일 파일 경로  
  
## 팁: CI/CD 환경에서 사용하기

로컬에서 브라우저 인증을 완료한 후 생성된 `~/.config/roster/jira_token.json` 또는 `google_token.json` 파일에서 `refresh_token` 값을 복사하여 CI/CD 환경변수(`JIRA_REFRESH_TOKEN`, `GOOGLE_REFRESH_TOKEN`)로 등록하세요. 브라우저 없이도 인증이 유지됩니다.

---

#### Roster CLI 응용 - org3 수준의 개발 프로젝트 월간 조회

- Page ID: `543066760`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543066760/Roster+CLI+%EC%9D%91%EC%9A%A9+-+org3+%EC%88%98%EC%A4%80%EC%9D%98+%EA%B0%9C%EB%B0%9C+%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8+%EC%9B%94%EA%B0%84+%EC%A1%B0%ED%9A%8C
- Depth: `2`

Payment Engineering의 2026년 월 별 capacity, plan, worklog를 조회하는 방법을 예로 들어 설명합니다.

## 희망 사항

org3 수준의 월간 조직원별, 프로젝트별 worklog 합계

ex) 우리팀이 지난달에 프로젝트별로 worklog를 얼마나 들어가는지 보고 싶고 어떤 프로젝트에 더 많은 리소스가 들어가는지 보고 싶어요.

org3 수준의 월간 프로젝트별 worklog 합계

ex) 지난달에 특정 팀원이 얼마나 일했는지, 혹은 Worklog를 잘 입력하지 않는 팀원이 누군지 알고 싶어요.

org3 수준의 월간 예측량, 사용량을 팀 가용 리소스와 비교

ex) 우리팀의 지난달 estimation, worklog가 얼마나 되었는지 보고 싶어요, 가용 리소스 대비 어느정도 사용 되었는지 알고 싶어요.

## 준비

Payment Engineering 구성원이 assignee로 되어 있는 issue와 상위 issue를 조회하는 쿼리를 작성합니다.
[code] 
    issueFunction in strictBottomUpPortfolio("assignee in membersOf('Payment Engineering') AND issuetype in (Story, Task) AND project not in (QA)")
[/code]

이 쿼리를 config.yaml의 jql 값으로 넣습니다.
[code] 
    jira:
      jql: >
        issueFunction in strictBottomUpPortfolio("assignee in membersOf('Payment Engineering') AND issuetype in (Story, Task) AND project not in (QA)")
[/code]

결과값을 넣을 google sheets 파일을 준비하고 이 파일의 id를 config.yaml의 spreadsheet_id 값으로 넣습니다. (예시의 id는 <https://docs.google.com/spreadsheets/d/1J-VfWFdUpAg7aIlj15aTULyw0FUrqwcyVF_3hqD-kaA/edit?usp=sharing> 를 가리킵니다.)
[code] 
    google:
      spreadsheet_id: "1J-VfWFdUpAg7aIlj15aTULyw0FUrqwcyVF_3hqD-kaA"
[/code]

프로그램을 실행합니다.
[code] 
    > .\roster.exe sheets -r 202601:202612
[/code]

Google sheets 파일에 issue, plan, actual sheet가 생성되고 값이 채워졌는지 확인합니다.

Google sheets 파일에 capacity sheet를 추가하고 A1 cell에 아래 함수를 넣습니다.
[code] 
    =QUERY(IMPORTRANGE("https://docs.google.com/spreadsheets/d/1X6DqzISucqb7UHbivbfkic5xo3aZv_Qjq6V4X67-JJI", "team_capacity!A:AC"), "SELECT * WHERE Col2 = 'Payment Engineering'", 1)
[/code]

## 지표 구성

### 조직원, 월 별 estimation 합계

plan_per_assignee sheet를 추가하고 A1 cell에 아래 함수를 삽입합니다.
[code] 
    =LET(
      keys, INDIRECT("plan!A2:A"),
      persons, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 8, FALSE), ""))),
      parents, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      cond1, ARRAYFORMULA(parents <> ""),
      cond2, ARRAYFORMULA(LEFT(parents, 4) <> "ROAD"),
      f_persons, FILTER(persons, cond1, cond2),
      f_data, FILTER(INDIRECT("plan!B2:M"), cond1, cond2),
      headers, INDIRECT("plan!B1:M1"),
      u_persons, UNIQUE(FILTER(f_persons, f_persons<>"")),
      sums, MAKEARRAY(ROWS(u_persons), COLUMNS(headers), LAMBDA(r, c,
        SUMPRODUCT((f_persons = INDEX(u_persons, r)) * 1, INDEX(f_data, 0, c))
      )),
      VSTACK(HSTACK("Person", headers), HSTACK(u_persons, sums))
    )
[/code]

### 조직원, 월 별, worklog 합계

actual_per_assignee sheet를 추가하고 A1 cell에 아래 함수를 삽입합니다.
[code] 
    =LET(
      keys, INDIRECT("actual!A2:A"),
      persons, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 8, FALSE), ""))),
      parents, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      cond1, ARRAYFORMULA(parents <> ""),
      cond2, ARRAYFORMULA(LEFT(parents, 4) <> "ROAD"),
      f_persons, FILTER(persons, cond1, cond2),
      f_data, FILTER(INDIRECT("actual!B2:M"), cond1, cond2),
      headers, INDIRECT("actual!B1:M1"),
      u_persons, UNIQUE(FILTER(f_persons, f_persons<>"")),
      sums, MAKEARRAY(ROWS(u_persons), COLUMNS(headers), LAMBDA(r, c,
        SUMPRODUCT((f_persons = INDEX(u_persons, r)) * 1, INDEX(f_data, 0, c))
      )),
      VSTACK(HSTACK("Person", headers), HSTACK(u_persons, sums))
    )
[/code]

### 프로젝트, 월 별, estimation 합계

plan_per_initiative sheet를 추가하고 A1 cell에 아래 함수를 삽입합니다.
[code] 
    =LET(
      keys, INDIRECT("plan!A2:A"),
      parents, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      initiatives, ARRAYFORMULA(IF(parents="", "", IFERROR(VLOOKUP(parents, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      cond1, ARRAYFORMULA(parents <> ""),
      cond2, ARRAYFORMULA(LEFT(parents, 4) <> "ROAD"),
      f_init, FILTER(initiatives, cond1, cond2),
      f_data, FILTER(INDIRECT("plan!B2:M"), cond1, cond2),
      headers, INDIRECT("plan!B1:M1"),
      u_init, UNIQUE(FILTER(f_init, f_init<>"")),
      u_summary, ARRAYFORMULA(IFERROR(VLOOKUP(u_init, INDIRECT("issue!A:I"), 5, FALSE), "")),
      sums, MAKEARRAY(ROWS(u_init), COLUMNS(headers), LAMBDA(r, c,
        SUMPRODUCT((f_init = INDEX(u_init, r)) * 1, INDEX(f_data, 0, c))
      )),
      VSTACK(HSTACK("Initiative Key", "Summary", headers), HSTACK(u_init, u_summary, sums))
    )
[/code]

### 프로젝트, 월 별, worklog 합계

actual_per_initiative sheet를 추가하고 A1 cell에 아래 함수를 삽입합니다.
[code] 
    =LET(
      keys, INDIRECT("actual!A2:A"),
      parents, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      initiatives, ARRAYFORMULA(IF(parents="", "", IFERROR(VLOOKUP(parents, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      cond1, ARRAYFORMULA(parents <> ""),
      cond2, ARRAYFORMULA(LEFT(parents, 4) <> "ROAD"),
      f_init, FILTER(initiatives, cond1, cond2),
      f_data, FILTER(INDIRECT("actual!B2:M"), cond1, cond2),
      headers, INDIRECT("actual!B1:M1"),
      u_init, UNIQUE(FILTER(f_init, f_init<>"")),
      u_summary, ARRAYFORMULA(IFERROR(VLOOKUP(u_init, INDIRECT("issue!A:I"), 5, FALSE), "")),
      sums, MAKEARRAY(ROWS(u_init), COLUMNS(headers), LAMBDA(r, c,
        SUMPRODUCT((f_init = INDEX(u_init, r)) * 1, INDEX(f_data, 0, c))
      )),
      VSTACK(HSTACK("Initiative Key", "Summary", headers), HSTACK(u_init, u_summary, sums))
    )
[/code]

### 가용, 계획, 사용 월 별 비교

Google sheets 파일에 dashboard sheet를 추가하고 아래와 같이 A1~A4, B1~M1 cell에 값을 채웁니다.
[code] 
            |   A       B         C         D         E         F         G         H         I         J         K         L         M
    --------+----------------------------------------------------------------------------------------------------------------------------
      1     | month  2026-01   2026-02   2026-03   2026-04   2026-05   2026-06   2026-07   2026-08   2026-09   2026-10   2026-11   2026-12
    --------+----------------------------------------------------------------------------------------------------------------------------
      2     | capacity
    --------+----------------------------------------------------------------------------------------------------------------------------
      3     | plan
    --------+----------------------------------------------------------------------------------------------------------------------------
      4     | spent
    --------+----------------------------------------------------------------------------------------------------------------------------
[/code]

B2 cell에 아래의 함수를 입력합니다.
[code] 
    ={capacity!R2:AC2}
[/code]

B3 cell에 아래의 함수를 입력합니다.
[code] 
    =BYCOL(plan_per_initiative!C2:N, LAMBDA(c, SUM(c)))
[/code]

  


  


B4 cell에 아래의 함수를 입력합니다.
[code] 
    =BYCOL(actual_per_initiative!C2:N, LAMBDA(c, SUM(c)))
[/code]

## 결과

위의 과정을 모두 거친 Google sheets 파일 - <https://docs.google.com/spreadsheets/d/1J-VfWFdUpAg7aIlj15aTULyw0FUrqwcyVF_3hqD-kaA/edit?usp=sharing>

## See also

  * Jira 커스텀 함수 - 포트폴리오 상향식 조회

---

##### (Deprecated)Roster CLI 응용 - org3 수준의 개발 프로젝트 월간 조회

- Page ID: `543087324`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543087324/Deprecated+Roster+CLI+%EC%9D%91%EC%9A%A9+-+org3+%EC%88%98%EC%A4%80%EC%9D%98+%EA%B0%9C%EB%B0%9C+%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8+%EC%9B%94%EA%B0%84+%EC%A1%B0%ED%9A%8C
- Depth: `3`

Payment Engineering의 2026년 월 별 capacity, plan, worklog를 조회하는 방법을 예로 들어 설명합니다.

## 희망 사항

org3 수준의 월간 조직원별, 프로젝트별 worklog 합계

ex) 우리팀이 지난달에 프로젝트별로 worklog를 얼마나 들어가는지 보고 싶고 어떤 프로젝트에 더 많은 리소스가 들어가는지 보고 싶어요.

org3 수준의 월간 프로젝트별 worklog 합계

ex) 지난달에 특정 팀원이 얼마나 일했는지, 혹은 Worklog를 잘 입력하지 않는 팀원이 누군지 알고 싶어요.

org3 수준의 월간 예측량, 사용량을 팀 가용 리소스와 비교

ex) 우리팀의 지난달 estimation, worklog가 얼마나 되었는지 보고 싶어요, 가용 리소스 대비 어느정도 사용 되었는지 알고 싶어요.

## 준비

Payment Engineering 구성원이 assignee로 되어 있는 issue와 상위 issue를 조회하는 쿼리를 작성합니다.
[code] 
    issueFunction in strictBottomUpPortfolio("assignee in membersOf('Payment Engineering') AND issuetype in (Story, Task) AND project not in (QA)")
[/code]

이 쿼리를 config.yaml의 jql 값으로 넣습니다.
[code] 
    jira:
      jql: >
        issueFunction in strictBottomUpPortfolio("assignee in membersOf('Payment Engineering') AND issuetype in (Story, Task) AND project not in (QA)")
[/code]

결과값을 넣을 google sheets 파일을 준비하고 이 파일의 id를 config.yaml의 spreadsheet_id 값으로 넣습니다. (예시의 id는 <https://docs.google.com/spreadsheets/d/1J-VfWFdUpAg7aIlj15aTULyw0FUrqwcyVF_3hqD-kaA/edit?usp=sharing> 를 가리킵니다.)
[code] 
    google:
      spreadsheet_id: "1J-VfWFdUpAg7aIlj15aTULyw0FUrqwcyVF_3hqD-kaA"
[/code]

프로그램을 실행합니다.
[code] 
    > .\roster.exe sheets -r 202601:202612
[/code]

Google sheets 파일에 issue, plan, actual sheet가 생성되고 값이 채워졌는지 확인합니다.

Google sheets 파일에 capacity sheet를 추가하고 A1 cell에 아래 함수를 넣습니다.
[code] 
    =QUERY(IMPORTRANGE("https://docs.google.com/spreadsheets/d/1X6DqzISucqb7UHbivbfkic5xo3aZv_Qjq6V4X67-JJI", "team_capacity!A:AC"), "SELECT * WHERE Col2 = 'Payment Engineering'", 1)
[/code]

## 지표 구성

### 조직원, 월 별 estimation 합계

plan_per_assignee sheet를 추가하고 A1 cell에 아래 함수를 삽입합니다.
[code] 
    =LET(
      keys, INDIRECT("plan!A2:A"),
      persons, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 8, FALSE), ""))),
      parents, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      cond1, ARRAYFORMULA(parents <> ""),
      cond2, ARRAYFORMULA(LEFT(parents, 4) <> "ROAD"),
      f_persons, FILTER(persons, cond1, cond2),
      f_data, FILTER(INDIRECT("plan!B2:M"), cond1, cond2),
      headers, INDIRECT("plan!B1:M1"),
      u_persons, UNIQUE(FILTER(f_persons, f_persons<>"")),
      sums, MAKEARRAY(ROWS(u_persons), COLUMNS(headers), LAMBDA(r, c,
        SUMPRODUCT((f_persons = INDEX(u_persons, r)) * 1, INDEX(f_data, 0, c))
      )),
      VSTACK(HSTACK("Person", headers), HSTACK(u_persons, sums))
    )
[/code]

### 조직원, 월 별, worklog 합계

actual_per_assignee sheet를 추가하고 A1 cell에 아래 함수를 삽입합니다.
[code] 
    =LET(
      keys, INDIRECT("actual!A2:A"),
      persons, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 8, FALSE), ""))),
      parents, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      cond1, ARRAYFORMULA(parents <> ""),
      cond2, ARRAYFORMULA(LEFT(parents, 4) <> "ROAD"),
      f_persons, FILTER(persons, cond1, cond2),
      f_data, FILTER(INDIRECT("actual!B2:M"), cond1, cond2),
      headers, INDIRECT("actual!B1:M1"),
      u_persons, UNIQUE(FILTER(f_persons, f_persons<>"")),
      sums, MAKEARRAY(ROWS(u_persons), COLUMNS(headers), LAMBDA(r, c,
        SUMPRODUCT((f_persons = INDEX(u_persons, r)) * 1, INDEX(f_data, 0, c))
      )),
      VSTACK(HSTACK("Person", headers), HSTACK(u_persons, sums))
    )
[/code]

### 프로젝트, 월 별, estimation 합계

plan_per_initiative sheet를 추가하고 A1 cell에 아래 함수를 삽입합니다.
[code] 
    =LET(
      keys, INDIRECT("plan!A2:A"),
      parents, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      initiatives, ARRAYFORMULA(IF(parents="", "", IFERROR(VLOOKUP(parents, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      cond1, ARRAYFORMULA(parents <> ""),
      cond2, ARRAYFORMULA(LEFT(parents, 4) <> "ROAD"),
      f_init, FILTER(initiatives, cond1, cond2),
      f_data, FILTER(INDIRECT("plan!B2:M"), cond1, cond2),
      headers, INDIRECT("plan!B1:M1"),
      u_init, UNIQUE(FILTER(f_init, f_init<>"")),
      u_summary, ARRAYFORMULA(IFERROR(VLOOKUP(u_init, INDIRECT("issue!A:I"), 5, FALSE), "")),
      sums, MAKEARRAY(ROWS(u_init), COLUMNS(headers), LAMBDA(r, c,
        SUMPRODUCT((f_init = INDEX(u_init, r)) * 1, INDEX(f_data, 0, c))
      )),
      VSTACK(HSTACK("Initiative Key", "Summary", headers), HSTACK(u_init, u_summary, sums))
    )
[/code]

### 프로젝트, 월 별, worklog 합계

actual_per_initiative sheet를 추가하고 A1 cell에 아래 함수를 삽입합니다.
[code] 
    =LET(
      keys, INDIRECT("actual!A2:A"),
      parents, ARRAYFORMULA(IF(keys="", "", IFERROR(VLOOKUP(keys, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      initiatives, ARRAYFORMULA(IF(parents="", "", IFERROR(VLOOKUP(parents, INDIRECT("issue!A:I"), 9, FALSE), ""))),
      cond1, ARRAYFORMULA(parents <> ""),
      cond2, ARRAYFORMULA(LEFT(parents, 4) <> "ROAD"),
      f_init, FILTER(initiatives, cond1, cond2),
      f_data, FILTER(INDIRECT("actual!B2:M"), cond1, cond2),
      headers, INDIRECT("actual!B1:M1"),
      u_init, UNIQUE(FILTER(f_init, f_init<>"")),
      u_summary, ARRAYFORMULA(IFERROR(VLOOKUP(u_init, INDIRECT("issue!A:I"), 5, FALSE), "")),
      sums, MAKEARRAY(ROWS(u_init), COLUMNS(headers), LAMBDA(r, c,
        SUMPRODUCT((f_init = INDEX(u_init, r)) * 1, INDEX(f_data, 0, c))
      )),
      VSTACK(HSTACK("Initiative Key", "Summary", headers), HSTACK(u_init, u_summary, sums))
    )
[/code]

### 가용, 계획, 사용 월 별 비교

Google sheets 파일에 dashboard sheet를 추가하고 아래와 같이 A1~A4, B1~M1 cell에 값을 채웁니다.
[code] 
            |   A       B         C         D         E         F         G         H         I         J         K         L         M
    --------+----------------------------------------------------------------------------------------------------------------------------
      1     | month  2026-01   2026-02   2026-03   2026-04   2026-05   2026-06   2026-07   2026-08   2026-09   2026-10   2026-11   2026-12
    --------+----------------------------------------------------------------------------------------------------------------------------
      2     | capacity
    --------+----------------------------------------------------------------------------------------------------------------------------
      3     | plan
    --------+----------------------------------------------------------------------------------------------------------------------------
      4     | spent
    --------+----------------------------------------------------------------------------------------------------------------------------
[/code]

B2 cell에 아래의 함수를 입력합니다.
[code] 
    ={capacity!R2:AC2}
[/code]

B3 cell에 아래의 함수를 입력합니다.
[code] 
    =BYCOL(plan_per_initiative!C2:N, LAMBDA(c, SUM(c)))
[/code]

  


  


B4 cell에 아래의 함수를 입력합니다.
[code] 
    =BYCOL(actual_per_initiative!C2:N, LAMBDA(c, SUM(c)))
[/code]

## 결과

위의 과정을 모두 거친 Google sheets 파일 - <https://docs.google.com/spreadsheets/d/1J-VfWFdUpAg7aIlj15aTULyw0FUrqwcyVF_3hqD-kaA/edit?usp=sharing>

## See also

  * Jira 커스텀 함수 - 포트폴리오 상향식 조회

---

#### Story, Task, Bug type issue로 Epic, Initiative type issue까지 한번에 조회하기

- Page ID: `543086871`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543086871/Story+Task+Bug+type+issue%EB%A1%9C+Epic+Initiative+type+issue%EA%B9%8C%EC%A7%80+%ED%95%9C%EB%B2%88%EC%97%90+%EC%A1%B0%ED%9A%8C%ED%95%98%EA%B8%B0
- Depth: `2`

Roster CLI에서 issue 정보를 조회하기 위해서는 Story, Task, Bug type issue 및 이들 issue의 상위 Epic, Initiative type issue까지 한번에 조회가 필요합니다.

세 종류의 방법이 가능합니다.

## 방법 1 - 단일 쿼리
[code] 
    OR issueFunction in epicsOf("")
    OR issueFunction in portfolioParentsOf("issueFunction in epicsOf('')")
[/code]

## 방법 2 - subquery용 필터 사용
[/code]
[code] 
    <필터>
    OR issueFunction in epicsOf("<필터>")
    OR issueFunction in portfolioParentsOf("issueFunction in epicsOf('<필터>')")
[/code]

## 방법 3 - 커스텀 함수 사용
[code] 
    issueFunction in bottomUpPortfolio("")
[/code]

## 예) Technology 조직에 속한 임직원이 assignee로 된 2025-09-01 이후 생성된 issue와 상위 issue를 조회

### 방법 1
[code] 
    (assignee in membersOf('Technology') and created >= 2025-09-01)
    OR issueFunction in epicsOf("assignee in membersOf('Technology') and created >= 2025-09-01") 
    OR issueFunction in portfolioParentsOf("issueFunction in epicsOf('assignee in membersOf(\"Technology\") and created >= 2025-09-01')")
[/code]

### 방법 2
[code] 
    assignee in membersOf('Technology') and created >= 2025-09-01
[/code]
[code] 
    filter = tech
    OR issueFunction in epicsOf("filter = tech") 
    OR issueFunction in portfolioParentsOf("issueFunction in epicsOf('filter = tech')")
[/code]

### 방법 3
[code] 
    issueFunction in bottomUpPortfolio("assignee in membersOf('Technology') and created >= 2025-09-01")
[/code]

  


## Initiative까지 있는 issue만 조회하기

방법1, 2로는 불가능합니다. 방법3을 사용하되 커스텀 함수 strictBottomUpPortfolio를 사용합니다.

bottomUpPortfolio, strictBottomUpPortfolio 두 개의 차이는 아래와 같습니다.

Tree Structure| bottomUpPortfolio| strictBottomUpPortfolio  
---|---|---  
[Initiative 1]  
└ [Epic 1]  
└ [Story 1]| 
[code]
    포함  
    포함  
    포함
[/code]

| 
[code]
    포함  
    포함  
    포함
[/code]  
  
[Epic 2]  
└ [Story 2]| 
[code]
    포함  
    포함
[/code]

| 
[code]
    제외 (Initiative 없음)  
    제외 (Initiative 없음)
[/code]  
  
[Story 3]| 
[code]
    포함
[/code]

| 
[code]
    제외 (상위 계층 없음)
[/code]  
  
예) Technology 조직에 속한 임직원이 assignee로 된 2025-09-01 이후 생성된 issue와 상위 issue를 조회 단, Initiative 하위의 issue가 아닌 issue는 제외
[code] 
    issueFunction in strictBottomUpPortfolio("assignee in membersOf('Technology') and created >= 2025-09-01")
[/code]

---

#### console 명령어 사용 가이드

- Page ID: `543086993`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543086993/console+%EB%AA%85%EB%A0%B9%EC%96%B4+%EC%82%AC%EC%9A%A9+%EA%B0%80%EC%9D%B4%EB%93%9C
- Depth: `2`

이 문서는 `roster console` 명령어의 모든 옵션과 활용 패턴을 설명합니다.

## 1\. 플래그 상세 설명

### `--type` / `-t` (출력 데이터 타입)

값| 설명| 분석 용  
---|---|---  
`plan`| 표준 이슈(Task, Story 등)의 계획 공수| 리소스 배분 계획 확인 (Epic/Initiative/Battle 제외)  
`actual`| 표준 이슈의 실제 Worklog 기반 투입 실적| 계획 대비 실적 비교 (Epic/Initiative/Battle 제외)  
`issue`| 모든 종류의 이슈 속성 (상태, 담당자, 일정 등)| 상위 레벨 이슈(Epic 등)를 포함한 전수 조회  
  
### `--range` / `-r` (출력 월 범위)

  * **단일 월** : `202503` (2025년 3월)
  * **기간** : `202501:202506` (2025년 1월 ~ 6월)
  * 미지정 시 조회된 데이터에 포함된 가장 빠른 월부터 가장 늦은 월까지 전체 기간이 자동으로 설정됩니다.



### `--format` / `-f` (출력 포맷)

값| 용도  
---|---  
`table`| 터미널에서 사람이 읽기 좋은 형태 (기본값)  
`json`| 에이전트가 파싱하기 쉬운 구조화 데이터 (분석 권장)  
`csv`| 스프레드시트로 내보낼 때  
`markdown`| 문서나 리포트에 바로 삽입할 때  
  
### `--layout` / `-l` (출력 레이아웃)

값| 설명  
---|---  
`column`| 이슈를 행, 월별 공수를 열로 표시 (기본값)  
`row`| 각 월별 데이터를 별도의 행으로 풀어서 표시 (데이터 가공용)  
  
### `--jql` (Jira Query Language)

Jira JQL 문법으로 조회 대상 이슈를 필터링합니다. `--type`에 관계없이 적용됩니다.

### `--config` / `-c` (설정 파일)

기본값 `./config.yaml` 대신 다른 설정 파일을 사용할 때 지정합니다.

### `--holidays` (공휴일 파일)

배분 계산 시 제외할 날짜 목록 파일 경로입니다. 환경변수 `ROSTER_HOLIDAYS_PATH`로도 지정 가능하며, 기본값은 `holidays.txt`입니다.

## 2\. 사용 예시

### 기본 리소스 계획 조회
[code]
    # Q1 2026 전체 플랜 조회
    ./roster console --type plan --range 202601:202603 --format json
    
[/code]

### 특정 프로젝트만 필터링
[code]
    ./roster console --type plan --range 202603 --jql "project = 'PAYMENT'" --format json
    
[/code]

### 담당자별 계획 대비 실적 비교
[code]
    # 계획 (plan)
    ./roster console --type plan --range 202603 --jql "assignee = 'user@example.com'" --format json
    
    # 실적 (actual)
    ./roster console --type actual --range 202603 --jql "assignee = 'user@example.com'" --format json
    
[/code]

### 고우선순위 이슈 속성 전수 조회
[code]
    ./roster console --type issue --jql "priority = High AND status != Done" --format json
    
[/code]

### CSV로 내보내기
[code]
    ./roster console --type plan --range 202601:202606 --format csv > plan_h1_2026.csv
    
[/code]

## 3\. 에이전트 사용 권장 패턴

  1. 분석 시작 전 항상 `--format json`을 사용하여 구조화된 데이터를 확보하세요.
  2. 대용량 조회 시 `--range`를 월 단위로 나누어 API 부하를 줄이세요.
  3. `list-types` 명령으로 현재 시스템의 지원 타입과 필드를 먼저 확인하세요.

---

#### 개발자 가이드 (Developer Guide)

- Page ID: `543087001`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543087001/%EA%B0%9C%EB%B0%9C%EC%9E%90+%EA%B0%80%EC%9D%B4%EB%93%9C+Developer+Guide
- Depth: `2`

이 문서는 `roster` 프로그램의 코드를 수정하고, 일반 사용자를 위한 실행 파일(바이너리)을 빌드 및 배포하는 개발자를 위한 가이드입니다.

## 1\. 인증 정보(OAuth Credentials) 내장 배포의 이해

일반 사용자가 복잡한 환경 변수나 설정 파일을 만지지 않도록, **빌드 시점(Build Time)**에 Jira와 Google의 `Client ID` 및 `Client Secret`을 바이너리 내부에 주입(Embedding)하여 배포하는 것을 원칙으로 합니다.

## 2\. 로컬 개발 환경 세팅 (.env)

개발자 본인의 PC나 빌드 서버에는 소스 코드에 인증 정보가 포함되지 않도록 `.env` 파일을 사용합니다. (Jira/Google 관리자로부터 자격 증명을 전달받으세요.)

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래와 같이 작성합니다.
[code]
    # Jira 자격 증명 (필수)
    JIRA_CLIENT_ID=your_jira_client_id
    JIRA_CLIENT_SECRET=your_jira_client_secret
    
    # Google Sheets 자격 증명 (시트 기능 빌드 시 필수)
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    
[/code]

> **주의:** `.env` 파일과 `Client Secret`은 절대 Git에 커밋하지 마세요.

## 3\. 사용자 배포용 바이너리 빌드

`Taskfile.yml`에 설정된 `build` 명령어를 실행하면, `.env`에 있는 자격 증명이 `ldflags`를 통해 실행 파일 안에 안전하게 주입됩니다.
[code]
    # 1. 의존성 다운로드 및 바이너리 빌드 (인증 정보 주입 포함)
    task build
    
    # 2. 크로스 컴파일 (Windows, Mac, Linux 용 동시 빌드)
    task build-skill-binaries
    
[/code]

빌드가 완료되면 `bin/` 및 `.gemini/skills/roster/scripts/` 디렉토리에 실행 파일이 생성됩니다. 이 파일들을 사용자들에게 배포하면 됩니다.

## 4\. 수동 오버라이드 (Power User)

바이너리에 기본 인증 정보가 내장되어 있더라도, 파워 유저나 개발자는 시스템 환경 변수나 로컬 `.env` 파일에 `JIRA_CLIENT_ID` 등을 명시함으로써 내장된 값을 무시하고 자신만의 OAuth 앱을 덮어쓸(Override) 수 있습니다.

## 5\. 인증 디버깅 팁

  * **인증 초기화** : 로컬 테스트 중 인증 과정을 처음부터 다시 시도하고 싶다면 토큰 저장 폴더(`~/.config/roster/`)에 있는 `jira_token.json` 및 `google_token.json` 파일을 삭제하세요.
  * **로컬 서버 포트** : OAuth Callback을 받기 위해 로컬 서버는 `localhost:0`을 사용하여 임의의 비어있는 포트를 엽니다.
  * **상태 점검** : `./roster doctor` 명령을 실행하여 현재 설정된 Client ID 유무와 연결 상태를 확인할 수 있습니다.

---

#### 데이터 엔지니어 가이드 (Data Engineer Guide)

- Page ID: `543086999`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543086999/%EB%8D%B0%EC%9D%B4%ED%84%B0+%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4+%EA%B0%80%EC%9D%B4%EB%93%9C+Data+Engineer+Guide
- Depth: `2`

이 문서는 `roster` 프로그램이 수집한 리소스 데이터를 사내 데이터베이스(SQLite, PostgreSQL, MySQL)에 적재하고, BI 도구(Grafana, Metabase 등)와 연동하여 시각화 대시보드를 구축하려는 **데이터 엔지니어** 를 위한 가이드입니다.

## 1\. 지원하는 데이터베이스

현재 `roster`​는 다음 세 가지 타입의 데이터베이스를 공식 지원합니다.

  * **SQLite** : 별도 설치가 필요 없는 파일 기반 DB입니다. 개인적인 이력 관리용으로 추천합니다. (기본값)
  * **PostgreSQL** : 엔터프라이즈 환경에서 가장 권장되는 관계형 DB입니다.
  * **MySQL** : 널리 쓰이는 오픈 소스 DB로, 대규모 데이터 처리에 적합합니다.



## 2\. 설정 방법 (환경 변수)

데이터베이스 연동은 **환경 변수** 를 통해 설정합니다. `.env` 파일이나 OS 환경 변수에 아래 항목들을 지정하세요.

### 필수 환경 변수 (.env 권장)
[code]
    # DB 타입 (sqlite, postgres, mysql)
    # 미지정 시 기본값은 sqlite 입니다.
    ROSTER_DB_TYPE=postgres
    
    # 접속 정보 (비밀번호 포함)
    # - SQLite: 파일명 (예: roster.db)
    # - PostgreSQL/MySQL: 연결 문자열(DSN)
    # 이 변수가 설정되어 있어야 DB 기능이 활성화됩니다.
    ROSTER_DB_DSN="host=localhost user=roster password=your_secret dbname=roster port=5432 sslmode=disable"
    
[/code]

## 3\. 주요 명령어

데이터베이스 관련 작업은 `db` 하위 명령어를 사용합니다.

### 분석 결과 저장

현재 JQL 조건으로 분석된 모든 데이터를 DB에 기록합니다. 실행할 때마다 새로운 **동기화 세션** ​이 생성됩니다.
[code]
    roster db
    
[/code]

### 저장 이력 확인

최근 20개의 동기화 세션 목록을 조회합니다. 언제, 누가, 어떤 JQL로 저장했는지 확인할 수 있습니다.
[code]
    roster db list
    
[/code]

### 데이터베이스 초기화

모든 데이터를 삭제하고 테이블 구조를 처음부터 다시 생성합니다. (현재 SQLite만 지원)
[code]
    roster db init
    
[/code]

## 4\. 데이터베이스 구조 (Schema)

데이터를 직접 분석하거나 시각화 도구에서 사용하기 위해 다음 세 가지 핵심 테이블 구조를 참고하세요.

### 1\. `sync_sessions` (동기화 세션)

데이터의 "버전"을 관리하며 세션 간 계획 변화를 추적하는 기준이 됩니다.

컬럼명| 데이터 타입| 필수/PK| 예시 데이터| 설명  
---|---|---|---|---  
`id`| BIGINT| **PK**| `10`| 세션 고유 ID (자동 증가)  
`created_at`| TIMESTAMP| 필수| `2024-04-04 11:30`| 동기화 실행 시각  
`executed_by`| VARCHAR(100)| 필수| `jseungbum`| 실행한 OS 사용자명  
`jql`| TEXT| 필수| `project = ABC AND status = 'In Progress'`| 사용된 Jira JQL 쿼리  
`cli_version`| VARCHAR(50)| -| `v1.9.0`| 사용된 `roster` CLI 버전  
  
### 2\. `issue_snapshots` (이슈 상세 스냅샷)

동기화 시점의 Jira 이슈 속성을 그대로 저장하여 과거 시점의 데이터를 복원할 때 사용합니다.

컬럼명| 데이터 타입| 필수/PK| 예시 데이터| 설명  
---|---|---|---|---  
`id`| BIGINT| **PK**| `1024`| 고유 ID (자동 증가)  
`session_id`| BIGINT| **FK**| `10`| `sync_sessions.id` 참조  
`issue_key`| VARCHAR(20)| 필수| `PLATFORM-123`| Jira 이슈 키 (Key)  
`issue_type`| VARCHAR(50)| -| `Story`| 이슈 유형 (Issue Type)  
`summary`| TEXT| -| `DB 연동 모듈 개발`| 이슈 제목 (Summary)  
`status`| VARCHAR(50)| -| `In Progress`| 현재 상태 (Status)  
`priority`| VARCHAR(50)| -| `Medium`| 우선순위 (Priority)  
`assignee`| VARCHAR(100)| -| `전승범`| 담당자명 (Assignee)  
`parent_key`| VARCHAR(50)| -| `EPIC-123`| 부모 이슈 키 (Epic, Initiative 등)  
`target_start`| DATE| -| `2024-04-01`| 계획된 시작일 (Target start)  
`target_end`| DATE| -| `2024-04-30`| 계획된 종료일 (Target end)  
`estimate_md`| FLOAT| -| `12.5`| 초기 추정치 (Original Estimate, MD 단위)  
`logged_md`| FLOAT| -| `5.0`| 실제 투입 공수 (Time Spent, MD 단위)  
  
### 3\. `monthly_allocations` (월별 공수 배분)

가장 핵심이 되는 통계 테이블로, 월별 리소스 투입량을 쪼개어 저장합니다.

컬럼명| 데이터 타입| 필수/PK| 예시 데이터| 설명  
---|---|---|---|---  
`id`| BIGINT| **PK**| `5120`| 고유 ID (자동 증가)  
`session_id`| BIGINT| **FK**| `10`| `sync_sessions.id` 참조  
`issue_key`| VARCHAR(20)| 필수| `PLATFORM-123`| 연결된 Jira 이슈 키  
`category`| VARCHAR(10)| 필수| `PLAN` 또는 `ACTUAL`| 계획/실제 공수 구분  
`target_month`| DATE| 필수| `2024-04-01`| 해당 월의 1일 날짜 (YYYY-MM-01)  
`man_days`| FLOAT| 필수| `3.2`| 해당 월의 투입 공수 (MD 단위)  
`assignee`| VARCHAR(100)| -| `전승범`| 담당자 (그룹핑/필터링 최적화용)  
`epic_key`| VARCHAR(50)| -| `EPIC-123`| Epic 키 (그룹핑/필터링 최적화용)  
`initiative_key`| VARCHAR(50)| -| `INIT-456`| Initiative 키 (그룹핑/필터링 최적화용)  
`battle_key`| VARCHAR(50)| -| `BATTLE-24Q1`| Battle 키 (그룹핑/필터링 최적화용)  
  
### 5\. 시각화 팁 (SQL 예시)

"특정 세션에서 담당자별 월별 투입 계획"을 확인하려면 다음과 같이 쿼리할 수 있습니다.
[code]
    SELECT target_month, assignee, SUM(man_days) as total_md
    FROM monthly_allocations
    WHERE session_id = 10 AND category = 'PLAN'
    GROUP BY target_month, assignee;
    
[/code]

## 자주 묻는 질문 (FAQ)

  * **Q: 테이블을 미리 만들어야 하나요?**
    * 아니요, `roster`​가 실행될 때 필요한 테이블을 **자동으로 생성(Auto-Migrate)** ​하므로 데이터베이스(Schema)만 비어있는 상태로 준비해 두시면 됩니다.

---

#### 리소스 배분(Allocation) 규칙 가이드

- Page ID: `543086989`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543086989/%EB%A6%AC%EC%86%8C%EC%8A%A4+%EB%B0%B0%EB%B6%84+Allocation+%EA%B7%9C%EC%B9%99+%EA%B0%80%EC%9D%B4%EB%93%9C
- Depth: `2`

이 문서는 Roster CLI가 시트를 생성할 때 사용하는 리소스 배분 로직과 그 예시를 설명합니다.

## 1\. 핵심 원칙 (Core Principles)

Roster의 모든 시간 데이터는 **'순차적 평일 배분'** 기준을 근거로 계산됩니다.

  * **8시간 = 1일 (가변):** 하루 기본 작업량은 8시간으로 설정되나, `hours_per_day` 설정을 통해 사용자 환경에 맞게 조정 가능합니다.
  * **영업일 기준:** 토요일, 일요일 및 **지정된 공휴일** ​은 배분에서 제외됩니다.
  * **공휴일 설정:** `ROSTER_HOLIDAYS_PATH`로 지정된 파일의 날짜를 따릅니다. (기본값: `holidays.txt`)
  * **순차 할당:** 시작 시점부터 시간이 소진될 때까지 영업일에만 8시간씩 차례대로 채워 나갑니다.



## 2\. 시트별 배분 기준

### [plan] 시트 (계획 데이터)

  * **기준 필드:** Jira의 `Estimated` (Original Estimate)
  * **시작 일자:** 이슈의 `Target start` 필드값



### [actual] 시트 (실제 데이터)

  * **기준 필드:** 각 개별 업무 로그의 `Time Spent`
  * **시작 일자** : 각 업무 로그의 **" Date started"**(사용자가 로그 입력 시 지정한 날짜)
  * **합산 방식:** 한 이슈에 여러 로그가 있을 경우, 각 로그별로 배분한 결과를 월별로 합산합니다. 누가 Work log를 작성했는지는 고려하지 않습니다.



## 3\. 이슈 필터링 정책 (Filtering Policy)

Roster는 투입 공수 계산의 정확도를 위해 이슈 타입을 구분하여 필터링합니다.

분류| 대상 타입| [plan] / [actual] 포함 여부| 용도  
---|---|---|---  
**표준 이슈**|  Story, Task, Bug 등| **포함**|  실제 리소스 투입량 계산 및 시트 생성  
**상위 이슈**|  Battle, Initiative, Epic| **제외**|  계층 구조(Key 매핑) 파악을 위한 참조 데이터  
  
> [!NOTE] `plan`과 `actual` 시트의 `Epic`, `Initiative`, `Battle` 열에는 해당 표준 이슈가 속한 상위 이슈의 Key가 자동으로 매핑되어 출력됩니다.

## 4\. 다이어그램 표현

### 계획 배분 예시 (Plan Allocation)

`Estimated: 20h`, `Target start: 목요일` 인 경우의 흐름입니다.

## 4\. 상세 시나리오 예시

### 예시 1: 주말을 포함한 계획 배분 (plan)

  * **입력** : `Estimated: 24h (3d)`, `Target start: 2026-03-13 (금)`
  * **배분 결과** :
    * **13일(금)** : 8.00h (소진 예정: 16h)
    * **14일(토)** : 0.00h (주말 제외)
    * **15일(일)** : 0.00h (주말 제외)
    * **16일(월)** : 8.00h (소진 예정: 8h)
    * **17일(화)** : 8.00h (배분 완료)



### 예시 2: 여러 업무 로그가 있는 실제 배분 (actual)

한 이슈에 두 번 각각 다른 날짜에 로그를 남긴 경우입니다.

  * **입력** :
    * 로그 A: `8h`, `Date started: 2026-03-10 (화)`
    * 로그 B: `12h`, `Date started: 2026-03-12 (목)`
  * **배분 과정** :
    1. **로그 A 처리** : 10일(화)에 8.00h 할당
    2. **로그 B 처리** : 12일(목)에 8.00h, 13일(금)에 4.00h 할당
  * **최종 시트 합산 (3월)** : 8.00 (화) + 8.00 (목) + 4.00 (금) = **20.00h**



### 예시 3: 소수점 정밀도 (2-decimal)

  * **입력** : `Estimated: 10h (1.25d)`, `Target start: 월요일`
  * **배분 결과** :
    * **월요일** : 8.00h
    * **화요일** : 2.00h
  * 데이터가 정확히 8의 배수가 아니더라도 소수점 둘째 자리까지 정밀하게 계산되어 시트에 반영됩니다.



## 5\. 요약 테이블

항목| plan 시트| actual 시트  
---|---|---  
**계산 기준 시간**|  Original Estimate (계획 시간)| Individual Worklogs (실제 시간)  
**시작 날짜**|  이슈의 `Target start`| 각 로그의 `Date started`  
**일일 최대치**|  8시간 (평일만)| 8시간 (평일만)  
**주말/공휴일**|  건너뜀| 건너뜀  
**주말/공휴일**|  건너뜀| 건너뜀  
**출력 컬럼 (A~F)**|  Key -> Epic -> Initiative -> Battle -> Assignee -> Target start| Key -> Epic -> Initiative -> Battle -> Assignee -> Target start  
**필터링 대상**|  Epic, Initiative, Battle 자동 제외| Epic, Initiative, Battle 자동 제외

---

#### 비즈니스 활용 시나리오 (Use Cases)

- Page ID: `543087007`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543087007/%EB%B9%84%EC%A6%88%EB%8B%88%EC%8A%A4+%ED%99%9C%EC%9A%A9+%EC%8B%9C%EB%82%98%EB%A6%AC%EC%98%A4+Use+Cases
- Depth: `2`

`roster` 프로그램은 데이터를 바라보는 관점에 따라 업무 현장에서 매우 다양하게 활용될 수 있습니다. 이 문서는 4가지 핵심 비즈니스 사용자 유형이 자신의 업무 목적에 맞게 이 도구를 어떻게 활용할 수 있는지 구체적인 시나리오와 JQL 예시를 제공합니다.  
  
## 1\. 실무 담당자 (Assignee)

**" 내 업무량과 워라밸 방어 및 회고"**

실무 개발자나 기획자는 본인에게 할당된 업무가 가용 시간(Capacity)을 초과하지 않는지 확인하고, 지난 업무를 회고하는 데 이 도구를 사용합니다.

  * **주요 목적:**
    * 이번 달에 나에게 할당된 계획(Plan) 공수가 과도하지 않은가? (번아웃 방지)
    * 내가 지난달 티켓에 시간(Worklog)을 누락 없이 잘 기록했는가?
  * **활용 예시 (명령어 및 JQL):**
[code]# 내 할당 이슈만 가져오는 기본 JQL 설정 (config.yaml 또는 환경변수 JIRA_JQL)
        # JQL: assignee = currentUser()
        
        # 향후 3개월간 내 예상 부하량(Overload) 확인
        ./roster console --type plan --range 202604:202606
        
        # 지난 달 내가 실제로 투입한 시간(Worklog) 회고
        ./roster console --type actual --range 202603
        
[/code]




## 2\. 피플 매니저

**" 팀원 업무 분배 및 리소스 밸런싱"**

팀장이나 파트장은 소속 팀원들의 업무 부하를 모니터링하고, 병목(Bottleneck)을 해결하기 위해 티켓을 재분배하는 데 활용합니다.

  * **주요 목적:**
    * 우리 팀원 중 특정 인원에게 업무가 몰려 있는가?
    * 어떤 팀원의 리소스가 남아 추가 작업 할당이 가능한가?
    * 주간 회의(Weekly Sync) 시 팀 전체의 업무 현황 리뷰.
  * **활용 예시 (명령어 및 JQL):**
[code]# 특정 팀이나 파트의 인원만 필터링하는 JQL 적용
        # JQL: assignee in membersOf("Payment Engineering") AND resolution is EMPTY
        
        # 팀원 전체의 향후 2개월 계획을 터미널에서 빠르게 확인
        ./roster console --type plan --range 202604:202605
        
        # 팀 주간 회의를 위해 구글 시트로 데이터를 내보내어 팀원들과 공유
        ./roster sheets --type plan --range 202604
        
[/code]




## 3\. 프로젝트 관리자

**" 프로젝트 일정 및 진행률 트래킹"**

특정 프로젝트나 에픽을 리딩하는 PM/PO는 목표한 일정 내에 개발 리소스가 충분히 투입되고 있는지 모니터링합니다.

  * **주요 목적:**
    * 내가 리딩하는 Epic(또는 Initiative)에 필요한 개발 리소스가 제때 투입되고 있는가?
    * 계획된 공수(Plan) 대비 실제 투입된 공수(Actual)가 부족하거나 초과하여 일정이 지연되고 있지는 않은가?
  * **활용 예시 (명령어 및 JQL):**
[code]# 특정 프로젝트(Epic) 단위로 하위 이슈를 묶어서 조회하는 JQL 적용
        # JQL: "Epic Link" = SELLER-3365
        
        # 특정 프로젝트(Initiative) 단위로 하위 이슈를 묶어서 조회하는 JQL 적용
        # JQL: issueFunction in issuesInEpics("issueFunction in portfolioChildrenOf('key = ROAD-75')")
        
        # 특정 프로젝트에 투입되는 개발자들의 리소스를 확인
        ./roster console --type plan --range 202604:202606
        
[/code]




## 4\. 전사 프로젝트 / 조직 총괄 (PMO / C-Level)

**" 전사 전략 달성 및 리소스 포트폴리오 관리"**

전사 차원에서 다수의 프로젝트를 총괄하는 PMO는 회사의 개발 리소스가 올해의 핵심 과제(Battle/Initiative)에 올바른 비율로 투자되고 있는지 거시적으로 분석합니다.

  * **주요 목적:**
    * 올해 전사 핵심 전략 과제들에 경영진의 가이드라인(Guardrail) 대비 실제 할당(Booking)된 리소스가 일치하는가?
    * 투자 우선순위가 낮은 레거시 유지보수 프로젝트에 리소스가 과도하게 낭비되고 있지는 않은가?
  * **활용 예시 (명령어 및 JQL):**
[code]# 특정 Battle 단위로 하위 이슈를 묶어서 조회하는 JQL 적용
        # JQL: issueFunction in issuesInEpics("issueFunction in portfolioChildrenOf('key = ROAD-17')")
        
        # 본부원 전체를 대상으로 조회하는 JQL 적용
        # JQL: assignee in membersOf("Technology") AND created >= 2026-01-01
        
        # 사내 데이터베이스에 지속적으로 적재하여 BI 대시보드(Grafana 등) 구축
        ./roster db
        
        # JSON 형태로 통계를 추출하여 별도의 사내 시스템과 연동
        ./roster console --format json > portfolio_analysis.json
        
[/code]

---

#### 일반 사용자 가이드 (User Guide)

- Page ID: `543087009`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543087009/%EC%9D%BC%EB%B0%98+%EC%82%AC%EC%9A%A9%EC%9E%90+%EA%B0%80%EC%9D%B4%EB%93%9C+User+Guide
- Depth: `2`

이 문서는 모든 사용자가 `roster` 프로그램을 설치하고 실행하는 과정을 안내합니다.

## 1\. 프로그램 준비

`roster` 프로그램은 보안을 위해 **웹 브라우저를 통한 간편 로그인(OAuth 2.0)**을 지원합니다. 개발자로부터 전달받은 실행 파일(`roster` 또는 `roster.exe`)을 실행하면 됩니다. (만일 사내 github에 접근 가능하다면, https://github.gmarket.com/jseungbum/roster 의 Release에서 다운로드 받습니다.)

### Jira 로그인 (필수)

프로그램을 실행하여 데이터를 분석하려면 사내 Jira 계정 로그인이 필요합니다.

  1. 터미널(또는 명령 프롬프트)에서 다운로드 받은 프로그램을 실행합니다.
[code]./roster console
         
[/code]

  2. **자동 브라우저 실행:** 기본 브라우저가 열리며 Jira 로그인 화면이 나타납니다.
  3. **로그인 및 승인:** 본인의 사내 Jira 계정으로 로그인한 후, 권한 요청 화면에서 **[Allow(허용)]**을 클릭합니다.
  4. 브라우저에 "Jira 인증 성공!" 메시지가 표시되면 창을 닫고 터미널로 돌아옵니다. 분석 결과가 즉시 출력됩니다.



### Google Sheets 로그인 (선택)

분석 결과를 구글 시트로 바로 내보내려면 구글 인증이 추가로 필요합니다.

  1. 시트 출력 명령어를 실행합니다.
[code]./roster sheets
         
[/code]

  2. **자동 브라우저 실행:** 구글 로그인 화면이 나타납니다.
  3. **로그인 및 승인:** 본인의 사내 구글 계정으로 로그인 후 **[허용]**을 선택합니다.
  4. 브라우저에 "인증 성공!" 메시지가 표시되면 창을 닫습니다. 데이터가 시트에 성공적으로 기록됩니다.



## 2\. 자주 묻는 질문 (FAQ)

  * **Q: 매번 실행할 때마다 로그인을 해야 하나요?**
    * **A:** 아니요. 처음에 한 번만 로그인하면 인증 정보가 컴퓨터에 안전하게 자동 저장(`~/.config/roster/`)되어 다음부터는 묻지 않습니다.
  * **Q: 브라우저가 자동으로 열리지 않아요.**
    * **A:** 터미널 화면에 출력된 긴 영어 주소(`http://localhost:...`)를 마우스로 복사하여, 인터넷 브라우저 주소창에 직접 붙여넣으세요.
  * **Q: '확인되지 않은 앱' 경고가 표시됩니다. (Google)**
    * **A:** 사내 내부용 앱으로 등록된 상태이므로 안심하셔도 됩니다. **[고급] > [roster(으)로 이동]**을 클릭하여 계속 진행하세요.
  * **Q: 다른 컴퓨터로 자리를 옮겼는데 어떻게 하나요?**
    * **A:** 새 컴퓨터에서 처음 실행할 때 위 1단계의 로그인 과정을 한 번만 다시 진행해 주시면 됩니다.



## 3\. 리소스 계산 및 공휴일 안내

Roster CLI는 정확한 리소스 투입량 계산을 위해 대한민국 법정 공휴일(2025~2027) 데이터를 **기본적으로 내장** 하고 있습니다.

  * 별도의 설정 없이도 주말 및 공휴일이 계산에서 자동으로 제외됩니다.
  * 만약 별도의 휴일을 적용하고 싶다면, `holidays.txt` 파일을 생성하여 날짜를 입력하면 내장된 데이터보다 우선적으로 적용됩니다.

---

### 중요 필드 입력 누락 방지, 입력 독려

- Page ID: `543086919`
- URL: https://wiki.gmarket.com/spaces/PDLC/pages/543086919/%EC%A4%91%EC%9A%94+%ED%95%84%EB%93%9C+%EC%9E%85%EB%A0%A5+%EB%88%84%EB%9D%BD+%EB%B0%A9%EC%A7%80+%EC%9E%85%EB%A0%A5+%EB%8F%85%EB%A0%A4
- Depth: `1`

## 미작성자 식별 (JQL 필터링 및 대시보드 시각화)

전사 공용 대시보드의 'Two Dimensional Filter Statistics' 가젯에 담당자(Assignee) 기준으로 배치하여 데이터 누락 현황을 시각화
[code] 
    filter = pdlc_missing_fields
[/code]

팀 공용 대시보드의 'Two Dimensional Filter Statistics' 가젯에 담당자(Assignee) 기준으로 배치하여 데이터 누락 현황을 시각화
[code] 
    filter = pdlc_missing_fields AND assignee in (membersOf("Payment Engineering"))
[/code]

## 프로세스 강제 (Workflow Validator 적용)

필수 데이터가 입력되지 않으면 이슈의 상태를 변경할 수 없도록 시스템 단에서 차단.

### 시작 통제 ('To Do' -> 'In Progress')

상태 전환 시 Target start, Target end, Original estimate 필드에 값이 존재하는지 검사하는 Validator를 추가. 누락 시 입력 요구 에러 메시지를 출력하고 전환을 취소.

### 완료 통제 ('In Progress' -> 'Done')

Time spent 필드의 값이 0보다 큰지 검사하는 Validator를 추가. Worklog가 단 1분이라도 기록되어야만 작업을 완료할 수 있음.

## 자동화된 알림

관리자의 개입을 최소화하기 위해 정기적인 자동 독려 시스템을 구축하십시오.

Trigger: 매일? 매주?

Condition: 위에서 정의한 미작성자 식별 JQL 실행

## Filter pdlc_missing_fields

Initiative 하위 issue 중 중요 필드 누락된 issue.
[code] 
    (
        issuetype = Initiative
        OR issueFunction in portfolioChildrenOf('issuetype = Initiative')
        OR issueFunction in issuesInEpics("issueFunction in portfolioChildrenOf('issuetype = Initiative')")
    )
    AND
    (
        "Target start" is EMPTY 
        OR "Target end" is EMPTY 
        OR originalEstimate is EMPTY 
        OR (resolution is not EMPTY AND timespent is EMPTY)
    )
    AND assignee is not EMPTY
[/code]

Initiative 하위가 아닌 issue는 팀 수준에서 관리.
