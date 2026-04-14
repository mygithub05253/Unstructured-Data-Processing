# 비정형 데이터 처리 (Unstructured Data Processing)

가천대학교 비정형 데이터 처리 수업 실습 코드 저장소입니다.

## 📁 프로젝트 구조

```
unstructured-data-processing/
├── code/
│   ├── Week02/          # Python 문자열 처리 & 판다스 str 메서드
│   ├── Week03/          # 형태소 분석 & 정규표현식 & 워드클라우드
│   ├── Week04/          # 웹 스크래핑 (requests, BeautifulSoup)
│   ├── Week05/          # 텍스트 벡터화 (TF-IDF, 코사인 유사도)
│   ├── Week06/          # 텍스트 분류 (머신러닝 파이프라인)
│   └── Week07/          # 토픽 모델링 (LDA)
├── main.py
├── pyproject.toml       # uv 패키지 관리
└── uv.lock
```

## 📚 주차별 내용

| 주차 | 주제 | 주요 라이브러리 |
|------|------|----------------|
| Week 02 | Python 문자열 처리, Pandas `str` 메서드 | `pandas` |
| Week 03 | 형태소 분석, 정규표현식, 워드클라우드 | `konlpy`, `pecab`, `re`, `wordcloud` |
| Week 04 | HTTP 요청, 정적/동적 웹 스크래핑, CSV 저장 | `requests`, `beautifulsoup4`, `selenium` |
| Week 05 | BoW · TF-IDF 벡터화, n-gram, 코사인 유사도 | `scikit-learn`, `pecab` |
| Week 06 | 텍스트 분류 파이프라인, 랜덤포레스트, 로지스틱 회귀 | `scikit-learn`, `shap` |
| Week 07 | LDA 토픽 모델링, pyLDAvis 시각화 | `pyldavis`, `gensim` |

## ⚙️ 환경 설정

이 프로젝트는 [uv](https://docs.astral.sh/uv/)를 사용하여 패키지를 관리합니다.

### 1. uv 설치

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 가상환경 생성 및 패키지 설치

```bash
uv sync
```

### 3. Jupyter 커널 등록

```bash
uv run python -m ipykernel install --user --name unstructured-data-processing
```

### 4. 노트북 실행

VS Code에서 `.ipynb` 파일을 열고 `unstructured-data-processing` 커널을 선택하여 실행합니다.

## 🐍 Python 버전

Python 3.12 이상이 필요합니다. (`.python-version` 참고)

## 📦 주요 의존성

- `pandas` - 데이터프레임 처리
- `konlpy` / `pecab` - 한국어 형태소 분석
- `scikit-learn` - 머신러닝 파이프라인
- `beautifulsoup4` / `requests` - 웹 스크래핑
- `wordcloud` - 워드클라우드 생성
- `pyldavis` - LDA 시각화
- `matplotlib` / `seaborn` - 데이터 시각화
- `shap` - 모델 설명력 분석

## 👤 작성자

- 이동원 (202136006)
- 가천대학교
