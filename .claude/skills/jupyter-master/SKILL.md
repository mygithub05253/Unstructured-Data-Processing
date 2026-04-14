---
name: jupyter-master
description: >
  Jupyter Notebook(.ipynb) 파일을 안전하게 생성하고 대회 제출 규격에 맞게 정리하는 스킬.
  다음 상황에서 반드시 사용하라:
  - 파이썬 스크립트(.py)를 노트북(.ipynb)으로 변환해야 할 때
  - 경쟁 대회(Kaggle, DACON, 기타 AI 경진대회)에 노트북을 제출하기 위해 정리할 때
  - ".ipynb 수정", "노트북 출력 지우기", "셀 결과 초기화", "대회 제출용 노트북" 등의 요청이 있을 때
  - 사용자가 노트북 JSON 구조가 깨질까 봐 걱정할 때
  - Jupyter, Colab, Kaggle, DACON 노트북 관련 작업 전반에서 사용하라.
  절대 사용하지 말 것: .ipynb 파일을 직접 텍스트 편집(Edit/Write 도구)하는 것. 이 스킬을 통해서만 처리하라.
compatibility:
  python_packages:
    - jupytext
    - nbconvert
---

# Jupyter Master — 대회용 노트북 안전 처리 스킬

## 핵심 원칙 (왜 이 스킬이 필요한가)

`.ipynb` 파일은 겉으로는 Python 코드처럼 보이지만, 실제로는 **복잡한 JSON 구조**를 가진 파일이다.
Claude가 Edit/Write 도구로 `.ipynb`를 직접 수정하면 JSON이 깨져서 노트북 자체가 열리지 않게 된다.

이 스킬은 두 가지 안전한 CLI 도구를 제공하여 이 문제를 근본적으로 해결한다.

**황금 규칙: Claude는 `.ipynb` 파일을 절대 직접 편집하지 않는다. 항상 이 스킬의 스크립트를 통해서만 처리한다.**

---

## 사전 준비: 의존성 설치

스크립트 실행 전, 필요한 패키지가 설치되어 있는지 확인한다.

```bash
pip install jupytext nbconvert
```

---

## 기능 1: `.py` → `.ipynb` 변환 (`convert`)

사용자가 작성한 순수 파이썬 스크립트를 노트북으로 변환할 때 사용한다.

### 사용법

```bash
# 기본 변환 (같은 폴더에 동일 이름으로 생성)
python .claude/skills/jupyter-master/scripts/jupyter_tools.py convert solution.py

# 출력 경로 지정
python .claude/skills/jupyter-master/scripts/jupyter_tools.py convert solution.py --output submission.ipynb
```

### 작동 방식

`jupytext` 라이브러리가 `.py` 파일의 주석 구조(`# %%` 또는 `# In[N]:`)를 분석하여
올바른 JSON 형식의 `.ipynb`를 생성한다. Claude가 JSON을 직접 조작할 필요가 없다.

### `.py` 파일에서 셀 구분하기

jupytext는 파이썬 스크립트에서 셀 구분자를 자동으로 인식한다:

```python
# %% [markdown]
# # 제목 셀 (마크다운)

# %%
# 코드 셀 1
import pandas as pd
df = pd.read_csv('train.csv')

# %%
# 코드 셀 2
print(df.head())
```

셀 구분자가 없는 일반 `.py` 파일도 변환은 되지만, 전체가 하나의 코드 셀로 만들어진다.

---

## 기능 2: 대회 제출용 출력 초기화 (`clean`)

대회 채점 시스템의 감점 규칙을 피하기 위해 사용한다.

> **왜 필요한가?** 일부 대회(Kaggle 등)는 노트북에 셀 실행 결과(output)가 저장되어 있으면
> "노트북을 실제로 실행하지 않고 결과만 붙여넣었다"고 의심하거나,
> 반대로 실행 결과가 없으면 "미실행 상태"로 간주하여 감점한다.
> 제출 규칙을 확인하고, 대부분의 대회는 **출력 없이 제출**을 요구한다.

### 사용법

```bash
python .claude/skills/jupyter-master/scripts/jupyter_tools.py clean submission.ipynb
```

원본 파일이 in-place로 수정된다. 모든 셀의 `outputs`와 `execution_count`가 초기화된다.

---

## 작업 흐름 (일반적인 시나리오)

### 시나리오 A: 처음부터 대회용 노트북 만들기

1. **Claude가 코드 작성**: `solution.py` (순수 파이썬 스크립트)
2. **변환**: `jupyter_tools.py convert solution.py --output submission.ipynb`
3. **출력 초기화**: `jupyter_tools.py clean submission.ipynb`
4. **최종 확인** → 아래 경고 출력

### 시나리오 B: 기존 노트북 제출 준비

1. **출력 초기화**: `jupyter_tools.py clean existing_notebook.ipynb`
2. **최종 확인** → 아래 경고 출력

---

## 작업 완료 후 필수 경고

**모든 작업이 완료된 후, Claude는 반드시 다음 메시지를 사용자에게 출력해야 한다:**

```
✨ 작업 완료! 제출하기 전에 반드시 Google Colab에 업로드하고
   '런타임 > 모두 실행'을 눌러 에러가 없는지 확인하세요!
```

이 경고는 생략할 수 없다. 로컬 환경과 Colab/Kaggle 환경의 패키지 버전 차이로 인한
런타임 오류를 제출 전에 발견하는 것이 목적이다.

---

## 오류 처리

| 오류 메시지 | 원인 | 해결책 |
|---|---|---|
| `jupytext 변환 실패` | jupytext 미설치 또는 .py 파일 인코딩 오류 | `pip install jupytext` 실행 |
| `nbconvert 출력 초기화 실패` | nbconvert 미설치 | `pip install nbconvert` 실행 |
| `입력 파일을 찾을 수 없습니다` | 잘못된 파일 경로 | 경로를 다시 확인 |
| `.py 파일만 변환할 수 있습니다` | .ipynb를 convert에 전달 | clean 명령어 사용 |

---

## 스크립트 직접 import하여 사용하기 (고급)

Claude가 Python 코드 내에서 기능을 호출해야 할 때:

```python
import sys
sys.path.insert(0, '.claude/skills/jupyter-master/scripts')
from jupyter_tools import convert_to_ipynb, clean_for_submission

# 변환
dest = convert_to_ipynb('solution.py', output='submission.ipynb')

# 출력 초기화
clean_for_submission('submission.ipynb')
```
