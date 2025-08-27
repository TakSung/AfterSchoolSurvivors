# 작업 일지 작성 명령어

이 세션에서 진행한 모든 작업 내용을 체계적으로 정리하여 문서화합니다.

## 사용법
```
/write-work-docs [파일명] [세부옵션]
```

예시:
```
/write-work-docs
/write-work-docs custom-filename.md
/write-work-docs --format=detailed
```

## 실행 절차

### 1단계: 세션 작업 내용 수집
- Task Master 작업 이력 분석
- 생성/수정된 파일 목록 확인
- 사용자 요청사항 및 대화 내용 정리
- 코드 변경사항 및 리팩토링 내용 파악

### 2단계: 작업 일지 구조화
```markdown
# [작업명] 작업 일지

**작업 일자**: YYYY-MM-DD
**작업자**: Claude Code
**Task Master ID**: [해당되는 경우]

## 📋 작업 개요
[세션에서 수행한 주요 작업들 요약]

### 사용자 요청사항
1. [첫 번째 요청]
2. [두 번째 요청]
...

### 완료된 작업
- [x] [완료된 작업 1]
- [x] [완료된 작업 2]
...

## 🔄 상세 작업 내용

### [작업 카테고리 1]
[해당 작업의 상세 설명]

#### Before/After 비교
```python
# Before
[이전 코드 또는 상태]

# After  
[변경 후 코드 또는 상태]
```

## 📁 생성/수정된 파일

### 새로 생성된 파일
```
path/to/file1.py - [파일 설명]
path/to/file2.py - [파일 설명]
```

### 수정된 파일
```
path/to/modified1.py - [수정 내용 요약]
path/to/modified2.py - [수정 내용 요약]
```

## 🧪 테스트 결과
[실행한 테스트들과 그 결과]

## 💡 핵심 개선사항
1. [개선사항 1]
2. [개선사항 2]
...

## 🔄 다음 단계
[남은 작업이나 제안사항]

---
**작업 완료 시간**: [소요 시간]
**코드 품질**: [린터/타입 체크 결과]
**전체 상태**: [프로젝트 진행 상황]
```

### 3단계: 자동 파일 생성
- 기본 경로: `docs/done/YYYY-MM-DD-session-work.md`
- 사용자 지정 파일명이 있으면 해당 이름 사용
- 중복 파일명 처리 (자동 번호 추가)

### 4단계: 품질 검증
- 한국어 설명 포함 여부 확인
- 마크다운 문법 검증
- 필수 섹션 포함 여부 체크
- 코드 블록 언어 지정 확인

## 출력 포맷

### 성공 시
```json
{
    "success": true,
    "message": "작업 일지가 성공적으로 생성되었습니다",
    "data": {
        "file_path": "docs/done/2025-08-26-session-work.md",
        "sections_count": 8,
        "total_lines": 150,
        "files_documented": 3
    },
    "summary": "📄 작업 일지 완성: 3개 파일 변경사항, 2개 새 기능 구현 문서화"
}
```

### 실패 시
```json
{
    "success": false,
    "message": "작업 일지 생성 중 오류가 발생했습니다",
    "error": "디렉토리 생성 실패: docs/done",
    "suggestion": "docs/done 디렉토리를 먼저 생성해주세요"
}
```

## 사용자 편집 가능 부분

이 명령어는 다음 부분을 사용자가 커스터마이징할 수 있습니다:

- [ ] **문서 템플릿**: 작업 일지 구조와 섹션 수정
- [ ] **출력 경로**: 기본 `docs/done/` 경로 변경  
- [ ] **파일명 패턴**: 날짜 형식이나 네이밍 규칙 조정
- [ ] **상세도 레벨**: `--format=simple|detailed|comprehensive` 옵션
- [ ] **언어 설정**: 한국어/영어 혼합 사용 비율 조정

## 고급 옵션

### 상세도 레벨
```bash
# 간단한 요약만
/write-work-docs --format=simple

# 기본 상세도 (권장)
/write-work-docs --format=detailed  

# 모든 대화와 코드 변경사항 포함
/write-work-docs --format=comprehensive
```

### 특정 작업만 문서화
```bash
# Task Master 특정 태스크만
/write-work-docs --task-id=44.1

# 특정 파일 변경사항만
/write-work-docs --files=src/core/entity.py,src/core/entity_factory.py
```

### 출력 형식 선택
```bash
# 마크다운 (기본)
/write-work-docs --output=markdown

# JSON 형태로
/write-work-docs --output=json

# 플레인 텍스트로
/write-work-docs --output=text
```