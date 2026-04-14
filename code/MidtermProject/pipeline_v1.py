"""
pipeline_v1.py
한국어 감성 분류 파이프라인 v1

구성: pecab 형태소 분석기 + Word TF-IDF + Logistic Regression
목표: MCC(Matthews Correlation Coefficient) 최대화
제약: sklearn만 사용, random_state=42 고정

참고 강의:
  - UD-05-320: 한국어 TF-IDF (pecab 연결 패턴)
  - UD-05-220: TF-IDF 가중치 원리 (sublinear_tf, min_df 의미)
  - UD-06-300: LogisticRegression (텍스트 분류 강력한 baseline)
  - UD-06-200: 평가지표 (Precision/Recall/F1 — MCC가 최우선)
"""

import re
import warnings

import joblib
import numpy as np
import pandas as pd
from pecab import PeCab
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import matthews_corrcoef, make_scorer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

warnings.filterwarnings('ignore')
np.random.seed(42)

# ============================================================
# 0. 상수 설정
# ============================================================
DATA_DIR = './data'
RANDOM_STATE = 42


# ============================================================
# 1. 전처리 함수
# ============================================================
def cleanText(text: str) -> str:
    """
    기본 텍스트 정제 (한국어 감성 단서 보존)

    URL 제거 후 반복 자음/특수문자를 적당히 압축한다.
    감성 단서(ㅋㅋ, ㅠㅠ, !!!)는 제거하지 않고 최대 3회로 제한 — 의미 정보 유지.
    """
    text = str(text)
    # URL 제거
    text = re.sub(r'http\S+', '', text)
    # 반복 자음 압축: ㅋㅋㅋㅋ → ㅋㅋㅋ (감성 단서 보존, 과도한 반복만 줄임)
    text = re.sub(r'([ㅋㅎㅠㅜㄷ])\1{3,}', r'\1\1\1', text)
    # 반복 특수문자 압축: !!!!!! → !!!
    text = re.sub(r'([!?~])\1{2,}', r'\1\1\1', text)
    return text.strip()


class PecabTokenizer:
    """
    pecab 형태소 분석기 기반 토크나이저.

    sklearn Pipeline 직렬화(joblib) 호환을 위해 callable class로 구현.
    __getstate__에서 PeCab 인스턴스를 제외하고 역직렬화 시 재생성한다.

    [노트] 감성 분석은 nouns() 대신 morphs() 사용 — 이유:
      - nouns()는 명사만 추출 → "않다", "못", "안" 등 부정어 손실
      - morphs()는 전체 형태소 반환 → 부정 극성 단서 보존 가능
      참고: UD-05-320 강의 노트 "감성 분석: nouns() 대신 morphs() 검토"
    """

    def __init__(self):
        self._pecab = None  # 지연 초기화 (직렬화 시 제외됨)

    def _getPecab(self) -> PeCab:
        """PeCab 인스턴스 지연 초기화"""
        if self._pecab is None:
            self._pecab = PeCab()
        return self._pecab

    def __call__(self, text: str) -> list:
        """TfidfVectorizer tokenizer 인터페이스"""
        cleaned = cleanText(text)
        return self._getPecab().morphs(cleaned)

    def __getstate__(self):
        """joblib 직렬화 시 PeCab 인스턴스 제외 (역직렬화 후 재생성)"""
        state = self.__dict__.copy()
        state['_pecab'] = None
        return state


# ============================================================
# 2. 데이터 로드
# ============================================================
print('=== 1. 데이터 로드 ===')
train_df = pd.read_csv(f'{DATA_DIR}/public_train.csv')
test_df  = pd.read_csv(f'{DATA_DIR}/public_test.csv')
sub_df   = pd.read_csv(f'{DATA_DIR}/sample_submission.csv')

print(f'학습: {train_df.shape}, 테스트: {test_df.shape}')
print(f'라벨 분포:\n{train_df["label"].value_counts().to_string()}\n')

# 라벨은 문자열 그대로 사용 (POSITIVE / NEGATIVE)
# → LabelEncoder 없이 직접 학습 → predict()가 문자열 반환 → 역매핑 오류 방지
# 참고: student_guide 6장 "라벨을 0/1로 수동 인코딩은 비권장"
X_train = train_df['text'].tolist()
y_train = train_df['label'].tolist()
X_test  = test_df['text'].tolist()


