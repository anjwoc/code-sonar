import os
#!/usr/bin/env python3
import requests
import json
import argparse
from datetime import datetime

TOKEN = os.environ.get("ATLS_JIRA_TOKEN") or os.environ.get("ATLS_CONFLUENCE_TOKEN", "")
BASE_URL = "https://jira.gmarket.com/rest/api/2/issue"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def add_worklog(issue_id, comment, time_spent, start_time=None):
    """지정된 이슈에 워크로그를 추가합니다."""
    url = f"{BASE_URL}/{issue_id}/worklog"
    payload = {
        "comment": comment,
        "timeSpent": time_spent
    }
    if start_time:
        # start_time 포맷 예시: '2026-03-31T09:00:00.000+0900'
        payload["started"] = start_time
        
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=10)
    if resp.status_code in (200, 201):
        print(f"[SUCCESS] {issue_id} 워크로그 추가 완료")
    else:
        print(f"[FAILED] {issue_id} 에러: {resp.text}")

def update_worklog_time(issue_id, worklog_id, new_start_time, time_spent=None, comment=None):
    """지정된 워크로그의 시간이나 내용을 수정합니다."""
    url = f"{BASE_URL}/{issue_id}/worklog/{worklog_id}"
    payload = {"started": new_start_time}
    if time_spent:
        payload["timeSpent"] = time_spent
    if comment:
        payload["comment"] = comment
        
    resp = requests.put(url, headers=HEADERS, json=payload, timeout=10)
    if resp.status_code == 200:
        print(f"[SUCCESS] {issue_id}의 워크로그({worklog_id}) 수정 완료")
    else:
        print(f"[FAILED] 워크로그 수정 실패: {resp.text}")

def get_worklogs(issue_id):
    """해당 이슈의 모든 워크로그를 조회합니다."""
    url = f"{BASE_URL}/{issue_id}/worklog"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code == 200:
        logs = resp.json().get("worklogs", [])
        for log in logs:
            print(f"ID: {log['id']}, 저자: {log['author'].get('displayName')}, 소요시간: {log.get('timeSpent')}, 시작: {log.get('started')}, 내용: {log.get('comment')}")
    else:
        print(f"[FAILED] 조회 실패: {resp.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JIRA Worklog Manager")
    parser.add_argument("action", choices=["add", "update", "list"], help="액션 (add/update/list)")
    parser.add_argument("--issue", required=True, help="지라 이슈 키 (예: GEMINI-1234)")
    parser.add_argument("--comment", help="워크로그 코멘트 내용")
    parser.add_argument("--time", help="소요시간 (예: 15m, 1h 30m)")
    parser.add_argument("--started", help="시작 시간 (예: 2026-03-31T09:00:00.000+0900)")
    parser.add_argument("--worklog-id", help="update 시 변경할 워크로그 ID")

    args = parser.parse_args()

    if args.action == "list":
        get_worklogs(args.issue)
    elif args.action == "add":
        if not args.comment or not args.time:
            print("[ERROR] add 시에는 --comment 와 --time 이 필수입니다.")
        else:
            add_worklog(args.issue, args.comment, args.time, args.started)
    elif args.action == "update":
        if not args.worklog_id or not args.started:
            print("[ERROR] update 시에는 --worklog-id 와 --started 가 필수입니다.")
        else:
            update_worklog_time(args.issue, args.worklog_id, args.started, args.time, args.comment)
