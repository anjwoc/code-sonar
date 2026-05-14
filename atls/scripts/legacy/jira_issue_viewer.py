import os
#!/usr/bin/env python3
import requests
import json
import argparse

TOKEN = os.environ.get("ATLS_JIRA_TOKEN") or os.environ.get("ATLS_CONFLUENCE_TOKEN", "")
BASE_URL = "https://jira.gmarket.com/rest/api/2/issue"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

def get_issue(issue_id):
    """특정 지라의 상태, 담당자, 디스크립션 등을 조회하여 출력합니다."""
    url = f"{BASE_URL}/{issue_id}?fields=summary,description,status,assignee,priority"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    
    if resp.status_code == 200:
        data = resp.json()
        fields = data.get("fields", {})
        
        status = fields.get("status", {}).get("name", "Unknown")
        assignee = fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned"
        priority = fields.get("priority", {}).get("name", "Unknown")
        summary = fields.get("summary", "")
        desc = fields.get("description", "")
        
        print("="*60)
        print(f"[{issue_id}] {summary}")
        print(f"상태: {status} | 담당자: {assignee} | 중요도: {priority}")
        print("-" * 60)
        print("내용:")
        print(desc if desc else "설명이 없습니다.")
        print("="*60)
    else:
        print(f"[FAILED] {issue_id} 조회 실패: {resp.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JIRA Issue Viewer")
    parser.add_argument("issue", help="조회할 지라 이슈 키 (예: GEMINI-1234)")
    
    args = parser.parse_args()
    get_issue(args.issue)
