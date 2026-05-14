# Team Distribution Guide

## 목표

`atls`를 팀원들이 공통 CLI처럼 설치하고 동일한 명령 체계를 쓰도록 준비한다.

## 현재 준비 상태

- `src/` 기반 패키지 구조 적용
- `pyproject.toml` 추가
- `project.scripts.atls` 엔트리포인트 제공
- 루트 `atls.py` / `bin/atls` 호환 실행 유지
- `scripts/build_dist.sh`로 wheel / sdist 빌드 가능

## 로컬 검증

```bash
cd /path/to/atsl
python3 -m pip install -e .
atls meta
atls doctor
```

## 배포 산출물 만들기

```bash
cd /path/to/atsl
./scripts/build_dist.sh
```

생성 결과:

```text
dist/
├── atls_cli-0.1.0-py3-none-any.whl
└── atls_cli-0.1.0.tar.gz
```

## 팀원 설치 방식

### 1. pipx 권장

```bash
pipx install atls_cli-0.1.0-py3-none-any.whl
atls meta
```

### 2. pip 설치

```bash
python3 -m pip install atls_cli-0.1.0-py3-none-any.whl
atls meta
```

## 배포 전 체크리스트

- `atls meta` 정상 동작
- `atls doctor` 정상 동작
- `atls workflow daily-review --max 5` read-only 검증
- `atls workflow qa-gemini-harness --no-jira --workspace-root /path/to/adcenter` 검증
- requests 의존성 포함 여부 확인
- 사내 기본 프로파일/토큰 배포 방식 별도 정의

## 다음 단계 권장

- 토큰/기본 profile을 코드 하드코딩이 아니라 외부 config 템플릿으로 분리
- CI에서 `python -m build`와 smoke test 자동화
- legacy 스크립트 기능을 점진적으로 `src/atls/cli.py`로 흡수
