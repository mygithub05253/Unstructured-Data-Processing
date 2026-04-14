# Command: /save-state

## Description
Claude Code 세션을 종료하기 전에 현재까지의 작업 진행 상황, 최고 점수, 다음 할 일을 요약하여 기억합니다.

## Instructions
프로젝트 루트 디렉토리에 `MEMORY.md` 파일을 생성하거나 기존 파일을 업데이트하여 다음 내용을 마크다운으로 기록하세요:
1. **Current Best Score**: 현재 달성한 최고 MCC 점수와 해당 점수를 낸 모델명(알고리즘), 주요 하이퍼파라미터.
2. **Preprocessing State**: 현재 적용 중인 텍스트 전처리 기법 (예: Pecab 형태소 분석 여부, 정규표현식 클리닝 규칙 등).
3. **Next TODO**: 다음 세션에서 이어서 해야 할 실험(예: SVM 파라미터 C값 튜닝)이나 코드 수정 사항.
