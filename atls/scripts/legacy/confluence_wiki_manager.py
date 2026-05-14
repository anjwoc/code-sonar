import os
#!/usr/bin/env python3
import requests
import json
import argparse
import urllib.parse

TOKEN = os.environ.get("ATLS_JIRA_TOKEN") or os.environ.get("ATLS_CONFLUENCE_TOKEN", "")
BASE_URL = "https://wiki.gmarket.com/rest/api/content"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def search_page(space_key, title):
    """space와 제목으로 컨플루언스 페이지를 검색하여 정보를 콘솔에 출력합니다."""
    cql = f'space="{space_key}" and title="{title}"'
    url = f"{BASE_URL}/search?cql={urllib.parse.quote(cql)}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code == 200:
        results = resp.json().get('results', [])
        for r in results:
            print(f"ID: {r['id']}, 제목: {r['title']}, 웹경로: {r['_links']['webui']}")
        if not results:
            print("검색 결과가 없습니다.")
        return results
    else:
        print(f"[FAILED] 검색 실패: {resp.text}")
        return []

def create_page(space_key, parent_id, title, content_html):
    """새로운 컨플루언스 페이지를 지정된 상위 페이지 아래에 생성합니다."""
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "ancestors": [{"id": str(parent_id)}],
        "body": {
            "storage": {
                "value": content_html,
                "representation": "storage"
            }
        }
    }
    resp = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print(f"[SUCCESS] 페이지 생성 완료! ID: {data['id']}, URL: /spaces/{space_key}/pages/{data['id']}")
    else:
        print(f"[FAILED] 페이지 생성 실패: {resp.text}")

def update_page(page_id, title, content_html):
    """기존 특정 컨플루언스 페이지의 내용을 덮어씌워 수정(version UP)합니다."""
    # 1. 문서 현재 버전 조회 (PUT은 버전을 올려서 전송해야 함)
    get_resp = requests.get(f"{BASE_URL}/{page_id}?expand=version", headers=HEADERS, timeout=10)
    if get_resp.status_code != 200:
        print(f"[FAILED] 페이지 버전 정보 획득 실패: {get_resp.status_code}")
        return
    
    current_version = get_resp.json()['version']['number']
    
    payload = {
        "type": "page",
        "title": title,
        "version": {"number": current_version + 1},
        "body": {
            "storage": {
                "value": content_html,
                "representation": "storage"
            }
        }
    }
    upp_resp = requests.put(f"{BASE_URL}/{page_id}", headers=HEADERS, json=payload, timeout=10)
    if upp_resp.status_code == 200:
        print(f"[SUCCESS] 페이지 업데이트 완료! 버전: {current_version + 1}")
    else:
        print(f"[FAILED] 페이지 업데이트 실패: {upp_resp.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confluence Wiki Manager")
    parser.add_argument("action", choices=["search", "create", "update"], help="액션 (search/create/update)")
    parser.add_argument("--space", default="~jaecjeong", help="위키 Space Key (기본값: ~jaecjeong)")
    parser.add_argument("--title", help="문서 검색 제목 혹은 생성/수정될 문서의 타이틀")
    parser.add_argument("--parent-id", help="create 시: 상위 페이지 ID")
    parser.add_argument("--page-id", help="update 시: 기존 수정할 페이지 ID")
    parser.add_argument("--html", help="본문 HTML 내용 문자열", default="<h1>자동 생성 문서</h1><p>내용을 입력하세요.</p>")

    args = parser.parse_args()

    if args.action == "search":
        if not args.title:
            print("[ERROR] search 액션은 --title 매개변수가 필수입니다.")
        else:
            search_page(args.space, args.title)
    
    elif args.action == "create":
        if not args.title or not args.parent_id:
            print("[ERROR] create 액션은 --title 과 --parent-id 가 필수입니다.")
        else:
            create_page(args.space, args.parent_id, args.title, args.html)
            
    elif args.action == "update":
        if not args.title or not args.page_id:
            print("[ERROR] update 액션은 --title 과 --page-id 가 필수입니다.")
        else:
            update_page(args.page_id, args.title, args.html)
