# Coding Standards

## 🚨 [분류 경쟁 대회 필수 제약 조건 - Critical Rules]

> **이 섹션은 모든 다른 규칙보다 최우선으로 적용된다. 위반 시 즉각 코드를 폐기하고 에러 수준으로 경고해야 한다.**

### 1. [0점 방지] 금지 라이브러리 엄격 검사

`xgboost`, `lightgbm`, `catboost`, `tensorflow`, `pytorch`, `keras` 등의 외부 ML/DL 라이브러리가 코드에 포함되거나 import 되는지 100% 차단한다. 오직 `scikit-learn` 기반의 모델링만 허용된다.

- **검사 대상 import 패턴**: `import xgboost`, `import lightgbm`, `import catboost`, `import tensorflow`, `import torch`, `import keras`, `from xgboost`, `from lightgbm`, `from catboost`, `from tensorflow`, `from torch`, `from keras`
- **위반 시 조치**: 즉각 **ERROR** 수준으로 경고하고 해당 코드를 폐기한다. 어떠한 예외도 허용하지 않는다.
- **허용 라이브러리**: `scikit-learn` (sklearn) 계열만 허용

### 2. [감점 방지] Random State 강제 고정

`train_test_split` 및 무작위성이 포함된 모든 모델 객체 생성 시 반드시 `random_state=42`가 명시되어야 한다.

- **검사 대상**: `train_test_split(...)`, `RandomForestClassifier(...)`, `LogisticRegression(...)`, `SVC(...)`, `DecisionTreeClassifier(...)`, `GradientBoostingClassifier(...)`, `KMeans(...)` 등 random_state 파라미터를 지원하는 모든 sklearn 객체
- **위반 시 조치**: 즉시 `random_state=42`를 추가하도록 코드를 수정한다.
- **올바른 예시**: `train_test_split(X, y, test_size=0.2, random_state=42)`

### 3. [점수 반전 방지] 라벨 인코딩 절대 금지

예측 라벨(`label`)을 `0`과 `1`로 치환(mapping)하거나 변환하는 코드를 절대 작성하지 않는다. 모델은 반드시 원본 문자열인 `'POSITIVE'`, `'NEGATIVE'`를 그대로 학습하고 예측해야 한다.

- **금지 패턴**: `label.map({'POSITIVE': 1, 'NEGATIVE': 0})`, `LabelEncoder().fit_transform(...)`, `{'POSITIVE': 1}`, `{'NEGATIVE': 0}` 등 라벨을 숫자로 변환하는 모든 코드
- **위반 시 조치**: 즉각 **ERROR** 수준으로 경고하고 해당 변환 코드를 제거한다. 점수 반전(0점 처리)으로 이어지는 치명적 오류다.
- **올바른 예시**: `model.fit(X_train, y_train)` — `y_train`은 반드시 `'POSITIVE'`/`'NEGATIVE'` 문자열 그대로 유지

---

## Overview

This reference guide provides comprehensive information for code reviewer.

## Patterns and Practices

### Pattern 1: Best Practice Implementation

**Description:**
Detailed explanation of the pattern.

**When to Use:**
- Scenario 1
- Scenario 2
- Scenario 3

**Implementation:**
```typescript
// Example code implementation
export class Example {
  // Implementation details
}
```

**Benefits:**
- Benefit 1
- Benefit 2
- Benefit 3

**Trade-offs:**
- Consider 1
- Consider 2
- Consider 3

### Pattern 2: Advanced Technique

**Description:**
Another important pattern for code reviewer.

**Implementation:**
```typescript
// Advanced example
async function advancedExample() {
  // Code here
}
```

## Guidelines

### Code Organization
- Clear structure
- Logical separation
- Consistent naming
- Proper documentation

### Performance Considerations
- Optimization strategies
- Bottleneck identification
- Monitoring approaches
- Scaling techniques

### Security Best Practices
- Input validation
- Authentication
- Authorization
- Data protection

## Common Patterns

### Pattern A
Implementation details and examples.

### Pattern B
Implementation details and examples.

### Pattern C
Implementation details and examples.

## Anti-Patterns to Avoid

### Anti-Pattern 1
What not to do and why.

### Anti-Pattern 2
What not to do and why.

## Tools and Resources

### Recommended Tools
- Tool 1: Purpose
- Tool 2: Purpose
- Tool 3: Purpose

### Further Reading
- Resource 1
- Resource 2
- Resource 3

## Conclusion

Key takeaways for using this reference guide effectively.
