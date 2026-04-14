# Command: /build-pipeline

## Description
현재까지 전처리된 데이터와 실험한 내용을 바탕으로 scikit-learn 기반의 최적 분류 파이프라인 코드를 작성하고 대회 규격에 맞게 피클링(저장)합니다.

## Instructions
1. 데이터 로드, 텍스트 벡터화(TF-IDF 등), 분류 모델(scikit-learn)을 반드시 하나의 `sklearn.pipeline.Pipeline` 객체로 묶는 코드를 작성하세요.
2. 교차 검증을 통해 얻은 최고 MCC 점수를 코드 주석이나 출력문으로 확인하세요.
3. 지정된 네이밍 컨벤션에 따라 모델을 저장하는 코드를 작성하세요.
   - 파일명 규칙: `{알고리즘}_v{버전}_mcc{소수점4자리}.pkl`
   - 예시: `logistic_regression_v1_mcc0.4521.pkl`
   - 라이브러리: `joblib` 사용 권장
4. 모델 객체와 데이터 분할 시 반드시 `random_state=42`가 적용되었는지 교차 검증하세요.
