# 🏨 호텔 객실 수요 예측 시스템

## 📌 프로젝트 개요
호시노야 도쿄 인턴십 경험을 바탕으로 SK AX의 재고 관리 솔루션을 학습하고, 
Prophet 시계열 예측 모델을 활용하여 호텔 예약 수요를 예측하는 시스템을 구현했습니다.

## 🎯 프로젝트 목표
- 과거 호텔 예약 데이터를 분석하여 향후 30일 수요 예측
- SK AX의 수요 예측 기반 재고 관리 솔루션 이해 및 구현
- 실무에 적용 가능한 대시보드 개발

## 📊 데이터
- **출처**: Kaggle Hotel Booking Demand Dataset
- **기간**: 2015년 7월 ~ 2017년 8월
- **규모**: 약 119,390건의 호텔 예약 데이터

## 🛠️ 기술 스택
- **언어**: Python 3.10
- **라이브러리**:
  - pandas, numpy (데이터 처리)
  - matplotlib, seaborn (시각화)
  - Prophet (시계열 예측)
  - Streamlit (대시보드)
  - Plotly (인터랙티브 그래프)

## 📁 프로젝트 구조
Hotel_Project/
├── data/
│   ├── hotel_bookings.csv      # 원본 데이터
│   ├── daily_bookings.csv      # 전처리된 일별 데이터
│   └── forecast_results.csv    # 예측 결과
├── notebooks/
│   ├── 01_data_analysis.ipynb  # 데이터 분석 및 전처리
│   └── 02_prediction_model.ipynb  # 예측 모델
├── app.py                       # Streamlit 대시보드
└── README.md

## 🚀 실행 방법

### 환경 설정
```bash
conda create -n Hotel_Project python=3.10
conda activate Hotel_Project
conda install pandas numpy matplotlib seaborn jupyterlab scikit-learn
pip install prophet plotly streamlit