# ============================================================
# 3. TF-IDF 파라미터 설정
# ============================================================
# Word TF-IDF 파라미터
# - analyzer='word': 형태소 토큰 단위 (PecabTokenizer가 반환하는 리스트)
# - ngram_range=(1,2): 단일 형태소 + 연속 2형태소 바이그램 — 문맥 포착
# - min_df=3: 3회 미만 등장 토큰 제거 → 노이즈 감소
# - max_df=0.95: 95% 이상 문서에 등장하는 극히 흔한 토큰 제거
# - sublinear_tf=True: log(1+tf) 변환 → 고빈도 단어 과다 반영 완화
# - max_features=100_000: 메모리/속도 트레이드오프 (15만 건 기준 적정값)
WORD_TFIDF_PARAMS = dict(
    analyzer='word',
    tokenizer=PecabTokenizer(),
    ngram_range=(1, 2),
    min_df=3,
    max_df=0.95,
    sublinear_tf=True,
    max_features=100_000,
)


# ============================================================
# 4. 파이프라인 구성
# ============================================================
# sklearn Pipeline: 전처리 + 모델을 하나로 묶음
#   → fit/predict 한 번 호출로 일관된 처리
#   → joblib.dump 시 벡터라이저 + 분류기 함께 저장 (재현성 보장)
pipeline_v1 = Pipeline([
    ('tfidf', TfidfVectorizer(**WORD_TFIDF_PARAMS)),
    ('clf',   LogisticRegression(
        C=1.0,          # 정규화 강도 역수 — 값이 클수록 규제 약함
        max_iter=1000,  # lbfgs 수렴 보장을 위해 충분히 설정
        random_state=RANDOM_STATE,
        solver='lbfgs', # 중소 규모 데이터셋에 안정적인 solver
        n_jobs=-1,      # 다중 클래스 OvR 병렬화 (이진 분류는 자동 무시)
    )),
])

print(f'파이프라인 구성:\n{pipeline_v1}\n')


# ============================================================
# 5. 교차검증 (MCC 기준 5-Fold)
# ============================================================
print('=== 2. 5-Fold 교차검증 (MCC) ===')
MCC_SCORER = make_scorer(matthews_corrcoef)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

cv_scores = cross_val_score(
    pipeline_v1, X_train, y_train,
    cv=cv,
    scoring=MCC_SCORER,
    n_jobs=-1,
)
cv_mean = cv_scores.mean()
cv_std  = cv_scores.std()
print(f'LogisticRegression(word) | CV MCC: {cv_mean:.4f} ± {cv_std:.4f}')
print(f'Fold 별 MCC: {[round(s, 4) for s in cv_scores]}\n')


# ============================================================
# 6. 전체 학습 데이터로 최종 모델 학습
# ============================================================
print('=== 3. 최종 모델 학습 (전체 데이터) ===')
pipeline_v1.fit(X_train, y_train)
print('학습 완료\n')


# ============================================================
# 7. 모델 저장
# ============================================================
# 파일 네이밍 규칙: {알고리즘}_v{버전}_mcc{점수}.pkl (student_guide 6장)
model_filename = f'logreg_v1_mcc{cv_mean:.4f}.pkl'
joblib.dump(pipeline_v1, model_filename)
joblib.dump(pipeline_v1, 'final_pipeline.pkl')  # 최종 제출용 필수 파일
print(f'=== 4. 모델 저장 완료 ===')
print(f'  → {model_filename}')
print(f'  → final_pipeline.pkl (LMS 제출 필수)\n')


# ============================================================
# 8. 테스트 예측 및 제출 파일 생성
# ============================================================
print('=== 5. 테스트 예측 및 제출 파일 생성 ===')
y_pred = pipeline_v1.predict(X_test)

# 라벨 검증 (student_guide 7장 권장 검증)
assert set(y_pred) <= {'POSITIVE', 'NEGATIVE'}, \
    f'라벨 형식 오류: {set(y_pred)}'
assert len(y_pred) == len(sub_df), \
    f'행 수 불일치: 예측 {len(y_pred)}행 vs 제출 샘플 {len(sub_df)}행'

# sample_submission 컬럼명에 맞춰 예측값 삽입
# student_guide: pred_label / 실제 샘플 파일이 label일 경우 모두 대응
if 'pred_label' in sub_df.columns:
    sub_df['pred_label'] = y_pred
else:
    sub_df['label'] = y_pred

sub_df.to_csv('./submission.csv', index=False, encoding='utf-8')
print('submission.csv 생성 완료')
print(pd.Series(y_pred, name='pred_label').value_counts().to_string())
print()
print(sub_df.head())
