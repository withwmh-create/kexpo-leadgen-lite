# K-Expo LeadGen Lite (kexpo-leadgen-lite)

전시회 참가기업 리드 데이터를 다루는 실습용 미니 프로젝트입니다.
실제 크롤링 없이 샘플 데이터로 Lead Scoring을 진행하고 Streamlit 대시보드까지 시각화하는 것을 목표로 합니다.

## 폴더 구조 (Folder Structure)

```text
kexpo-leadgen-lite/
├── data/          # 샘플 데이터 및 결과 CSV 파일 저장소
├── scoring/       # Lead Scoring 평가 모델 로직
├── dashboard/     # Streamlit 대시보드 코드
└── docs/          # 문서 및 기획서 저장소
```

## 핵심 폴더 및 역할 요약

1. **`data/`**: 샘플 전시회(`exhibitions.csv`), 참가기업(`companies.csv`) 데이터 및 분석 결과(`lead_scores.csv`)를 보관합니다.
2. **`scoring/`**: 리드 점수를 계산하고 최종 등급을 분류하는 규칙 기반 스코어링 알고리즘을 포함합니다.
3. **`dashboard/`**: 분석 결과를 시각화하고 필터링해주는 Streamlit 대시보드 애플리케이션 코드를 포함합니다.
4. **`docs/`**: 기획 문서 및 분석 로직 정의 문서를 보관합니다.
